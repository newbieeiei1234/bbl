import jwt
from datetime import datetime, timedelta
from api.auth.config import ENCRYPT_ALGORITHM, EXPIRE_MINUTE
import os
from dotenv import load_dotenv
from passlib.context import CryptContext

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes=EXPIRE_MINUTE)
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ENCRYPT_ALGORITHM)
    return token

password_hash = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hashed_password(password: str):
    return password_hash.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return password_hash.verify(plain_password, hashed_password)