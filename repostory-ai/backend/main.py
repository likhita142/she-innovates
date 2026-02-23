from github_fetcher import fetch_commits
from vector_store import build_vectorstore
from storyteller import create_story

# 1️⃣ Fetch commits
data = fetch_commits("facebook/react")

# 2️⃣ Build AI memory
vectordb = build_vectorstore(data)

# 3️⃣ Generate story
story = create_story(vectordb)

print("\n⭐ STORY MODE\n")
print(story)