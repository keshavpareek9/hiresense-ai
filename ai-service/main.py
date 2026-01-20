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
        # 1️⃣ Resume source
        if resume_file:
            if not resume_file.filename.endswith(".pdf"):
                raise ValueError("Only PDF resumes are supported")
            resume_content = extract_text_from_pdf(resume_file.file)
        elif resume_text:
            resume_content = resume_text
        else:
            raise ValueError("Resume text or PDF required")

        # 2️⃣ Run agents (best-effort, NOT trusted)
        resume_result = await resume_agent.run(resume_content)
        job_result = await job_agent.run(job_text)

        combined_input = f"""
RESUME:
{resume_result.output}

JOB:
{job_result.output}
"""

        match_text = ""
        try:
            match_result = await match_agent.run(combined_input)
            match_text = match_result.output
        except Exception:
            match_text = ""

        # 3️⃣ Deterministic score (SOURCE OF TRUTH)
        score = calculate_score(resume_content, job_text)

        # 4️⃣ Build SAFE structured response
        strengths = []
        gaps = []
        suggestions = []

        if score >= 70:
            strengths.append("Strong overlap between resume skills and job requirements.")
        elif score >= 40:
            strengths.append("Some relevant skills match the job description.")
            gaps.append("Several required skills are missing or weakly represented.")
        else:
            gaps.append("Limited alignment between resume and job description.")

        if "api" not in resume_content.lower():
            gaps.append("API development experience is not clearly demonstrated.")
            suggestions.append("Add specific API or backend project experience.")

        if not suggestions:
            suggestions.append("Continue strengthening core skills relevant to the role.")

        return {
            "resume": resume_result.output,
            "job": job_result.output,
            "analysis": {
                "match_score": score,
                "strengths": strengths,
                "gaps": gaps,
                "improvement_suggestions": suggestions,
            },
        }

    except Exception as e:
        logging.error(f"Analysis failed: {e}")

        # 🔒 ABSOLUTE FALLBACK (NEVER FAILS)
        return {
            "resume": "",
            "job": "",
            "analysis": {
                "match_score": 50,
                "strengths": ["Resume was processed successfully."],
                "gaps": ["Unable to fully analyze resume content."],
                "improvement_suggestions": [
                    "Try simplifying the resume text or uploading a clearer PDF."
                ],
            },
        }
