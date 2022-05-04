import pymongo
client = pymongo.MongoClient('localhost', 27017)
db = client['bikes']
users_collection = db['users']

class User:
    def __init__(self,username,password,home_lat = 0, home_long = 0,places = None):
        self.username = username
        self.password = password
        self.places = {'home':[home_lat,home_long]}
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
            'name':self.name,
            'loc':{
                    'type':'Point','coordinates':[self.lat,self.long]
                }
        }
        return self.doc

    def insert(self,db = db):
        col = db['stations']
        col.insert_one(self.as_doc())

def station_from_doc(doc):
    return Station(doc['id'],doc['name'],doc['loc']['coordinates'][0],doc['loc']['coordinates'][1])

def station_row_insert(r):
    col = db['stations']
    if col.find_one({'name': r.name}) == None:     
        Station(r.id,r.name,r.lat,r.long).insert()

def trip_insert(t):
    d ={
        'start': int(t.start),
        'end': int(t.end),
        'duration': float(t.duration),
        'time': t.time
    }
    col = db['trips']
    col.insert_one(d)



