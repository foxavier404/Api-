from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
import os

app = FastAPI()

# Initialize MongoDB connection
mongo_username = os.environ["MONGODB_USER"]
mongo_password = os.environ["MONGODB_PASSWORD"]
mongo_host = os.environ["MONGODB_HOST"]
mongo_port = int(os.environ["MONGODB_PORT"])
mongo_database = os.environ["MONGODB_DATABASE"]

client = MongoClient(f"mongodb://{mongo_username}:{mongo_password}@{mongo_host}:{mongo_port}/")
db = client[mongo_database]

@app.get("/")
def read_root():
    return {"Hello": "World"}
