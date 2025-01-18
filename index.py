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
import matplotlib.pyplot as plt
from umap import UMAP
import numpy as np
import uuid
import dotenv


dir_path = os.path.dirname(os.path.realpath(__file__))
dotenv.load_dotenv(os.path.join(dir_path, ".env"))
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
pc_idx = "uofthacks12"

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        print("Successfully connected to MongoDB!")
        print("Successfully connected to Pinecone!")
        yield
    finally:
        try:
            print("Successfully disconnected from Pinecone!")
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
        self.router.add_api_route("/question", self.add_question, methods=["POST"])
        self.router.add_api_route("/query", self.query_question, methods=["POST"])
        self.router.add_api_route("/visualize", self.compute_graph, methods=["GET"])
        self.router.add_api_route("/query_by_field", self.query_by_field, methods=["GET"])
        self.router.add_api_route("/update_question", self.update_question, methods=["PUT"])

    def read_root(self) -> Dict:
        return {"Hello": "World"}
    
    def add_question(self, question: UserQuestion) -> Dict:
        try:
            # Get embeddings
            response = openai_client.embeddings.create(
                input=question.QuestionAnswer,
                model="text-embedding-ada-002"
            )
            vector = response.data[0].embedding
            
            # Prepare document
            question_doc = {
                "text": f"question: {question.QuestionAsked} answer: {question.QuestionAnswer}",
                "userId": question.UserID,
                "questionAsked": question.QuestionAsked,
                "answer": question.QuestionAnswer,
                "timestamp": datetime.now(timezone.utc)
            }
            # Store in Pinecone
            pc.Index(pc_idx).upsert(
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
    
    def query_by_field(self, field: str, id: str) -> dict:
        dummy_vec = np.zeros(1536).tolist()

        response = pc.Index(pc_idx).query(
            vector=dummy_vec,
            filter={field: {"$eq": id}},
            top_k=10000,  # Adjust based on your needs
            include_metadata=True,
            namespace="questions"
        )

        # Process the results to ensure they're JSON-serializable
        processed_results = []
        for match in response['matches']:
            processed_match = {
                "id": match['id'],
                "score": float(match['score']),  # Convert numpy float to Python float
                "metadata": match['metadata']
            }
            processed_results.append(processed_match)

        # Return the results as JSON
        return JSONResponse(content={"results": processed_results})


    def update_question(self, responses: UserQuestion) -> dict:
        try:
            # Assuming the update is for the metadata fields
            updated_metadata = {
                "question": responses.QuestionAsked,
                "answer": responses.QuestionAnswer,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "userId": responses.UserID
            }
            pc.Index(pc_idx).update(
                id=responses.UserID,
                namespace="questions",
                metadata=updated_metadata
            )
            return {
                "status": "success",
                "message": "Entry updated successfully"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
        
    def query_question(self, question: UserQuestion) -> dict:
        try:
            query_response = openai_client.embeddings.create(
                input=question.QuestionAsked,
                model="text-embedding-ada-002"
            )
            query_vector = query_response.data[0].embedding

            response = pc.Index(pc_idx).query(
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
    
    def compute_graph(self) -> dict:
        try:
            vectors = []
            ids = []

            # print(pinecone_client.Index(pinecone_index).fetch())
            print(pc.Index(pc_idx).describe_index_stats())
            print(list(pc.Index(pc_idx).list(namespace="questions")))

            # gets list of ALL vectors
            indices = list(pc.Index(pc_idx).list(namespace="questions"))
            rows = pc.Index(pc_idx).fetch(*indices, namespace="questions")

            ids, vectors = {id: rows['vectors'][id]['values'] for id in rows['vectors']}
            vectors = np.array(vectors)
            print(vectors)

            umap = UMAP(n_components=2, random_state=42)
            embeddings_2d = umap.fit_transform(vectors).tolist()
            print(embeddings_2d)

            return {"embeddings_2d": embeddings_2d, "labels": ids}

        except Exception as e:
            raise e
            return {
                "status": "error",
                "message": str(e)
            }
    
app = FastAPI(lifespan=lifespan)
# Initialize router
main_router = MainRouter()
app.include_router(main_router.router)