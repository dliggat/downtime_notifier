# Downtime Notifier

A Lambda function that monitors a set of websites, and [smartly] notifies an SNS topic about a change in the up/down state.

## Procedure

Specifically, it does the following:

For each invocation of a CloudWatch Event:

1. Read configuration details, some of which are in SSM Parameter Store
2. For each website in the configuration:
    1. Attempt an HTTP `GET`
    2. Inspect the result for an `expected_code` or `expected_text`
    3. Record the result to DynamoDB
    4. If the up/down state has changed from the prior DynamoDB record, mark this site for notification
3. If any sites have been marked for notification, collate the results and notify the SNS topic

