from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import psycopg2

import config
from sqlalchemy import URL

# load environment variables, config, and API functions
from dotenv import load_dotenv

# TODO: PROBABLY DON'T NEED THIS ANYMORE

# load .env file
load_dotenv()

# get databse URL from config.py
db_url = config.Config.DATABASE_URL
db_host = config.Config.DATABASE_HOST
db_name = config.Config.DATABASE_NAME
db_user = config.Config.DATABASE_USER
db_pw = config.Config.DATABASE_PW
db_port = config.Config.DATABASE_PORT

# database URL
SQLALCHEMY_DATABASE_URL = URL.create(
    "postgresql+psycopg2",
    username=db_user,
    password=db_pw,  # plain (unescaped) text
    host=db_host,
    database=db_name,
)

# create the engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)

# create a session local class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# create a base class
Base = declarative_base()