from pydantic_ai import Agent

resume_agent = Agent(
    model="openrouter:mistralai/mistral-7b-instruct",
    system_prompt="""
    You are a professional hiring AI.
    Extract structured resume information from text.
    Respond ONLY with valid JSON.
    """
)
