from pyspark.sql import SparkSession
from os import listdir
from os.path import isfile, join
from pyspark.sql.types import *
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
import logging
import shutil
import os


class SAS7ToParquet(BaseOperator):

    ui_color = '#87CEFA'

    @apply_defaults
    def __init__(self,
                 input_path,
                 output_path,
                 *args, **kwargs):

        super(SAS7ToParquet, self).__init__(*args, **kwargs)
        self.input_path = input_path
        self.output_path = output_path

    def execute(self, context):
        logging.info("Creating spark session ...")
        spark = SparkSession.builder \
        .config("spark.jars.packages",
                "saurfang:spark-sas7bdat:2.0.0-s_2.11") \
        .enableHiveSupport() \
        .getOrCreate()

        # spark context
        sc = spark.sparkContext

        # column names
        logging.info('Defining column names and resulting schema ... ')
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

        logging.info('Reading sas7bdat files from disc ... ')
        onlyfiles = [join(self.input_path, f) for f in
                     listdir(self.input_path) if
                     isfile(join(self.input_path, f))]

        for f in onlyfiles:
            file_name, file_extension = os.path.splitext(f)
            if file_extension == '.' + 'sas7bdat':
                df_temp = spark.read.format(
                    'com.github.saurfang.sas.spark').load(f)\
                                                    .select(columns)
                df_all = df_all.union(df_temp)

        logging.info('Writing parquet to disc ... ')
        if os.path.exists(self.output_path):
            shutil.rmtree(self.output_path)

        df_temp = df_all.filter(df_all.i94addr.isNotNull())\
                        .filter(df_all.i94res.isNotNull())
        df_temp.write.parquet(self.output_path)