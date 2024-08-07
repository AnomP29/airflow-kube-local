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

(options, args) = parser.parse_args()

if not options.table:
    parser.error('table is not given')
if not options.db:
    parser.error('database is not given')
if not options.schema:
    parser.error('schema is not given')
if not options.dataset:
    parser.error('dataset is not given')

table = options.table
db = options.db
schema = options.schema
dataset = options.dataset
