from pydantic import BaseModel
from typing import List

class Resume(BaseModel):
    name: str
    years_experience: int
    skills: List[str]
    education: str
    projects: List[str]
