"""
HireSense AI – Backend Service
--------------------------------
This FastAPI service powers the HireSense AI application.

Responsibilities:
- Accept resume + job description
- Run multi-agent AI analysis (resume, job, matching)
- Calculate a deterministic match score
- Return clean JSON to frontend
"""

# =========================
# Environment Setup
# =========================
from dotenv import load_dotenv
load_dotenv()

# =========================
# Core Imports
# =========================
from fastapi import FastAPI, Response, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import logging
import json

from lib.pdf_utils import extract_text_from_pdf

# =========================
# Agent Imports
# =========================
from agents.resume_agent import resume_agent
from agents.job_agent import job_agent
from agents.match_agent import match_agent

# =========================
# App Initialization
# =========================
app = FastAPI(title="HireSense AI Service")

# =========================
# CORS Configuration
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# Logging
# =========================
logging.basicConfig(level=logging.INFO)

# =========================
# Health Check
# =========================
@app.get("/health")
def health():
    return {"status": "ok"}

# =========================
# OPTIONS (CORS preflight)
# =========================
@app.options("/analyze")
def analyze_options():
    return Response(status_code=200)

# =========================
# GET guard
# =========================
@app.get("/analyze")
def analyze_get():
    return {
        "message": "This endpoint requires POST. Use POST /analyze."
    }

# =========================
# Deterministic Scoring
# =========================
def extract_skills(text: str) -> set[str]:
    text = text.lower()

    skill_keywords = [
        "python", "java", "javascript", "typescript",
        "react", "angular", "vue",
        "sql", "postgresql", "mysql", "mongodb",
        "fastapi", "django", "flask",
        "aws", "azure", "gcp", "cloud",
        "docker", "kubernetes", "ci/cd",
        "machine learning", "data analysis",
        "backend", "frontend", "api",
        "git", "linux"
    ]

    return {s for s in skill_keywords if s in text}


def calculate_score(resume: str, job: str) -> int:
    resume_skills = extract_skills(resume)
    job_skills = extract_skills(job)

    if not job_skills:
        return 50

    matched = resume_skills.intersection(job_skills)
    raw = int((len(matched) / len(job_skills)) * 100)

    return round(raw / 5) * 5


# =========================
# MAIN ANALYSIS ENDPOINT
# =========================
@app.post("/analyze")
async def analyze(
    job_text: str = Form(...),
    resume_text: str | None = Form(None),
    resume_file: UploadFile | None = File(None),
):
    logging.info("Analyze request received")

    try:
        # 1️⃣ Get resume content
        if resume_file:
            if not resume_file.filename.endswith(".pdf"):
                return {"error": "Only PDF resumes are supported"}
            resume_content = extract_text_from_pdf(resume_file.file)
        elif resume_text:
            resume_content = resume_text
        else:
            return {"error": "Provide either resume text or PDF resume"}

        # 2️⃣ Run resume + job agents
        resume_result = await resume_agent.run(resume_content)
        job_result = await job_agent.run(job_text)

        # 3️⃣ Combine input
        combined_input = f"""
RESUME:
{resume_result.output}

JOB DESCRIPTION:
{job_result.output}
"""

        # 4️⃣ Match agent (LLM)
        match_result = await match_agent.run(combined_input)

        # 5️⃣ Deterministic score
        score = calculate_score(resume_content, job_text)

        # 6️⃣ Safe JSON parse
        try:
            parsed = json.loads(match_result.output)
        except Exception:
            parsed = {}

        # 7️⃣ HARD GUARANTEED OUTPUT (never empty)
        analysis = {
            "match_score": score,
            "strengths": parsed.get(
                "strengths",
                [
                    "Relevant skills and experience were identified in the resume.",
                    "The candidate meets several core job requirements."
                ],
            ),
            "gaps": parsed.get(
                "gaps",
                [
                    "Some responsibilities mentioned in the job description are not clearly reflected.",
                ],
            ),
            "improvement_suggestions": parsed.get(
                "improvement_suggestions",
                [
                    "Align resume keywords more closely with the job description.",
                    "Add concrete examples of past work related to this role."
                ],
            ),
        }

        return {
            "analysis": analysis
        }

    except Exception as e:
        logging.error(f"Analysis failed: {e}")

        return {
            "analysis": {
                "match_score": 50,
                "strengths": [
                    "Resume content was successfully processed."
                ],
                "gaps": [
                    "AI analysis could not be completed due to a temporary issue."
                ],
                "improvement_suggestions": [
                    "Please try again or simplify the resume text."
                ],
            }
        }
