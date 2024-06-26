import gspread
import pandas as pd
import numpy as np
import json

from google.cloud import bigquery
from google.oauth2 import service_account
from google.auth.transport.requests import AuthorizedSession


# Object client bigquery cursor
scope = ('https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/spreadsheets.readonly',)
client = bigquery.Client(client_options={'scopes': bigquery.Client.SCOPE + scope})


def schemaGenerator(df):
    df_raw = df.reset_index(drop=True)
    df_raw['Required'] = df_raw['Required'].replace('TRUE','REQUIRED')
    df_raw['Required'] = df_raw['Required'].replace('FALSE','NULLABLE')
    df_raw['Column Names'] = df_raw['Column Name']
    df_raw = df_raw.rename(columns={'Data Type':'type'
                                                ,'Required':'mode'
                                                ,'Column Name':'name'
                                                ,'Description':'description'})
    # df_raw['Reference Column'] = df_raw['Reference Column'].str.replace('\n',', ')
    df_raw['type'] = df_raw['type'].str.replace('INTEGER','INT64').replace('FLOAT','FLOAT64').replace('BOOLEAN','BOOL')
    df_raw['description'] = df_raw['description'].str.replace('\n',', ').str.replace('"',"'")
    # df_raw['description'] = ''
    # for i in range(len(df_raw)):
    #     if df_raw['Referenced Column'][i] != '' and df_raw['Possible Values'][i] != '':
    #         df_raw['description'][i] = df_raw['Column Description'][i] + ' ' + '[Foreign key to ' + df_raw['Referenced Column'][i] + ']' + ' (' + df_raw['Possible Values'][i] + ')'
    #     if df_raw['Referenced Column'][i] != '' and df_raw['Possible Values'][i] == '':
    #         df_raw['description'][i] = df_raw['Column Description'][i] + ' ' + '[Foreign key to ' + df_raw['Referenced Column'][i] + ']'
    #     if df_raw['Referenced Column'][i] == '' and df_raw['Possible Values'][i] != '':
    #         df_raw['description'][i] = df_raw['Column Description'][i] +  ' (' + df_raw['Possible Values'][i] + ')'
    #     if df_raw['Referenced Column'][i] == '' and df_raw['Possible Values'][i] == '':
    #         df_raw['description'][i] = df_raw['Column Description'][i]

    try:
        df_raw['split'],df_raw['name'] = df_raw['name'].str.split('.', 1).str
        df_raw['names'] = df_raw['name']
    except:
        pass

    try:
        df_raw['splits'],df_raw['name'] = df_raw['name'].str.split('.', 1).str
    except:
        pass

    if 'splits' in df_raw:
        print('splits')
        split = df_raw[['name','description','type','mode']].reset_index(drop=True)
        df_raw['level3'] = split.apply(lambda x: x.to_json(), axis=1) + ','
        df_schema = df_raw[df_raw['name'].notnull()]
        df_schema = df_schema[['splits','level3']].reset_index(drop=True)
        df_schema = df_schema.groupby('splits').sum()
        df_schema['name'] = df_schema.index
        df_result = pd.merge(df_raw, df_schema, how="left", on="splits")
        df_result = df_result.fillna('')
        df_result = df_result.drop(df_result[df_result['names'].str.contains(r'[...]')].index.tolist())
        df_result = df_result.drop(columns=['name_x'])
        df_result['name'] = df_result['names']
        df_result = df_result[['name','split','type','mode','level3_y','description']].reset_index(drop=True)
        df_result['fields'] = '[' + df_result['level3_y'] + ']'
    if 'splits' not in df_raw:
        print('not splits')
        df_raw['fields'] = '[]'
        df_result = df_raw

    if 'split' in df_raw:
        print('two splits')
        split = df_result[['name','description','type','mode','fields']].reset_index(drop=True)
        df_result['level2'] = split.apply(lambda x: x.to_json(), axis=1) + ','
        df_result = df_result.replace(r'^\s*$', np.nan, regex=True)
        df_results = df_result[df_result['name'].notnull()]
        df_results = df_results[['split','level2']].reset_index(drop=True)
        df_resultss = df_results.groupby('split')['level2'].apply(' '.join).reset_index()
        df_resultss['Column Names'] = df_resultss.index
        df_result = pd.merge(df_raw, df_resultss, how="left", on="split")
        df_result = df_result.drop(df_result[df_result['names'].notna()].index.tolist())
        df_result = df_result.drop(columns=['name', 'names'])
        try:
            df_result[['level2_x','level2_y']]
            df_result['fields'] = '[' + df_result['level2_y'] + ']'
        except:
            df_result['fields'] = '[' + df_result['level2'] + ']'
        df_result = df_result.rename(columns={'split':'name'})

    split = df_result[['name','description','type','mode','fields']].reset_index(drop=True)
    split['final'] = split.apply(lambda x: x.to_json(), axis=1)
    schema_cleaning = '[' + split['final'].str.cat(sep=', ') + ']'
    schema_cleaner = schema_cleaning.replace('\\', '')
    schema_cleaner = schema_cleaner.replace('""', '"')
    schema_cleaner = schema_cleaner.replace('"[', '[')
    schema_cleaner = schema_cleaner.replace(']"', ']')
    schema_cleaner = schema_cleaner.replace(",]", ']')
    schema_cleaner = schema_cleaner.replace('],"type"', ']","type"')
    schema_cleaner = schema_cleaner.replace(':","type"', ':"","type"')
    schema_cleaner = schema_cleaner.replace('"description":[', '"description":"[')
    schema_cleaner = schema_cleaner.replace('null', '[]')
    data = json.loads(schema_cleaner)

    with open('schema.json', 'w') as f:
        json.dump(data, f)

    schema = client.schema_from_json('schema.json')

    return schema


def read_td(table_name, sheet):
    worksheet = sheet.worksheet('Topic')
    list_of_lists = worksheet.get_all_values()

    df = pd.DataFrame()
    df = df.append(list_of_lists)
    df.columns = df.iloc[0]
    df = df.reindex(df.index.drop([0]))
    df = df.loc[df['Table Name'] == '{}'.format(table_name)]

    table_description = df.iloc[0]['Description']

    return table_description


def read_cd(table_name, sheet):
    worksheet = sheet.worksheet(table_name)
    list_of_lists = worksheet.get_all_values()
    df = pd.DataFrame()
    df = df.append(list_of_lists)
    df.columns = df.iloc[3]
    df = df.reindex(df.index.drop([0,1,2,3]))

    partition = ''
    if df.loc[df['Partition'] == 'TRUE'].empty == False:
        df_partition = df.loc[df['Partition'] == 'TRUE']
        partition = df_partition.iloc[0]['Column Name']

    cluster = ''
    if df.loc[df['Cluster'] == 'TRUE'].empty == False:
        df_cluster = df.loc[df['Cluster'] == 'TRUE']
        df_cluster = df_cluster[['Column Name','Cluster']].reset_index(drop=True)
        cluster = df_cluster["Column Name"].tolist()

    columns = ', '+ df['Column Name']
    rm = columns[6]
    rm = rm[2 : : ]
    columns = columns.drop(labels=6)
    columns = columns.append(pd.Series(rm), ignore_index=False)
    column_list = pd.DataFrame(columns).sort_index()
    column_list = column_list.to_string(header=False,index=False)

    schema = schemaGenerator(df)

    return schema, partition, cluster, column_list


def createTable(dataset,table_name,schema,query,table_description,partition,cluster):
    client.delete_table('{}.{}'.format(dataset,table_name), not_found_ok=True)
    table_ref = client.dataset(dataset).table(table_name)
    table = bigquery.Table(table_ref, schema=schema)
    if cluster:
        table.clustering_fields = cluster
    if partition:
        table.time_partitioning = bigquery.TimePartitioning(
                type_=bigquery.TimePartitioningType.DAY,
                field=partition)
    table = client.create_table(table)
    table.schema = schema
    table = client.update_table(table, ["schema"])
    table.description = table_description
    table = client.update_table(table, ["description"])


def try_load(dataset,table_name,schema,query,table_description,partition,cluster,column_list):
    datasets = dataset + '_dev'
    createTable(datasets,table_name,schema,query,table_description,partition,cluster)
    client.query("""INSERT {dataset}.{table_name} ({column_list})
                    SELECT {column_list}
                    FROM ({query}) a""".format(
                        dataset=datasets,
                        table_name=table_name,
                        column_list=column_list,
                        query=query)).result()
    client.delete_table('{}.{}'.format(datasets,table_name), not_found_ok=True)


def replace_table(dataset,table_name,schema,query,table_description,partition,cluster,column_list):
    createTable(dataset,table_name,schema,query,table_description,partition,cluster)
    client.query("""INSERT {dataset}.{table_name} ({column_list})
                    SELECT {column_list}
                    FROM ({query}) a""".format(
                        dataset=dataset,
                        table_name=table_name,
                        column_list=column_list,
                        query=query)).result()

    return 'Table has been updated'


def createfromQuery(dataset,table_name,query):
    client.delete_table('{}.{}'.format(dataset,table_name), not_found_ok=True)
    client.query("""CREATE OR REPLACE TABLE {dataset}.{table_name} AS
                    {query}""".format(
                        dataset=dataset,
                        table_name=table_name,
                        query=query)).result()

    return 'Table has been updated'


def main(table_name, query):
    # Tabulate
    pd.options.display.max_colwidth = 100000

    # Attach credential file from developer google (API)
    scope = ['https://www.googleapis.com/auth/spreadsheets.readonly']
    credentials = service_account.Credentials.from_service_account_file('/opt/account/secrets/datawarehouse.json', scopes=scope)
    gc = gspread.Client(auth=credentials)
    gc.session = AuthorizedSession(credentials)

    # Target dataset
    dataset = 'p2p_mart'

    # Create the pandas DataFrame
    google_sheet_id = '1yYN3yme10SXyoy5jtkr7NNcsXnAOneKlkVluB6_gFmc'
    sheet = gc.open_by_key(google_sheet_id)

    try:
        table_description = read_td(table_name, sheet)
        schema, partition, cluster, column_list = read_cd(table_name, sheet)

        try_load(dataset,table_name,schema,query,table_description,partition,cluster,column_list)
        replace_table(dataset,table_name,schema,query,table_description,partition,cluster,column_list)
    except:
        createfromQuery(dataset,table_name,query)

    return 'SUCCESS'
