import os

from fastapi import FastAPI, APIRouter
from fastapi.responses import JSONResponse
from typing import Dict
from models import UserQuestion
# from database.db_test import test_mongo_connection
from contextlib import asynccontextmanager
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime, timezone
from pinecone import Pinecone
from openai import OpenAI
import uuid
import dotenv
dir_path = os.path.dirname(os.path.realpath(__file__))
dotenv.load_dotenv(os.path.join(dir_path, ".env"))
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
pinecone_client = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
pinecone_index = "uofthacks12"

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Test database connection on startup
    try:
        # test_mongo_connection()
        print("Successfully connected to MongoDB!")
        # index = pinecone_client.Index(pinecone_index)
        print("Successfully connected to Pinecone!")
        yield
    finally:
        # Shutdown logic
        try:
            # Close Pinecone connection
            # pinecone_client.deinit()
            print("Successfully disconnected from Pinecone!")
            
            # Close MongoDB connection if you're using it
            # await mongo_client.close()
            # print("Successfully disconnected from MongoDB!")
            
        except Exception as e:
            print(f"Error during shutdown: {str(e)}")

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
        self.router.add_api_route("/query", self.query_question, methods=["POST"])

    def read_root(self) -> Dict:
        return {"Hello": "World"}

    def hello(self) -> Dict:
        return {"message": "Hello from UofTHacks!"}
    
    def add_question(self, question: UserQuestion) -> Dict:
        try:
            # Get embeddings
            response = openai_client.embeddings.create(
                input=question.QuestionAnswer,
                model="text-embedding-ada-002"
            )
            vector = response.data[0].embedding
            # print("Vector: ", vector)
            # Prepare document
            question_doc = {
                "userId": question.UserID,
                "questionAsked": question.QuestionAsked,
                "answer": question.QuestionAnswer,
                "timestamp": datetime.now(timezone.utc)
            }
            # Store in Pinecone
            pinecone_client.Index(pinecone_index).upsert(
                vectors=[{
                    "id": str(uuid.uuid4()),
                    "values": vector,
                    "metadata": {
                        "question": question.QuestionAsked,
                        "answer": question.QuestionAnswer,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "userId": question.UserID
                    }
                }],
                namespace="questions"
            )
            return {
                "status": "success",
                "id": question.UserID,
                "question": question_doc
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    def query_question(self, question: UserQuestion) -> list:
        try:
            query_response = openai_client.embeddings.create(
                input=question.QuestionAsked,
                model="text-embedding-ada-002"
            )
            query_vector = query_response.data[0].embedding

            response = pinecone_client.Index(pinecone_index).query(
                namespace="questions",
                vector=query_vector,
                top_k=3,
                include_metadata=True,
                include_values=False
            )
            results = [
                {
                    "id": match["id"],
                    "score": float(match["score"]),  # Convert score to float
                    "metadata": match.get("metadata", {})
                }
                for match in response.get("matches", [])
            ]

            return JSONResponse(content=results)
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    

app = FastAPI(lifespan=lifespan)
# Initialize router
main_router = MainRouter()
app.include_router(main_router.router)