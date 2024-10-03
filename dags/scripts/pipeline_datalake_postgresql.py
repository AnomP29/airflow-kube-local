import psycopg2
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
parser.add_option('--date_col', dest='date_col', help='table column represent date')
parser.add_option('--exc_date', dest='exc_date', help='execution date')
parser.add_option('--encr', dest='encr', help='encryption table or not')


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
if not options.encr:
    parser.error('encr is not given')


table = options.table
db = options.db
schema = options.schema
dataset = options.dataset
date_col = options.date_col
exc_date = options.exc_date
encr = options.encr
client = bigquery.Client('hijra-data-dev')

def get_count(schema, table, db_name, date_col, exc_date):
    # TODO: Ini juga perlu kita sederhanakan logic-nya.
    # Di sini untuk p2p perlu pakai db_name juga.
    if (db != 'hijra_staging' and table in ['audit_trail','log_login','anl_user_register','user_lounges','rdl_api_log']) == True:
#         if db == 'hijra' and table in ['application_activity']:
#             sql = "SELECT COUNT(*) FROM {}.{} WHERE DATE(insert_date) >= (CURRENT_DATE - INTERVAL '1 DAY')".format(schema,table)
        if db_name == 'p2p_prod' and table in ['rdl_api_log']:
            sql = "SELECT COUNT(*) FROM {}.{} WHERE to_char({}, 'YYYY-MM-DD/HH:MM') >= '{}'".format(schema,table,date_col,exc_date)
        if db == 'hijra' and table in ['anl_user_register']:
            sql = """
            SELECT COUNT(*) FROM {schema}.{table}
            WHERE 9=9
            AND id != 7934
            AND to_char({date_col}, 'YYYY-MM-DD') >= TO_CHAR((to_timestamp('{exc_date}', 'YYYY-MM-DD/HH24:MI') - INTERVAL '1 DAY'),'YYYY-MM-DD')
            AND to_char({date_col}, 'YYYY-MM-DD') <= TO_CHAR(TO_TIMESTAMP('{exc_date}', 'YYYY-MM-DD/HH24:MI'), 'YYYY-MM-DD')
            """.format(schema=schema,table=table,date_col=date_col, exc_date=exc_date)

            # sql = "SELECT COUNT(*) FROM {}.{} WHERE to_char({}, 'YYYY-MM-DD/HH:MM') >= '{}' AND id != 7934".format(schema,table,date_col,exc_date)
        # if db == 'hijra' and table in ['user_lounges']:
        #     sql = "SELECT COUNT(*) FROM {}.{} WHERE id != 7534".format(schema,table)
        # if db_name == 'p2p_prod' and table in ['log_login']:
        #     sql = "SELECT COUNT(*) FROM {}.{} WHERE DATE(log_date) >= (CURRENT_DATE - INTERVAL '2 DAY')".format(schema,table)
        # if db_name == 'p2p_prod' and table in ['audit_trail','application_activity']:
        #     sql = "SELECT COUNT(*) FROM {}.{} WHERE DATE(activity_date) >= (CURRENT_DATE - INTERVAL '5 DAY')".format(schema,table)
    else:
        sql = """
        SELECT COUNT(*) FROM {schema}.{table}
        WHERE 9=9
        AND to_char({date_col}, 'YYYY-MM-DD') >= TO_CHAR((to_timestamp('{exc_date}', 'YYYY-MM-DD/HH24:MI') - INTERVAL '1 DAY'),'YYYY-MM-DD')
        AND to_char({date_col}, 'YYYY-MM-DD') <= TO_CHAR(TO_TIMESTAMP('{exc_date}', 'YYYY-MM-DD/HH24:MI'), 'YYYY-MM-DD')
        """.format(schema=schema,table=table,date_col=date_col, exc_date=exc_date)

    # print(sql)
    # print(encr)
    df = rdbms_operator('postgres', 'hijra', sql).execute('Y')
    count = int(str(df['count'].values).replace('[','').replace(']',''))
    print(count)
    
    return count

def get_data(db, dataset, schema, table, db_name, date_col, exc_date):
    # Object client bigquery cursor
    client = bigquery.Client('hijra-data-dev')
    # client.query("""SELECT * FROM datalakes.{table} LIMIT 1""".format(table=table)).result()

    sql = """
    SELECT * FROM {schema}.{table} 
    WHERE 9=9
    AND to_char({date_col}, 'YYYY-MM-DD') >= TO_CHAR((to_timestamp('{exc_date}', 'YYYY-MM-DD/HH24:MI') - INTERVAL '1 DAY'),'YYYY-MM-DD')
    AND to_char({date_col}, 'YYYY-MM-DD') <= TO_CHAR(TO_TIMESTAMP('{exc_date}', 'YYYY-MM-DD/HH24:MI'), 'YYYY-MM-DD')
    """.format(schema=schema,table=table,date_col=date_col, exc_date=exc_date)
    
    results = rdbms_operator('postgres', 'hijra', sql).execute('N')
    
    print(sys.getsizeof(results))

    df = pd.DataFrame(results)
    df = df.applymap(lambda x: " ".join(x.splitlines()) if isinstance(x, str) else x)
    df = df.astype('str')    
    # df = df.fillna(value='', inplace=True)
    df = df.replace('None', '')
    df = df.replace('NaT', '')
    # df['row_loaded_ts'] = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S.%s')
    # df = df[['row_loaded_ts'] + [x for x in df.columns if x != 'row_loaded_ts']]

    tables___ = 'dl__{db}__{schema}__{table}__dev'.format(db=db, schema=schema, table=table)
    print('create TEMP tables')
    try:
        pandas_gbq.to_gbq(df, dataset + '.' + tables___ + '__temp' , project_id='hijra-data-dev',if_exists='append',api_method='load_csv', chunksize=100000)
    except Exception as e:
        print(e)
    else:
        # override temp_table_01
        sql = '''
        CREATE OR REPLACE TABLE {dataset}.{tables___}__temp
        AS
        SELECT CURRENT_TIMESTAMP() row_loaded_ts, * FROM {dataset}.{tables___}__temp
        '''.format(tables___ = tables___, dataset=dataset)

        client.query(sql).result()

        if encr == 'True':
            print(encr)
            pass
        # else:
        #     check_bq_tables(dataset, tables___)
        #     print(encr)

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
        df = pd.DataFrame(worksheet.get_all_records())
        # print(df)

    except gspread.exceptions.WorksheetNotFound as e:
        print("Trying to open non-existent sheet. Verify that the sheet name exists (%s)." % table)  

    # print(df)
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
                    ),CAST(tmptbl. \
                '''.lstrip().format(
                        dataset=dataset, 
                        table_name=table, 
                        key=encrypted_key, 
                        target_column=result["target_column"],
                        supported_key=result["Supported Key"]
                        ) + result["target_column"] + ' ' +
                ''' \
                    AS STRING), CAST( tmptbl.\
                '''.strip() + result["Supported Key"] + ' ' +
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


def main(db, dataset, schema, table, date_col, exc_date):
    # DB connect
    if db == 'hijra':
        db_host  = db_config.db_hijra_host
        db_username = db_config.db_hijra_username
        db_password = db_config.db_hijra_password
        db_name = db_config.db_hijra_name
        db_port = db_config.db_hijra_port

    print("Processing: {}: {}.{}".format(db, schema, table))

    count = get_count(schema, table, db_name, date_col, exc_date)
    print(count)

    tables___ = 'dl__{db}__{schema}__{table}__dev'.format(db=db, schema=schema, table=table)
    if count != 0:
        get_data(db, dataset, schema, table, db_name, date_col, exc_date)
        dframe = read_gsheet_file(db, dataset, schema, table)
        column_select, encrypted_key, column_list = transform_gsheet(dframe, tables___)
        bq_operator('hijra-data-dev', dataset, tables___, '', encr, column_select, encrypted_key, column_list)

    else:
        tables___ = 'dl__{db}__{schema}__{table}__dev'.format(db=db, schema=schema, table=table)
        # drop_tables(dataset, tables___)
    

    return "SUCCESS"

if __name__ == "__main__":
    main(db, dataset, schema, table, date_col, exc_date)
