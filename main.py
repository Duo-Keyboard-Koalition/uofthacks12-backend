from fastapi import FastAPI, APIRouter
from models import UserQuestion

app = FastAPI()
router = APIRouter()

class QuestionView:
    @router.post("/question")
    async def create_question(self, question: UserQuestion):
        # Here you would typically save to a database
        # For now, just return the received data
        return question

    @router.get("/")
    async def root(self):
        return {"message": "Question API is running"}

# Initialize the view
question_view = QuestionView()

# Include the router
app.include_router(router)
