import os
from fastapi import FastAPI, APIRouter
from fastapi.responses import JSONResponse
from typing import Dict
from models import Document
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pinecone import Pinecone
from openai import OpenAI
from umap import UMAP
import numpy as np
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
        self.router.add_api_route("/add_document", self.add_document, methods=["POST"])
        self.router.add_api_route("/find_document", self.find_document, methods=["GET"])
        self.router.add_api_route("/visualize", self.compute_graph, methods=["GET"])

    def read_root(self) -> Dict:
        return {"Hello": "World"}
        
    def add_document(self, document: Document) -> Dict:
        # 1 document per user
        # overrides existing docs
        # Get embeddings
        response = openai_client.embeddings.create(
            input=document.text,
            model="text-embedding-ada-002"
        )
        vector = response.data[0].embedding

        # Prepare document
        user_document = document.model_dump()
        user_document["timestamp"] = datetime.now(timezone.utc)

        # Store in Pinecone
        pc.Index(pc_idx).upsert(
            vectors=[{
                "id": user_document['user_id'],
                "values": vector,
                "metadata": {k: v for k, v in user_document.items() if k != 'user_id'}
            }],
            namespace="questions"
        )
        
        return {
            "status": "complete",
            "id": user_document['user_id'],
            "text": user_document['text']
        }

    def find_document(self, userId: str) -> dict:
        response = pc.Index(pc_idx).fetch(
            ids=[userId],
            namespace="questions"
        )
        
        metadata_results = {}
        for vector_id, vector_data in response.get('vectors', {}).items():
            metadata_results[vector_id] = vector_data.get('metadata', {})

        # Return the results as JSON
        return JSONResponse(content={"results": metadata_results})
        
    def compute_graph(self) -> dict:
        vectors = []
        ids = []

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
    
app = FastAPI(lifespan=lifespan)
# Initialize router
main_router = MainRouter()
app.include_router(main_router.router)