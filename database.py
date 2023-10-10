from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import config
from sqlalchemy import URL

# load environment variables, config, and API functions
from dotenv import load_dotenv

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
    "postgresql+psychopg2",
    username=db_user,
    password=db_pw,  # plain (unescaped) text
    host=db_host,
    database=db_name,
)

# database URL
# SQLALCHEMY_DATABASE_URL = config.Config.DATABASE_URL
# SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"

# create the engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)

# create a session local class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base = declarative_base()