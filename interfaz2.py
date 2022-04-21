
import streamlit as st
import hashlib
from cassandra.cluster import Cluster
import cassandra
from ssl import SSLContext, PROTOCOL_TLSv1_2 , CERT_REQUIRED
from cassandra.auth import PlainTextAuthProvider
from cassandra.cluster import Cluster, ExecutionProfile, EXEC_PROFILE_DEFAULT
from cassandra.policies import WhiteListRoundRobinPolicy, DowngradingConsistencyRetryPolicy
from cassandra.query import tuple_factory
import pandas as pd

NoneType = type(None)
# Configure connection to Cassandra
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


def login(user, password):
    """
    Login with user and password.
    """
    r = session.execute(f"SELECT * FROM libreria.users WHERE name = '{user}'").one()
    if r != None:
        return r.password == password
    else:
        st.warning('User not registered')
        return False

def signup(user, password, membership= 'Free',country = 'Mexico'):
    """
    Creates new user.
    """
    r = session.execute(f"SELECT * FROM libreria.users WHERE name = '{user}'").one()
    if r == None:
        session.execute(f"INSERT INTO libreria.users(country, membership, name, password) VALUES ('{country}', '{membership}', '{user}', '{password}');")
        return True
    else:
        st.warning('User already registered')
        return False

def logout():
    st.session_state['user'] = None

def submit_review(user, title, score):
    session.execute(f"INSERT INTO libreria.review(user, book, score) VALUES ('{user}', '{title}', {score});")
    r = session.execute(f"SELECT * FROM libreria.book WHERE title = '{title}'").one()
    # If the book isn't yet in the library, tag it as  'General' Awaiting further classification
    if r == None:
        session.execute(f"INSERT INTO libreria.book(title, category) VALUES ('{title}', 'General');")
        return True
def submit_class(book_title,book_cat):
    session.execute("INSERT INTO libreria.book(book, category) VALUES ('{book_title}', '{book_cat}');")

def get_fav(user):
    q = session.execute(f"SELECT book,score FROM libreria.review WHERE user = '{user}' ALLOW FILTERING")
    fav_df = pd.DataFrame(q)
    fav_df = fav_df.sort_values('score')

    def _get_cat(title):
        print(f"SELECT * FROM libreria.book WHERE title = '{title}';")
        return session.execute(f"SELECT * FROM libreria.book WHERE title = '{title}';").one().category
    fav_df['category'] = fav_df.book.apply(_get_cat)
    fav_df = fav_df.loc[:,['category','score']].groupby('category').mean().sort_values('score',ascending = False)
    return fav_df

# Interfaz
if 'user' not in st.session_state:
    st.session_state['user'] = None

header = st.title("Proyecto 2 Cassandra")
    

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
    new_country= signup_form.text_input("Country")  
    new_membership = signup_form.selectbox('Membership',['Free','Básica','Premium'])
    signup_button = signup_form.form_submit_button()

    if signup_button:
        st.session_state['user'] = new_user if signup(new_user, new_password,membership=new_membership,country=new_country) else "auth_error"
        st.experimental_rerun()

else:
    current_user = st.session_state['user']
    # Versión del administrador
    if st.session_state['user'] == "root":
        header = st.title(f"Bienvenido Administrador")
        # Categorias favoritas del cliente
        fav_form = st.form('Favorite category of client')
        fav_form.title("Get client's favorite category")
        fuser = fav_form.text_input('Username')
        fav_button = fav_form.form_submit_button()
        if fav_button:
            fav_df = st.dataframe(get_fav(fuser))  
    else:
        header = st.title(f"Bienvenido {st.session_state['user']}")

    # My reviews tab
    ratings = st.container()
    ratings.title('My reviews')
    reviews_df = pd.DataFrame(session.execute(f"SELECT book,score FROM libreria.review WHERE user = '{st.session_state['user']}' ALLOW FILTERING"))
    if len(reviews_df) == 0:
        ratings.warning('No reviews yet :(')
        my_books = []
    else:
        ratings.dataframe(reviews_df)
        my_books = reviews_df.book.unique()

    # Form for new review
    review_form = st.form("New review")
    review_form.title('New review')
    book_title = review_form.text_input('Book title')
    book_score = review_form.slider('Score', 0, 10, 1)
    review_button = review_form.form_submit_button()

    if review_button:
        submit_review(st.session_state['user'], book_title,book_score)
    
    class_form = st.form("Classify book")
    class_form.title('Classify book')
    cbook_title = class_form.selectbox('Book title',my_books)
    cbook_cat = class_form.text_input('Category')
    class_button = class_form.form_submit_button()

    if class_button:
        submit_class(cbook_title,cbook_cat)


    logout_button =st.button('Logout', on_click = logout)
    if logout_button:
        st.experimental_rerun()