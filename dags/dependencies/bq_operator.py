from google.cloud import bigquery
from google.api_core.exceptions import NotFound
from dependencies import db_config

import pandas as pd
import pandas_gbq


class bq_operator():
    def __init__(self, projid, dataset, tables, query, encr='True',
                 column_select=None, encrypted_key=None, column_list=None, 
                 *args, **kwargs) -> None:
        self.projid = projid
        self.dataset = dataset
        self.tables = tables
        self.query = query
        self.encr = encr
        self.column_select = column_select
        self.encrypted_key = encrypted_key    
        self.column_list = column_list   
        self.client = bigquery.Client(self.projid)

        if self.encr == 'True':
            # print(self.encr)
            # if self.check_bq_tables(self.dataset) == 1:
            #     self.rsql = self.__insert_tables__(self.dataset, self.column_select)
            #     print(self.rsql)
            # else:
            #     self.rsql = self.__create_tables__(self.dataset, self.column_select)
            #     print(self.rsql)
            pass
        else:
            print(self.encr)
            if self.check_bq_tables(self.dataset) == 1:
                self.rsql = self.__insert_tables__(self.dataset, self.column_select)
                self.__execute__(self.rsql)
                print(self.rsql)
            else:
                self.rsql = self.__create_tables__(self.dataset, self.column_select)
                self.__execute__(self.rsql)
                print(self.rsql)

    def __encryption__(self):
        print(self.column_select)
        print(self.encrypted_key)
        print(self.column_list)
        
        if self.check_bq_tables('enigma') == 1:
            print('table exist')
            sql = '''
            CONCAT({encrypted_key},row_loaded_ts) {encrypted_key},
            KEYS.NEW_KEYSET('AEAD_AES_GCM_256') AS keyset
            '''.format(encrypted_key=self.encrypted_key)
            sql_insert = self.__insert_tables__('enigma', sql=sql)
            print(sql_insert)
        else:
            print('table NOT exist')

        pass
        
        
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
        try:
            print('start execution')
            self.client.query(sql)
        except Exception as e:
            print('failed execution')
        else:
            print('success execution')
        #     mtables = '''
        #     SELECT {column_select}
        #     FROM {dataset}.{tables}__temp
        #     '''.format(column_select=self.column_select, dataset=self.dataset, tables=self.tables)
        #     rsql = self.__insert_tables__('datalakes', mtables)
        #     print(rsql)
            
    def __create_tables__(self, dataset=None, sql=None):
        self.dset = dataset 
        self.sql = sql
        if self.dset == 'enigma':
            self.tables__ = self.tables + '_keys'
        else:
            self.tables__ = self.tables
            
        self.sql_str = """
        CREATE TABLE {dataset}.{table_name} AS {sql}
        """.format(
            table_name=self.tables__,
            dataset=self.dset, 
            sql = self.sql
            )
        return self.sql_str
        
    def __insert_tables__(self, dataset=None, sql=None):
        self.dset = dataset 
        self.sql = sql
        if self.dset == 'enigma':
            self.tables__ = self.tables + '_keys'
        else:
            self.tables__ = self.tables
            
        self.sql_str = """
        INSERT INTO {dataset}.{table_name} 
        SELECT {sql}
        FROM datalakes.{table_name}__temp
        """.format(
            dataset=self.dset,
            table_name=self.tables__, 
            sql = self.sql
            )
        # print(self.sql)
        return self.sql_str
        

    
    def generate_schema(self):
        sql = '''
        SELECT column_name as target_column, data_type
        FROM
        {dataset}.INFORMATION_SCHEMA.COLUMNS
        WHERE
        table_name='{table_name}'
        '''.format(dataset=self.dataset,table_name=self.tables)
        self.original_schema = self.client.query(sql).to_dataframe()
        
        return self.original_schema
