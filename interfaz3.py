
import streamlit as st
from proyecto3 import *
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt

st.set_page_config(page_title=None, page_icon=None, layout="wide", initial_sidebar_state="auto", menu_items=None)
# Get collections
users = db['users']
stations = db['stations']
trips = db['trips']

# Session variables
#st.session_state['u'] = None

# Interface functions
def login(user, password):
    """
    Login with user and password.
    """
    u = users.find_one({'username':user})
    if u == None:
        st.warning("User not registered")
        return False
    else:
        st.session_state['u'] = user_from_doc(u)
        return u['password'] == password

def signup(user, password,lat,long):
    """
    Creates new user.
    """
    u = users.find_one({'username':user})
    if u != None:
        st.warning('User already registered.')
        return False
    else:
        u = User(user,password,lat,long)
        u.insert()
        st.session_state['u'] = u
        st.success("Registrado")
        return True
        

def logout():
    """
    Logs out and resets session variables.
    """
    st.session_state['user'] = None
    st.session_state['u'] = None
    st.experimental_rerun()

def get_user(user):
    u = users.find_one({'username':user})

# Interfaz
if 'user' not in st.session_state:
    st.session_state['user'] = None
if 'u' not in st.session_state:
    st.session_state['u'] = None

header = st.title("Proyecto III MongoDB")


if st.session_state['user'] == "auth_error":
    st.warning("Incorrect login credentials")

if st.session_state['user'] == None or  st.session_state['user'] == "auth_error":
    a,b = st.columns(2)
    login_form = a.form("Login")
    login_form.header("LOGIN")
    user = login_form.text_input("User")
    password = login_form.text_input("Password")    
    login_button = login_form.form_submit_button()
    
    if login_button:
        st.session_state['user'] = user if login(user, password) else "auth_error"
        st.experimental_rerun()
    
    signup_form = b.form("SIGNUP")
    signup_form.header("SIGN UP")
    new_user = signup_form.text_input("New User")
    new_password = signup_form.text_input("New Password")  
    new_lat = signup_form.number_input("Home Latitude",value = 40.)  
    new_long = signup_form.number_input("Home Longitude",value = -100.)  
    signup_button = signup_form.form_submit_button()

    if signup_button:
        st.session_state['user'] = new_user if signup(new_user, new_password,new_lat,new_long) else "auth_error"
        st.experimental_rerun()
        #st.write(st.session_state['user'])
    

else:
    
    current_user = st.session_state['user']
    if st.session_state['user'] == "root":
        header = st.title(f"Bienvenido Administrador")

        # Administrator Interface
    else:
        header = st.title(f"Bienvenido {st.session_state['user']}")
    u = st.session_state['u']
    home_coords = u.places['home']
    a,b = st.columns(2)
    with a.expander("Search near stations"):
        near_form = st.form('Place')
        near_form.header("Select place to search from")
        near_place = near_form.selectbox('Select place', u.places.keys())
        near_button = near_form.form_submit_button()

        if near_button:
            near_df = pd.DataFrame(u.search_near(near_place))
            try:
            
                near_df = near_df[near_df.distance <= 500]
                st.dataframe(near_df[['distance','name']])
                f = lambda x:x['loc']['coordinates']
                cdf = pd.DataFrame(near_df.iloc[:,1:]['loc']).apply(f,axis = 1,result_type = 'expand')
                cdf.columns = ['lon','lat'] 
                cdf['name'] = near_df['name']
                fig = px.scatter_mapbox(cdf, lat="lat", lon="lon", zoom=14,hover_name = 'name')
                fig.update_layout(mapbox_style="open-street-map")
                st.plotly_chart(fig)
            except:
                st.warning("No near stations to the given location.")


    with b.expander('Add place'):
        place_form = st.form("New place")
        place_form.header("Add new place")
        place_name = place_form.text_input('New place name')
        place_lat = place_form.number_input("Latitude",value = 40.9052)  
        place_long = place_form.number_input("Longitude",value = -73.8048) 
        place_button = place_form.form_submit_button()

        if place_button:
            u.places[place_name] = [place_long,place_lat]
            u.update_places()
            st.session_state['u'] = u
            st.success("Place added")

    with st.expander("Recommend a trip"):
        trip_form = st.form('Recommend a trip')
        trip_form.header('Recommend a trip')
        trip_place = trip_form.selectbox('Select starting place', u.places.keys())
        trip_time = trip_form.number_input("Duration of trip",value = 10)
        circular = trip_form.checkbox('Circular trip')
        trip_hour=trip_form.time_input('Expected start time')
        trip_button = trip_form.form_submit_button()

        if trip_button:
            near_df = pd.DataFrame(u.search_near(trip_place))
            nearest = near_df.iloc[0]
            st.success(f"The nearest station is in {nearest['name']}")

            nearest = station_by_id(nearest['id'])
            st.dataframe(nearest.route(trip_time,circular,trip_hour))

    st.button('Logout', on_click = logout)
    