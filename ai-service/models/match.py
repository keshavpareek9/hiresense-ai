from pydantic import BaseModel
from typing import List

class MatchResult(BaseModel):
    match_score: int
    strengths: List[str]
    gaps: List[str]
    improvement_suggestions: List[str]
