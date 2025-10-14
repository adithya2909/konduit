# main.py
import yaml
import time
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
from dotenv import load_dotenv
load_dotenv()
from crawler.crawler import WebCrawler
from crawler.parser import HTMLParser
from indexing.chunker import chunk_documents
from indexing.embedder import get_embedding_model
from indexing.vectorstore import FaissVectorStore
#from retrieval.retriever import Retriever
from generation.generator import make_llm, build_qa_chain
from utils.logger import get_logger
from fastapi.middleware.cors import CORSMiddleware

logger = get_logger()

# Load config
with open("config/settings.yaml") as f:
    cfg = yaml.safe_load(f)

app = FastAPI(title="RAG-Web API (LangChain prototype)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost:8501"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory/global objects
_embeddings = None
_vector_store = None
_retriever = None
_parsed_docs = []  # list of parsed pages (dicts)
_crawled_pages = {}  # {url: html}

# Request models
class CrawlRequest(BaseModel):
    start_url: str
    max_pages: Optional[int] = cfg["crawl"]["max_pages"]
    max_depth: Optional[int] = cfg["crawl"]["max_depth"]
    crawl_delay_ms: Optional[int] = cfg["crawl"]["crawl_delay_ms"]

class IndexRequest(BaseModel):
    chunk_size: Optional[int] = cfg["index"]["chunk_size"]
    chunk_overlap: Optional[int] = cfg["index"]["chunk_overlap"]
    embedding_model: Optional[str] = cfg["index"]["embedding_model"]

class AskRequest(BaseModel):
    question: str
    top_k: Optional[int] = 3
    hf_model: Optional[str] = cfg["generation"]["hf_model"]

@app.post("/crawl")
def api_crawl(req: CrawlRequest):
    global _crawled_pages, _parsed_docs
    crawler = WebCrawler(
        start_url=req.start_url,
        max_depth=req.max_depth,
        max_pages=req.max_pages,
        delay=req.crawl_delay_ms / 1000.0
    )
    result = crawler.start()
    _crawled_pages = crawler.pages

    # parse immediately for easy indexing later
    parser = HTMLParser()
    _parsed_docs = parser.parse_multiple(_crawled_pages)
    logger.info(f"Crawled {len(_parsed_docs)} pages.")
    return result

@app.post("/index")
def api_index(req: IndexRequest):
    global _embeddings, _vector_store, _retriever
    try:
        if not _parsed_docs:
            return {"error": "No pages crawled. Call /crawl first."}

        # chunk
        logger.info(f"Received /index request with chunk_size")
                    


        docs = chunk_documents(
            _parsed_docs,
            chunk_size=req.chunk_size,
            chunk_overlap=req.chunk_overlap
        )

        # embeddings
        _embeddings = get_embedding_model(req.embedding_model)

        # vector store (FAISS)
        _vector_store = FaissVectorStore(_embeddings)
        _vector_store.index_documents(docs)

        # retriever wrapper
        _retriever = _vector_store.index.as_retriever()

        return {
            "status": "success",
            "message": "Documents indexed successfully.",
            "documents_indexed": len(docs),
            "chunk_size": req.chunk_size,
        }

    except Exception as e:
        logger.error(f"Indexing failed: {e}")
        return {"error": f"Indexing failed: {str(e)}"}


@app.post("/ask")
def api_ask(req: AskRequest):
    global _vector_store, _retriever
    if _retriever is None:
        return {"error": "Index not built. Call /index first."}

    # Build LLM (HuggingFace pipeline)
    llm = make_llm(
        model_name=req.hf_model,
        max_new_tokens=cfg["generation"]["max_new_tokens"],
        temperature=cfg["generation"]["temperature"]
    )

    # Use the new chain
    qa_chain = build_qa_chain(llm, _retriever)

    t0 = time.time()
    # Run the chain using the new invoke method with 'input' key
    out = qa_chain.invoke({"input": req.question})
    t1 = time.time()

    # The answer is now in the 'answer' key, and sources are in the 'context' key.
    answer = out.get("answer") or ""
    source_docs = out.get("context", [])

    sources = []
    for sd in source_docs:
        meta = sd.metadata
        snippet = sd.page_content[:300]
        sources.append({"url": meta.get("source"), "snippet": snippet})

    timings = {
        "retrieval_ms": "n/a (internal to chain)",
        "generation_ms": round((t1 - t0) * 1000, 2),
        "total_ms": round((t1 - t0) * 1000, 2)
    }

    return {"answer": answer, "sources": sources, "timings": timings}