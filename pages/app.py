# pages/app.py
import streamlit as st
import requests
from gtts import gTTS
import os
import numpy as np
import faiss
import pandas as pd
from sentence_transformers import SentenceTransformer

# ===============================
# CONFIG & PATHS
# ===============================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.getenv("KHBAYER_DATASET", os.path.join(os.path.dirname(BASE_DIR), "dataset_with_category.csv"))
EMBEDDINGS_PATH = os.path.join(BASE_DIR, "article_embeddings.npy")
FAISS_PATH = os.path.join(BASE_DIR, "faiss_index.idx")

# ===============================
# 1. LOAD DATA (CSV + EMBEDDINGS + FAISS)
# ===============================
@st.cache_data
def load_data():
    try:
        df = pd.read_csv(DATASET_PATH, encoding="utf-8", sep=";", on_bad_lines="skip", engine="python")
        return df
    except Exception as e:
        st.error(f"Failed to load CSV: {e}")
        return pd.DataFrame()

@st.cache_resource
def load_embeddings():
    if os.path.exists(EMBEDDINGS_PATH):
        try:
            return np.load(EMBEDDINGS_PATH)
        except Exception as e:
            st.error(f"Failed to load embeddings: {e}")
            return None
    else:
        st.error(f"Embeddings not found: {EMBEDDINGS_PATH}")
        return None

@st.cache_resource
def load_faiss_index():
    if os.path.exists(FAISS_PATH):
        try:
            return faiss.read_index(FAISS_PATH)
        except Exception as e:
            st.error(f"Failed to load FAISS index: {e}")
            return None
    else:
        st.error(f"FAISS index not found: {FAISS_PATH}")
        return None

# Load everything
df = load_data()
documents = df['content'].tolist() if not df.empty else []
article_embeddings = load_embeddings()
index = load_faiss_index()

# ===============================
# 2. LOAD EMBEDDING MODEL
# ===============================
@st.cache_resource
def load_embedding_model():
    try:
        model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
        return model
    except Exception as e:
        st.error(f"Model load failed: {e}")
        return None

embed_model = load_embedding_model()

# ===============================
# 3. OLLAMA & UTILS
# ===============================
OLLAMA_URL = "http://127.0.0.1:11434/api/generate"

def ask_ollama(prompt: str, model_name: str = "llama3.2") -> str:
    if not prompt.strip():
        return "No input."
    try:
        payload = {"model": model_name, "prompt": prompt, "stream": False}
        r = requests.post(OLLAMA_URL, json=payload, timeout=60)
        if r.status_code == 200:
            return r.json().get("response", "No response.")
        return f"Error: {r.status_code}"
    except Exception as e:
        return f"Connection failed: {e}"

def summarize_llama(text: str) -> str:
    return ask_ollama(f"Summarize in 3 bullet points:\n\n{text}")

def translate(text: str, target: str = "fr") -> str:
    lang_name = "French" if target == "fr" else "Arabic"
    prompt = f"Translate the following text **exactly** to {lang_name}. Return ONLY the translation, no extra text:\n\n{text}"
    return ask_ollama(prompt)

def text_to_speech(text: str, lang: str = "en") -> str | None:
    try:
        tts = gTTS(text=text, lang=lang)
        path = "output.mp3"
        tts.save(path)
        return path
    except Exception as e:
        st.error(f"TTS failed: {e}")
        return None

# ===============================
# 4. RETRIEVAL (RAG)
# ===============================
def retrieve(query, top_k=5):
    if embed_model is None or article_embeddings is None or index is None:
        return []
    try:
        query_vec = embed_model.encode([query], convert_to_numpy=True)
        distances, indices = index.search(query_vec, top_k)
        return [documents[i] for i in indices[0] if i < len(documents)]
    except Exception as e:
        st.error(f"Search error: {e}")
        return []

# ===============================
# 1. LOGIN GUARD
# ===============================
if not st.session_state.get("logged_in", False):
    st.switch_page("welcome.py")
    st.stop()

# ===============================
# 2. LOGOUT
# ===============================
if st.session_state.get("logged_in"):
    st.sidebar.markdown("---")
    if st.sidebar.button("**Logout**", type="secondary", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.switch_page("welcome.py")
        st.stop()

# ===============================
# 3. CSS – WHITE DROPDOWN + STYLE
# ===============================
st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
    .stApp { background: #e5e7eb !important; font-family: 'Inter', sans-serif; }
    .block-container { padding-top: 1rem !important; }
    .stMetric, .stAlert, section[data-testid="stDecoration"] { display: none !important; }
    .dashboard-title {
        font-size: 4.8rem !important; font-weight: 800;
        background: linear-gradient(90deg, #dc2626, #b91c1c, #7f1d1d);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        text-align: center; margin: 20px 0 10px; letter-spacing: -2px;
    }
    .ai-card {
        background: #f8fafc !important; border-radius: 36px; padding: 36px; margin: 24px 0;
        border: 2px solid #e2e8f0 !important; box-shadow: 0 10px 30px rgba(0,0,0,0.12);
    }
    .stTextInput > div > div > input {
        background: #ffffff !important; color: #1f2937 !important; border: 2px solid #d1d5db !important;
        border-radius: 16px !important; padding: 14px !important; font-size: 1.1rem !important;
    }
    .stTextInput > div > div > label,
    .stCheckbox > label { color: #1f2937 !important; font-weight: 600; }

    /* TRANSLATE SELECTBOX */
    .stSelectbox > div > label { color: #ffffff !important; font-weight: 600; }
    .stSelectbox > div > div {
        background: #374151 !important;
        color: #ffffff !important;
        border-radius: 12px !important;
        border: 1px solid #4b5563 !important;
        padding: 6px 10px !important;
        font-size: 0.95rem !important;
    }
    .stSelectbox svg { color: #ffffff !important; fill: #ffffff !important; }

    /* DROPDOWN OPTIONS – WHITE TEXT */
    .stSelectbox [data-baseweb="select"] [role="listbox"],
    .stSelectbox [role="option"],
    .stSelectbox [role="option"] > div { background: #1f2937 !important; }

    .stSelectbox [data-baseweb="select"] [role="option"] span,
    .stSelectbox [data-baseweb="select"] [role="option"] div > span,
    .stSelectbox [data-baseweb="select"] [role="option"] div > div > span,
    .stSelectbox [data-baseweb="select"] [role="option"] * {
        color: #ffffff !important;
        background: #1f2937 !important;
        font-weight: 500 !important;
    }

    .stSelectbox [role="option"]:hover,
    .stSelectbox [data-baseweb="select"] [role="option"]:hover,
    .stSelectbox [role="option"]:hover span {
        background: #374151 !important;
        color: #ffffff !important;
    }

    .stSelectbox [data-baseweb="select"] [aria-selected="true"],
    .stSelectbox [data-baseweb="select"] [aria-selected="true"] span {
        background: #dc2626 !important;
        color: #ffffff !important;
        font-weight: 600 !important;
    }

    .stSelectbox option,
    .stSelectbox option * {
        color: #ffffff !important;
        background: #1f2937 !important;
    }

    .stSelectbox [data-baseweb="select"] > div > div > div > span,
    .stSelectbox [data-baseweb="select"] > div > div > div { color: #ffffff !important; }

    /* BUTTONS */
    .stButton > button, button[kind="primary"] {
        background: #dc2626 !important; color: #ffffff !important; border: none !important;
        border-radius: 20px !important; height: 56px !important; font-size: 1.1rem !important;
        font-weight: 600 !important; text-transform: uppercase !important; letter-spacing: 1.2px !important;
        width: 100% !important;
    }
    button[kind="secondary"] {
        background: #6b7280 !important; color: #ffffff !important; border: none !important;
        border-radius: 20px !important; height: 56px !important; font-size: 1.1rem !important;
        font-weight: 600 !important; text-transform: uppercase !important; letter-spacing: 1.2px !important;
        width: 100% !important;
    }

    [data-testid="stSidebar"] { background: #1f2937 !important; }
    .footer { text-align: center; padding: 32px; background: #f1f5f9; border-radius: 24px; margin-top: 50px; border: 2px solid #e2e8f0; }
    .footer p { color: #1f2937 !important; font-size: 1.15rem; margin: 0; font-weight: 500; }
    .stMarkdown, .stWrite, p, div, span, label, h1, h2, h3, h4, h5, h6 { color: #1f2937 !important; }
</style>
""",
    unsafe_allow_html=True,
)

# ===============================
# 4. TITLE
# ===============================
st.markdown(
    """
<div style='text-align: center; margin-bottom: 30px;'>
    <h1 class="dashboard-title">KHBAYER AI</h1>
    <p style="font-size:1.4rem; color:#1f2937; text-align:center; max-width:800px; margin:auto;">
        Ask anything • Powered by Llama 3.2 + RAG
    </p>
</div>
""",
    unsafe_allow_html=True,
)

# ===============================
# 5. MODE + ARTICLE DISPLAY
# ===============================
article = st.session_state.get("selected_article")
if article:
    st.markdown('<div class="ai-card">', unsafe_allow_html=True)
    st.markdown(f'<div style="font-size:2.1rem; font-weight:700; color:#1f2937;">{article.get("title", "No title")}</div>', unsafe_allow_html=True)
    st.markdown(f'<p style="color:#1f2937; font-size:1rem;"><strong>{article.get("source", "Unknown")}</strong> • {article.get("date", "Unknown")}</p>', unsafe_allow_html=True)
    st.markdown(f'<p style="color:#1f2937; font-size:1.15rem; line-height:1.7;">{article.get("summary", "No summary")}</p>', unsafe_allow_html=True)
    st.markdown(f"[Read full article]({article.get('url', '#')})", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    mode = "article"
else:
    st.info("**Free Chat + RAG Mode** — Ask me anything from your knowledge base!")
    mode = "free"

# ===============================
# 6. INPUT + OPTIONS
# ===============================
with st.container():
    st.markdown('<div class="ai-card">', unsafe_allow_html=True)
    query = st.text_input("Your question:", placeholder="e.g., What is the main point?", key="query_input")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        summarize_opt = st.checkbox("Summarize answer?")
    with col2:
        translate_opt = st.selectbox("Translate:", ["None", "French", "Arabic"], key="translate_select")
    with col3:
        audio_opt = st.checkbox("Read aloud?")

    if st.button("Send", type="primary", use_container_width=True):
        if not query.strip():
            st.warning("Please enter a question.")
        else:
            with st.spinner("Thinking..."):
                # ----- BUILD CONTEXT -----
                context = ""
                if mode == "article" and article:
                    context = (article.get("text") or article.get("summary") or article.get("title") or "").strip()
                    if not context:
                        st.warning("Article has no text. Using RAG from knowledge base...")
                # Always use RAG if no article context
                if not context:
                    retrieved = retrieve(query, top_k=5)
                    context = "\n\n".join(retrieved) if retrieved else "No relevant documents found."

                # ----- FINAL PROMPT -----
                prompt = f"""
You are KHBAYER AI. Answer using ONLY this context:
{context}

QUESTION: {query}
ANSWER (clear, natural, concise):
"""
                answer = ask_ollama(prompt)

                # ----- POST-PROCESSING -----
                if summarize_opt:
                    with st.spinner("Summarizing..."):
                        answer = summarize_llama(answer)

                if translate_opt != "None":
                    t_lang = "fr" if translate_opt == "French" else "ar"
                    with st.spinner(f"Translating to {translate_opt}..."):
                        answer = translate(answer, t_lang)

                # ----- DISPLAY ANSWER -----
                st.markdown("</div>", unsafe_allow_html=True)
                st.markdown('<div class="ai-card">', unsafe_allow_html=True)
                st.markdown("### Answer")
                st.markdown(f'<div style="color:#1f2937; font-size:1.15rem; line-height:1.7;">{answer}</div>', unsafe_allow_html=True)

                if audio_opt:
                    audio_lang = "en" if translate_opt == "None" else ("fr" if translate_opt == "French" else "ar")
                    with st.spinner("Generating audio..."):
                        audio_path = text_to_speech(answer, lang=audio_lang)
                        if audio_path and os.path.exists(audio_path):
                            st.audio(audio_path, format="audio/mp3")

                st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown("</div>", unsafe_allow_html=True)

# ===============================
# 7. BUTTONS
# ===============================
col_a, col_b = st.columns(2, gap="medium")
with col_a:
    if st.button("Back to Dashboard", use_container_width=True, type="secondary"):
        if "selected_article" in st.session_state:
            del st.session_state.selected_article
        st.switch_page("pages/page1.py")
with col_b:
    if mode == "article":
        if st.button("Clear Article & Free Chat", use_container_width=True, type="secondary"):
            del st.session_state.selected_article
            st.rerun()

# ===============================
# 8. FOOTER
# ===============================
st.markdown(
    """
<div class="footer">
    <p><strong>KHBAYER AI</strong> • Llama 3.2 + RAG | Nov 12, 2025</p>
</div>
""",
    unsafe_allow_html=True,
)