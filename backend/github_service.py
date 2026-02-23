import requests
import os
from dotenv import load_dotenv
load_dotenv(".env")

TOKEN = os.getenv("GITHUB_TOKEN")

def get_commits(owner, repo):
    all_commits = []
    page = 1
    while True:
        url = f"https://api.github.com/repos/{owner}/{repo}/commits?page={page}&per_page=100"
        headers = {
            "Authorization": f"Bearer {TOKEN}",
            "Accept": "application/vnd.github+json"
        }
        response = requests.get(url, headers=headers)
        data = response.json()
        if not isinstance(data, list) or len(data) == 0:
            break
        all_commits.extend(data)
        page += 1
    return all_commits


def classify_commit(message):
    message = message.lower()
    if "fix" in message or "bug" in message:
        return "bug fix"
    elif "feat" in message or "add" in message:
        return "feature"
    elif "refactor" in message:
        return "refactor"
    elif "doc" in message:
        return "docs"
    else:
        return "other"


# ✅ NEW: Flatten raw GitHub commit into clean dict for MongoDB + AI
def flatten_commit(raw_commit: dict, owner: str, repo: str) -> dict:
    commit_data = raw_commit.get("commit", {})
    author = commit_data.get("author", {})
    files = raw_commit.get("files", [])  # only present in single-commit API calls

    message = commit_data.get("message", "")

    return {
        "owner": owner,                              # ✅ needed for /story query
        "repo": repo,                                # ✅ needed for /story query
        "sha": raw_commit.get("sha", "")[:7],
        "message": message.split("\n")[0][:200],     # first line only
        "author": author.get("name", "unknown"),
        "date": author.get("date", ""),
        "files": [f["filename"] for f in files[:5]] if files else [],
        "type": classify_commit(message),
    }
