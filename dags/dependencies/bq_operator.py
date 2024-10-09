from google.cloud import bigquery
from google.api_core.exceptions import NotFound
from dependencies import db_config

import pandas as pd
import pandas_gbq


class bq_operator():
    def __init__(self, projid, dataset, tables, query, encr='True',
                 column_select=None, encrypted_key=None, column_list=None, columns_insert=None,
                 *args, **kwargs) -> None:
        self.projid = projid
        self.dataset = dataset
        self.tables = tables
        self.query = query
        self.encr = encr
        self.column_select = column_select
        self.encrypted_key = encrypted_key    
        self.column_list = column_list   
        self.columns_insert = columns_insert
        self.client = bigquery.Client(self.projid)

        if self.encr == 'True':
            if self.check_bq_tables(self.dataset) == 0:
                print('a')
                sql_create_main = '''
                CREATE TABLE {dataset}.{table_name} ({column_list})
                PARTITION BY DATE(row_loaded_ts)
                '''.format(dataset=self.dataset, table_name=self.tables, column_list=self.column_list)
                print(sql_create_main)
                self.__execute__(sql_create_main)
            else:
                pass

        else:
            print(self.encr)
            if self.check_bq_tables(self.dataset) == 1:
                self.rsql = self.__insert_tables__(self.dataset, self.column_select, '')
                self.__execute__(self.rsql)
                print(self.rsql)
            else:
                print('maint table tidak ada')
                sql_create_main = '''
                CREATE TABLE {dataset}.{table_name} ({column_list})
                PARTITION BY DATE(row_loaded_ts)
                '''.format(dataset=self.dataset, table_name=self.tables, column_list=self.column_list)
                self.rsql = self.__create_tables__(self.dataset, sql_create_main)
                print(self.rsql)
                if self.__execute__(sql_create_main) == 'SUCCESS':
                    self.__to_main_table__()
                else:
                    raise ValueError('failed to insert to MAIN TABLES')
                

    def __create_tables__(self, dataset=None, sql=None):
        self.dset = dataset 
        self.sql = sql
        if self.dset == 'enigma':
            self.tables__ = self.tables + '_keys'
        else:
            self.tables__ = self.tables
            
        self.sql_str = """
        CREATE TABLE {dataset}.{table_name} AS {sql}
        FROM datalakes.{tables}__temp
        """.format(
            table_name=self.tables__,
            dataset=self.dset, 
            sql = self.sql,
            tables = self.tables,
            )
        return self.sql_str

    def __encryption__(self):
        print(self.column_select)
        print(self.encrypted_key)
        print(self.column_list)
        
        if self.check_bq_tables('enigma') == 1:
            print('table exist')
            sql = ''' 
            CONCAT({encrypted_key},row_loaded_ts) AS {encrypted_key},\
            KEYS.NEW_KEYSET('AEAD_AES_GCM_256') AS keyset \
            '''.lstrip().format(encrypted_key=self.encrypted_key)
            sql_insert = self.__insert_tables__('enigma', sql, '')
            
            if self.__execute__(sql_insert) == 'SUCCESS':
                self.__to_main_table__()                

        else:
            sql = '''
            SELECT
            CONCAT({encrypted_key},row_loaded_ts) AS {encrypted_key},
            KEYS.NEW_KEYSET('AEAD_AES_GCM_256') AS keyset
            '''.lstrip().format(encrypted_key=self.encrypted_key)
            sql_create = self.__create_tables__('enigma', sql)
            print(sql_create)
            if self.__execute__(sql_create) == 'SUCCESS':
                self.__to_main_table__()
            else:
                raise ValueError('failed to insert to MAIN TABLES')
            # print('table NOT exist')

    def __to_main_table__(self):
        sql_insert = self.__insert_tables__(self.dataset, self.column_select, 'tmptbl')
        print(sql_insert)
        self.__execute__(sql_insert)
        
    def check_bq_tables(self, dataset=None):
        self.dset = dataset 
        if self.dset == 'enigma':
            self.tables__ = self.tables + '_keys'
        else:
            self.tables__ = self.tables
            
        self.sql = '''
        select
        COUNT(DISTINCT
        table_name) f0_
        from
        `hijra-data-dev.{dataset}.INFORMATION_SCHEMA.COLUMNS`
        WHERE 9=9
        AND table_name = '{bqtable}'
        '''.format(dataset=self.dset, bqtable=self.tables__)
        # print(self.sql)

        bq_results = self.client.query(self.sql)
        self.df = bq_results.to_dataframe()

        return self.df.iloc[0]['f0_']
    
        # self.sql2 = '''
        #     SELECT 
        #     CONCAT({encrypted_key}, row_loaded_ts) {encrypted_key},
        #     KEYS.NEW_KEYSET('AEAD_AES_GCM_256') AS keyset
        #     FROM {dataset}.{table_name}__temp
        #     '''.format(
        #         column_select=self.column_select, 
        #         encrypted_key=self.encrypted_key, 
        #         table_name=self.tables, 
        #         dataset=self.dataset
        #         )
        # print(self.query)
            
    def __execute__(self, sql):
        self.exsql = sql
        try:
            print('start execution')
            print(self.exsql)
            self.client.query(sql).result()
            
        except Exception as e:
            print(f'The error is {e}')
        else:
            print('success execution')
            return 'SUCCESS'
            
        
    def __insert_tables__(self, dataset=None, sql=None, alias=None):
        self.dset = dataset 
        self.sql = sql
        if self.dset == 'enigma':
            self.tables__ = self.tables + '_keys'
        else:
            self.tables__ = self.tables
            
        self.sql_str = """
        INSERT INTO {dataset}.{table_name} 
        SELECT {sql}
        FROM datalakes.{tables}__temp {alias}
        """.format(
            dataset=self.dset,
            table_name=self.tables__, 
            sql = self.sql,
            tables = self.tables,
            alias = alias
            )
        # print(self.sql)
        return self.sql_str
        

    
    # def generate_schema(self):
    #     sql = '''
    #     SELECT column_name as target_column, data_type
    #     FROM
    #     {dataset}.INFORMATION_SCHEMA.COLUMNS
    #     WHERE
    #     table_name='{table_name}'
    #     '''.format(dataset=self.dataset,table_name=self.tables)
    #     self.original_schema = self.client.query(sql).to_dataframe()
        
    #     return self.original_schema
