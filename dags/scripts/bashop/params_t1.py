from function import main

"""-----------------------------INPUT HERE-----------------------------"""

# Target table
table_name = 'rw_mis_lawsuit_termohon_levenshtein_score'

# Your query. Make sure you are running on the biqquery console
query = '''
{{ execution_date.strftime('%Y-%m-%dT%H:%M:%S') }}
'''
"""---------------------------------END--------------------------------"""
print({{ execution_date.strftime('%Y-%m-%dT%H:%M:%S') }})
print(query)

# if __name__ == "__main__":
#   main(query)
