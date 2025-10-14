from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

def chunk_documents(docs, chunk_size=256, chunk_overlap=50):
    """
    Splits document content into smaller chunks using a RecursiveCharacterTextSplitter
    to keep context coherent. The chunk size should now reliably be small enough
    to fit within the Groq API limits.

    docs: list of dicts { 'url', 'title', 'content' }
    returns list of LangChain Document objects (with page_content and metadata)
    """
    # Using RecursiveCharacterTextSplitter is robust for web content
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        # Default separators are usually best for web text: ["\n\n", "\n", " ", ""]
    )

    outputs = []
    for d in docs:
        # Create a single document object from the raw page content and metadata
        doc = Document(
            page_content=f"{d.get('title','')}\n{d.get('content','')}",
            metadata={
                "source": d["url"],
                "title": d.get("title","")
            }
        )
        
        # Split the document
        chunks = splitter.split_documents([doc])
        
        # Format the output into the expected list of dictionaries
        for i, c in enumerate(chunks):
            # Ensure metadata is copied and we add the chunk_index
            metadata = c.metadata.copy()
            metadata["chunk_index"] = i
            
            outputs.append({
                "page_content": c.page_content,
                "metadata": metadata
            })
            
    return outputs
