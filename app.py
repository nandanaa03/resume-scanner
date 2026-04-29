from flask import Flask, request, jsonify, render_template
import requests
import json
import PyPDF2
import io

app = Flask(__name__)

import os
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

def call_ai(prompt):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:5000",
        "X-Title": "ResumeIQ"
    }
    payload = {
        "model": "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",
        "messages": [{"role": "user", "content": prompt}]
    }
    response = requests.post(OPENROUTER_URL, headers=headers, json=payload)
    result = response.json()
    print("OpenRouter response:", result)
    return result["choices"][0]["message"]["content"]

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/scan", methods=["POST"])
def scan():
    resume_text = ""

    if "resume_file" in request.files:
        file = request.files["resume_file"]
        if file.filename.endswith(".pdf"):
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file.read()))
            for page in pdf_reader.pages:
                resume_text += page.extract_text()
        else:
            resume_text = file.read().decode("utf-8")
    else:
        resume_text = request.form.get("resume_text", "")

    jd = request.form.get("jd", "")

    if not resume_text or not jd:
        return jsonify({"error": "Please provide both resume and job description."}), 400

    prompt = f"""You are a senior ATS (Applicant Tracking System) expert and technical recruiter. Analyze the resume against the job description thoroughly.

RESUME:
{resume_text}

JOB DESCRIPTION:
{jd}

Provide a detailed analysis in this EXACT format with no deviations:

Match Score: <number between 0-100>
Experience Match: <number between 0-100>
Skills Match: <number between 0-100>
Education Match: <number between 0-100>

Strong Points:
- <strong point 1>
- <strong point 2>
- <strong point 3>

Missing Skills:
- <missing skill 1>
- <missing skill 2>
- <missing skill 3>

Suggested Courses:
- <course or certification to fill gap 1>
- <course or certification to fill gap 2>
- <course or certification to fill gap 3>

Resume Improvements:
- <specific improvement 1>
- <specific improvement 2>
- <specific improvement 3>

Keyword Gaps:
- <important keyword from JD missing in resume 1>
- <important keyword from JD missing in resume 2>
- <important keyword from JD missing in resume 3>

Verdict: <2-3 sentence professional verdict on the candidate's fit for this role>"""

    result = call_ai(prompt)
    return jsonify({"result": result})

if __name__ == "__main__":
    app.run(debug=True)