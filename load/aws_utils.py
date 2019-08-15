import boto3
from config import *
import json
from botocore.exceptions import ClientError
import sys
import time
import logging


class AWSUtils:

    def __init__(self, access_key, secret_key):
        self.access_key = access_key
        self.secret_key = secret_key
    
    @staticmethod
    def animate():
        chars = r"|/—\|"
        for char in chars:
            sys.stdout.write('\r' + 'Please Wait ...' + char)
            time.sleep(.1)
            sys.stdout.flush()
    
    def create_iam_role(self, iam_role):
        """
        This function creates an iam role based on your config
        :return:
        """
        iam = boto3.client('iam',
                           aws_access_key_id=self.access_key,
                           aws_secret_access_key=self.secret_key,
                           region_name='us-west-2'
                           )
        logging.info("1.1 creating role")
        try:
            iam.create_role(
                Path='/',
                RoleName=iam_role,
                Description="Allows Redshift to call AWS Services.",
                AssumeRolePolicyDocument=json.dumps(
                {'Statement': [{'Action': 'sts:AssumeRole',
                                'Effect': 'Allow',
                                'Principal':
                                    {'Service': 'redshift.amazonaws.com'}
                                }], 'Version': '2012-10-17'}))
    
        except ClientError as e:
            logging.info(f'ERROR: {e}')
    
        logging.info("1.2 Attaching Policy")
        try:
            iam.attach_role_policy(
                RoleName=iam_role,
                PolicyArn="arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess"
            )['ResponseMetadata']['HTTPStatusCode']
        except ClientError as e:
            logging.info(f'ERROR: {e}')
    
        logging.info("1.3 Get the IAM role ARN")
        role_arn = iam.get_role(RoleName=iam_role)['Role']['Arn']
        return role_arn
    
    def create_redshift_cluster(self, role_arn):
        """
        This function creates a cluster on your behalf
        :param role_arn:
        :return:
        """
        logging.info("1.1 Client is created ...")
        redshift = boto3.client('redshift',
                                region_name="us-west-2",
                                aws_access_key_id=self.access_key,
                                aws_secret_access_key=self.secret_key
                                )
        try:
            logging.info("1.2 Cluster config is being created ...")
            redshift.create_cluster(
                # HW
                ClusterType=DWH_CLUSTER_TYPE,
                NodeType=DWH_NODE_TYPE,
                NumberOfNodes=int(DWH_NUM_NODES),
    
                # Identifiers & Credentials
                DBName=DWH_DB,
                ClusterIdentifier=DWH_CLUSTER_IDENTIFIER,
                MasterUsername=DWH_DB_USER,
                MasterUserPassword=DWH_DB_PASSWORD,
    
                # Roles (for s3 access)
                IamRoles=[role_arn])
        except ClientError as e:
            logging.info(f'ERROR: {e}')
    
        logging.info("1.3 Cluster is being created ...")
        while redshift.describe_clusters(
                ClusterIdentifier=DWH_CLUSTER_IDENTIFIER)\
                ['Clusters'][0]['ClusterStatus'] != 'available':
            AWSUtils.animate()
    
        logging.info("\r1.4 Cluster is created successfully ...")
        return redshift.describe_clusters(
            ClusterIdentifier=DWH_CLUSTER_IDENTIFIER)['Clusters'][0]
        ['Endpoint']['Address']
    
    def delete_redshift_cluster(self):
        """
        This function deletes a cluster
        :return:
        """
        logging.info("1.1 Client is created ...")
        redshift = boto3.client('redshift',
                                region_name="us-west-2",
                                aws_access_key_id=self.access_key,
                                aws_secret_access_key=self.secret_key
                                )
        logging.info("1.2 Cluster is identified ...")
        try:
            redshift.delete_cluster(
                ClusterIdentifier=DWH_CLUSTER_IDENTIFIER,
                SkipFinalClusterSnapshot=True)
        except ClientError as e:
            logging.info(f'ERROR: {e}')
    
        try:
            logging.info("1.3 Cluster is being deleted ...")
            while redshift.describe_clusters(
                    ClusterIdentifier=DWH_CLUSTER_IDENTIFIER)\
                    ['Clusters'][0]['ClusterStatus'] == 'deleting':
                AWSUtils.animate()
        except:
            logging.info("\r1.4 Cluster is deleted successfully ...")
        return None
    
    def list_bucket(self, bucket_name, prefix):
        """
        This function lists files in a bucket
        :param bucket_name:
        :param prefix:
        :return: files
        """
        files = []
        s3 = boto3.resource('s3',
                            region_name="us-west-2",
                            aws_access_key_id=self.access_key,
                            aws_secret_access_key=self.secret_key
                            )
        bucket = s3.Bucket(bucket_name)
        for obj in bucket.objects.filter(Prefix=prefix):
            files.append(obj)
        return files
    
    def detach_iam_role(self, iam_role):
        iam = boto3.client('iam',
                           aws_access_key_id=self.access_key,
                           aws_secret_access_key=self.secret_key,
                           region_name='us-west-2'
                           )
        iam.detach_role_policy(RoleName=iam_role,
                               PolicyArn="arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess")
        iam.delete_role(RoleName=iam_role)
