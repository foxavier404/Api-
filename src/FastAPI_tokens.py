from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pymongo import MongoClient
import os
from jose import JWTError, jwt
from datetime import datetime, timedelta

app = FastAPI()

# Initialize MongoDB connection
mongo_username = os.environ["MONGODB_USER"]
mongo_password = os.environ["MONGODB_PASSWORD"]
mongo_host = os.environ["MONGODB_HOST"]
mongo_port = int(os.environ["MONGODB_PORT"])
mongo_database = os.environ["MONGODB_DATABASE"]

client = MongoClient(f"mongodb://{mongo_username}:{mongo_password}@{mongo_host}:{mongo_port}/")
db = client[mongo_database]

# JWT configuration
SECRET_KEY = os.environ["JWT_SECRET"]
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Mock user database
users = {
    "john.doe@example.com": {
        "username": "john.doe@example.com",
        "password": "$2b$12$eUkJ9lQ4zWd4Q1a6z4H97eXJG39R8UyvJ6jc4gZj8vj39XjFqh8lC",  # hashed password
    }
}

def authenticate_user(fake_db, username: str, password: str):
    user = fake_db.get(username)
    if not user:
        return False
    if not verify_password(password, user["password"]):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

@app.post("/token", response_model={"access_token": str, "token_type": str})
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(users, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/protected", dependencies=[Depends(oauth2_scheme)])
async def protected_route():
    return {"message": "This is a protected route"}
