from transformers import pipeline
from langchain_community.llms import HuggingFacePipeline

# free local text generation model
pipe = pipeline(
    "text-generation",
    model="TinyLlama/TinyLlama-1.1B-Chat-v1.0",
    max_new_tokens=250,
    do_sample=False
)

llm = HuggingFacePipeline(pipeline=pipe)

STORY_PROMPT = """
You are a senior software engineer.

Create a development timeline and explain why changes happened.
"""

def create_story(vectordb):

    retriever = vectordb.as_retriever(
    search_type="mmr",   # ⭐ avoids duplicates
    search_kwargs={"k":6, "fetch_k":20}
)

    docs = retriever.invoke(STORY_PROMPT)

    # remove duplicate commit texts
    unique = list(dict.fromkeys([d.page_content for d in docs]))
    context = " ".join(unique)

    response = llm.invoke(f"""
Act like a senior engineer reviewing commits.

Write ONLY 3–4 short bullet points:
Phase → Change → Reason.

If commits are similar, group them together.

Git history:
{context}
""")

    return response