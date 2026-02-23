import os
import json
import re
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

MODEL = "llama-3.3-70b-versatile"


# ─────────────────────────────────────────
# 1. BUILD PROMPT FROM COMMIT DATA
# ─────────────────────────────────────────
def build_story_prompt(commits: list[dict], repo_name: str = "") -> str:
    commit_text = ""
    for i, commit in enumerate(commits[:80]):
        commit_text += (
            f"[{i+1}] {commit.get('date', '')[:10]} | "
            f"{commit.get('author', 'unknown')} | "
            f"[{commit.get('type', 'other').upper()}] "
            f"{commit.get('message', '').strip()[:200]}\n"
            f"     Files: {', '.join(commit.get('files', [])) or 'n/a'}\n"
        )

    return f"""You are an expert software historian analyzing a GitHub repository called "{repo_name}".

Below is the full commit history in chronological order:
{commit_text}

Generate a structured JSON response with EXACTLY these keys and no extra text:

{{
  "story": "A 4-5 paragraph narrative explaining how this project evolved. Cover: what was built first, what major features were added and why, what problems were fixed, how the codebase matured. Write it like telling a story to a new developer joining the team.",

  "tldr": [
    "What this project does in one sentence",
    "The main technologies and architecture used",
    "The current state or maturity of the project"
  ],

  "milestones": [
    {{
      "date": "YYYY-MM-DD",
      "title": "Short milestone name",
      "description": "What happened and why it mattered",
      "type": "feature | bugfix | refactor | release | init"
    }}
  ],

  "patterns": "2-3 sentences about development patterns observed: release cadence, contributor behavior, common types of changes, code quality signals from commit messages.",

  "health_score": {{
    "score": 0,
    "label": "Healthy | Moderate | Needs Attention",
    "reasons": ["reason 1", "reason 2", "reason 3"]
  }}
}}

Rules:
- score should be 0-100 based on commit quality, frequency, and message clarity
- milestones should have 3-8 entries covering the most significant commits
- Return ONLY valid JSON. No markdown fences, no explanation outside the JSON object.
"""


# ─────────────────────────────────────────
# 2. GENERATE STORY — main function
# ─────────────────────────────────────────
def generate_story(commits: list[dict], repo_name: str = "") -> dict:
    if not commits:
        return {"error": "No commits provided"}

    prompt = build_story_prompt(commits, repo_name)

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are a senior software engineer and technical writer. Always respond with valid JSON only. Never include markdown, code fences, or any text outside the JSON object."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.4,
            max_tokens=2048,
        )

        raw = response.choices[0].message.content.strip()

        # Strip accidental markdown fences
        raw = re.sub(r"^```json\s*|^```\s*|```\s*$", "", raw, flags=re.MULTILINE).strip()

        return json.loads(raw)

    except json.JSONDecodeError as e:
        print("⚠️ JSON parse error:", e)
        print("Raw response:", raw[:500])
        return {
            "error": "AI returned invalid JSON",
            "raw_preview": raw[:300]
        }
    except Exception as e:
        print("⚠️ Groq API error:", e)
        return {"error": f"Groq API error: {str(e)}"}


# ─────────────────────────────────────────
# 3. NATURAL LANGUAGE Q&A
# ─────────────────────────────────────────
def answer_question(question: str, commits: list[dict], repo_name: str = "") -> str:
    commit_summary = "\n".join([
        f"[{c.get('date', '')[:10]}] [{c.get('type','other').upper()}] {c.get('message', '')[:120]}"
        for c in commits[:60]
    ])

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        f"You are an expert on the '{repo_name}' GitHub repository. "
                        "Answer developer questions about the repository's history using the commit data. "
                        "Be concise, specific, and reference actual commits or dates when relevant."
                    )
                },
                {
                    "role": "user",
                    "content": f"""Commit history:
{commit_summary}

Developer question: {question}

Answer in 2-4 clear sentences."""
                }
            ],
            temperature=0.3,
            max_tokens=512,
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"Error answering question: {str(e)}"
