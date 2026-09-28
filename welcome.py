# welcome.py
import streamlit as st
import json
import os
import hashlib
import streamlit_lottie as st_lottie
import requests
import base64

# =============================================
# GLOBAL LOGOUT
# =============================================
def logout():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.success("Logged out!")
    st.rerun()

if st.session_state.get("logged_in"):
    st.sidebar.markdown("---")
    if st.sidebar.button("**Logout**", type="secondary", use_container_width=True):
        logout()

# =============================================
# CONFIG
# =============================================
st.set_page_config(page_title="KHBAYER", page_icon="Newspaper", layout="centered")

# =============================================
# LOAD LOCAL IMAGE: téléchargement.jpg
# =============================================
image_path = os.path.join(os.path.dirname(__file__), "téléchargement.jpg")
bg_img = None
if os.path.exists(image_path):
    with open(image_path, "rb") as f:
        bg_img = f"data:image/jpeg;base64,{base64.b64encode(f.read()).decode()}"
else:
    st.error("téléchargement.jpg NOT FOUND! Place it in the same folder as welcome.py")
    bg_img = "https://images.unsplash.com/photo-1457369804613-52c61a468e7d?ixlib=rb-4.0.3&auto=format&fit=crop&w=2070&q=80"

# =============================================

# CSS: PURE GREY BOXES + BLACK TEXT
# =============================================
st.markdown(f"""
<style>
    .stApp {{
        background: url("{bg_img}") center/cover no-repeat fixed;
        min-height: 100vh;
    }}
    .block-container {{
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
        max-width: 1100px;
    }}
    /* GREY HEADER */
    header[data-testid="stHeader"] {{
        background-color: #374151 !important;
    }}
    /* GREY SIDEBAR */
    [data-testid="stSidebar"] {{
        background-color: #1f2937 !important;
    }}
    [data-testid="stSidebar"] .css-1d391kg,
    [data-testid="stSidebar"] a {{
        color: white !important;
    }}
    /* KHBAYER: 60% TRANSPARENT GLASS */
    .title-box {{
        background: rgba(15, 23, 42, 0.40);
        backdrop-filter: blur(34px);
        -webkit-backdrop-filter: blur(34px);
        border-radius: 52px;
        padding: 95px 130px;
        max-width: 1000px;
        margin: 90px auto 65px;
        border: 2.5px solid rgba(255, 255, 255, 0.38);
        box-shadow: 0 50px 120px rgba(0, 0, 0, 0.65);
        text-align: center;
        transition: all 0.6s ease;
    }}
    .title-box:hover {{
        background: rgba(15, 23, 42, 0.58);
        transform: translateY(-12px);
        border: 2.5px solid rgba(255, 255, 255, 0.48);
    }}
    /* PURE GREY DASHBOARD & AI BOXES (NO WHITE) */
    .card {{
        background: #9ca3af !important;
        border-radius: 38px;
        padding: 48px;
        text-align: center;
        border: 2.5px solid #6b7280 !important;
        transition: all 0.7s ease;
        height: 100%;
        box-shadow: 0 12px 35px rgba(0, 0, 0, 0.25);
        backdrop-filter: blur(10px);
    }}
    .card:hover {{
        transform: translateY(-22px) scale(1.08);
        box-shadow: 0 50px 110px rgba(0, 0, 0, 0.4);
        border: 2.5px solid #4b5563 !important;
        background: #8b919d !important;
    }}
    .card h3 {{
        color: #000000 !important;
        font-size: 2.3rem;
        margin: 26px 0 20px;
        font-weight: 700;
    }}
    .card p {{
        color: #000000 !important;
        font-size: 1.16rem;
        font-weight: 500;
        line-height: 1.6;
    }}
    /* RED ICONS */
    .icon-container {{
        width: 115px; height: 115px;
        margin: 0 auto 26px;
        background: #dc2626;
        border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        box-shadow: 0 18px 45px rgba(220, 38, 38, 0.6);
    }}
    .icon {{ font-size: 3.8rem; color: white; }}
    /* GREY BUTTONS BELOW CARDS */
    .stButton > button,
    .stFormSubmitButton > button,
    button[kind="primary"],
    button[kind="secondary"] {{
        background: #6b7280 !important;
        color: white !important;
        border: none !important;
        border-radius: 22px !important;
        height: 72px !important;
        font-size: 1.4rem !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 1.8px !important;
        transition: all 0.5s ease !important;
        width: 100% !important;
        box-shadow: 0 8px 20px rgba(0,0,0,0.2) !important;
        margin-top: 20px !important;
    }}
    .stButton > button:hover,
    .stFormSubmitButton > button:hover {{
        background: #4b5563 !important;
        transform: translateY(-7px) !important;
        box-shadow: 0 22px 50px rgba(0,0,0,0.35) !important;
    }}
    /* GREY INPUTS & TABS */
    .stTextInput > div > div > input,
    .stTextInput > div > div > textarea {{
        background: #4b5563 !important;
        color: white !important;
        border: 1px solid #6b7280 !important;
        border-radius: 18px !important;
        padding: 22px !important;
        font-size: 1.15rem !important;
    }}
    .stSelectbox > div > div,
    .stMultiSelect > div > div {{
        background: #4b5563 !important;
        color: white !important;
        border-radius: 18px !important;
    }}
    .stTabs [data-baseweb="tab"] {{
        background: #4b5563 !important;
        color: white !important;
        border-radius: 18px 18px 0 0 !important;
    }}
    .stTabs [data-baseweb="tab"][aria-selected="true"] {{
        background: #374151 !important;
        color: #dc2626 !important;
        border-bottom: 6px solid #dc2626 !important;
    }}

    /* === FORCE BLACK TEXT EVERYWHERE === */
    .stExpander > div > label,
    .stExpander p,
    .stWrite,
    .stMarkdown,
    .css-1d391kg,
    p, span, div, label, h1, h2, h3, h4, h5, h6 {{
        color: #000000 !important;
    }}
    /* Profile Settings & Caption */
    .stExpander > div > label {{
        font-weight: 700 !important;
        font-size: 1.4rem !important;
        color: #000000 !important;
    }}
    .stCaption {{
        color: #000000 !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
    }}
</style>
""", unsafe_allow_html=True)

# =============================================
# MAIN CSS: BLACK TEXT + FONTS
# =============================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
    body, h1, h2, h3, h4, h5, h6, p, span, div, label, .stMarkdown {
        color: #000000 !important;
        font-family: 'Inter', sans-serif;
    }
    .title {
        font-size: 6.6rem !important;
        font-weight: 800;
        background: linear-gradient(90deg, #dc2626, #b91c1c, #7f1d1d);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -3.5px;
        text-shadow: 0 7px 20px rgba(0,0,0,0.5);
        margin: 0 !important;
    }
    .subtitle {
        font-size: 1.85rem;
        color: #000000 !important;
        line-height: 1.7;
        font-weight: 600;
        margin: 22px 0 0 !important;
        opacity: 0.97;
    }
    .lottie { width: 250px; margin: 26px auto; }
</style>
""", unsafe_allow_html=True)

# =============================================
# LOTTIE
# =============================================
def load_lottie(url):
    try:
        r = requests.get(url, timeout=10)
        return r.json() if r.status_code == 200 else None
    except:
        return None

lottie_news = load_lottie("https://assets5.lottiefiles.com/packages/lf20_2jZqQq.json")
lottie_ai = load_lottie("https://assets9.lottiefiles.com/packages/lf20_2srkn5t9.json")

# =============================================
# USERS & AUTH
# =============================================
USERS_FILE = "users.json"
if not os.path.exists(USERS_FILE):
    # Seed the demo account used by the "Demo Login" button
    with open(USERS_FILE, "w") as f:
        json.dump({"admin": {
            "password": hashlib.sha256("admin123".encode()).hexdigest(),
            "preferences": {"theme": "light", "language": "en", "notifications": True, "auto_refresh": False}
        }}, f, indent=2)

with open(USERS_FILE, "r") as f:
    users = json.load(f)

def hash_password(pwd):
    return hashlib.sha256(pwd.encode()).hexdigest()

def save_users():
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

def login(u, p):
    if u in users and users[u]["password"] == hash_password(p):
        st.session_state.logged_in = True
        st.session_state.username = u
        st.session_state.prefs = users[u]["preferences"].copy()
        return True
    return False

def register(u, p, prefs):
    if u in users:
        return False
    users[u] = {"password": hash_password(p), "preferences": prefs}
    save_users()
    return True

# =============================================
# UI: LOGIN + DASHBOARD
# =============================================
if not st.session_state.get("logged_in"):
    st.markdown("""
    <div class="title-box">
        <h1 class="title">KHBAYER</h1>
        <p class="subtitle">Your AI-Powered News Intelligence Platform • Real-Time</p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["Login", "Create Account"])

    with tab1:
        with st.form("login_form"):
            st.subheader("Sign In")
            login_user = st.text_input("Username", placeholder="Enter your username")
            login_pass = st.text_input("Password", type="password", placeholder="Enter your password")
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("Login", use_container_width=True):
                    if login(login_user, login_pass):
                        st.success("Welcome back!")
                        st.rerun()
                    else:
                        st.error("Invalid credentials")
            with col2:
                if st.form_submit_button("Demo Login", use_container_width=True):
                    if login("admin", "admin123"):
                        st.success("Demo mode activated!")
                        st.rerun()

    with tab2:
        with st.form("register_form"):
            st.subheader("Create Your Account")
            new_user = st.text_input("Username", placeholder="Choose a username")
            new_pass = st.text_input("Password", type="password", placeholder="Strong password")
            confirm_pass = st.text_input("Confirm Password", type="password", placeholder="Repeat password")
            st.markdown("#### Your Interests")
            topics = st.multiselect("Select topics", [
                "Technology", "Politics", "Business", "Sports", "Health", "Science",
                "Entertainment", "Environment", "AI & Robotics", "Startups", "Finance", "World News"
            ], default=["Technology", "AI & Robotics"])
            col1, col2 = st.columns(2)
            with col1:
                theme = st.selectbox("Theme", ["light", "dark"], index=1)
                lang = st.selectbox("Language", ["English", "Français", "العربية"])
            with col2:
                st.checkbox("Breaking Alerts", value=True)
                st.checkbox("Auto-refresh", value=True)
            if st.form_submit_button("Create Account", use_container_width=True):
                if not new_user or not new_pass:
                    st.error("Fill all fields")
                elif new_pass != confirm_pass:
                    st.error("Passwords don't match")
                elif register(new_user, new_pass, {
                    "theme": theme,
                    "language": "en" if lang == "English" else "fr" if lang == "Français" else "ar",
                    "topics": topics
                }):
                    st.success(f"Welcome, {new_user}!")
                    login(new_user, new_pass)
                    st.rerun()
                else:
                    st.error("Username taken")

else:
    st.markdown(f'<h1 class="title">Welcome, {st.session_state.username}!</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Your AI news hub is ready.</p>', unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="large")
    with col1:
        st.markdown("""
        <div class="card">
            <div class="icon-container">Chart</div>
            <h3>News Dashboard</h3>
            <p>Real-time updates, sentiment, and your topics.</p>
        </div>
        """, unsafe_allow_html=True)
        if lottie_news:
            st_lottie.st_lottie(lottie_news, height=140, key="news")
        if st.button("Open Dashboard", use_container_width=True):
            st.switch_page("pages/page1.py")

    with col2:
        st.markdown("""
        <div class="card">
            <div class="icon-container">Robot</div>
            <h3>AI Assistant</h3>
            <p>Ask, summarize, translate — in any language.</p>
        </div>
        """, unsafe_allow_html=True)
        if lottie_ai:
            st_lottie.st_lottie(lottie_ai, height=140, key="ai")
        if st.button("Talk to AI", use_container_width=True):
            st.switch_page("pages/app.py")

    # === PROFILE SETTINGS – BLACK TEXT ===
    with st.expander("**Profile Settings**"):
        p = st.session_state.prefs
        st.markdown(f"**Username:** {st.session_state.username}")
        st.markdown(f"**Topics:** {', '.join(p.get('topics', [])) or 'None'}")
        st.markdown(f"**Language:** {p.get('language', 'en').upper()}")

    # === FOOTER – BLACK TEXT ===
    st.caption("**KHBAYER** • AI-Powered News Intelligence")