from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import configparser
import os
from dotenv import load_dotenv

load_dotenv()

user = os.environ.get('DB_USER')
password = os.environ.get('DB_PASSWORD')
host = os.environ.get('DB_HOST')
port = os.environ.get('DB_PORT')
name = os.environ.get('DB_NAME')

config = configparser.ConfigParser()
config.read('config.ini')

SQLALCHEMY_DATABASE_URL = f'postgresql+psycopg2://{user}:{password}@{host}:{port}/{name}'
engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
