import os
import psycopg2
from psycopg2 import pool
from dotenv import load_dotenv

# Load environment variables from a .env file if present. The database
# connection parameters below are read at import time, so it's important that
# they are populated before attempting to access them. Previously the values
# were read from os.environ without first loading the .env file, which caused
# KeyError exceptions when running the application locally without exporting
# the variables. Calling ``load_dotenv`` ensures that the expected variables are
# available.
load_dotenv()

host = os.environ["DATABASE_HOST"]
dbname = os.environ["DATABASE_NAME"]
user = os.environ["DATABASE_USER"]
password = os.environ["DATABASE_PASSWORD"]
    
# def connect_tcp_socket():

#     connection = None

#     if os.environ.get("DATABASE_ROOT_CERT"):
#         connection = psycopg2.connect(
#             user=user,
#             password=password,
#             host=host,
#             port="5432",
#             database=dbname,
#             sslmode="require",
#             sslrootcert=os.environ["DATABASE_ROOT_CERT"],
#             sslcert=os.environ["DATABASE_CLIENT_CERT"],
#             sslkey=os.environ["DATABASE_CLIENT_KEY"]
#         )
#     else:
#         connection = psycopg2.connect(
#             user=user,
#             password=password,
#             host=host,
#             port="5432",
#             database=dbname,
#         )

#     # Construct connection string
#     # conn_string = "host={0} user={1} dbname={2} password={3} sslmode={4}".format(host, user, dbname, password, sslmode)
#     # connection = psycopg2.connect(conn_string)

#     print("Connection established")

#     return connection


def connect_tcp_socket():
    connection_pool = None
    
    min_connections = 1
    max_connections = 5
    
    if os.environ.get("DATABASE_ROOT_CERT"):
        
        path_to_current_directory = os.path.dirname(os.path.abspath(__file__))

        SSL_ROOT_CERT = os.path.join(path_to_current_directory, os.environ["DATABASE_ROOT_CERT"])
        SSL_CLIENT_CERT = os.path.join(path_to_current_directory, os.environ["DATABASE_CLIENT_CERT"])
        SSL_CLIENT_KEY = os.path.join(path_to_current_directory, os.environ["DATABASE_CLIENT_KEY"])
        
        connection_pool = psycopg2.pool.ThreadedConnectionPool(min_connections, 
            max_connections, 
            user=user,
            password=password,
            host=host,
            port="5432",
            database=dbname,
            sslmode="require",
            sslrootcert=SSL_ROOT_CERT,
            sslcert=SSL_CLIENT_CERT,
            sslkey=SSL_CLIENT_KEY
            )
    else:
        connection_pool = psycopg2.pool.ThreadedConnectionPool(min_connections, 
            max_connections, 
            user=user,
            password=password,
            host=host,
            port="5432",
            database=dbname
            )        
    
    if (connection_pool):
        print("Connection pool created successfully using ThreadedConnectionPool")

    return connection_pool


def init_connection_pool():
    # add logic here if requiring different protocols to connect
    return connect_tcp_socket()
    
