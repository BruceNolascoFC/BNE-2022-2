import pymongo
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Establish local connection
client = pymongo.MongoClient('localhost', 27017)
db = client['bikes']
users= db['users']
stations = db['stations']
trips = db['trips']
class User:
    def __init__(self,username,password,home_lat = 0, home_long = 0,places = None):
        self.username = username
        self.password = password
        self.places = {'home':[home_long,home_lat]}
        if places != None:
            self.places = places
    
    def as_doc(self):
        self.doc = {
            'username':self.username,
            'password':self.password,
            'places':[
                {'name':p[0],'loc':{
                    'type':'Point','coordinates':p[1]
                }}
                for p in self.places.items()
            ]
        }
        return self.doc
    def insert(self,db = db):
        col = db['users']
        col.insert_one(self.as_doc())
    
    def update_places(self):
        col = db['users']
        col.update_one({'username':self.username},{"$set":{
            'places':self.as_doc()['places']
        }})

    def search_near(self,place = 'home',maxd = 1500):
        p = self.places[place]
        lat = p[1]
        long = p[0]
        return list(stations.aggregate( [
        {
            '$geoNear': {
                'near': { 'type': "Point",  'coordinates': [long, lat] },
                'spherical': 'true',
                'query': { },
                #'maxDistance':maxd,
                'distanceField': "distance"
            }
        }
        ] ))


def user_from_doc(doc):
    places = doc['places']
    places = {p['name']:p['loc']['coordinates'] for p in places}
    return User(doc['username'],doc['password'],places=places)

class Station:
    def __init__(self,id,name,lat = 0,long = 0):
        self.id = id
        self.name = name
        self.lat = lat
        self.long = long
    def as_doc(self):
        self.doc = {
            'id':int(self.id),
            'name':str(self.name),
            'loc':{
                    'type':'Point','coordinates':[float(self.long),float(self.lat)]
                }
        }
        return self.doc

    def insert(self,db = db):
        col = db['stations']
        col.insert_one(self.as_doc())
    
    def as_dic(self):
        self.dic = {
            'name':self.name,
            'latitude':self.lat,
            'longitude':self.long
        }
        return self.dic

    def route(self, time = 100,circular = False):
        otime = time*60
        m = 1
        time = otime
        if circular:
            time = time/2 
            m = 2

        q = [(self.id,time)]
        visited = {self.id}
        parents = {self.id : None}
        end_nodes = []
        while  len(q)>0:
            u,time = q.pop(0)
            
            n = map( lambda x: (x['_id'], time - x['duration']),
                list(
                    trips.aggregate([
                        {'$match':{'$and':[
                    {'start':u},
                    {'duration':{'$lt':time}}
                    ]}},
                    {'$group':
                    {'_id':'$end', 'duration':{'$avg': '$duration'}}}]
                    )
                ))
            
            print(q)
            for v,tr in n:
                #print(v,tr)
                if v in visited:
                    continue
                else:
                    visited.add(v)
                    parents[v] = u
                    
                    if  tr <= 120:
                        end_nodes.append((v,(otime-m*tr)/60))
                    else:
                        q.append((v,tr))

        print(end_nodes)
        def _name_by_id(idd):
            s = stations.find_one({'id':idd})
            if s ==None:
                return ""
            return s['name']
        def _recover_route(en):
            en, _ = en
            route = [en]
            while en != None:
                route.append(parents[en])
                en = parents[en]
            route = route[:-1][::-1]
            return list(map(_name_by_id,route))
        
        return pd.DataFrame({'total_duration':map(lambda x:x[1],end_nodes) ,
            'route': map(_recover_route,end_nodes)})

            


            

def station_by_id(id):
    doc = stations.find_one({'id':int(id)})
    return station_from_doc(doc)

def station_from_doc(doc):
    return Station(doc['id'],doc['name'],doc['loc']['coordinates'][0],doc['loc']['coordinates'][1])

def station_row_insert(r):
    col = db['stations']
    if col.find_one({'name': str(r.sname)}) == None:     
        Station(r.id,r.sname,r.lat,r.long).insert()

def trip_insert(t):
    d ={
        'start': int(t.start),
        'end': int(t.end),
        'duration': float(t.duration),
        'time': t.time
    }
    col = db['trips']
    col.insert_one(d)







