import app.config as config
import psycopg2

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
