from google.cloud import bigquery
from google.api_core.exceptions import NotFound
from dependencies import db_config

import pandas as pd
import pandas_gbq


class bq_operator():
    def __init__(self, projid, dataset, tables, query, *args, **kwargs) -> None:
        self.projid = projid
        self.dataset = dataset
        self.tables = tables
        self.query = query       
        self.client = bigquery.Client(self.projid)
        
    def check_bq_tables(self): 
        bq_results = self.client.query(self.query)
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
    
    if check_bq_tables() == 1:
        print('check schema')
        print('inserting row to MAIN TABLE')
        # try:
        #     insert_tables(dataset, bqtable)
        # except Exception as e:
        #     print(e)
        # else:
        #     drop_tables(dataset, bqtable)
    else:
        print('create table')
        # try:
        #     create_tables(dataset, bqtable)
        # except Exception as e:
        #     print(e)
        # else:
        #     drop_tables(dataset, bqtable)