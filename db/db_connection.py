from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import os

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE = 30

DB_URL = "sqlite:///database.db"

engine = create_engine(DB_URL)

LocalSession = sessionmaker(autoflush=False, autocommit=False, bind=engine)

def get_db():
    db = LocalSession()
    try:
        yield db
    finally:
        db.close()
