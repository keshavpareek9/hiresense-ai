from pydantic_ai import Agent

job_agent = Agent(
    model="openrouter:mistralai/mistral-7b-instruct",
    system_prompt="""
    You are an expert recruiter.
    Extract structured job description information from text.
    Respond ONLY with valid JSON.
    """
)
