import configparser

config = configparser.ConfigParser()
config.read_file(open('dwh.cfg'))

# amazon aws
KEY = config.get('AWS', 'key')
SECRET = config.get('AWS', 'secret')

# Redshift
DWH_CLUSTER_TYPE = config.get('DWH', 'DWH_CLUSTER_TYPE')
DWH_NUM_NODES = config.get('DWH', 'DWH_NUM_NODES')
DWH_NODE_TYPE = config.get('DWH', 'DWH_NODE_TYPE')

DWH_IAM_ROLE_NAME = config.get('DWH', 'DWH_IAM_ROLE_NAME')
DWH_CLUSTER_IDENTIFIER = config.get('DWH', 'DWH_CLUSTER_IDENTIFIER')
DWH_DB = config.get('DWH', 'DWH_DB')
DWH_DB_USER = config.get('DWH', 'DWH_DB_USER')
DWH_DB_PASSWORD = config.get('DWH', 'DWH_DB_PASSWORD')
DWH_PORT = config.get('DWH', 'DWH_PORT')
DWH_SCHEMA = config.get('DWH', 'DWH_SCHEMA')
DWH_REGION = config.get('DWH', 'DWH_REGION')

# S3
LOG_JSON_FORMAT = config.get('S3', 'LOG_JSON_FORMAT')
S3_BUCKET_LOG_JSON_PATH = config.get('S3', 'S3_BUCKET_LOG_JSON_PATH')
S3_BUCKET_SONG_JSON_PATH = config.get('S3', 'S3_BUCKET_SONG_JSON_PATH')