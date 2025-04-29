from pydantic import BaseModel
from typing import List

class GradeModel(BaseModel):
    subject: str
    score: float

class StudentModel(BaseModel):
    name: str
    grades: List[GradeModel]
