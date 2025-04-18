from pydantic import BaseModel

class AnswerSchema(BaseModel):
    answer: str
