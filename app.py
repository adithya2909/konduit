import streamlit as st
import requests
import time

# Define the base URL for your FastAPI backend
API_URL = "http://localhost:8000"

st.set_page_config(page_title="RAG-Web UI", layout="wide")
st.title("RAG-Web Application")

st.markdown("""
This app provides a simple UI to interact with your RAG system.
You can crawl a website, index the documents, and then ask questions about the content.
""")
st.divider()

# Section 1: Crawl a Website
st.header("1. Crawl a Website 🕸️")
with st.container():
    st.markdown("Enter a starting URL to begin the crawling process.")
    
    crawl_url = st.text_input("Start URL:", value="https://docs.streamlit.io/")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        max_pages = st.number_input("Max Pages:", min_value=1, value=10, step=1)
    with col2:
        max_depth = st.number_input("Max Depth:", min_value=0, value=2, step=1)
    with col3:
        crawl_delay_ms = st.number_input("Crawl Delay (ms):", min_value=0, value=250, step=50)

    if st.button("Start Crawl", use_container_width=True):
        if not crawl_url:
            st.error("Please enter a valid URL.")
        else:
            with st.spinner("Crawling in progress... This may take a while."):
                try:
                    crawl_data = {
                        "start_url": crawl_url,
                        "max_pages": int(max_pages),
                        "max_depth": int(max_depth),
                        "crawl_delay_ms": int(crawl_delay_ms)
                    }
                    response = requests.post(f"{API_URL}/crawl", json=crawl_data)
                    response.raise_for_status()
                    st.success("Crawling completed successfully! ✅")
                    st.json(response.json())
                except requests.exceptions.RequestException as e:
                    st.error(f"Error during crawl: {e}")
                except Exception as e:
                    st.error(f"An unexpected error occurred: {e}")

st.divider()

# Section 2: Index the Documents
st.header("2. Index Documents 📊")
st.markdown("Once the crawl is complete, click this button to index the crawled documents.")
#index_button_key = "index_button_" + str(time.time())
if st.button("Index Documents", key="index_button", use_container_width=True):
    with st.spinner("Indexing documents..."):
        try:
            payload = {
                "chunk_size": 256,
                "chunk_overlap": 50,
                "embedding_model": "sentence-transformers/all-MiniLM-L6-v2"
            }
            response = requests.post(f"{API_URL}/index", json=payload)
            response.raise_for_status()
            st.success("Documents indexed successfully! Ready to ask questions. 🎉")
            st.json(response.json())
        except requests.exceptions.RequestException as e:
            st.error(f"Error during indexing: {e}")
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")

st.divider()

# Section 3: Ask a Question
st.header("3. Ask a Question 💬")
st.markdown("Type a question and get an answer based on the indexed content.")

question = st.text_area("Your Question:")

if st.button("Get Answer", use_container_width=True):
    if not question:
        st.warning("Please enter a question.")
    else:
        with st.spinner("Thinking..."):
            try:
                ask_data = {"question": question}
                response = requests.post(f"{API_URL}/ask", json=ask_data)
                response.raise_for_status()
                result = response.json()
                
                st.subheader("Answer")
                st.info(result.get("answer", "No answer found."))
                
                if "sources" in result:
                    st.subheader("Sources")
                    for source in result["sources"]:
                        st.markdown(f"**URL:** [{source['url']}]({source['url']})")
                        st.caption(f"**Snippet:** {source['snippet']}...")
                        
                st.subheader("Timings")
                st.json(result["timings"])

            except requests.exceptions.RequestException as e:
                st.error(f"Error getting an answer: {e}")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")

st.divider()
