import logging

from boto3_batch_utils.Base import BaseDispatcher
from boto3_batch_utils.utils import convert_floats_in_dict_to_decimals

logger = logging.getLogger()

dynamodb_batch_write_limit = 25


class DynamoBatchDispatcher(BaseDispatcher):
    """
    Control the submission of writes to DynamoDB
    """

    def __init__(self, dynamo_table_name, primary_partition_key, partition_key_data_type=str,
                 max_batch_size=dynamodb_batch_write_limit, flush_payload_on_max_batch_size=True):
        self.dynamo_table_name = dynamo_table_name
        self.primary_partition_key = primary_partition_key
        self.partition_key_data_type = partition_key_data_type
        super().__init__('dynamodb', 'batch_write_item', batch_size=max_batch_size,
                         flush_payload_on_max_batch_size=flush_payload_on_max_batch_size)
        self.individual_dispatch_method = self.subject.Table(self.dynamo_table_name).put_item

    def _send_individual_payload(self, payload, retry=4):
        """
        Write an individual record to Dynamo
        :param payload: JSON representation of a new record to write to the Dynamo table
        """
        super()._send_individual_payload(payload, retry=4)

    def _process_batch_send_response(self, response):
        """
        Parse the response from a batch_write call, handle any failures as required.
        :param response: Response JSON from a batch_write_item request
        """
        unprocessed_items = response['UnprocessedItems']
        if unprocessed_items:
            logger.warning("Batch write failed to write all items, {} were rejected".format(
                len(unprocessed_items[self.dynamo_table_name])))
            for item in unprocessed_items[self.dynamo_table_name]:
                self._send_individual_payload(item)

    def _batch_send_payloads(self, batch=None, **nested_batch):
        """
        Submit the batch to DynamoDB
        """
        super()._batch_send_payloads({'RequestItems': {self.dynamo_table_name: batch}})

    def flush_payloads(self):
        """
        Send any metrics remaining in the current batch bucket
        """
        super().flush_payloads()

    def submit_payload(self, payload, partition_key_location="Id"):
        """
        Submit a metric ready for batch sending to Cloudwatch
        """
        if self.primary_partition_key not in payload.keys():
            payload[self.primary_partition_key] = self.partition_key_data_type(payload[partition_key_location])
        super().submit_payload(
            {"PutRequest": {
                "Item": convert_floats_in_dict_to_decimals(payload)
            }}
        )
