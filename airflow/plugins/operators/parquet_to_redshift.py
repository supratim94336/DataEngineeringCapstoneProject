from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults


class ParquetToRedshiftOperator(BaseOperator):
    @apply_defaults
    def __init__(self,
                 redshift_conn_id,
                 table,
                 s3_bucket,
                 s3_key,
                 sql_stmt,
                 iam_role,
                 *args, **kwargs):

        super(ParquetToRedshiftOperator, self).__init__(*args, **kwargs)
        self.table = table
        self.redshift_conn_id = redshift_conn_id
        self.s3_bucket = s3_bucket
        self.s3_key = s3_key
        self.sql_stmt = sql_stmt
        self.iam_role = iam_role

    def execute(self, context):
        redshift = PostgresHook(postgres_conn_id=self.redshift_conn_id)
        self.log.info("Copying data from S3 to Redshift")
        rendered_key = self.s3_key.format(**context)
        s3_path = "s3://{}/{}".format(self.s3_bucket, rendered_key)
        formatted_sql = self.sql_stmt.format(
            self.table,
            s3_path,
            self.iam_role
        )
        redshift.run(formatted_sql)
