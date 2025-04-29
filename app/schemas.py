from pydantic import BaseModel
from typing import List, Optional

class Grade(BaseModel):
    subject: str
    score: float

class Student(BaseModel):
    name: str
    grades: List[Grade]
