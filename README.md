![Master Pipeline](https://github.com/g-farrow/boto3_batch_utils/workflows/Master%20Pipeline/badge.svg)

Boto3 Batch Utils
=================
This library offers some functionality to assist in writing records to AWS services in batches, where your data is not 
naturally batched. This helps to achieve significant efficiencies when interacting with those AWS services as batch 
writes are often much more efficient than individual writes.

[Documentation]()

# Installation
The package can be installed using `pip`:
```
pip install boto3-batch-utils
```

You may install a specific version of the package:
```
pip install boto3-batch-utils==3.0.0
```

### Boto3 and Configuration
Boto3 Batch Utils is an abstraction around AWS' Boto3 library. `boto3` is a dependency and will be installed 
automatically, if it is not already present.

You will need to configure your AWS credentials and roles in exactly the same way as you would if using `boto3`
directly.

For more information on `boto3` configuration, refer to the AWS documentation 
[here](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html).

# Concepts
The library is very simple to use. To use it, you must initialise a client, send it the payloads you want to transmit
 and finally tell the client to clear down.

To use the package you do not need care how to batch up the payloads and send them into their target service. The 
package will take care of this for you. This allows you to utilise the significant efficiencies of `boto3`'s batch 
send/put/write methods, without the headaches of error handling and batch sizes.

Each of the supported services has it's own dispatcher client. Each has the same 2 methods with which to interact. So
interacting with each of the various service clients is similar and follows the same 3 steps: 
* **Initialise**: Instantiate the batch dispatcher, passing in the required configuration. e.g. 
`sqs_client = SQSBatchDispatcher("MySqsQueue")`
* **submit_payload**: pass in a payload (e.g. a single message, metric etc): e.g.
`sqs_client.submit_payload({'test': 'message'})`
* **flush_payloads**: send all payloads in the backlog. e.g. `sqs_client.flush_payloads()`

> If you are using `boto3-batch-utils` in AWS Lambda, you should call `.flush_payloads()` at the end of every 
invocation.

# Supported Services

## Kinesis
### Abstracted Boto3 Methods:
* `put_records()`
* `put_record()`

### Example
Batch Put items to a Kinesis stream
```python
from boto3_batch_utils import KinesisBatchDispatcher


kn = KinesisBatchDispatcher('MyExampleStreamName')

kn.submit_payload({"something": "in", "my": "message"})
kn.submit_payload({"tells": "me", "this": "is", "easy": True})

kn.flush_payloads()
```

## Dynamo
### Abstracted Boto3 Methods:
* `batch_write_item()`

### Example
Batch write records to a DynamoDB table
```python
from boto3_batch_utils import DynamoBatchDispatcher


dy = DynamoBatchDispatcher('MyExampleDynamoTable', partition_key='Id')

dy.submit_payload({"something": "in", "my": "message"})
dy.submit_payload({"tells": "me", "this": "is", "easy": True})

dy.flush_payloads()
```

## Cloudwatch
#### Abstracted Boto3 Methods:
* `put_metric_data()`

#### Example
Batch put metric data to Cloudwatch. Cloudwatch comes with a handy dimension builder function `cloudwatch_dimension` 
to help you construct dimensions
```python
from boto3_batch_utils import CloudwatchBatchDispatcher, cloudwatch_dimension


cw = CloudwatchBatchDispatcher('TestService')

cw.submit_payload('DoingACountMetric', dimensions=cloudwatch_dimension('dimA', '12345'), value=555, unit='Count')
cw.submit_payload('DoingACountMetric', dimensions=cloudwatch_dimension('dimA', '12345'), value=1234, unit='Count')

cw.flush_payloads()
```

## SQS Standard Queues
#### Abstracted Boto3 Methods:
* `send_message_batch`
* `send_message`

#### Example
Batch send messages to an SQS queue
```python
from boto3_batch_utils import SQSBatchDispatcher


sqs = SQSBatchDispatcher("aQueueWithAName")

sqs.submit_payload("some message of some sort")
sqs.submit_payload("a different message, probably a similar sort")

sqs.flush_payloads()
```

## SQS FIFO Queues
#### Abstracted Boto3 Methods:
* `send_message_batch`
* `send_message`

#### Example
Batch send messages to an SQS queue
```python
from boto3_batch_utils import SQSFifoBatchDispatcher


sqs = SQSFifoBatchDispatcher("aQueueWithAName")

sqs.submit_payload("some message of some sort")
sqs.submit_payload("a different message, probably a similar sort")

sqs.flush_payloads()
```