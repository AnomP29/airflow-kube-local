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
from datetime import datetime, timedelta


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
parser.add_option('--gsheet', dest='gsheet', help='GoogleSheet Id')

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
if not options.gsheet:
    parser.error('gsheet is not given')


table = options.table
db = options.db
schema = options.schema
dataset = options.dataset
date_col = options.date_col
exc_date = options.exc_date
encr = options.encr
gsheet = options.gsheet
client = bigquery.Client('hijra-data-dev')

def get_count(schema, table, db_name, date_col, exc_date):
    if (db != 'hijra_staging' and table in ['audit_trail','log_login','anl_user_register','user_lounges','rdl_api_log']) == True:
        if db_name == 'p2p_prod' and table in ['rdl_api_log']:
            sql = "SELECT COUNT(*) FROM {}.{} WHERE to_char({}, 'YYYY-MM-DD/HH:MM') >= '{}'".format(schema,table,date_col,exc_date)

        if db == 'hijra' and table in ['user_lounges']:
            sql = """
            SELECT COUNT(*) FROM {schema}.{table}
            WHERE 9=9
            AND id != 7534
            AND to_char({date_col}, 'YYYY-MM-DD') >= TO_CHAR((to_timestamp('{exc_date}', 'YYYY-MM-DD/HH24:MI') - INTERVAL '1 DAY'),'YYYY-MM-DD')
            AND to_char({date_col}, 'YYYY-MM-DD') <= TO_CHAR(TO_TIMESTAMP('{exc_date}', 'YYYY-MM-DD/HH24:MI'), 'YYYY-MM-DD')
            """.format(schema=schema,table=table,date_col=date_col, exc_date=exc_date)
        
        if db == 'hijra' and table in ['anl_user_register']:
            sql = """
            SELECT COUNT(*) FROM {schema}.{table}
            WHERE 9=9
            AND id != 7934
            AND to_char({date_col}, 'YYYY-MM-DD') >= TO_CHAR((to_timestamp('{exc_date}', 'YYYY-MM-DD/HH24:MI') - INTERVAL '1 DAY'),'YYYY-MM-DD')
            AND to_char({date_col}, 'YYYY-MM-DD') <= TO_CHAR(TO_TIMESTAMP('{exc_date}', 'YYYY-MM-DD/HH24:MI'), 'YYYY-MM-DD')
            """.format(schema=schema,table=table,date_col=date_col, exc_date=exc_date)

            # sql = "SELECT COUNT(*) FROM {}.{} WHERE to_char({}, 'YYYY-MM-DD/HH:MM') >= '{}' AND id != 7934".format(schema,table,date_col,exc_date)
    else:
        sql = """
        SELECT COUNT(*) FROM {schema}.{table}
        WHERE 9=9
        AND to_char({date_col}, 'YYYY-MM-DD') >= TO_CHAR((to_timestamp('{exc_date}', 'YYYY-MM-DD/HH24:MI') - INTERVAL '1 DAY'),'YYYY-MM-DD')
        AND to_char({date_col}, 'YYYY-MM-DD') <= TO_CHAR(TO_TIMESTAMP('{exc_date}', 'YYYY-MM-DD/HH24:MI'), 'YYYY-MM-DD')
        """.format(schema=schema,table=table,date_col=date_col, exc_date=exc_date)

    # print(sql)
    df = rdbms_operator('postgres', db_name, sql).execute('Y')
    count = int(str(df['count'].values).replace('[','').replace(']',''))
    # print(count)
    
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
    
    results = rdbms_operator('postgres', db_name, sql).execute('N')
    
    print(sys.getsizeof(results))

    df = pd.DataFrame(results)
    df = df.replace('None', '')
    df = df.replace('NaT', '')
    df = df.replace('nan', '')
    df = df.map(lambda x: " ".join(x.splitlines()) if isinstance(x, str) else x)
    df = df.replace('None', '')
    df = df.replace('NaT', '')
    df = df.replace('nan', '')
    # df = df.astype('str')    
    # df = df.fillna(value='', inplace=True)
    # df['row_loaded_ts'] = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S.%s')
    # df = df[['row_loaded_ts'] + [x for x in df.columns if x != 'row_loaded_ts']]

    tables___ = 'dl__{db}__{schema}__{table}__dev'.format(db=db, schema=schema, table=table)
    print('create TEMP tables')
    # print(df)

    format_date = datetime.strptime(exc_date.replace('/', 'T') + ':00', '%Y-%m-%dT%H:%M:%S')
    format_date_min_7 = datetime.strftime((format_date - timedelta(hours=7)), '%Y-%m-%dT%H:%M:%S').replace('T', ' ')
    
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
        '''.format(format_date_min_7=format_date_min_7, tables___ = tables___, dataset=dataset)

        client.query(sql).result()

        if encr == 'True':
            # print(encr)
            pass
    print(sql)
def read_gsheet_file(db, dataset, schema, table):
    # Tabulate
    pd.options.display.max_colwidth = 100000

    # Attach credential file from developer google (API)
    # print('connect to gsheet')
    scope = ['https://www.googleapis.com/auth/spreadsheets.readonly']
    credentials = service_account.Credentials.from_service_account_file('/opt/account/secrets/service_account2.json', scopes=scope)
    gc = gspread.Client(auth=credentials)
    gc.session = AuthorizedSession(credentials)

    # Target dataset
    dataset = dataset

    # Create the pandas DataFrame
    # google_sheet_id = '1HSyAlLe7mWWOPKeNWE7H0dSO-xRysdCbZqb8RjtJ_g0'
    google_sheet_id = gsheet
    sheet = gc.open_by_key(google_sheet_id)

    try:
        worksheet = sheet.worksheet(table)
        df = pd.DataFrame(worksheet.get_all_records())
        # print(df)

    except gspread.exceptions.WorksheetNotFound as e:
        print("Trying to open non-existent sheet. Verify that the sheet name exists (%s)." % table)  
        data = []
        df = pd.DataFrame(data)

    # print(df)
    return df  

def transform_gsheet(dframe, table, src_schema):
    # dframe
    # print(src_schema)
    # print(dframe)
    
    df_sheets = dframe.rename(columns={'Column Name':'column_name', 'Data type':'data_type'})
    df_sheets_slice = df_sheets[['column_name','data_type']]

    # print(df_sheets_slice)

    df_src_ = pd.merge(df_sheets_slice, src_schema, on=["column_name"], how="left")
    with pd.option_context('future.no_silent_downcasting', True):
        df_src_.replace(to_replace=[None], value=np.nan, inplace=True)
        df_src_.fillna(value='', inplace=True)
    
    # print(df_src_)
    df_src_['data_type_x'] = np.where(df_src_['data_type_y']=='',df_src_['data_type_x'],df_src_['data_type_y']) 
    df_src_['src_ins'] = df_src_.agg('CAST({0[column_name]} AS {0[data_type_x]}) AS {0[column_name]}'.format, axis=1)
    df_src_ = df_src_.rename(columns={'data_type_x':'data_type'})
    df_src_slice = df_src_[['column_name','data_type','src_ins']]

    columns_insert = df_src_slice.src_ins + ','.strip()
    columns_insert = columns_insert.to_string(header=False,index=False)
    columns_insert = " ".join(columns_insert.split())
    # print(columns_insert)
    
    
    if "PII" in dframe:
        if (any(dframe['PII'] == 'TRUE') == True) == True:
            df_src_slice = df_src_slice.rename(columns={'column_name':'target_column'})
            df_selected = dframe[dframe['PII'] == 'TRUE']
            df_n = df_selected.copy()
            df_n['data_type'] = 'BYTES'
            df_n = df_n.rename(columns={'Column Name':'target_column'})
            df_init = df_n[['target_column','data_type','Supported Key']]
            df_inits = list(df_n['target_column'])
            
            encrypted_key = df_n.head(1)['Encrypted Key'].to_string(index=False)
            
            df_raw = df_n.reset_index(drop=True)
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
            
            enc = df_n.drop_duplicates(subset='Encrypted Key', keep="first")
    
            if not original_schema.empty:
                result = pd.merge(original_schema, df_init, on=["target_column"], how="left")
                result = pd.merge(result, df_src_slice, on=["target_column"], how="left")
                enc = pd.merge(enc['Encrypted Key'], original_schema, left_on="Encrypted Key", right_on='target_column', how="outer")
            else:
                # print('table tidak ada')
                df_emp = dframe[['Column Name', 'Data type']]
                df_emp = df_emp.rename(columns={'Column Name':'target_column', 'Data type': 'data_type'})
                df_emp = pd.merge(df_emp, df_src_slice, on=["target_column"], how="left")
                df_emp = df_emp[['target_column','data_type_y','src_ins']]
                df_emp = df_emp.rename(columns={'data_type_y': 'data_type'})
                result = pd.merge(df_emp, df_init, on=["target_column"], how="left")
                enc = pd.merge(enc['Encrypted Key'], df_emp, left_on="Encrypted Key", right_on='target_column', how="outer")
                
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
            
            result['src_ins'] = np.where((result['data_type_y']==''), result['src_ins'], result['enc'])

            enc = enc.dropna()

            columns_insert = result.src_ins + ','.strip()
            columns_insert = columns_insert.to_string(header=False,index=False)
            columns_insert = " ".join(columns_insert.split())

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
        
            return column_select, encrypted_key, column_list, columns_insert
        
        else:
            df_src_slice = df_src_slice.rename(columns={'column_name':'target_column'})
            df_selected = dframe.rename(columns={'Column Name':'target_column'})
            df_selected['data_type'] = df_selected['Data type']
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
    
            df_emp = dframe[['Column Name', 'Data type']]
            df_emp = df_emp.rename(columns={'Column Name':'target_column', 'Data type': 'data_type'})
            df_emp = pd.merge(df_emp, df_src_slice, on=["target_column"], how="left")
            df_emp = df_emp[['target_column','data_type_y','src_ins']]
            df_emp = df_emp.rename(columns={'data_type_y': 'data_type'})
                
            result = pd.merge(df_emp, df_init, on=["target_column"], how="left")
            
            result.replace(to_replace=[None], value=np.nan, inplace=True)
            result.fillna(value='', inplace=True)
            
            columns_insert = result.src_ins + ','.strip()
            columns_insert = columns_insert.to_string(header=False,index=False)
            columns_insert = " ".join(columns_insert.split())
                
            # List column to select
            column_select = result.target_column + ','.strip()
            column_select = column_select.to_string(header=False,index=False)
            column_select = " ".join(column_select.split())
            
            columns = result.target_column + ' ' + result.data_type_x + ','.strip()
            column_list = pd.DataFrame(columns).sort_index()
            column_list = column_list.to_string(header=False,index=False)
            column_list = " ".join(column_list.split())

            return column_select, '', column_list, columns_insert

def get_source_schema(schema, db_name, table):
    sql ='''
    select 
    column_name, 
    CASE
        WHEN column_name IN ('logo_web') THEN 'STRING'
        WHEN column_name IN ('bni_trx_id_va') THEN 'NUMERIC'
        WHEN udt_name IN ('int8','int4','int2','bigserial') THEN 'INT64'
        WHEN udt_name IN ('bytea') THEN 'STRING'
        WHEN udt_name IN ('varchar','text','bpchar','jsonb','json','uuid','UUID','_text') THEN 'STRING'
        WHEN udt_name IN ('float8','float4','numeric') THEN 'FLOAT64'
        WHEN udt_name IN ('timestamptz','timestamp') THEN 'TIMESTAMP'
        ELSE UPPER(udt_name)
    END AS data_type, 
    col_description('{schema}.{source_table}'::regclass, ordinal_position) as description
    from information_schema.columns
    where column_name NOT IN ('log_data','call_to_action') and table_schema = '{schema}' and table_name = '{source_table}'
    '''.format(schema=schema,source_table=table)
    
    src_schema = rdbms_operator('postgres', db_name, sql).execute('Y')
    return src_schema


def main(db, dataset, schema, table, date_col, exc_date):
    # DB connect
    db_host  = db_config.db_hijra_host
    db_username = db_config.db_hijra_username
    db_password = db_config.db_hijra_password
    db_port = db_config.db_hijra_port

    if db == 'hijra':
        db_name = db_config.db_hijra_name
    elif db == 'hijra_account':
        db_name = db_config.db_hijra_account_name
        
    print("Processing: {}: {}.{}".format(db, schema, table))

    count = get_count(schema, table, db_name, date_col, exc_date)
    print(count)

    tables___ = 'dl__{db}__{schema}__{table}__dev'.format(db=db, schema=schema, table=table)
    if count != 0:
        src_schema = get_source_schema(schema, db_name, table)
        # print(src_schema)
        dframe = read_gsheet_file(db, dataset, schema, table)
        # print(dframe)
        if not dframe.empty:
            column_select, encrypted_key, column_list, columns_insert = transform_gsheet(dframe, tables___, src_schema)
            get_data(db, dataset, schema, table, db_name, date_col, exc_date)
            # print(column_select)
            # print(encrypted_key)
            # print(column_list)
            # print(columns_insert)
            bq_operator('hijra-data-dev', dataset, tables___, '', encr, column_select, encrypted_key, column_list, columns_insert)
        # else:
        #     raise ValueError('Trying to open non-existent sheet. Verify that the sheet name exists ' + table + '.')

    else:
        tables___ = 'dl__{db}__{schema}__{table}__dev'.format(db=db, schema=schema, table=table)
        # drop_tables(dataset, tables___)
    

    return "SUCCESS"

if __name__ == "__main__":
    main(db, dataset, schema, table, date_col, exc_date)
