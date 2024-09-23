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

from pathlib import Path
from datetime import datetime
from google.cloud import bigquery
from google.api_core.exceptions import NotFound
from dependencies import db_config
from dependencies.rdbms_operator import rdbms_operator

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
            AND to_char({date_col}, 'YYYY-MM-DD/HH:MM') >= TO_CHAR((to_timestamp('{exc_date}', 'YYYY-MM-DD/HH24:MI') - INTERVAL '2 HOUR'),'YYYY-MM-DD/HH24:MI')
            AND to_char({date_col}, 'YYYY-MM-DD/HH:MM') <= '{exc_date}'
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
        AND to_char({date_col}, 'YYYY-MM-DD/HH:MM') >= TO_CHAR((to_timestamp('{exc_date}', 'YYYY-MM-DD/HH24:MI') - INTERVAL '2 HOUR'),'YYYY-MM-DD/HH24:MI')
        AND to_char({date_col}, 'YYYY-MM-DD/HH:MM') <= '{exc_date}'
        """.format(schema=schema,table=table,date_col=date_col, exc_date=exc_date)

    # print(sql)
    # print(encr)
    df = rdbms_operator('postgres', 'hijra', sql).execute('Y')
    count = int(str(df['count'].values).replace('[','').replace(']',''))
    print(count)
    
    return count

def check_bq_tables(dataset, bqtable):
    client = bigquery.Client('hijra-data-dev')
    sql = '''
    select
    COUNT(DISTINCT
    table_name) counts
    from
    `hijra-data-dev.{dataset}.INFORMATION_SCHEMA.COLUMNS`
    WHERE 9=9
    AND table_name = '{bqtable}'
    '''.format(dataset=dataset, bqtable=bqtable)

    bq_results = client.query(sql)
    df = bq_results.to_dataframe()

    if df.iloc[0]['counts'] == 1:
        print('check schema')
        print('inserting row to MAIN TABLE')
        try:
            insert_tables(dataset, bqtable)
        except Exception as e:
            print(e)
        else:
            drop_tables(dataset, bqtable)
    else:
        print('create table')
        try:
            create_tables(dataset, bqtable)
        except Exception as e:
            print(e)
        else:
            drop_tables(dataset, bqtable)


    return df.iloc[0]['counts']

def create_tables(dataset, bqtable):
    print('creating table : ' + bqtable)
    client = bigquery.Client('hijra-data-dev')
    try:
        query = """
        CREATE OR REPLACE TABLE {dataset}.{bqtable}
        PARTITION BY DATE(row_loaded_ts)
        AS
        SELECT
        CURRENT_TIMESTAMP() row_loaded_ts
        ,*
        FROM
        `{dataset}.{bqtable}__temp`
        """.format(dataset=dataset, bqtable=bqtable)

        print(query)
        client.query(query).result()            

    except Exception as e:
        print(e)

def insert_tables(dataset, bqtable):
    client = bigquery.Client('hijra-data-dev')
    sql = """
    INSERT INTO `{dataset}.{bqtable}`
    SELECT 
    -- CURRENT_TIMESTAMP() row_loaded_ts,
    *
    FROM `{dataset}.{bqtable}__temp`
    """.format(dataset=dataset, bqtable=bqtable)
    # print(sql)
    client.query(sql).result()

def drop_tables(dataset, bqtable):
    client = bigquery.Client('hijra-data-dev')
    try:
        sql = """
        DROP TABLE `{dataset}.{bqtable}__temp`
        """.format(dataset=dataset, bqtable=bqtable)
        print(sql)
        client.query(sql).result()
    except Exception as d:
        print(d)


def get_data(db, dataset, schema, table, db_name, date_col, exc_date):
    # Object client bigquery cursor
    client = bigquery.Client('hijra-data-dev')
    # client.query("""SELECT * FROM datalakes.{table} LIMIT 1""".format(table=table)).result()

    sql = """
    SELECT * FROM {schema}.{table} 
    WHERE 9=9
    AND to_char({date_col}, 'YYYY-MM-DD/HH:MM') >= TO_CHAR((to_timestamp('{exc_date}', 'YYYY-MM-DD/HH24:MI') - INTERVAL '2 HOUR'),'YYYY-MM-DD/HH24:MI')
    AND to_char({date_col}, 'YYYY-MM-DD/HH:MM') <= '{exc_date}'
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
        sql = '''
        CREATE OR REPLACE TABLE {dataset}.{tables___}__temp
        AS
        SELECT CURRENT_TIMESTAMP() row_loaded_ts, * FROM {dataset}.{tables___}__temp
        '''.format(tables___ = tables___, dataset=dataset)
        client.query(sql).result()
        if encr == 'True':
            print(encr)
            drop_tables(dataset, tables___)
        else:
            check_bq_tables(dataset, tables___)
            print(encr)
            
        

def main(db, dataset, schema, table, date_col, exc_date):
    # DB connect
    # if db in ['p2p_realtime','p2p_prod']:
    #     db_host  = db_config.db_p2p_realtime_host
    #     db_username = db_config.db_p2p_realtime_username
    #     db_password = db_config.db_p2p_realtime_password
    #     db_name = db_config.db_p2p_realtime_name
    #     db_port = db_config.db_p2p_realtime_port

    # print('host---- ' + db_config.db_hijra_host)
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
        # check_bq_tables(dataset, tables___)
    else:
        tables___ = 'dl__{db}__{schema}__{table}__dev'.format(db=db, schema=schema, table=table)
        # drop_tables(dataset, tables___)
    

    return "SUCCESS"


if __name__ == "__main__":
    main(db, dataset, schema, table, date_col, exc_date)
