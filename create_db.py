
from os import listdir
import pandas as pd
from proyecto3 import *
from os.path import isfile, join
files = [join(r'data', f) for f in listdir(r'data') if isfile(join(r'data', f)) ]


for f in files[:1]:
    df = pd.read_csv(f)
    print(df.columns)
    trips = df[['start station id','end station id','tripduration','starttime']]
    trips.columns = ['start','end','duration','time']
    trips.loc[:,'time'] = pd.to_datetime(trips.time)

    N = len(trips)
    i = 0
    for r in trips.iloc:
        trip_insert(r)
        i+= 1
        print("\r","%.2f"%(100*i/N),end = '')

    print(f"Trips from {f} done")
    stations = df.groupby(['start station id','start station name','start station latitude','start station longitude']).count().reset_index().iloc[:,:4]
    stations.columns = ['id','name','lat','long']
    N = len(stations)
    i = 0
    for r in stations.iloc:
        station_row_insert(r)
        i+= 1
        print("\r","%.2f"%(100*i/N),end = '')
    #stations.apply(station_row_insert,axis = 1)
    print(f"File {f} done")