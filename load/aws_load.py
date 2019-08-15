import os
from boto3.s3.transfer import S3Transfer
import boto3
import logging


class AWSLoad:

    def __init__(self, access_key, secret_key):
        self.access_key = access_key
        self.secret_key = secret_key

    def transfer_files_to_s3(self, input_path, bucket_name, file_ext):
        """
        This function transfers data from local file system to remote S3
        storage
        :param input_path:
        :param bucket_name:
        :param file_ext:
        :return:
        """
        client = boto3.client('s3', aws_access_key_id=self.access_key,
                              aws_secret_access_key=self.secret_key)
        transfer = S3Transfer(client)
        for subdir, dirs, files in os.walk(input_path):
            for file in files:
                file_name, file_extension = os.path.splitext(file)
                full_path = os.path.join(subdir, file)
                if file_extension == '.' + file_ext:
                    logging.info("transferring file {}".format(file_name))
                    transfer.upload_file(full_path, bucket_name, file_ext
                                         + '/' + file)
