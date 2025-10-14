# 🧠 RAG Web – Website Crawler + Retrieval-Augmented Generation Pipeline

A modular **Retrieval-Augmented Generation (RAG)** system that crawls websites, extracts and indexes their textual content, embeds it into a vector store, retrieves the most relevant chunks, and generates **grounded, source-cited answers** using an LLM.

---

## ⚙️ Setup

1. **Clone and enter the project**
   git clone https://github.com/jaipratham/Website-Crawler.git
   cd Website-Crawler
   
2.Create and activate a virtual environment
  python -m venv venv
  source venv/bin/activate        # On Windows: venv\Scripts\activate

3.Install dependencies
  pip install -r requirements.txt

4.Configure settings
  Edit config/settings.yaml to set crawl depth, embedding model, chunk size, vector store type, etc.

# 🕸️ Website-Crawler RAG Pipeline

This project implements a comprehensive Retrieval-Augmented Generation (RAG) pipeline that uses a website crawler to build its knowledge base.

## 🚀 Architecture Overview
```

Website-Crawler/
├── main.py                 # Entry point for the RAG pipeline
│
├── config/
│   └── settings.yaml       # Configuration (crawl depth, model, embedding type, etc.)
│
├── crawler/
│   ├── crawler.py          # Crawls website (respects robots.txt, domain limits)
│   └── parser.py           # Cleans & extracts text from HTML pages
│
├── indexing/
│   ├── chunker.py          # Splits text into chunks
│   ├── embedder.py         # Embeds chunks via OpenAI / SentenceTransformers
│   └── vectorstore.py      # Stores and retrieves embeddings (FAISS / Chroma)
│
├── retrieval/
│   └── retriever.py        # Retrieves top-k relevant chunks
│
├── generation/
│   └── generator.py        # Generates grounded answers using retrieved context
│
├── evaluation/
│   └── evaluate.py         # Computes recall@k, grounding correctness, etc.
│
├── utils/
│   └── logger.py           # Logging, timing, and error handling utilities
│
└── data/
    ├── raw_html/           # Cached raw HTML pages
    ├── cleaned_text/       # Cleaned text extracted from pages
    └── index/              # Stored embeddings / vector DB '''

```

📊 Config (config/settings.yaml)
```
crawl:
  max_depth: 2
  delay: 500
  max_pages: 20

embedding:
  model: sentence-transformers/all-MiniLM-L6-v2 # opens source model from Huggingface for embeddings.
  chunk_size: 256
  overlap: 50

vectorstore:
  backend: faiss
  dimension: 384

generation:
  model: llama-3.1-8b-instant
  max_tokens: 500
  temperature: 0.0
  ```

⚖️ Design Trade-offs:

✅ Modular architecture – Each stage (crawl → index → retrieve → generate) is isolated and reusable.

✅ Config-driven – Change depth, embedding model, and vector DB via YAML.

✅ Embeddings backend – Supports FAISS or Chroma seamlessly.

✅ LLM flexibility – Works with OpenAI, HuggingFace, or local models.

✅ Respects robots.txt – Ethical crawling with domain limits and delay.

✅ Logging included – Detailed logs and runtime metrics in utils/logger.py.

✅ Lightweight dependencies – Pure Python, no JS rendering or heavy frameworks.

⚠️ No dynamic JS rendering – Won’t extract content from SPA-heavy pages.

⚠️ Basic evaluation metrics – Extend for F1, ROUGE, BLEU, etc.

⚠️ Local storage – Data and vector DB stored in /data/, migrate for scale.

✅ Easy to extend – Add retrieval strategies or chain-of-thought generators.

✅ Compatible with LangChain / LlamaIndex – Plug-and-play design.

✅ Portable – Works locally or via Docker.

✅ End-to-end reproducible – Crawl, embed, retrieve, and generate in one run.

🧑‍💻 Author

Developed by Jaipratham
For learning, research, and practical experimentation with RAG systems.
