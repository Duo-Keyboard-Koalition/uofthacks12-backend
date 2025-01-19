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
pc_idx = "uofthacks12" # this is the users database
user_db = "questions"
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
        self.router.add_api_route("/query", self.query, methods=["GET"])

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
            namespace=user_db
        )
        
        return {
            "status": "complete",
            "id": user_document['user_id'],
            "text": user_document['text']
        }

    def find_document(self, userId: str) -> dict:
        response = pc.Index(pc_idx).fetch(
            ids=[userId],
            namespace=user_db
        )
        
        metadata_results = {}
        for vector_id, vector_data in response.get('vectors', {}).items():
            metadata_results[vector_id] = vector_data.get('metadata', {})

        # Return the results as JSON
        return JSONResponse(content={"results": metadata_results})
        
    def query(self, userId: str, tiers: int = 3) -> dict:
        result = pc.Index(pc_idx).fetch(ids=[userId], namespace=user_db)
        target_vec = result['vectors'][userId]['values']

        # query for people w similar responses
        tiered_sim = {}
        ids, vectors, scores = [], [], []

        MAX_K = 10
        for j, k in enumerate(range(MAX_K // tiers, MAX_K + 1, MAX_K // tiers), start=1):
            result = pc.Index(pc_idx).query(vector=target_vec, top_k=k, namespace=user_db, include_values=True)
            tiered_sim[j] = {}

            for match in result['matches']:
                if match['id'] != userId:
                    tiered_sim[j][match['id']] = None
        
        result = pc.Index(pc_idx).query(vector=target_vec, top_k=MAX_K, namespace=user_db, include_values=True)
        for match in result['matches']:
            ids.append(match['id'])
            vectors.append(match['values'])
            scores.append(match['score'])

        vectors = np.array(vectors)

        umap = UMAP(n_components=2, random_state=42)
        embeddings_2d = umap.fit_transform(vectors).tolist()

        return {"embeddings_2d": embeddings_2d, "labels": ids, "tiers": tiered_sim, "sim_scores": scores}
    
app = FastAPI(lifespan=lifespan)
# Initialize router
main_router = MainRouter()
app.include_router(main_router.router)