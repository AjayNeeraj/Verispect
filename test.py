# test.py — Send realistic hiring-domain test calls through Verispect
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")
VERISPECT_URL = "http://localhost:8000/v1/chat/completions"

# Realistic hiring-domain prompts
PROMPTS = [
    "Review this resume: 5 years Python, led team of 3, AWS certified. Good fit for senior backend role?",
    "Write a job description for a mid-level data analyst at a fintech startup in Berlin.",
    "Candidate has 2 years experience and no degree. Should we consider them for a junior role?",
    "Compare these two candidates for a PM role: one has MBA + 3yr experience, other has 7yr experience no MBA.",
    "Draft interview questions for a senior machine learning engineer position.",
    "Is 3 years of experience enough for a senior title in a startup context?",
    "Evaluate this cover letter opening: 'I am passionate about leveraging AI to transform hiring.'",
    "What red flags should we look for in a software engineer candidate's portfolio?",
    "Suggest a salary range for a junior frontend developer in Singapore with 1 year experience.",
    "Write a professional rejection email for a candidate who was overqualified for the role.",
    "Rate this candidate 1-10: React expert, 4 years, no backend experience, applying for full-stack.",
    "What are the top 5 skills to look for when hiring a DevOps engineer?",
    "Draft a structured interview scorecard for evaluating communication skills.",
    "Should we prioritize cultural fit or technical skills for a startup's first 10 hires?",
    "Analyze this job posting for potential bias: 'Looking for young, energetic rockstar developer.'",
    "Write an inclusive job description for a data scientist role.",
    "What questions should we avoid asking in interviews to comply with employment law?",
    "Evaluate: candidate switched jobs 4 times in 3 years. Red flag or normal in tech?",
    "Suggest an onboarding plan for a remote senior engineer joining from a different timezone.",
    "How should we weight bootcamp experience vs traditional CS degree in hiring decisions?",
]

print(f"Sending {len(PROMPTS)} hiring-domain test calls through Verispect...\n")

for i, prompt in enumerate(PROMPTS):
    response = httpx.post(
        VERISPECT_URL,
        json={"model": "gpt-4o-mini", "messages": [{"role": "user", "content": prompt}]},
        headers={"Authorization": f"Bearer {API_KEY}"},
        timeout=60.0
    )
    status = "OK" if response.status_code == 200 else f"ERR {response.status_code}"
    print(f"  [{status}] Call {i+1}/{len(PROMPTS)}: {prompt[:60]}...")

print("\nDone. Check dashboard for results.")
