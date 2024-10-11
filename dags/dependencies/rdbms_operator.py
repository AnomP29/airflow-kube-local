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


from dependencies import db_config

class rdbms_operator():
    # def __init__(self, db_type, schema, table, db_name, date_col, exc_date, *args, **kwargs) -> None:
    def __init__(self, db_type, db, query, *args, **kwargs) -> None:
        self.db_type = db_type
        self.db = db
        self.query = query
        # self.schema = schema
        # self.table = table
        # self.db_name = db_name
        # self.date_col = date_col
        # self.exc_date = exc_date
        # pass
        db_host  = db_config.db_hijra_host
        db_username = db_config.db_hijra_username
        db_password = db_config.db_hijra_password
        db_port = db_config.db_hijra_port
    
        if db == 'hijra':
            db_name = db_config.db_hijra_name
        elif db == 'hijra_account':
            db_name = db_config.db_hijra_account_name
                    
    def conn_postgres_(self):
        try:
            conn = psycopg2.connect(
                host=self.db_host,
                user=self.db_username,
                password=self.db_password,
                database=self.db_name,
                port=self.db_port,
                connect_timeout=5)
        except Exception as e:
            print(e)
        else:
            pass
            # print('connection success')
        
        return conn

    def execute(self, dframe='N'):
        self.conn = self.conn_postgres_()
        if dframe == 'Y':            
            results = pd.read_sql_query(self.query, self.conn)
        else:
            cursor = self.conn.cursor(name='fetch_large_result')
            cursor.execute(self.query)
            records = cursor.fetchmany(size=1000000)
            columns = [column[0] for column in cursor.description]
            results = []
            for row in records:
                results.append(dict(zip(columns, row)))

            cursor.close()


        
        return results
        
        
    
    def rdbms_type(self):
        if self.db_type == 'postgres':
            print('postgres connections')
            self.conn_postgres_()
        elif self.db_type == 'mssql':
            print('mssql')
