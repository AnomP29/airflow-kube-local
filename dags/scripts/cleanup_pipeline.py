import pandas as pd
import optparse
import numpy as np
import petl as etl
import pandas_gbq
import datetime as dt
import os
import pytz
import sys
import gspread


from pathlib import Path
from datetime import datetime
from google.cloud import bigquery
from google.oauth2 import service_account
from google.auth.transport.requests import AuthorizedSession
from google.api_core.exceptions import NotFound
from dependencies import db_config
from dependencies.rdbms_operator import rdbms_operator
from dependencies.bq_operator import bq_operator

pd.options.display.max_colwidth = 100000

parser = optparse.OptionParser(usage="usage: %prog [options]")
parser.add_option('--table', dest='table', help='specify table source')
parser.add_option('--db', dest='db', help='specify database source')
parser.add_option('--schema', dest='schema', help='specify schema source')
parser.add_option('--dataset', dest='dataset', help='specify dataset source')
# parser.add_option('--date_col', dest='date_col', help='table column represent date')
# parser.add_option('--exc_date', dest='exc_date', help='execution date')
# parser.add_option('--encr', dest='encr', help='encryption table or not')


(options, args) = parser.parse_args()

if not options.table:
    parser.error('table is not given')
if not options.db:
    parser.error('database is not given')
if not options.schema:
    parser.error('schema is not given')
if not options.dataset:
    parser.error('dataset is not given')
# if not options.date_col:
#     parser.error('date_col is not given')
# if not options.exc_date:
#     parser.error('exc_date is not given')
# if not options.encr:
#     parser.error('encr is not given')


table = options.table
db = options.db
schema = options.schema
dataset = options.dataset
# date_col = options.date_col
# exc_date = options.exc_date
# encr = options.encr
client = bigquery.Client('hijra-data-dev')


def __cleanup__(dataset, table):
    q_string='''
    DROP TABLE IF EXISTS {dataset}.{table}__temp
    '''.format(dataset=dataset, table=table)
    try:
        client.query(q_string)
    except Exception as e:
        print(e)
    
def main(db, dataset, schema, table):
    tables___ = 'dl__{db}__{schema}__{table}__dev'.format(db=db, schema=schema, table=table)
    __cleanup__(dataset, tables___)

if __name__ == "__main__":
    main(db, dataset, schema, table)
