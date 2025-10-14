import os
from typing import Any, Dict, List
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain_core.prompt_values import PromptValue  # Added this to ensure type safety

# --- Groq-Specific Imports ---
from groq import Groq
# ------------------------------

def _call_groq_api(prompt_value: PromptValue, model_name: str, max_new_tokens: int, temperature: float) -> str:
    """
    Internal function to call the Groq API for content generation.
    It takes the PromptValue object and converts it to the final string expected by the API.
    """
    try:
        # 1. Initialize client inside the function to guarantee API key is available
        groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

        if groq_client.api_key is None:
            return "Error: Groq API Key is not set in the environment variables."

        # 2. Convert the LangChain PromptValue object into the final string
        final_prompt_string = prompt_value.to_string() 

        # 3. Call the chat completion endpoint
        response = groq_client.chat.completions.create(
            model=model_name,
            # Groq chat API expects a list of message objects
            messages=[
                {"role": "user", "content": final_prompt_string}
            ],
            temperature=temperature,
            max_tokens=max_new_tokens,
            stream=False 
        )
        
        # 4. Extract the text content
        return response.choices[0].message.content
    
    except Exception as e:
        print(f"Groq API Call Error: {e}")
        # Added a check for common Groq API errors (like 401/404)
        if "400" in str(e) or "401" in str(e):
             return f"Error during Groq API call: API Key or model error detected."
        return f"Error during Groq API call: {str(e)}"


def make_llm(model_name="llama3-8b-8192", max_new_tokens=256, temperature=0.0):
    """
    Wraps the Groq API call within a RunnableLambda to function as the LLM in the LCEL chain.
    """
    
    # We define the LLM wrapper as a RunnableLambda that takes a PromptValue and calls the API
    return RunnableLambda(
        lambda prompt_value: _call_groq_api(prompt_value, model_name, max_new_tokens, temperature)
    )

# ----------------------------------------------------------------------
# RAG Chain Definition (LCEL structure) - This part remains the same
# ----------------------------------------------------------------------

GROUND_PROMPT = """You are an assistant that answers questions using ONLY the provided context.
If the answer is not in the context, say "I don't know" and do not hallucinate.
Cite sources inline as [SOURCE_URL].

Context:
{context}

Question:
{input}

Answer concisely and include source citations.
"""

def build_qa_chain(llm, retriever):
    # The PromptTemplate expects the 'input' and 'context' variables from the chain.
    prompt = PromptTemplate(
        template=GROUND_PROMPT,
        input_variables=["context", "input"] 
    )
    
    document_chain = create_stuff_documents_chain(llm, prompt)
    retrieval_chain = create_retrieval_chain(retriever, document_chain)
    
    return retrieval_chain
