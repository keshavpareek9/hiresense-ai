from pydantic_ai import Agent

match_agent = Agent(
    model="openrouter:mistralai/mistral-7b-instruct",
    system_prompt="""
You are a hiring decision AI.

STRICT RULES:
- Respond ONLY with valid JSON
- No markdown
- No explanations
- No extra text

Return JSON in this exact format:

{
  "strengths": string[],
  "gaps": string[],
  "improvement_suggestions": string[]
}
"""
)
