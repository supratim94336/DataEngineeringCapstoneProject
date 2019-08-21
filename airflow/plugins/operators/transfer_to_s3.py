from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
import logging
import os
from boto3.s3.transfer import S3Transfer
import boto3
from airflow.contrib.hooks.aws_hook import AwsHook


class TransferToS3Operator(BaseOperator):

    ui_color = '#89DA59'

    @apply_defaults
    def __init__(self,
                 aws_credentials_id,
                 input_path,
                 bucket_name,
                 file_ext,
                 *args, **kwargs):

        super(TransferToS3Operator, self).__init__(*args, **kwargs)
        self.aws_credentials_id = aws_credentials_id
        self.input_path = input_path
        self.bucket_name = bucket_name
        self.file_ext = file_ext

    def execute(self, context):
        logging.info('Reading AWS Credentials ... ')
        aws_hook = AwsHook(self.aws_credentials_id)
        credentials = aws_hook.get_credentials()
        client = boto3.client(
                            's3',
                            aws_access_key_id=credentials.access_key,
                            aws_secret_access_key=credentials.secret_key)
        transfer = S3Transfer(client)
        logging.info('Copying Files ... ')
        for subdir, dirs, files in os.walk(self.input_path):
            for file in files:
                file_name, file_extension = os.path.splitext(file)
                full_path = os.path.join(subdir, file)
                if file_extension == '.' + self.file_ext:
                    logging.info(
                        "transferring file {}".format(file_name))
                    transfer.upload_file(full_path, self.bucket_name,
                                         self.file_ext
                                         + '/' + file)
        logging.info('Successfully finished copying all the files ... ')
