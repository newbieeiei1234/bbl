from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from db.db_connection import get_db
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from db.models.users import Users
from api.auth.utils import hashed_password, verify_password, create_access_token, SECRET_KEY
import jwt
from api.auth.config import ENCRYPT_ALGORITHM

router = APIRouter(prefix="")

class RegisterRequest(BaseModel):
    username: str = Field(min_length=1, max_length=20)
    password: str = Field(min_length=1, max_length=20)
    admin_status: bool

@router.post("/register")
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    exist = db.query(Users.username).filter(Users.username == req.username).first()
    if exist:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="username already exists.")
    hashed_pw = hashed_password(req.password)
    newUser = Users(username=req.username, hashed_password=hashed_pw, admin_status=req.admin_status)
    try:
        db.add(newUser)
        db.commit()
        db.refresh(newUser)
    except Exception:
        db.rollback()
        raise
    return {"id": newUser.id, "username": newUser.username, "admin_status": newUser.admin_status}

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(Users).filter(Users.username == req.username).first()
    if user is None or not verify_password(req.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Username or password is incorrect.")

    token = create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}

oauth_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def get_current_user(token: str = Depends(oauth_scheme), db: Session = Depends(get_db)):
    credentail_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token.")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ENCRYPT_ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentail_exception
    except jwt.PyJWTError:
        raise credentail_exception
    user = db.query(Users).filter(Users.username == username).first()
    if user is None:
        raise credentail_exception
    return user
