import streamlit as st
import logging
#import controller  as c
import hashlib
import os
import redis 
import pandas as pd

r = redis.Redis(
    host='127.0.0.1',
    port= '6379', 
    password='')

DOMAIN = '.url.unam'

def shortener(url):
    hash_object = hashlib.md5(url.encode())
    return str(hash_object.hexdigest())[:5]+DOMAIN

def add_public(url):
    short= shortener('public:'+url)
    r.set('public'+':'+short,url)
    return short

def add_private(url,user):
    short= shortener(user+':'+url)
    r.set(user+':'+short,url)
    return short

def expand(short,user = None):
    if user== None:
        st.session_state['user']
    if not (user== None or  user == "auth_error"):
        if r.exists(user+":"+short) == 1:
            return(r.get(user+":"+short).decode())
    if r.exists("public:"+short) == 1:
        return(r.get("public:"+short).decode())
    else:
        return(None)

def add_to_wishlist(url,user):
    short = add_private(url,user)
    r.append(user+":wishlist", short+"\n")
    return short

def get_wishlist(user):
    wishlist_raw = r.get(user+":wishlist")
    if wishlist_raw == None:
        return ""
    wishlist_raw = wishlist_raw.decode()
    wishlist = pd.DataFrame(wishlist_raw.split('\n')[:-1],columns= ["short"])
    wishlist['full'] = wishlist.short.map(lambda x: expand(x,user))
    return wishlist

def login(user, password):
    if r.exists("user:"+user) == 0:
        return False
    return r.get("user:"+user).decode('ascii') == password

def signup(user, password):
    if r.exists("user:"+user) == 1:
        return False
    r.set("user:"+user, password)
    return True

# Callbacks de interfaz


# Interfaz
if 'user' not in st.session_state:
    st.session_state['user'] = None

st.title("Proyecto 1 REDIS")

if st.session_state['user'] == "auth_error":
    st.warning("Incorrect login credentials")

if st.session_state['user'] == None or  st.session_state['user'] == "auth_error":
    #st.warning("Enter credentials")
    login_form = st.form("Login")
    login_form.title("LOGIN")
    user = login_form.text_input("User")
    password = login_form.text_input("Password")    
    login_button = login_form.form_submit_button()
    st.warning(str(r.get("user:"+user)))
    if login_button:
        st.session_state['user'] = user if login(user, password) else "auth_error"
        
    
    signup_form = st.form("SIGNUP")
    signup_form.title("SIGN UP")
    new_user = signup_form.text_input("New User")
    new_password = signup_form.text_input("New Password")  
    signup_button = signup_form.form_submit_button()

    if signup_button:
        st.session_state['user'] = new_user if signup(new_user, new_password) else "auth_error"


elif st.session_state['user'] == "root":
    st.title(f"Bienvenido Administrador")
else:
    current_user = st.session_state['user']
    st.title(f"Bienvenido {st.session_state['user']}")

    # public
    public_form =st.form("Shorten public url")
    public_form.title("Shorten public url")
    public_url = public_form.text_input("url")
    public_button = public_form.form_submit_button()

    if public_button:
        public_short =add_public(public_url)
        st.success("Created new public shortened url: "+public_short)

    # private
    private_form =st.form("Shorten private url")
    private_form.title("Shorten private url")
    private_url = private_form.text_input("url")
    private_button = private_form.form_submit_button()

    if private_button:
        private_short =add_private(private_url,current_user)
        st.success("Created new private shortened url: "+private_short)

    # wishlist
    st.title('My Wishlist')
    st.write(get_wishlist(current_user))
    wishlist_form =st.form("Add url to wishlist")
    wishlist_form.title("Add url to wishlist")
    wishlist_url = wishlist_form.text_input("url")
    wishlist_button = wishlist_form.form_submit_button()

    if wishlist_button :
        private_short =add_to_wishlist(wishlist_url,current_user)
        st.success("Created new private shortened url: "+private_short)