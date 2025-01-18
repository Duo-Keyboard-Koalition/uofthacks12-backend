from fastapi import FastAPI, APIRouter
from typing import Dict
from models import UserQuestion
from database.db_test import test_mongo_connection
from contextlib import asynccontextmanager
app = FastAPI()
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Test database connection on startup
    try:
        await test_mongo_connection()  # Ensure this function is async
        print("Database connection successful!")
        yield  # This allows the app to run
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
        
    def add_question(self, question: UserQuestion) -> Dict:
        return {
            "status": "success",
            "question": {
                "userId": question.UserID,
                "questionAsked": question.QuestionAsked,
                "answer": question.QuestionAnswer
            }
        }

# Initialize router
main_router = MainRouter()
app.include_router(main_router.router)