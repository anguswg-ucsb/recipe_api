import app.config as config
import psycopg2
from sqlalchemy import create_pool_from_url

# function that makes a database connection
def get_db_conn():
    conn = psycopg2.connect(
        dbname=config.Config.DATABASE_NAME,
        user=config.Config.DATABASE_USER,
        password=config.Config.DATABASE_PW,
        host=config.Config.DATABASE_HOST,
        port=config.Config.DATABASE_PORT
    )
    return conn

# # function that makes a database connection
# def connect_to_database():
#     conn = psycopg2.connect(
#         dbname=config.Config.DATABASE_NAME,
#         user=config.Config.DATABASE_USER,
#         password=config.Config.DATABASE_PW,
#         host=config.Config.DATABASE_HOST,
#         port=config.Config.DATABASE_PORT
#     )
#     return conn

# # Define the database dependency function
# def get_db_conn():
#     db = connect_to_database()
#     try:
#         yield db
#     finally:
#         db.close()

# # Create a pool
# pool = create_pool_from_url(config.Config.CONNECTION_URL)

# # Function that returns a connection from the pool
# def get_db_conn():
#     conn = pool.connect()
#     try:
#         yield conn
#     finally:
#         conn.close()
