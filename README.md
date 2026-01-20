HireSense AI 🚀

AI-Powered Resume & Job Matching Platform

HireSense AI is a full-stack web application that analyzes how well a candidate’s resume matches a given job description using AI-powered agents and deterministic scoring logic.

The platform supports PDF resume uploads, provides clear match scores, highlights strengths and gaps, and offers actionable improvement suggestions.

🔗 Live Project

Frontend (Vercel): https://hiresense-ai-beige.vercel.app

Backend (Render): https://hiresense-ai-backend.onrender.com

📌 Key Features

📄 Upload resume in PDF format or paste text

📝 Paste job description

🤖 Multi-agent AI analysis (Resume, Job, Matching)

📊 Deterministic match score

✅ Clear strengths, gaps, and suggestions

🧠 Robust fallback handling (never crashes)

⚡ Fast and responsive UI

🌐 Fully deployed and usable end-to-end

    🛠 Tech Stack
  Frontend

Next.js (App Router)

TypeScript

Tailwind CSS

Deployed on Vercel

Backend

FastAPI

Python

AI Agents using OpenRouter

PDF text extraction

Deployed on Render

    🧠 How It Works (Architecture)

User uploads a resume (PDF) or pastes text

User pastes job description

    Backend runs:

    Resume analysis agent
    
    Job description analysis agent
    
    Match analysis agent (best-effort)
    
    A deterministic scoring algorithm calculates the final match score
    
    Backend returns a structured JSON response
    
    Frontend displays:
    
    Match score
    
    Strengths

Gaps

Improvement suggestions

📤 API Endpoint
POST /analyze

Form Data:
    
    job_text (required)
    
    resume_text (optional)
    
    resume_file (optional, PDF)
    
    Response Format:
    
    {
      "resume": "...",
      "job": "...",
      "analysis": {
        "match_score": 75,
        "strengths": [],
        "gaps": [],
        "improvement_suggestions": []
      }
    }


🔐 Reliability & Error Handling

Safe JSON parsing

Deterministic fallback responses

Graceful handling of AI failures

Backend never crashes

User always receives a valid result

    📂 Repository Structure
    hiresense-ai/
    ├── frontend/        # Next.js frontend
    ├── ai-service/      # FastAPI backend
    │   ├── agents/
    │   ├── lib/
    │   └── main.py
    └── README.md
