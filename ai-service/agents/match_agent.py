from pydantic import BaseModel
from pydantic_ai import Agent

class MatchResult(BaseModel):
    match_score: int
    strengths: list[str]
    gaps: list[str]
    improvement_suggestions: list[str]

match_agent = Agent(
    model="openrouter:mistralai/mistral-7b-instruct",
    system_prompt="""
You are a hiring decision AI.

STRICT RULES:
- Respond ONLY with valid JSON
- No markdown
- No explanations
- No extra text

Follow this exact schema:

{
  "match_score": number (0-100),
  "strengths": string[],
  "gaps": string[],
  "improvement_suggestions": string[]
}
""",
    result_type=MatchResult
)
