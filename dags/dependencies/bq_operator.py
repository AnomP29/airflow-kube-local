from google.cloud import bigquery
from google.api_core.exceptions import NotFound
from dependencies import db_config

import pandas as pd
import pandas_gbq


class bq_operator():
    def __init__(self, projid, dataset, tables, query, column_list_enc=None, encrypted_key=None, *args, **kwargs) -> None:
        self.projid = projid
        self.dataset = dataset
        self.tables = tables
        self.query = query
        self.column_list_enc = column_list_enc
        self.encrypted_key = encrypted_key       
        self.client = bigquery.Client(self.projid)
        if self.check_bq_tables() == 1:
            print('check schema')
            self.__insert_enc_tables__()
        else:
            print('create table')
        
    def check_bq_tables(self): 
        sql = '''
        select
        COUNT(DISTINCT
        table_name) counts
        from
        `hijra-data-dev.{dataset}.INFORMATION_SCHEMA.COLUMNS`
        WHERE 9=9
        AND table_name = '{bqtable}'
        '''.format(dataset=self.dataset, bqtable=self.tables)

        bq_results = self.client.query(sql)
        df = bq_results.to_dataframe()

        return df.iloc[0]['f0_']
    
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
    
