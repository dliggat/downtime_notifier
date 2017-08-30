import boto3
import datetime
import logging
import sys

from downtime_notifier import configuration
from downtime_notifier import Checker
from downtime_notifier import StateTracker


MAX_LEN = 100
CONFIG = configuration()

def setup_logging(request_id):
    """Creates the logging formatter.

    Args:
        request_id: (str) The id of the execution context (i.e. the Lambda execution ID).
    """
    logger = logging.getLogger()
    logger.info('Setting up logging')
    console_handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '[%(levelname)s] %(asctime)s {0} [thread %(threadName)s][%(module)s:%(lineno)d]: %(message)s'.format(request_id))
    console_handler.setFormatter(formatter)

    logger.handlers = []  # Get rid of any default handlers (Lambda apparently adds one).
    logger.addHandler(console_handler)
    logger.setLevel(logging.INFO)
    return logger


def handler(event, context):
    """Entry point for the Lambda function."""
    global logger
    logger = setup_logging(context.aws_request_id)
    logger.info('Using configuration: {0}'.format(CONFIG))
    logger.info('Using event: {0}'.format(event))
    logger.info('Using context: {0}'.format(context))


    # Build a Checker object; start each as a thread and join on the set.
    checkers = []
    for site in CONFIG.get('sites', []):
        c = Checker(**site)
        c.start()
        checkers.append(c)

    for checker in checkers:
        checker.join()

    # Record the outcome of each Checker in the result table via a StateTracker.
    timestamp = datetime.datetime.now()
    trackers = [StateTracker(c, CONFIG['dynamo_table'], timestamp) for c in checkers]
    for tracker in trackers:
        tracker.put_result()

    # Notify the SNS topic if any StateTracker indicates thusly.
    checkers_to_notify = [t.checker for t in trackers if t.notify]
    if checkers_to_notify:
        if any([c.exceptional for c in checkers_to_notify]):
            title_prefix = CONFIG['downtime_detected_prefix']
        else:
            title_prefix = CONFIG['state_changed_prefix']
        logger.warn('{0} Will notify SNS topic'.format(title_prefix))
        notify(checkers_to_notify, title_prefix)
    else:
        logger.info('All checks passed.')


def notify(checkers, title_prefix):
    """Craft a message about the site downtime, and publish to the SNS topic.

    Args:
        checkers: (list) Sites which failed the check.
        title_prefix: (str) A prefix for the SNS message.
    """
    subject = "{0} {1}".format(title_prefix, ', '.join([r.name for r in checkers]))
    message = CONFIG['greeting'] + ',\n\n' + '\n\n'.join(
        ['{0}) {1} ({2}): {3}'.format(i, r.name, r.url, r.message) for i, r in enumerate(checkers)])

    client = boto3.client('sns')
    response = client.publish(
        TopicArn=CONFIG['topic_arn'],
        Message=message,
        Subject=subject[0:MAX_LEN],
        MessageStructure='string')
    logger.info(response)


if __name__ == '__main__':
    # For invoking the lambda function in the local environment.
    from downtime_notifier import LocalContext
    context = LocalContext()
    handler(None, context)
