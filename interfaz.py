
import streamlit as st
import hashlib
import redis 
import pandas as pd

NoneType = type(None)
# Configure connection to Redis
r = redis.Redis(
    host='127.0.0.1',
    port= '6379', 
    password='')

# Domain of shortened urls
DOMAIN = '.url.unam'

# Gets the short url version
def shortener(url):
    hash_object = hashlib.md5(url.encode())
    return str(hash_object.hexdigest())[:5]+DOMAIN

def add_public(url):
    """
    Generate public short url for url
    """
    short= shortener('public:'+url)
    r.set('public'+':'+short,url)
    return short

def add_private(url,user):
    """
    Generate private short url for url and user.
    """
    short= shortener(user+':'+url)
    r.set(user+':'+short,url)
    r.sadd(user+":private", short)
    return short

def expand(short,user = None,verbose = False):
    """
    Returns the full version of the short url short.
    Gives priority to private links.
    """
    #st.success(user)
    if user== None:
        user= st.session_state['user']
    #st.success(user)
    if not (user== None or  user == "auth_error"):
        
        if r.exists(user+":"+short) == 1:
            if verbose:
                st.success("Authenticated user for private url")
            return(r.get(user+":"+short).decode())
    if r.exists("public:"+short) == 1:
        return(r.get("public:"+short).decode())
    else:
        return(None)

def add_to_wishlist(url,user):
    short = add_private(url,user)
    r.sadd(user+":wishlist", short)
    return short

def get_wishlist(user):
    wishlist_raw = list(r.smembers(user+":wishlist"))
    
    if len(wishlist_raw) == 0:
        return None
    wishlist_raw = map(lambda x: x.decode('ascii'), wishlist_raw)
    wishlist = pd.DataFrame(wishlist_raw,columns= ["short"])
    wishlist['full'] = wishlist.short.map(lambda x: expand(x,user))
    return wishlist

def add_cat(user,category):
    r.sadd(user+':cats',category)

def add_url_to_cat(user,category,url):
    """
    Add the shortened version of url to the category cat.
    """
    short = add_private(url,user)
    if category not in get_cats(user):
        add_cat(user,category)
    r.sadd(f'{user}:{category}',short)
    return short


def get_cats(user):
    """
    Get all the categories registered by user.
    """
    cats_raw = list(r.smembers(user+":cats"))
    if len(cats_raw) == 0:
        return []
    cats_raw = map(lambda x: x.decode('ascii'), cats_raw)
    return list(cats_raw)

def get_links_in_cat(user, cat):
    """
    Get all the links stored under the category cat by user.
    """
    if cat == "All":
        cat = 'private'
    raw_links = r.smembers(f'{user}:{cat}')
    links = list(map(lambda x: x.decode('ascii'), raw_links))
    if len(links) == 0:
        return None
    links = pd.DataFrame(links,columns= ["short"])
    
    links['full'] = links.short.map(lambda x: expand(x,user))
    return links
    

def intersec_users(u,v):
    """
    Gets the intersection of the wishlists of users u and v
    """
    wishlist_u = get_wishlist(u)
    if type(wishlist_u) == NoneType:
        return None
    wishlist_v = get_wishlist(v)
    if type(wishlist_v) == NoneType:
        return None
    # Use pandas to join both dataframes
    inter = wishlist_u.merge(wishlist_v,on = "full")
    inter.columns = [f"{u}'s private link","Full url",f"{v}'s private link"]
    
    return inter

def login(user, password):
    """
    Login with user and password.
    """
    if r.exists("user:"+user) == 0:
        st.warning("User already registeres")
        return False
    return r.get("user:"+user).decode('ascii') == password

def signup(user, password):
    """
    Creates new user.
    """
    if r.exists("user:"+user) == 1:
        return False
    r.set("user:"+user, password)
    return True

def logout():
    st.session_state['user'] = None
    st.experimental_rerun()

# Interfaz
if 'user' not in st.session_state:
    st.session_state['user'] = None

header = st.title("Proyecto 1 REDIS")

# Expand url form
expand_form = st.form("Deshorten URL")
expand_form.title("Deshorten URL")
url_to_expand = expand_form.text_input("URL")  
expand_button = expand_form.form_submit_button()
if expand_button:
    large = expand(url_to_expand,verbose = True)
    if large == None:
        st.warning("Sorry, we couldn't find that URL")
    else:
        st.success(large)
    

if st.session_state['user'] == "auth_error":
    st.warning("Incorrect login credentials")

if st.session_state['user'] == None or  st.session_state['user'] == "auth_error":
    #st.warning("Enter credentials")
    login_form = st.form("Login")
    login_form.title("LOGIN")
    user = login_form.text_input("User")
    password = login_form.text_input("Password")    
    login_button = login_form.form_submit_button()
    #st.warning(str(r.get("user:"+user)))
    if login_button:
        st.session_state['user'] = user if login(user, password) else "auth_error"
        st.experimental_rerun()
    
    signup_form = st.form("SIGNUP")
    signup_form.title("SIGN UP")
    new_user = signup_form.text_input("New User")
    new_password = signup_form.text_input("New Password")  
    signup_button = signup_form.form_submit_button()

    if signup_button:
        st.session_state['user'] = new_user if signup(new_user, new_password) else "auth_error"
        st.experimental_rerun()

else:
    current_user = st.session_state['user']
    if st.session_state['user'] == "root":
        header = st.title(f"Bienvenido Administrador")

        # intersection of wishlists
        inter_form =st.form("Intersect users wishlists")
        inter_form.title("Intersect users wishlists")
        u = inter_form.text_input("User 1")
        v = inter_form.text_input("User 2")
        inter_button = inter_form.form_submit_button()

        if inter_button:
            inter_links = intersec_users(u,v)
            if type(inter_links)!= NoneType:
                st.dataframe(inter_links)
            else:
                st.warning("Intersection is empty")

    else:
        header = st.title(f"Bienvenido {st.session_state['user']}")
    with st.expander("Generate new short URLs"):
        # public link generation form
        public_form =st.form("Shorten public url")
        public_form.title("Shorten public url")
        public_url = public_form.text_input("url")
        public_button = public_form.form_submit_button()

        if public_button:
            public_short =add_public(public_url)
            st.success("Created new public shortened url: "+public_short)

        # private link generation form
        private_form =st.form("Shorten private url")
        private_form.title("Shorten private url")
        private_url = private_form.text_input("url")
        private_button = private_form.form_submit_button()
        cat_options = private_form.multiselect(
     'Add this url to the following categories', get_cats(current_user))

        if private_button:
            private_short =add_private(private_url,current_user)
            st.success("Created new private shortened url: "+private_short)
            for cat in cat_options:
                add_url_to_cat(current_user, cat, private_url)
                st.success(f"Added to {cat}.")
        
        # my links tab
    with st.expander("My links"):
        new_cat_form =st.form("Add category")
        new_cat = new_cat_form.text_input("New category")
        new_cat_button = new_cat_form.form_submit_button()
        if new_cat_button:
            add_cat(current_user,new_cat)
            st.success("Created new category")
            st.experimental_rerun()
        
        cat_selector = st.radio("Select category to display",['All']+get_cats(current_user))
        cat_display_button = st.button("See category" )
        if cat_display_button:
            cat_links = get_links_in_cat(current_user,cat_selector)
            if type(cat_links) != NoneType:
                st.dataframe(cat_links,width= 700)
            else:
                st.warning("This category doesn't have links yet.")
    # wishlist
    with st.expander("Wishlist"):
        st.title('My Wishlist')
        df = get_wishlist(current_user)
        if type(df)!= NoneType:
            wish_table = st.dataframe(df)
        wishlist_form =st.form("Add url to wishlist")
        wishlist_form.title("Add url to wishlist")
        wishlist_url = wishlist_form.text_input("url")
        wishlist_button = wishlist_form.form_submit_button()

        if wishlist_button :
            private_short =add_to_wishlist(wishlist_url,current_user)
            st.success("Created new private shortened url: "+private_short)


    st.button('Logout', on_click = logout)