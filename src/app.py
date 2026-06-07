import os
from pathlib import Path
import chromadb
from groq import Groq
import gradio as gr
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

REPO_ROOT = Path(__file__).resolve().parent.parent

# Load environment variables from .env (if present)
try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=REPO_ROOT / ".env")
except Exception:
    # If python-dotenv is not installed, environment variables must be set externally.
    pass

# 1. Initialize Clients & Environment Variables
# Gradio automatically loads the .env file, but we'll fetch the key safely
GROQ_KEY = os.environ.get("GROQ_API_KEY")
if not GROQ_KEY:
    raise ValueError("⚠️ Error: GROQ_API_KEY not found in environment variables or .env file.")

groq_client = Groq(api_key=GROQ_KEY)

# Connect to your existing local ChromaDB database from Milestone 4
DB_PATH = REPO_ROOT / "chroma_db"
chroma_client = chromadb.PersistentClient(path=str(DB_PATH))
embedding_function = SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
collection = chroma_client.get_collection(
    name="consumer_rights_protection", 
    embedding_function=embedding_function
)

# 2. Define the End-to-End RAG Pipeline Function
def ask_consumer_agent(user_query):
    """
    Retrieves relevant chunks from ChromaDB, formats a grounded prompt for Groq,
    and returns a programmatic response with strict citations.
    """
    if not user_query.strip():
        return "Please enter a valid question.", ""

    # A. Retrieve top-k relevant text chunks from local vector store
    k = 4
    retrieval_results = collection.query(
        query_texts=[user_query],
        n_results=k
    )

    # B. Extract text content and metadata
    retrieved_documents = retrieval_results['documents'][0]
    retrieved_metadatas = retrieval_results['metadatas'][0]
    
    if not retrieved_documents:
        return "I do not have enough information to answer that question based on the provided documents.", "None"

    # C. Format the Context and Programmatic Citations
    context_blocks = []
    source_links = []
    
    for doc_text, meta in zip(retrieved_documents, retrieved_metadatas):
        source_text = meta.get('source', 'Unknown source')
        source_url = meta.get('url', '')
        source_links.append((source_text, source_url))
        
        source_citation = f"Source: {source_text} (URL: {source_url})"
        context_blocks.append(f"[{source_citation}]\nText: {doc_text}\n")
    
    formatted_context = "\n---\n".join(context_blocks)
    # Deduplicate sources (the top-k chunks often come from the same document)
    # while preserving retrieval order, then render the full https link.
    seen = set()
    unique_sources = []
    for source_text, source_url in source_links:
        key = (source_text, source_url)
        if key in seen:
            continue
        seen.add(key)
        unique_sources.append((source_text, source_url))

    sources_output = "\n".join(
        f"- **{source_text}** — [{source_url}]({source_url})" if source_url else f"- {source_text}"
        for source_text, source_url in unique_sources
    )

    # D. Construct the Guardrailed System Prompt
    system_prompt = (
        "You are a strict QA assistant for a Consumer Rights Guide.\n"
        "Your task is to answer the user's question using ONLY the facts explicitly provided in the Context block below.\n"
        "CRITICAL RULES:\n"
        "1. Do NOT use your own pre-training general knowledge to answer.\n"
        "2. Every statement you make MUST be traceably grounded in the provided Context.\n"
        "3. You must explicitly mention which document or source rule you got your answer from inside your prose response.\n"
        "4. If the provided Context does not contain enough information to explicitly answer the question, or if the question is completely out of scope, you MUST reply exactly with:\n"
        "'I do not have enough information to answer that question based on the provided documents.' Do not make up a plausible response."
    )

    user_prompt = f"Context:\n{formatted_context}\n\nQuestion: {user_query}\n\nAnswer:"

    # E. Call Groq API (Llama 3.3 70B Versatile)
    try:
        completion = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.0  # Kept at 0 for strict deterministic accuracy
        )
        llm_response = completion.choices[0].message.content
    except Exception as e:
        llm_response = f"⚠️ Groq API Error occurred: {str(e)}"

    return llm_response, sources_output

# 3. Build the Gradio Web Interface Layout
with gr.Blocks(
    theme=gr.themes.Soft(
        primary_hue="purple",
        secondary_hue="blue"
    ),
    title="Universal Consumer Rights & Wealth Protection Agent"
) as demo:
    gr.Markdown("# 🏛️ Universal Consumer Rights & Wealth Protection Agent")
    gr.Markdown(
        "### A grounded Retrieval-Augmented Generation assistant for consumer rights questions. "
        "Ask anything about credit cards, tenant protections, airline refunds, or medical billing law."
    )
    gr.Markdown(
        "*Public sharing is enabled. The shared Gradio URL will appear in the terminal when the app starts.*"
    )

    with gr.Row():
        with gr.Column(scale=2):
            user_input = gr.Textbox(
                label="Your question",
                placeholder="e.g. What is my maximum liability if my credit card is stolen online?",
                lines=2
            )
            ask_button = gr.Button("Ask", variant="primary")

            gr.Markdown("**Try one of these — click to fill in the box, or type your own above:**")
            gr.Examples(
                examples=[
                    "What is my maximum liability if my credit card is stolen online?",
                    "Am I eligible for student loan forgiveness?",
                    "What are common bank overdraft fee loopholes I should know about?",
                    "How am I protected against credit card fraud?",
                    "Can I get a refund if my airline cancels my flight?",
                    "What are my rights as a tenant if my landlord won't return my deposit?",
                ],
                inputs=user_input,
                label="Example questions",
            )

        with gr.Column(scale=3):
            answer_output = gr.Textbox(
                label="Answer",
                lines=8,
                interactive=False
            )
            sources_box = gr.Markdown(
                "### Retrieved from\n- None yet.",
                elem_id="sources-box"
            )

    ask_button.click(
        fn=ask_consumer_agent,
        inputs=user_input,
        outputs=[answer_output, sources_box]
    )
    user_input.submit(
        fn=ask_consumer_agent,
        inputs=user_input,
        outputs=[answer_output, sources_box]
    )

# 4. Launch Application Local Server Instance
if __name__ == "__main__":
    print("Launching Gradio app in public share mode...")
    # Capture returned values from launch(): (app, local_url, share_url)
    app_obj, local_url, share_url = demo.launch(share=True, debug=True)
    print("Gradio local URL:", local_url)
    if share_url:
        print("Gradio public share URL:", share_url)
    else:
        print("No public share URL was created. If you expected one, ensure your network allows tunneling and that `share=True` is supported in this environment.")