import requests
import os
from dotenv import load_dotenv
load_dotenv()

TOKEN = os.getenv("GITHUB_TOKEN")

def get_commits(owner, repo, max_pages=10):
    """
    Fetch commits from GitHub API.
    max_pages: Limit to prevent fetching too many commits (default 10 pages = 1000 commits)
    """
    all_commits = []
    page = 1
    print(f"🔍 Fetching commits from {owner}/{repo}...")
    
    while page <= max_pages:
        url = f"https://api.github.com/repos/{owner}/{repo}/commits?page={page}&per_page=100"
        headers = {
            "Authorization": f"Bearer {TOKEN}",
            "Accept": "application/vnd.github+json"
        }
        
        print(f"  📄 Fetching page {page}...")
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            print(f"  ⚠️ GitHub API returned status {response.status_code}")
            if response.status_code == 403:
                print(f"  ⚠️ Rate limit hit or auth issue")
            break
            
        data = response.json()
        if not isinstance(data, list) or len(data) == 0:
            print(f"  ✅ No more commits (fetched {len(all_commits)} total)")
            break
            
        all_commits.extend(data)
        print(f"  ✓ Page {page}: {len(data)} commits (total: {len(all_commits)})")
        page += 1
        
    print(f"✅ Finished fetching {len(all_commits)} commits from {owner}/{repo}")
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
