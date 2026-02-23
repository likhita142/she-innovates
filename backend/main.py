from fastapi import FastAPI, Query
from .github_service import get_commits, flatten_commit
from .db import commits_collection
from .ai_story_generator import generate_story, answer_question

app = FastAPI()


@app.get("/")
def root():
    return {"message": "GitStory backend running ✅"}


# ─────────────────────────────────────────
# /ingest  — fetch from GitHub & store
# ─────────────────────────────────────────
@app.get("/ingest")
def ingest(owner: str, repo: str):
    try:
        print(f"INGEST STARTED: {owner}/{repo}")

        raw_commits = get_commits(owner, repo)
        print(f"COMMITS FETCHED: {len(raw_commits)}")

        if not raw_commits:
            return {"error": "No commits found. Check owner/repo name or GitHub token."}

        # ✅ Remove old data for this repo before re-ingesting
        commits_collection.delete_many({"owner": owner, "repo": repo})

        # ✅ Flatten each commit to clean structure before storing
        cleaned = [flatten_commit(c, owner, repo) for c in raw_commits]
        commits_collection.insert_many(cleaned)

        return {
            "message": "Repo ingested successfully ✅",
            "owner": owner,
            "repo": repo,
            "count": len(cleaned)
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e)}


# ─────────────────────────────────────────
# /story  — generate AI story from commits
# ─────────────────────────────────────────
@app.get("/story")
def story(owner: str, repo: str):
    try:
        commits = list(commits_collection.find(
            {"owner": owner, "repo": repo},
            {"_id": 0}   # exclude MongoDB _id
        ))

        if not commits:
            return {"error": "No commits found. Run /ingest first.", "hint": f"/ingest?owner={owner}&repo={repo}"}

        print(f"Generating story for {owner}/{repo} with {len(commits)} commits...")

        result = generate_story(commits, repo_name=f"{owner}/{repo}")
        return {
            "owner": owner,
            "repo": repo,
            "commit_count": len(commits),
            **result
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e)}


# ─────────────────────────────────────────
# /ask  — natural language Q&A
# e.g. GET /ask?owner=x&repo=y&q=Why was auth added?
# ─────────────────────────────────────────
@app.get("/ask")
def ask(owner: str, repo: str, q: str = Query(..., description="Your question about the repo")):
    try:
        commits = list(commits_collection.find(
            {"owner": owner, "repo": repo},
            {"_id": 0}
        ))

        if not commits:
            return {"error": "No commits found. Run /ingest first."}

        answer = answer_question(q, commits, repo_name=f"{owner}/{repo}")
        return {
            "question": q,
            "answer": answer
        }

    except Exception as e:
        return {"error": str(e)}
