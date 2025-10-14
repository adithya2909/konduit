import streamlit as st
import requests
import time


# App Configuration

st.set_page_config(page_title="RAG Assistant", layout="wide")


st.markdown("""
<style>
body {
    background: linear-gradient(135deg, #C6FFDD, #FBD786, #f7797d);
    color: #222222;
    font-family: 'Poppins', sans-serif;
}
h1, h2, h3 {
    color: #2b2b2b !important;
    font-weight: 600;
}
div.block-container {
    padding-top: 1rem;
    padding-bottom: 2rem;
    background-color: rgba(255, 255, 255, 0.8);
    border-radius: 12px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.15);
    padding: 2rem;
}
div.stButton>button {
    background: linear-gradient(90deg, #6EE7B7, #3B82F6);
    color: white;
    font-size: 1rem;
    font-weight: 500;
    border: none;
    border-radius: 10px;
    padding: 0.6rem 1.2rem;
    transition: all 0.3s ease;
}
div.stButton>button:hover {
    background: linear-gradient(90deg, #60A5FA, #A78BFA);
    transform: scale(1.05);
}
textarea, input[type=text], input[type=number] {
    background-color: #ffffffcc !important;
    border-radius: 8px !important;
    border: 1px solid #ccc !important;
    color: #111111 !important;
}
hr {
    border: none;
    height: 1px;
    background: #ddd;
    margin: 2rem 0;
}
</style>
""", unsafe_allow_html=True)


# Backend URL

API_URL = "http://localhost:8000"


# App Title

st.markdown("<h1 style='text-align:center;'>🧭 RAG Knowledge Explorer</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#444;'>Discover, structure, and interact with web knowledge seamlessly.</p>", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)


# Section 1: Crawl Website

st.markdown("### 🌍 Step 1: Discover a Website")
st.markdown("Provide a URL and let the explorer gather its contents.")

crawl_url = st.text_input("🔗 Website to Explore:", value="https://docs.streamlit.io/")
col1, col2, col3 = st.columns(3)
with col1:
    max_pages = st.number_input("📚 Number of Pages:", min_value=1, value=10)
with col2:
    max_depth = st.number_input("🧩 Link Depth:", min_value=0, value=2)
with col3:
    crawl_delay_ms = st.number_input("⏱ Delay per Page (ms):", min_value=0, value=250, step=50)

if st.button("🌐 Begin Exploration", use_container_width=True):
    if not crawl_url:
        st.error("Please enter a valid URL.")
    else:
        with st.spinner("Collecting pages... please wait."):
            try:
                payload = {
                    "start_url": crawl_url,
                    "max_pages": int(max_pages),
                    "max_depth": int(max_depth),
                    "crawl_delay_ms": int(crawl_delay_ms)
                }
                response = requests.post(f"{API_URL}/crawl", json=payload)
                response.raise_for_status()
                st.success("✨ Exploration completed successfully!")
                st.json(response.json())
            except requests.exceptions.RequestException as e:
                st.error(f"Error during crawl: {e}")
            except Exception as e:
                st.error(f"Unexpected error: {e}")

st.markdown("<hr>", unsafe_allow_html=True)


# Section 2: Index Documents

st.markdown("### 🧮 Step 2: Structure & Index")
st.markdown("Organize the collected content into searchable chunks.")

if st.button("📂 Generate Index", key="index_button", use_container_width=True):
    with st.spinner("Structuring content..."):
        try:
            payload = {
                "chunk_size": 256,
                "chunk_overlap": 50,
                "embedding_model": "sentence-transformers/all-MiniLM-L6-v2"
            }
            response = requests.post(f"{API_URL}/index", json=payload)
            response.raise_for_status()
            st.success("🗂️ Index generated successfully!")
            st.json(response.json())
        except requests.exceptions.RequestException as e:
            st.error(f"Error during indexing: {e}")
        except Exception as e:
            st.error(f"Unexpected error: {e}")

st.markdown("<hr>", unsafe_allow_html=True)


# Section 3: Ask a Question

st.markdown("### 💡 Step 3: Query the Knowledge Base")
st.markdown("Ask a question and retrieve insights from the indexed content.")

question = st.text_area("💬 Ask your Question here:")
if st.button("🔎 Retrieve Insight", use_container_width=True):
    if not question:
        st.warning("Please enter a question.")
    else:
        with st.spinner("Analyzing your query..."):
            try:
                response = requests.post(f"{API_URL}/ask", json={"question": question})
                response.raise_for_status()
                result = response.json()

                st.subheader("🎯 Insight")
                st.info(result.get("answer", "No answer found."))

                if "sources" in result:
                    st.subheader("📖 References")
                    for source in result["sources"]:
                        st.markdown(f"- **[{source['url']}]({source['url']})**")
                        st.caption(f"Excerpt: {source['snippet']}...")

                st.subheader("⏱️ Processing Details")
                st.json(result.get("timings", {}))

            except requests.exceptions.RequestException as e:
                st.error(f"Error fetching answer: {e}")
            except Exception as e:
                st.error(f"Unexpected error: {e}")

st.markdown("<hr>", unsafe_allow_html=True)
st.caption("🌸 © 2025 RAG Assistant • Designed with Streamlit & Care")
