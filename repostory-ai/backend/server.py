from fastapi import FastAPI
from pydantic import BaseModel

from github_fetcher import fetch_commits
from vector_store import build_vectorstore
from storyteller import create_story, create_tldr


app = FastAPI()


class RepoRequest(BaseModel):
    repo: str


@app.post("/generate")

def generate_story_api(data: RepoRequest):

    commits = fetch_commits(data.repo)

    vectordb = build_vectorstore(commits)

    story = create_story(vectordb)

    tldr = create_tldr(vectordb)

    return {

        "story": story,
        "tldr": tldr

    }