import gspread
import pandas as pd
import numpy as np
import json
import optparse

from google.cloud import bigquery
from google.oauth2 import service_account
from google.auth.transport.requests import AuthorizedSession

import os

# from pipeline_datalake_postgresql import check_bq_tables
from dependencies.bq_operator import bq_operator

# Object client bigquery cursor
client = bigquery.Client('hijra-data-dev')

# Tabulate
pd.options.display.max_colwidth = 100000

parser = optparse.OptionParser(usage="usage: %prog [options]")
parser.add_option('--table', dest='table', help='specify table source')
parser.add_option('--db', dest='db', help='specify database source')
parser.add_option('--schema', dest='schema', help='specify schema source')
parser.add_option('--dataset', dest='dataset', help='specify dataset source')

(options, args) = parser.parse_args()

if not options.table:
    parser.error('table is not given')
if not options.db:
    parser.error('database is not given')
if not options.schema:
    parser.error('schema is not given')
if not options.dataset:
    parser.error('dataset is not given')

table = options.table
db = options.db
schema = options.schema
dataset = options.dataset

print('encrypt_file.py')


def read_gsheet_file(db, dataset, schema, table):
    # Tabulate
    pd.options.display.max_colwidth = 100000

    # Attach credential file from developer google (API)
    print('connect to gsheet')
    scope = ['https://www.googleapis.com/auth/spreadsheets.readonly']
    credentials = service_account.Credentials.from_service_account_file('/opt/account/secrets/service_account2.json', scopes=scope)
    gc = gspread.Client(auth=credentials)
    gc.session = AuthorizedSession(credentials)

    # Target dataset
    dataset = dataset

    # Create the pandas DataFrame
    google_sheet_id = '1z-1SD-6rP0fukR_5HbtlZW2Wg9nbM1kOVQv8I6EBFMA'
    sheet = gc.open_by_key(google_sheet_id)

    try:
        worksheet = sheet.worksheet(table)
        list_of_lists = worksheet.get_all_values()
        df = pd.DataFrame(worksheet.get_all_records())
        # print(df)

    except gspread.exceptions.WorksheetNotFound as e:
        print("Trying to open non-existent sheet. Verify that the sheet name exists (%s)." % table)  
        
    return df  


def transform_gsheet(dframe):
    df = dframe
    if "PII" in df:
        if (any(df['PII'] == 'TRUE') == True) == True:
            df_selected = df[df['PII'] == 'TRUE']
            df_selected['data_type'] = 'BYTES'
            df_selected = df_selected.rename(columns={'Column Name':'target_column'})
            df_init = df_selected[['target_column','data_type','Supported Key']]
            df_inits = list(df_selected['target_column'])
            encrypted_key = df_selected.head(1)['Encrypted Key'].to_string(index=False)

def main(db, dataset, schema, table):
    dframe = read_gsheet_file(db, dataset, schema, table)
    transform_gsheet(dframe)

if __name__ == "__main__":
    main(db, dataset, schema, table)
