# indexing/vectorstore.py
import os
from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document
import faiss
import pickle

INDEX_DIR = "data/index"

class FaissVectorStore:
    def __init__(self, embeddings):
        self.embeddings = embeddings
        os.makedirs(INDEX_DIR, exist_ok=True)
        self.index_path = os.path.join(INDEX_DIR, "faiss_index")
        self.index = None
        self.docstore = None

    def index_documents(self, docs: list):
        """
        docs: list of dicts { page_content, metadata }
        """
        # convert to LangChain Document
        lc_docs = [Document(page_content=d["page_content"], metadata=d["metadata"]) for d in docs]
        vs = FAISS.from_documents(lc_docs, self.embeddings)
        # save to disk
        vs.save_local(self.index_path)
        self.index = vs
        return {"vector_count": len(lc_docs), "errors": []}

    def load(self):
        if os.path.exists(self.index_path):
            self.index = FAISS.load_local(self.index_path, self.embeddings)
            return True
        return False

    def retrieve(self, query, k=3):
        if self.index is None:
            raise ValueError("Index not loaded")
        docs = self.index.similarity_search(query, k=k)
        # each doc is langchain Document with .page_content and .metadata
        return docs
