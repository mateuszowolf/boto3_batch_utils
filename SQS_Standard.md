layout: page
title: SQS Standard
permalink: /sqs-standard/

# SQS Standard Queues
## Abstracted Boto3 Methods:
* `send_message_batch`
* `send_message`

## Example
Batch send messages to an SQS queue
```python
from boto3_batch_utils import SQSBatchDispatcher


sqs = SQSBatchDispatcher("aQueueWithAName")

sqs.submit_payload("some message of some sort")
sqs.submit_payload("a different message, probably a similar sort")

sqs.flush_payloads()
```