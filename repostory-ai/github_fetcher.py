from github import Github
import os
from dotenv import load_dotenv

load_dotenv()

token = os.getenv("GITHUB_TOKEN")
g = Github(token)

def fetch_commits(repo_name):

    repo = g.get_repo(repo_name)
    commits = repo.get_commits()

    data = []

    for commit in commits[:50]:   # limit for speed
        msg = commit.commit.message
        author = commit.commit.author.name
        date = str(commit.commit.author.date)

        text = f"""
Commit Message: {msg}
Author: {author}
Date: {date}
"""
        data.append(text)

    return data