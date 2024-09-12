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

def get_count(conn, schema, table, db_name, date_col, exc_date):
    # TODO: Ini juga perlu kita sederhanakan logic-nya.
    # Di sini untuk p2p perlu pakai db_name juga.
    if (db != 'hijra_staging' and table in ['audit_trail','log_login','anl_user_register','user_lounges','rdl_api_log']) == True:
#         if db == 'hijra' and table in ['application_activity']:
#             sql = "SELECT COUNT(*) FROM {}.{} WHERE DATE(insert_date) >= (CURRENT_DATE - INTERVAL '1 DAY')".format(schema,table)
        if db_name == 'p2p_prod' and table in ['rdl_api_log']:
            sql = "SELECT COUNT(*) FROM {}.{} WHERE to_char({}, 'YYYY-MM-DD/HH:MM') >= '{}'".format(schema,table,date_col,exc_date)
        if db == 'hijra' and table in ['anl_user_register']:
            sql = "SELECT COUNT(*) FROM {}.{} WHERE to_char({}, 'YYYY-MM-DD/HH:MM') >= '{}' AND id != 7934".format(schema,table,date_col,exc_date)
        # if db == 'hijra' and table in ['user_lounges']:
        #     sql = "SELECT COUNT(*) FROM {}.{} WHERE id != 7534".format(schema,table)
        # if db_name == 'p2p_prod' and table in ['log_login']:
        #     sql = "SELECT COUNT(*) FROM {}.{} WHERE DATE(log_date) >= (CURRENT_DATE - INTERVAL '2 DAY')".format(schema,table)
        # if db_name == 'p2p_prod' and table in ['audit_trail','application_activity']:
        #     sql = "SELECT COUNT(*) FROM {}.{} WHERE DATE(activity_date) >= (CURRENT_DATE - INTERVAL '5 DAY')".format(schema,table)
    else:
        sql = "SELECT COUNT(*) FROM {}.{} WHERE to_char({}, 'YYYY-MM-DD/HH:MM') >= '{}'".format(schema,table,date_col, exc_date)

    # print(sql)
    df = pd.read_sql_query(sql, conn)
    count = int(str(df['count'].values).replace('[','').replace(']',''))

    return count

def get_data(conn, db, dataset, schema, table, db_name, date_col, exc_date):
    # Object client bigquery cursor
    client = bigquery.Client('hijra-data-dev')
    # client.query("""SELECT * FROM datalakes.{table} LIMIT 1""".format(table=table)).result()

    cursor = conn.cursor(name='fetch_large_result')
    sql = "SELECT * FROM {}.{} WHERE to_char({}, 'YYYY-MM-DD/HH:MM') >= '{}'".format(schema,table,date_col, exc_date)
    cursor.execute(sql)
    records = cursor.fetchmany(size=100000)
    columns = [column[0] for column in cursor.description]
    results = []
    for row in records:
        results.append(dict(zip(columns, row)))

    print(sys.getsizeof(results))

    df = pd.DataFrame(results)
    df = df.applymap(lambda x: " ".join(x.splitlines()) if isinstance(x, str) else x)
    df = df.astype('str')    
    # df = df.fillna(value='', inplace=True)
    df = df.replace('None', '')
    # df['row_loaded_ts'] = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S.%s')
    # print(df)
    # df = df[['row_loaded_ts'] + [x for x in df.columns if x != 'row_loaded_ts']]
    # print(df)

    tables___ = '{dataset}.dl__{db}__{schema}__{table}__dev__temp'.format(dataset=dataset, db=db, schema=schema, table=table)
    print(tables___)
    pandas_gbq.to_gbq(df, tables___ , project_id='hijra-data-dev',if_exists='replace',api_method='load_csv')
    cursor.close()




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

    print('connecting to postgres DB')
    # conn = 'psycopg2.connection'
    conn = psycopg2.connect(
        host=db_host,
        user=db_username,
        password=db_password,
        database=db_name,
        port=db_port,
        connect_timeout=5)

    print("Processing: {}: {}.{}".format(db, schema, table))

    count = get_count(conn, schema, table, db_name, date_col, exc_date)
    print(count)

    if count != 0:
        get_data(conn, db, dataset, schema, table, db_name, date_col, exc_date)
    

    return "SUCCESS"


if __name__ == "__main__":
    main(db, dataset, schema, table, date_col, exc_date)




