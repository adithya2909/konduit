# indexing/embedder.py
from langchain_community.embeddings import SentenceTransformerEmbeddings

def get_embedding_model(model_name="sentence-transformers/all-MiniLM-L6-v2"):
    """
    Returns a langchain Embeddings object backed by sentence-transformers.
    """
    return SentenceTransformerEmbeddings(model_name=model_name)
