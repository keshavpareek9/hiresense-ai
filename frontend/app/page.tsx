"use client";

import { useState } from "react";

type AnalysisResult = {
  match_score: number;
  strengths: string[];
  gaps: string[];
  improvement_suggestions: string[];
};

export default function Home() {
  const [resumeText, setResumeText] = useState("");
  const [jobText, setJobText] = useState("");
  const [resumeFile, setResumeFile] = useState<File | null>(null);

  const [analysis, setAnalysis] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const analyzeMatch = async () => {
    setLoading(true);
    setError("");
    setAnalysis(null);

    try {
      const formData = new FormData();
      formData.append("job_text", jobText);

      if (resumeFile) {
        formData.append("resume_file", resumeFile);
      } else {
        formData.append("resume_text", resumeText);
      }

      const API_URL =
        process.env.NEXT_PUBLIC_API_URL ??
        "http://127.0.0.1:8000";

      const res = await fetch(`${API_URL}/analyze`, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        throw new Error("Backend error while analyzing resume");
      }

      const data = await res.json();

      // 🔒 HARD GUARANTEE: analysis must exist
      if (!data || !data.analysis) {
        throw new Error("Invalid analysis response from server");
      }

      setAnalysis({
        match_score:
          typeof data.analysis.match_score === "number"
            ? data.analysis.match_score
            : 0,
        strengths: Array.isArray(data.analysis.strengths)
          ? data.analysis.strengths
          : [],
        gaps: Array.isArray(data.analysis.gaps)
          ? data.analysis.gaps
          : [],
        improvement_suggestions: Array.isArray(
          data.analysis.improvement_suggestions
        )
          ? data.analysis.improvement_suggestions
          : [],
      });
    } catch (err: any) {
      console.error(err);
      setError(
        err?.message ||
          "Something went wrong. Please try again."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-gray-900 text-white">
      {/* Header */}
      <section className="py-14 text-center">
        <h1 className="text-5xl font-extrabold">
          HireSense AI
        </h1>
        <p className="mt-4 text-gray-300">
          AI-powered resume & job matching
        </p>
      </section>

      {/* Content */}
      <section className="max-w-6xl mx-auto px-6 pb-20 space-y-8">
        {/* Resume */}
        <div className="bg-gray-800 border border-gray-700 rounded-2xl p-6 space-y-4">
          <h2 className="text-xl font-semibold">
            Resume
          </h2>

          <input
            type="file"
            accept=".pdf"
            onChange={(e) =>
              setResumeFile(
                e.target.files?.[0] || null
              )
            }
            className="block w-full text-sm text-gray-300"
          />

          {!resumeFile && (
            <textarea
              className="w-full bg-gray-900 border border-gray-600 rounded-xl p-4 h-48"
              placeholder="Or paste resume text"
              value={resumeText}
              onChange={(e) =>
                setResumeText(e.target.value)
              }
            />
          )}

          {resumeFile && (
            <p className="text-sm text-green-400">
              Selected: {resumeFile.name}
            </p>
          )}
        </div>

        {/* Job */}
        <div className="bg-gray-800 border border-gray-700 rounded-2xl p-6 space-y-4">
          <h2 className="text-xl font-semibold">
            Job Description
          </h2>
          <textarea
            className="w-full bg-gray-900 border border-gray-600 rounded-xl p-4 h-48"
            placeholder="Paste job description"
            value={jobText}
            onChange={(e) =>
              setJobText(e.target.value)
            }
          />
        </div>

        {/* Button */}
        <button
          onClick={analyzeMatch}
          disabled={loading}
          className="w-full bg-white text-black py-4 rounded-xl text-lg font-semibold hover:bg-gray-200 transition"
        >
          {loading ? "Analyzing…" : "Analyze Match"}
        </button>

        {error && (
          <p className="text-red-400 text-center">
            {error}
          </p>
        )}

        {/* Results */}
        {analysis && (
          <div className="space-y-8">
            <div className="bg-black border border-gray-700 rounded-2xl p-8 text-center">
              <p className="text-gray-400">
                Match Score
              </p>
              <p className="text-6xl font-extrabold">
                {analysis.match_score}%
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <ResultCard
                title="Strengths"
                items={analysis.strengths}
              />
              <ResultCard
                title="Gaps"
                items={analysis.gaps}
              />
              <ResultCard
                title="Suggestions"
                items={
                  analysis.improvement_suggestions
                }
              />
            </div>
          </div>
        )}
      </section>
    </main>
  );
}

function ResultCard({
  title,
  items,
}: {
  title: string;
  items: string[];
}) {
  return (
    <div className="bg-gray-800 border border-gray-700 rounded-2xl p-6">
      <h3 className="text-xl font-semibold mb-4">
        {title}
      </h3>
      {items.length === 0 ? (
        <p className="text-gray-400 text-sm">
          No data available
        </p>
      ) : (
        <ul className="list-disc list-inside space-y-2 text-gray-300">
          {items.map((item, idx) => (
            <li key={idx}>{item}</li>
          ))}
        </ul>
      )}
    </div>
  );
}
