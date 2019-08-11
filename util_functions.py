import pandas as pd
import re
import os
from boto3.s3.transfer import S3Transfer
import boto3
import configparser
import logging
from pyspark.sql import SparkSession
from os import listdir
from os.path import isfile, join
from pyspark.sql.types import *


# to be moved later
config = configparser.ConfigParser()
config.read_file(open('dl.cfg'))
os.environ['AWS_ACCESS_KEY_ID'] = config['AWS']['KEY']
os.environ['AWS_SECRET_ACCESS_KEY'] = config['AWS']['SECRET']
access_key = config['AWS']['KEY']
secret_key = config['AWS']['SECRET']


def extract_sas_labels(file_path, output_path):
    """
    This function reads the SAS label descriptions and produces CSV
    files out of it for country, port, visa, state, mode
    :param file_path:
    :param output_path:
    :return:
    example:
    file_path = r"./data/I94_SAS_Labels_Descriptions.SAS"
    output_path = r"./output"
    """
    with open(file_path, "r") as f:
        file = f.read()

        sas_label_ext = {}
        temp_data = []
        attr_name = ''
        attr_desc = ''

        logging.info("reading file ...")
        for line in file.split("\n"):
            line = re.sub(r"\s+|\t+|\r+", " ", line)

            if "/*" in line and "-" in line:
                attr_name, attr_desc = [item.strip(" ") for item in
                                        line.split("*")[1].split("-",
                                                                 1)]
                attr_name = attr_name.replace(' & ', '&').lower()
                if attr_name != '':
                    sas_label_ext[attr_name] = {'desc': attr_desc}
            elif '=' in line:
                temp_data.append([item.strip(';').strip(" ").replace(
                    '\'', '').lstrip().rstrip().title() for item in
                                  line.split('=')])
            elif len(temp_data) > 0:
                if attr_name != '':
                    sas_label_ext[attr_name]['data'] = temp_data
                    temp_data = []

        # country
        logging.info("preparing country codes ...")
        sas_label_ext['i94cit&i94res']['df'] = pd.DataFrame(
            sas_label_ext['i94cit&i94res']['data'],
            columns=['country_code', 'country_name'])

        # port
        logging.info("preparing port codes ...")
        tempdf = pd.DataFrame(sas_label_ext['i94port']['data'],
                              columns=['port_code', 'port_name'])
        tempdf['port_code'] = tempdf['port_code'].str.upper()
        tempdf[['port_city', 'port_state']] = tempdf[
            'port_name'].str.rsplit(',', 1, expand=True)
        tempdf['port_state'] = tempdf['port_state'].str.upper()
        sas_label_ext['i94port']['df'] = tempdf

        # mode
        logging.info("preparing transport modes ...")
        sas_label_ext['i94mode']['df'] = pd.DataFrame(
            sas_label_ext['i94mode']['data'],
            columns=['trans_code', 'trans_name'])
        tempdf = pd.DataFrame(sas_label_ext['i94addr']['data'],
                              columns=['state_code', 'state_name'])
        tempdf['state_code'] = tempdf['state_code'].str.upper()

        # address
        logging.info("preparing state codes ...")
        sas_label_ext['i94addr']['df'] = tempdf

        # visa
        logging.info("preparing visa codes ...")
        sas_label_ext['i94visa']['df'] = pd.DataFrame(
            sas_label_ext['i94visa']['data'],
            columns=['reason_code', 'reason_travel'])

        # write to csv
        logging.info("writing to csv files ...")
        for table in sas_label_ext.keys():
            if 'df' in sas_label_ext[table].keys():
                with open(os.path.join(output_path, table + ".csv"), "w") as f:
                    sas_label_ext[table]['df'].to_csv(f, index=False)


def transfer_files_to_s3(input_path, bucket_name, file_ext):
    """
    This function transfers data from local file system to remote S3
    storage
    :param input_path:
    :param bucket_name:
    :param file_ext:
    :return:
    """
    client = boto3.client('s3', aws_access_key_id=access_key,
                          aws_secret_access_key=secret_key)
    transfer = S3Transfer(client)
    for subdir, dirs, files in os.walk(input_path):
        for file in files:
            file_name, file_extension = os.path.splitext(file)
            full_path = os.path.join(subdir, file)
            if file_extension == '.' + file_ext:
                logging.info("transferring file {}".format(file_name))
                transfer.upload_file(full_path, bucket_name, file_ext
                                     + '/' + file)


def create_dataframe_from_sas(filepath):
    """
    This function reads all the sas formatted files and returns a final
    dataframe containing all the required and consolidated rows as a
    pandas dataframe
    :param filepath:
    :return: df_all
    """
    # spark session
    logging.info("creating spark session ...")
    spark = SparkSession.builder \
                        .config("spark.jars.packages",
                                "saurfang:spark-sas7bdat:2.0.0-s_2.11")\
                        .enableHiveSupport() \
                        .getOrCreate()

    # spark context
    sc = spark.sparkContext

    # column names
    logging.info("defining column names and resulting schema ...")
    columns = ['cicid',
               'i94yr',
               'i94mon',
               'i94cit',
               'i94res',
               'i94port',
               'arrdate',
               'i94mode',
               'i94addr',
               'depdate',
               'i94bir',
               'i94visa',
               'count',
               'dtadfile',
               'visapost',
               'occup',
               'entdepa',
               'entdepd',
               'entdepu',
               'matflag',
               'biryear',
               'dtaddto',
               'gender',
               'insnum',
               'airline',
               'admnum',
               'fltno',
               'visatype']

    # schema definition
    schema = StructType([
        StructField('cicid', DoubleType(), True),
        StructField('i94yr', DoubleType(), True),
        StructField('i94mon', DoubleType(), True),
        StructField('i94cit', DoubleType(), True),
        StructField('i94res', DoubleType(), True),
        StructField('i94port', StringType(), True),
        StructField('arrdate', DoubleType(), True),
        StructField('i94mode', DoubleType(), True),
        StructField('i94addr', StringType(), True),
        StructField('depdate', DoubleType(), True),
        StructField('i94bir', DoubleType(), True),
        StructField('i94visa', DoubleType(), True),
        StructField('count', DoubleType(), True),
        StructField('dtadfile', StringType(), True),
        StructField('visapost', StringType(), True),
        StructField('occup', StringType(), True),
        StructField('entdepa', StringType(), True),
        StructField('entdepd', StringType(), True),
        StructField('entdepu', StringType(), True),
        StructField('matflag', StringType(), True),
        StructField('biryear', DoubleType(), True),
        StructField('dtaddto', StringType(), True),
        StructField('gender', StringType(), True),
        StructField('insnum', StringType(), True),
        StructField('airline', StringType(), True),
        StructField('admnum', DoubleType(), True),
        StructField('fltno', StringType(), True),
        StructField('visatype', StringType(), True)
    ])

    df_all = spark.createDataFrame(sc.emptyRDD(), schema)

    onlyfiles = [join(filepath, f) for f in listdir(filepath) if
                 isfile(join(filepath, f))]

    logging.info("reading files from the disc ... ")
    for f in onlyfiles:
        df_temp = spark.read.format(
            'com.github.saurfang.sas.spark').load(f).select(columns)
        df_all = df_all.union(df_temp)

    return df_all.toPandas()
