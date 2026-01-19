from pydantic import BaseModel
from typing import List

class JobDescription(BaseModel):
    role: str
    required_skills: List[str]
    experience_required: int
    responsibilities: List[str]
