from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import os
from pinecone import Pinecone, ServerlessSpec

def test_mongo_connection():
    # Test MongoDB connection
    mongodb_client = MongoClient(os.getenv("MONGODB_URI"), server_api=ServerApi('1'))
    try:
        mongodb_client.admin.command('ping')
        print("Successfully connected to MongoDB!")
    except Exception as e:
        print(f"MongoDB connection error: {e}")
    # stop the client
    mongodb_client.close()
def test_pinecone():
    # Test Pinecone connection
    try:
        pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        indexes = pc.list_indexes()
        print(f"Successfully connected to Pinecone. Available indexes: {indexes}")
    except Exception as e:
        print(f"Pinecone connection error: {e}")
