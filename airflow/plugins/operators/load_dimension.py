from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults


class LoadDimensionOperator(BaseOperator):
    ui_color = '#358140'

    @apply_defaults
    def __init__(self,
                 redshift_conn_id,
                 table,
                 sql_stmt,
                 mode,
                 *args, **kwargs):

        super(LoadDimensionOperator, self).__init__(*args, **kwargs)
        self.redshift_conn_id = redshift_conn_id
        self.table = table
        self.sql_stmt = sql_stmt
        self.mode = mode.lower()

    def execute(self, context):
        self.log.info(f""" Creating Postgres hook """)
        redshift = PostgresHook(self.redshift_conn_id)
        self.log.info(f""" Loading Data into table {self.table} """)
        if self.mode == 'update':
            formatted_sql = f""" INSERT INTO {self.table} ({self.sql_stmt})"""
            redshift.run(formatted_sql)
        elif self.mode == "insert":
            formatted_sql = f"""TRUNCATE TABLE {self.table}; 
                                INSERT INTO {self.table} ({self.sql_stmt})"""
            redshift.run(formatted_sql)


