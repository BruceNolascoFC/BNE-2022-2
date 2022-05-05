
from os import listdir
import pandas as pd
from proyecto3 import *
from os.path import isfile, join
import pymongo
files = [join(r'data', f) for f in listdir(r'data') if isfile(join(r'data', f)) ]

db['stations'].create_index([("loc", pymongo.GEOSPHERE)])
files = [join(r'data', f) for f in listdir(r'data') if isfile(join(r'data', f)) ]

for f in files[1:2]:
    df = pd.read_csv(f)
    print(df.columns)
    trips = df[['start station id','end station id','tripduration','starttime']]
    trips.columns = ['start','end','duration','time']
    trips.loc[:,'time'] = pd.to_datetime(trips.time)

    N = len(trips)
    i = 0
    
    #for r in trips.iloc:
    #    trip_insert(r)
    #    i+= 1
    #    print("\r","%.2f"%(100*i/N),end = '')
    
    print(f"Trips from {f} done")
    stations = df.groupby(['start station id','start station name','start station latitude','start station longitude']).count().reset_index().iloc[:,:4]
    stations.columns = ['id','sname','lat','long']
    N = len(stations)
    i = 0
    for r in stations.iloc:
        station_row_insert(r)
        i+= 1
        print("\r","%.2f"%(100*i/N),end = '')
    print(f"start stations from {f} done")
    stations = df.groupby(['end station id','end station name','end station latitude','end station longitude']).count().reset_index().iloc[:,:4]
    stations.columns = ['id','sname','lat','long']
    N = len(stations)
    i = 0
    for r in stations.iloc:
        station_row_insert(r)
        i+= 1
        print("\r","%.2f"%(100*i/N),end = '')
    print(f"end stations from {f} done")
    print(f"File {f} done")
db['stations'].create_index([("loc", pymongo.GEOSPHERE)])