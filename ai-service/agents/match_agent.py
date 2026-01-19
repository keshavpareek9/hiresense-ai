from pydantic_ai import Agent

match_agent = Agent(
    model="openrouter:mistralai/mistral-7b-instruct",
    system_prompt="""
You are a hiring analysis AI.

STRICT RULES:
- Respond with VALID JSON only
- Do NOT include explanations or markdown
- Do NOT generate a numeric score

TASK:
Given a resume and job description:
1. Identify strengths
2. Identify gaps
3. Provide improvement suggestions

RESPONSE FORMAT (STRICT):
{
  "strengths": [string],
  "gaps": [string],
  "improvement_suggestions": [string]
}
"""
)
