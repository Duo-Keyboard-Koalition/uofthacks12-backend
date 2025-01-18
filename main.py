from fastapi import FastAPI
from models import UserQuestion

app = FastAPI()

@app.post("/question")
async def create_question(question: UserQuestion):
    # Here you would typically save to a database
    # For now, just return the received data
    return question

@app.get("/")
async def root():
    return {"message": "Question API is running"}
