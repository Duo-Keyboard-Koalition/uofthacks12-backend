import os
from fastapi import FastAPI, APIRouter
from typing import Dict
from models import UserQuestion
# from database.db_test import test_mongo_connection
from contextlib import asynccontextmanager
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime, timezone
from pinecone import Pinecone



@asynccontextmanager
async def lifespan(app: FastAPI):
    # Test database connection on startup
    try:
        # test_mongo_connection()
        print("Successfully connected to MongoDB!")

        pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        index = pc.Index("meta3-hackathon")
        print("Successfully connected to Pinecone!")
        yield
    except Exception as e:
        print(f"Database connection failed: {str(e)}")
        raise e

class BaseRouter:
    def __init__(self):
        self.router = APIRouter()
        self.setup_routes()

    def setup_routes(self):
        pass

class MainRouter(BaseRouter):
    def setup_routes(self):
        self.router.add_api_route("/", self.read_root, methods=["GET"])
        self.router.add_api_route("/hello", self.hello, methods=["GET"])
        self.router.add_api_route("/question", self.add_question, methods=["POST"])

    def read_root(self) -> Dict:
        return {"Hello": "World"}

    def hello(self) -> Dict:
        return {"message": "Hello from UofTHacks!"}
    async def add_question(self, question: UserQuestion) -> Dict:
        try:
            # Create new MongoDB client
            client : MongoClient = MongoClient(os.getenv("MONGODB_URI"), server_api=ServerApi('1'))
            
            # Get database and collection
            db = client['uofthacks']
            questions = db['questions']
            
            # Prepare document
            question_doc = {
                "userId": question.UserID,
                "questionAsked": question.QuestionAsked,
                "answer": question.QuestionAnswer,
                "timestamp": datetime.now(timezone.utc)
            }
            
            # Insert document
            result = questions.insert_one(question_doc)
            
            return {
                "status": "success",
                "id": str(result.inserted_id),
                "question": question_doc
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
            
        finally:
            if client:
                client.close()
app = FastAPI(lifespan=lifespan)
# Initialize router
main_router = MainRouter()
app.include_router(main_router.router)