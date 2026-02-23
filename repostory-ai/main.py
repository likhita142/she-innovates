from github_fetcher import fetch_commits
from vector_store import build_vectorstore

data = fetch_commits("facebook/react")

vectordb = build_vectorstore(data)

print("Vector DB Built ✅")