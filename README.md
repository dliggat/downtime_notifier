# Downtime Notifier

A Lambda function that monitors a set of websites, and [smartly] notifies an SNS topic about a change in the up/down state.

## Procedure

Specifically, it does the following:

For each invocation of a CloudWatch Event:

1. Read configuration details, some of which are in SSM Parameter Store
2. For each website in the configuration:
  a. Attempt an HTTP GET
  b. Inspect the result for an `expected_code` or `expected_text`
  c. Record the result to DynamoDB
  d. If the up/down state has changed from the prior DynamoDB record, notify the SNS topic

