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
    google_sheet_id = '1HSyAlLe7mWWOPKeNWE7H0dSO-xRysdCbZqb8RjtJ_g0'
    sheet = gc.open_by_key(google_sheet_id)

    try:
        worksheet = sheet.worksheet(table)
        list_of_lists = worksheet.get_all_values()
        df = pd.DataFrame(worksheet.get_all_records())
        # print(df)

    except gspread.exceptions.WorksheetNotFound as e:
        print("Trying to open non-existent sheet. Verify that the sheet name exists (%s)." % table)  
        df = ''
        
    return df  


def transform_gsheet(dframe, table):
    df = dframe
    if "PII" in df:
        if (any(df['PII'] == 'TRUE') == True) == True:
            df_selected = df[df['PII'] == 'TRUE']
            df_selected['data_type'] = 'BYTES'
            df_selected = df_selected.rename(columns={'Column Name':'target_column'})
            df_init = df_selected[['target_column','data_type','Supported Key']]
            df_inits = list(df_selected['target_column'])
            
            encrypted_key = df_selected.head(1)['Encrypted Key'].to_string(index=False)
            
            df_raw = df_selected.reset_index(drop=True)
            df_raw = df_raw.rename(
                columns={
                    'Data Type':'type'
                    ,'Required':'mode'
                    ,'target_column':'name'
                    ,'Description':'description'
                    }
                )
            # Get original schema
            query_string = """
            SELECT 
                column_name as target_column, 
                data_type
            FROM
                {dataset}.INFORMATION_SCHEMA.COLUMNS
            WHERE
                table_name='{table_name}'""".format(dataset=dataset,table_name=table)
            original_schema = client.query(query_string).to_dataframe()

            # Check table is partition or not
            query_string = """
            SELECT 
                *
            FROM
                {dataset}.INFORMATION_SCHEMA.COLUMNS
            WHERE
                table_name='{table_name}' AND is_partitioning_column = 'YES'
            """.format(dataset=dataset,table_name=table)
            is_partition = client.query(query_string).to_dataframe()
            partition = is_partition
            
            result = pd.merge(original_schema, df_init, on=["target_column"], how="left")
            result.replace(to_replace=[None], value=np.nan, inplace=True)
            result.fillna(value='', inplace=True)
            result["data_type_x"] = np.where((result["data_type_y"]==''), result["data_type_x"], result["data_type_y"])
            result["enc"] = np.where(
                (result["data_type_y"]=='BYTES'), 
                '''\
                AEAD.ENCRYPT(\
                    (\
                        SELECT keyset FROM enigma.{table_name}_keys keys \
                        WHERE keys.{key} = CONCAT(tmptbl.{key}, tmptbl.row_loaded_ts) \
                    ),CAST(tmptbl.'''.lstrip().format(
                        dataset=dataset, 
                        table_name=table, 
                        key=encrypted_key, 
                        target_column=result["target_column"],
                        supported_key=result["Supported Key"]
                        ) + result["target_column"] + ' ' +
                '''AS STRING), CAST(tmptbl.'''.lstrip() + result["Supported Key"] + ' ' +
                ''' \
                    AS STRING) \
                ) AS 
                '''.strip() + ' ' + result['target_column']
                ,result["target_column"]
                )
            
            enc = df_selected.drop_duplicates(subset='Encrypted Key', keep="first")
            enc = pd.merge(enc['Encrypted Key'], original_schema, left_on="Encrypted Key", right_on='target_column', how="outer")
            enc = enc.dropna()
            columns_enc = enc.target_column + ' ' + enc.data_type
            column_list_enc = pd.DataFrame(columns_enc).sort_index()
            column_list_enc = column_list_enc.to_string(header=False,index=False)
            
            
            # List column to select
            column_select = result.enc + ','.strip()
            column_select = column_select.to_string(header=False,index=False)
            column_select = " ".join(column_select.split())
            
            columns = result.target_column + ' ' + result.data_type_x + ','.strip()
            column_list = pd.DataFrame(columns).sort_index()
            column_list = column_list.to_string(header=False,index=False)
            column_list = " ".join(column_list.split())
            
            return column_select, encrypted_key, column_list
        
        else:
            # df_selected = df
            df_selected = df.rename(columns={'Column Name':'target_column'})
            df_selected['data_type'] = 'STRING'
            df_init = df_selected[['target_column','data_type','Supported Key']]
            df_raw = df_selected.reset_index(drop=True)
            df_raw = df_raw.rename(
                columns={
                    'Data Type':'type'
                    ,'Required':'mode'
                    ,'target_column':'name'
                    ,'Description':'description'
                    }
                )
            # Get original schema
            query_string = """
            SELECT 
                column_name as target_column, 
                data_type
            FROM
                {dataset}.INFORMATION_SCHEMA.COLUMNS
            WHERE
                table_name='{table_name}'""".format(dataset=dataset,table_name=table)
            original_schema = client.query(query_string).to_dataframe()

            # Check table is partition or not
            query_string = """
            SELECT 
                *
            FROM
                {dataset}.INFORMATION_SCHEMA.COLUMNS
            WHERE
                table_name='{table_name}' AND is_partitioning_column = 'YES'
            """.format(dataset=dataset,table_name=table)
            is_partition = client.query(query_string).to_dataframe()
            partition = is_partition
            
            result = pd.merge(original_schema, df_init, on=["target_column"], how="left")
            result.replace(to_replace=[None], value=np.nan, inplace=True)
            result.fillna(value='', inplace=True)
            result["data_type_x"] = np.where((result["data_type_y"]==''), result["data_type_x"], result["data_type_y"])
            
            
            # List column to select
            column_select = result.target_column + ','.strip()
            column_select = column_select.to_string(header=False,index=False)
            column_select = " ".join(column_select.split())
            
            columns = result.target_column + ' ' + result.data_type_x + ','.strip()
            column_list = pd.DataFrame(columns).sort_index()
            column_list = column_list.to_string(header=False,index=False)
            column_list = " ".join(column_list.split())

            return column_select, '', column_list


def main(db, dataset, schema, table):
    tables___ = 'dl__{db}__{schema}__{table}__dev'.format(db=db, schema=schema, table=table)
    dframe = read_gsheet_file(db, dataset, schema, table)
    if not dframe.empty:
        column_select, encrypted_key, column_list = transform_gsheet(dframe, tables___)
        bq_operator('hijra-data-dev', dataset, tables___, '', '', column_select, encrypted_key, column_list).__encryption__()
    else:
        raise ValueError('Trying to open non-existent sheet. Verify that the sheet name exists ' + table + '.')

if __name__ == "__main__":
    main(db, dataset, schema, table)
