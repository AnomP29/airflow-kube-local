import gspread
import pandas as pd
import numpy as np
import json
import optparse

from google.cloud import bigquery
from google.oauth2 import service_account
from google.auth.transport.requests import AuthorizedSession

import os

from pipeline_datalake_postgresql import check_bq_tables

# Object client bigquery cursor
client = bigquery.Client('hijra-data-dev')

# Tabulate
pd.options.display.max_colwidth = 100000

parser = optparse.OptionParser(usage="usage: %prog [options]")
parser.add_option('--table', dest='table', help='specify table source')
parser.add_option('--db', dest='db', help='specify database source')
parser.add_option('--schema', dest='schema', help='specify schema source')
parser.add_option('--dataset', dest='dataset', help='specify dataset source')
parser.add_option('--date_col', dest='date_col', help='table column represent date')
parser.add_option('--exc_date', dest='exc_date', help='execution date')

(options, args) = parser.parse_args()

if not options.table:
    parser.error('table is not given')
if not options.db:
    parser.error('database is not given')
if not options.schema:
    parser.error('schema is not given')
if not options.dataset:
    parser.error('dataset is not given')
if not options.date_col:
    parser.error('date_col is not given')
if not options.exc_date:
    parser.error('exc_date is not given')

table = options.table
db = options.db
schema = options.schema
dataset = options.dataset
date_col = options.date_col
exc_date = options.exc_date




print('encrypt_file.py')


def main(db, dataset, schema, table, date_col):
    # Tabulate
    pd.options.display.max_colwidth = 100000

    # Attach credential file from developer google (API)
    print('connect to gsheet')
    scope = ['https://www.googleapis.com/auth/spreadsheets.readonly']
    credentials = service_account.Credentials.from_service_account_file('/opt/account/secrets/dwh_hijra_lake.json', scopes=scope)
    gc = gspread.Client(auth=credentials)
    gc.session = AuthorizedSession(credentials)

    # Target dataset
    dataset = 'hijra_lake'

    # Create the pandas DataFrame
    google_sheet_id = '1z-1SD-6rP0fukR_5HbtlZW2Wg9nbM1kOVQv8I6EBFMA'
    sheet = gc.open_by_key(google_sheet_id)




if __name__ == "__main__":
    main(db, dataset, schema, table, date_col)
