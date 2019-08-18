from __future__ import division, absolute_import, print_function
from airflow.plugins_manager import AirflowPlugin
import operators
import helpers

# Defining the plugin class
class UdacityPlugin(AirflowPlugin):
    name = "udacity_plugin"
    operators = [
        operators.SASToCSVOperator,
        operators.TransferToS3Operator,
        operators.SAS7ToParquet,
        operators.StageToRedshiftOperator,
        operators.ParquetToRedshiftOperator
    ]
    helpers = [
        helpers.SqlQueries
    ]