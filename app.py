import streamlit as st
from generator import generate_answer

# ---- Page config ----
st.set_page_config(
    page_title="PDF Assistant (RAG)",
    page_icon="📚",
    layout="centered"
)

# ---- Custom CSS Injection ----
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&display=swap');

    /* Global Font & Reset */
    html, body, [class*="css"] {
        font-family: 'Space Grotesk', sans-serif !important;
    }

    /* Hide only the Streamlit Deploy button, keep header for sidebar toggle */
    .stDeployButton {
        display: none !important;
    }
    header[data-testid="stHeader"] {
        background: transparent !important;
    }
    footer {display: none !important;}

    /* Main Background */
    .stApp {
        background: #09090b !important; /* Very dark zinc */
        background-image: 
            radial-gradient(circle at 15% 50%, rgba(99, 102, 241, 0.08), transparent 25%),
            radial-gradient(circle at 85% 30%, rgba(168, 85, 247, 0.08), transparent 25%) !important;
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #121214 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
    }
    
    /* Apply Courier New only to text elements, not to Streamlit's internal UI icons */
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"],
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] label, [data-testid="stSidebar"] div[data-baseweb="checkbox"] {
        font-family: 'Courier New', Courier, monospace !important;
    }
    
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
        color: #a1a1aa;
    }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        margin-bottom: 0.2rem;
        font-size: 0.9rem;
    }
    [data-testid="stSidebar"] hr {
        margin: 0.5em 0;
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: #e4e4e7 !important;
        font-weight: 600 !important;
        margin-top: 0.2rem !important;
        margin-bottom: 0.2rem !important;
    }

    /* Gradient Title */
    h1 {
        background: linear-gradient(to right, #818cf8, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700 !important;
        letter-spacing: -0.5px;
        margin-bottom: 0.5rem !important;
    }

    /* Chat Input Flat & Compact */
    .block-container, [data-testid="stAppViewBlockContainer"] {
        padding-bottom: 2rem !important; /* Reduces main scroll area padding */
    }
    [data-testid="stBottomBlockContainer"] {
        padding-bottom: 10px !important; /* Kills the space under the chat input */
    }
    .stChatInputContainer {
        padding-bottom: 0px !important;
        background: transparent !important;
    }
    .stChatInputContainer > div {
        background-color: rgba(39, 39, 42, 0.6) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 8px !important; /* Flatter corners */
        box-shadow: none !important; /* Flat design */
        backdrop-filter: blur(12px) !important;
        transition: all 0.2s ease;
        min-height: 24px !important;
    }
    .stChatInputContainer > div:focus-within {
        border-color: rgba(129, 140, 248, 0.5) !important;
        background-color: rgba(39, 39, 42, 0.9) !important;
    }
    .stChatInputContainer textarea {
        padding-top: 12px !important;
        padding-bottom: 2px !important;
        min-height: 24px !important;
    }

    /* Chat Messages */
    [data-testid="stChatMessage"] {
        background-color: transparent !important;
        border: none !important;
        padding: 0 !important;
        margin-bottom: 24px !important;
        display: flex;
    }
    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] {
        background-color: #18181b;
        border: 1px solid rgba(255, 255, 255, 0.05);
        padding: 16px 20px;
        border-radius: 16px;
        color: #e4e4e7;
        line-height: 1.6;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        display: inline-block;
        width: fit-content;
    }
    
    /* Bot message specific styling */
    [data-testid="stChatMessage"]:not(:has([data-testid="chatAvatarIcon-user"])) {
        padding-right: 15% !important; 
    }

    /* User message specific styling - FLIP EVERYTHING TO THE RIGHT */
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
        flex-direction: row-reverse !important;
        padding-left: 15% !important;
    }
    
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) [data-testid="stMarkdownContainer"] {
        background-color: rgba(99, 102, 241, 0.1) !important;
        border-color: rgba(99, 102, 241, 0.2) !important;
        text-align: right;
        margin-right: 1rem; 
    }

    /* Expanders */
    .streamlit-expanderHeader {
        background-color: #18181b !important;
        border: 1px solid rgba(255,255,255,0.05) !important;
        border-radius: 12px !important;
        color: #e4e4e7 !important;
        font-weight: 500 !important;
        font-size: 0.9rem !important;
    }
    [data-testid="stExpander"] {
        border: none !important;
        box-shadow: none !important;
    }
    /* Reset the chat bubble styling for markdown blocks INSIDE the expander */
    [data-testid="stExpander"] [data-testid="stMarkdownContainer"] {
        background-color: transparent !important;
        border: none !important;
        padding: 0 !important;
        box-shadow: none !important;
        width: 100% !important;
        display: block !important;
    }
    [data-testid="stExpander"] [data-testid="stMarkdownContainer"] p {
        font-size: 0.8rem !important;
        color: #a1a1aa !important;
        line-height: 1.4 !important;
    }

    /* File Uploader Box */
    [data-testid="stFileUploader"] {
        background-color: #18181b;
        border: 1px dashed rgba(255, 255, 255, 0.2);
        border-radius: 12px;
        padding: 16px;
    }

    /* Button Styling */
    .stButton > button {
        background-color: #4f46e5 !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        padding: 10px 24px !important;
        transition: all 0.2s !important;
    }
    .stButton > button:hover {
        background-color: #6366f1 !important;
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4) !important;
        transform: translateY(-1px);
    }

</style>
""", unsafe_allow_html=True)

# ---- Sidebar ----
with st.sidebar:
    st.header("About")
    st.write(
        "A RAG app built using LangChain, ChromaDB, and Gemini API. "
        "It answers questions using **only** the PDFs you provide."
    )
    st.markdown(
        "<div style='margin-top: 0.5rem;'><span style='color: #a1a1aa;'>Built by </span><a href='https://amankumargupta.vercel.app' target='_blank' style='color: #14b8a6; text-decoration: none; font-weight: 600;'>Aman Kumar Gupta</a></div>", 
        unsafe_allow_html=True
    )
    st.markdown("---")
    st.write("**Tech stack:** LangChain, ChromaDB, Gemini, Streamlit")
    st.markdown("---")
    st.subheader("Retrieval settings")

    k = st.slider("Number of context chunks to retrieve (k)", min_value=1, max_value=8, value=4)

    use_threshold = st.checkbox(
        "Require relevant context",
        value=True,
        help="If even the best-matching chunk is too dissimilar to your question, "
             "skip the LLM call and say the answer isn't in the document. "
             "(Only applies in Smart Match mode — see the search mode selector "
             "above the question box.)"
    )
    threshold_value = None
    if use_threshold:
        threshold_value = st.slider(
            "Max distance for best match",
            min_value=0.5, max_value=1.5, value=0.8, step=0.05,
            help="Lower = stricter. Chunks are scored by vector distance "
                 "(lower = more similar). On this corpus, relevant questions "
                 "score ~0.45-0.65 and unrelated ones ~0.9+, so 0.8 splits "
                 "them cleanly; run `python retriever.py` to re-check."
        )
    st.markdown("---")

    if st.button("Clear conversation"):
        st.session_state.messages = []
        st.rerun()

# ---- Main UI ----
st.title("📚 PDF Assistant")
st.write(
    "Upload your PDFs and ask any questions about their contents."
    "Follow-up questions are understood in context."
)

# ---- Add a new PDF — collapsible, in main UI ----
with st.expander("📄 Add a new PDF to the knowledge base"):
    uploaded_file = st.file_uploader("Upload a PDF", type="pdf", label_visibility="collapsed")

    if uploaded_file is not None:
        if st.button("Process and embed this PDF"):
            with st.spinner("Saving and embedding PDF... this may take a minute."):
                temp_path = f"uploaded_{uploaded_file.name}"
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                from loader import load_and_chunk_pdf
                from embedder import load_existing_vector_store

                new_chunks = load_and_chunk_pdf(temp_path)

                if not new_chunks:
                    st.error(
                        "Couldn't extract any text from this PDF — it might be a "
                        "scanned/image-only document without a text layer, or empty. "
                        "Try a different PDF with selectable text."
                    )
                else:
                    vector_store = load_existing_vector_store()
                    vector_store.add_documents(new_chunks)
                    st.success(f"'{uploaded_file.name}' embedded and added to the knowledge base!")

# ---- Retrieval mode selector — placed prominently near the chat input ----
st.markdown("---")
col1, col2 = st.columns(2)
with col1:
    st.markdown("**🔎 Smart Match**")
    st.caption("Finds chunks with *similar meaning*. Best for natural questions.")
    st.caption("*e.g. \"How do I connect with alumni on AlumioDTU?\"*")
with col2:
    st.markdown("**🔎 Smart + Exact Match**")
    st.caption("Also matches *exact keywords* — better for code terms, acronyms.")
    st.caption("*e.g. \"What is the AlumioDTU portal URL?\"*")

retrieval_mode = st.radio(
    "Choose search mode:",
    options=["Smart Match", "Smart + Exact Match"],
    index=0,
    horizontal=True,
    label_visibility="collapsed"
)
use_hybrid = (retrieval_mode == "Smart + Exact Match")

if use_hybrid and use_threshold:
    st.caption("ℹ️ The relevance threshold (sidebar) doesn't apply in this mode.")

st.markdown("---")

if "messages" not in st.session_state:
    st.session_state.messages = []


def render_sources(sources):
    with st.expander("View source chunks used"):
        for i, (source_file, page, score, text) in enumerate(sources):
            score_display = f" (distance: {score:.4f})" if score else ""
            st.markdown(f"**Source {i+1} — {source_file}, page {page}**{score_display}")
            st.write(text)
            st.markdown("---")


def render_user_message(content):
    st.markdown(f"""
    <div style="display: flex; justify-content: flex-end; margin-bottom: 24px; align-items: flex-start;">
        <div style="background-color: rgba(99, 102, 241, 0.15); border: 1px solid rgba(99, 102, 241, 0.3); padding: 12px 18px; border-radius: 16px; color: #e4e4e7; max-width: 75%; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); text-align: right; margin-right: 12px;">
            {content}
        </div>
        <div style="width: 32px; height: 32px; background-color: #ef4444; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 18px;">
            🧑
        </div>
    </div>
    """, unsafe_allow_html=True)

for message in st.session_state.messages:
    if message["role"] == "user":
        render_user_message(message["content"])
    else:
        with st.chat_message(message["role"]):
            st.write(message["content"])
            if message.get("sources"):
                render_sources(message["sources"])

question = st.chat_input("e.g. How do I register for an AlumioDTU account?")

if question and question.strip():
    render_user_message(question)

    history = []
    messages = st.session_state.messages
    for i in range(len(messages) - 1):
        if messages[i]["role"] == "user" and messages[i + 1]["role"] == "assistant":
            history.append((messages[i]["content"], messages[i + 1]["content"]))

    with st.chat_message("assistant"):
        with st.spinner("Retrieving relevant context and generating answer..."):
            try:
                result = generate_answer(
                    question, k=k, history=history,
                    max_distance=None if use_hybrid else threshold_value,
                    use_hybrid=use_hybrid
                )

                if result["gated"]:
                    st.info(
                        "No sufficiently relevant content was found in the document, "
                        "so the model was not called. Try rephrasing your question, "
                        "or loosen the distance threshold in the sidebar."
                    )
                else:
                    st.write(result["answer"])

                if result["standalone_question"] != question:
                    st.caption(f"Interpreted as: *{result['standalone_question']}*")

                sources = [
                    (
                        doc.metadata.get("source", "unknown").split("/")[-1],
                        doc.metadata.get("page_label", "unknown"),
                        score,
                        doc.page_content
                    )
                    for doc, score in zip(result["sources"], result["scores"])
                ]
                if sources:
                    render_sources(sources)

                st.session_state.messages.append({"role": "user", "content": question})
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": result["answer"],
                    "sources": sources
                })

            except Exception as e:
                st.error(f"Something went wrong: {e}")