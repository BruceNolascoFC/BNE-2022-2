#!/usr/bin/env python
# coding: utf-8

from cassandra.cluster import Cluster
import cassandra
from ssl import SSLContext, PROTOCOL_TLSv1_2 , CERT_REQUIRED
from cassandra.auth import PlainTextAuthProvider
from cassandra.cluster import Cluster, ExecutionProfile, EXEC_PROFILE_DEFAULT

ssl_context = SSLContext(PROTOCOL_TLSv1_2 )
ssl_context.load_verify_locations(r'./sf-class2-root.crt')
ssl_context.verify_mode = CERT_REQUIRED
auth_provider = PlainTextAuthProvider(username='Administrator-at-166369086707', password='YIvRYT1tSEMGQizTVFYE/bBu1QXv6g/Z9Zmyq6ub7IQ=')
profile = ExecutionProfile(
    consistency_level=cassandra.ConsistencyLevel.LOCAL_QUORUM
)
cluster = Cluster(['cassandra.us-east-1.amazonaws.com'], 
                  ssl_context=ssl_context, auth_provider=auth_provider, port=9142,
                 execution_profiles={EXEC_PROFILE_DEFAULT: profile})
session = cluster.connect()
#session.execute('consistency  local_quorum')
session.execute('use libreria;')


import pandas as pd
def upload_by_line(df,table,keyspace= 'libreria'):
    column_list = str(list(df.columns))[1:-1].replace("'",'')
    i  = 0
    n = len(df)
    for r in df.loc:
        i += 1
        if i<n:
            column_values = str(list(r.values))[1:-1]
            s = f"""INSERT INTO {keyspace}.{table}({column_list}) VALUES ({column_values});"""
            print(s)
            session.execute(s)
        else:
            break

#users = pd.read_csv(r'./users.csv')

#upload_by_line(users,'users')

#book = pd.read_csv(r'./book.csv')
#book['title'] = book.title.map(lambda x: x.replace("'",""))
#upload_by_line(book,'book')

review = pd.read_csv(r'./review.csv')
upload_by_line(review,'review')



