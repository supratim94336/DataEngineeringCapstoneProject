from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults


class DataQualityOperator(BaseOperator):

    ui_color = '#89DA59'

    @apply_defaults
    def __init__(self,
                 redshift_conn_id,
                 sql_stmt,
                 tables,
                 *args, **kwargs):

        super(DataQualityOperator, self).__init__(*args, **kwargs)
        self.redshift_conn_id = redshift_conn_id
        self.sql_stmt = sql_stmt
        self.tables = tables

    def execute(self, context):
        self.log.info(f""" Checking ETL result quality """)
        redshift = PostgresHook(self.redshift_conn_id)
        for cur_table in self.tables:
            try:
                if redshift.run(self.sql_stmt.format(cur_table)) == 1:
                    self.log.info(f""" Quality test passed for {cur_table} """)
            except Exception:
                raise ValueError(f""" Quality check for {cur_table} """)