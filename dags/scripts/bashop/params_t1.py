from function import main

"""-----------------------------INPUT HERE-----------------------------"""

# Target table
table_name = 'rw_mis_lawsuit_termohon_levenshtein_score'

# Your query. Make sure you are running on the biqquery console
query = '''
{{ params.exec_date }}
'''
"""---------------------------------END--------------------------------"""

if __name__ == "__main__":
  main(query)
