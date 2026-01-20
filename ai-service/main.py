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
load_dotenv()  # Load API keys from .env

# =========================
# Core Imports
# =========================
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
import logging
import json

from fastapi import UploadFile, File, Form
from lib.pdf_utils import extract_text_from_pdf

# =========================
# Agent Imports
# =========================
from agents.resume_agent import resume_agent
from agents.job_agent import job_agent
from agents.match_agent import match_agent

# =========================
# Request Models
# =========================
from models.analyze_request import AnalyzeRequest

# =========================
# App Initialization
# =========================
app = FastAPI(title="HireSense AI Service")

# =========================
# CORS Configuration
# IMPORTANT: Required for browser → backend calls
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # Allow all origins (OK for dev)
    allow_credentials=False,
    allow_methods=["*"],          # Allow GET, POST, OPTIONS, etc.
    allow_headers=["*"],
)

# =========================
# Logging Setup
# =========================
logging.basicConfig(level=logging.INFO)

# =========================
# Health Check Endpoint
# =========================
@app.get("/health")
def health():
    """
    Simple health check for deployment & monitoring
    """
    return {"status": "ok"}

# =========================
# OPTIONS Handler (CORS Preflight)
# =========================
@app.options("/analyze")
def analyze_options():
    """
    Explicitly handle browser preflight requests
    """
    return Response(status_code=200)

# =========================
# GET Guard for /analyze
# =========================
@app.get("/analyze")
def analyze_get():
    """
    Prevent accidental GET access in browser
    """
    return {
        "message": "This endpoint requires POST. Use POST /analyze with resume_text and job_text."
    }

# =========================
# Deterministic Score Calculator
# =========================
import re

def extract_skills(text: str) -> set[str]:
    """
    Extracts potential skills from text using simple heuristics.
    Deterministic and field-agnostic.
    """
    text = text.lower()

    # Common skill patterns (expandable)
    skill_keywords = [
        "python", "java", "javascript", "typescript",
        "react", "angular", "vue",
        "sql", "nosql", "postgresql", "mysql", "mongodb",
        "fastapi", "django", "flask",
        "aws", "azure", "gcp", "cloud",
        "docker", "kubernetes", "ci/cd",
        "machine learning", "deep learning",
        "data analysis", "pandas", "numpy",
        "backend", "frontend", "fullstack",
        "api", "microservices",
        "ui", "ux",
        "testing", "automation",
        "scalable", "distributed",
        "git", "linux"
    ]

    found = set()
    for skill in skill_keywords:
        if skill in text:
            found.add(skill)

    return found


def calculate_score(resume: str, job: str) -> int:
    """
    Generic, deterministic scoring for any job role.
    """

    resume_skills = extract_skills(resume)
    job_skills = extract_skills(job)

    if not job_skills:
        return 50  # neutral fallback

    matched = resume_skills.intersection(job_skills)

    raw_score = int((len(matched) / len(job_skills)) * 100)

    # Normalize score
    return round(raw_score / 5) * 5


# =========================
# MAIN ANALYSIS ENDPOINT
# =========================
@app.post("/analyze")
async def analyze(
    job_text: str = Form(...),
    resume_text: str | None = Form(None),
    resume_file: UploadFile | None = File(None),
):
    """
    Analyze resume-job match.
    Accepts either pasted resume text OR uploaded PDF.
    """

    logging.info("Analyze request received")

    try:
        # 1️⃣ Determine resume source
        if resume_file:
            if not resume_file.filename.endswith(".pdf"):
                return {"error": "Only PDF resumes are supported"}

            resume_content = extract_text_from_pdf(resume_file.file)

        elif resume_text:
            resume_content = resume_text

        else:
            return {"error": "Provide either resume text or PDF resume"}

        # 2️⃣ Run Resume Agent
        resume_result = await resume_agent.run(resume_content)

        # 3️⃣ Run Job Agent
        job_result = await job_agent.run(job_text)

        # 4️⃣ Combine outputs for match agent
        combined_input = f"""
        RESUME:
        {resume_result.output}

        JOB DESCRIPTION:
        {job_result.output}
        """

       # 5️⃣ Run Match Agent (qualitative)
    match_result = await match_agent.run(combined_input)

# 6️⃣ Deterministic score
    score = calculate_score(resume_content, job_text)

    analysis = json.loads(match_result.output)
    analysis["match_score"] = score

    return {
    "resume": resume_result.output,
    "job": job_result.output,
    "analysis": analysis,   # ✅ return JSON object, NOT string
        }
