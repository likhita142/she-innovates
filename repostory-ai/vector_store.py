from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document


def build_vectorstore(commit_data):

    docs = []

    for text in commit_data:
        docs.append(Document(page_content=text))

    embedding = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    vectordb = Chroma.from_documents(
        docs,
        embedding=embedding,
        persist_directory="db"
    )

    return vectordb