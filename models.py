from pydantic import BaseModel

class UserQuestion(BaseModel):
    UserID: str
    QuestionAsked: str
    QuestionAnswer: str
