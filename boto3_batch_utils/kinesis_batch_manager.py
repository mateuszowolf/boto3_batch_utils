import logging
from json import dumps

from boto3_batch_utils.base_dispatcher import BaseBatchManager
from boto3_batch_utils.utils import DecimalEncoder

logger = logging.getLogger()


kinesis_max_batch_size = 250


class KinesisBatchPutManager(BaseBatchManager):
    """
    Manage the batch 'put' of Kinesis records
    """

    def __init__(self, stream_name, partition_key_identifier='Id', max_batch_size=kinesis_max_batch_size, flush_payload_on_max_batch_size=True):
        self.stream_name = stream_name
        self.partition_key_identifier = partition_key_identifier
        super().__init__('kinesis', 'put_records', 'put_record', max_batch_size, flush_payload_on_max_batch_size)

    def _send_individual_payload(self, metric, retry=5):
        """ Send an individual metric to Cloudwatch """
        super()._send_individual_payload(metric)

    def _send_single_batch_to_kinesis(self, batch, nested=False):
        """
        Method to send a set of messages on to the Kinesis stream
        :param batch: List - messages to be sent
        :param nested: bool - Used for recursion identification. Do not override.
        """
        logger.debug("Attempting to send {} records to Kinesis::{}".format(len(batch), self.stream_name))
        response = self.kinesis_client.put_records(StreamName=self.stream_name, Records=batch)
        if "Records" in response:
            i = 0
            failed_records = []
            for r in response["Records"]:
                logger.debug("Response: {}".format(r))
                if "ErrorCode" in r:
                    logger.debug(
                        "Message failed to be processed, message will be retried. Message content: {}".format(r))
                    failed_records.append(i)
                i += 1
            successful_message_count = len(batch) - len(failed_records)
            if successful_message_count:
                logger.info("Sent messages to kinesis {}".format(successful_message_count))
            if failed_records:
                logger.debug(
                    "Failed Records: {}, Problems: {}".format(response["FailedRecordCount"], len(failed_records)))
                batch_of_problematic_records = [batch[i] for i in failed_records]
                self._send_single_batch_to_kinesis(batch_of_problematic_records, True)
            elif nested:
                logger.debug("Partial batch of {} records completed without error".format(len(batch)))

    def _batch_send_payloads(self, batch=None, **nested_batch):
        """ Attempt to send a single batch of metrics to Kinesis """
        self._send_single_batch_to_kinesis(batch)

    def flush_payloads(self):
        """ Push all metrics in the payload list to Kinesis """
        super().flush_payloads()

    def submit_payload(self, payload):
        """ Submit a metric ready to be batched up and sent to Kinesis """
        constructed_payload = {
            'Data': dumps(payload, cls=DecimalEncoder),
            'PartitionKey': '{}'.format(payload[self.partition_key_identifier])
        }
        super().submit_payload(constructed_payload)
