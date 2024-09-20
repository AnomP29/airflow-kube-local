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
    def __init__(self, db_type, db, *args, **kwargs) -> None:
        self.db_type = db_type
        self.db = db
        # self.schema = schema
        # self.table = table
        # self.db_name = db_name
        # self.date_col = date_col
        # self.exc_date = exc_date
        # pass
        if self.db == 'hijra':
            self.db_host  = db_config.db_hijra_host
            self.db_username = db_config.db_hijra_username
            self.db_password = db_config.db_hijra_password
            self.db_name = db_config.db_hijra_name
            self.db_port = db_config.db_hijra_port
                    
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
            print('connection success')
        
        return conn

    def rdbms_type(self):
        if self.db_type == 'postgres':
            print('postgres connections')
            self.conn_postgres_()
        elif self.db_type == 'mssql':
            print('mssql')