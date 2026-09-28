# pages/page1.py
import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from io import BytesIO
from PIL import Image
import sys
import os
import re
import time
import hashlib

# =============================================
# PROJECT ROOT
# =============================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

try:
    from data import scrape_news
except Exception as e:
    scrape_news = None
    SCRAPE_IMPORT_ERROR = e
else:
    SCRAPE_IMPORT_ERROR = None

# =============================================
# 1. LOGIN + PREFERENCES
# =============================================
if not st.session_state.get("logged_in"):
    st.switch_page("welcome.py")
    st.stop()

prefs = st.session_state.get("prefs", {}) if isinstance(st.session_state.get("prefs", {}), dict) else {}

if prefs.get("theme") == "dark":
    st._config.set_option("theme.base", "dark")

if prefs.get("auto_refresh"):
    st.rerun()

# =============================================
# 2. LOGOUT
# =============================================
if st.session_state.get("logged_in"):
    st.sidebar.markdown("---")
    if st.sidebar.button("**Logout**", type="secondary", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.switch_page("welcome.py")

# =============================================
# 3. CSS – ENHANCED SECTION TITLES
# =============================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
  
    .stApp { background: #e5e7eb !important; background-image: none !important; font-family: 'Inter', sans-serif; }
    .block-container { padding-top: 1rem !important; }
    .stMetric, .stAlert, section[data-testid="stDecoration"] { display: none !important; }
    .dashboard-title {
        font-size: 4.8rem !important; font-weight: 800;
        background: linear-gradient(90deg, #dc2626, #b91c1c, #7f1d1d);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        text-align: center; margin: 20px 0 10px; letter-spacing: -2px;
    }
    .dashboard-subtitle {
        font-size: 1.4rem; color: #4b5563; text-align: center; margin: 0 auto 30px; max-width: 800px;
    }
    .section-title {
        font-size: 2.2rem !important; font-weight: 800; color: #1f2937 !important;
        margin: 40px 0 20px; padding-bottom: 8px;
        border-bottom: 3px solid #dc2626;
        display: inline-block;
    }
    .metric-card {
        background: #f1f5f9 !important; border-radius: 32px; padding: 28px; text-align: center;
        border: 2px solid #d1d5db !important; height: 100%; box-shadow: 0 10px 30px rgba(0,0,0,0.15);
        transition: all 0.4s ease;
    }
    .metric-card:hover { transform: translateY(-8px); border-color: #dc2626 !important; }
    .metric-card h3 { color: #1f2937 !important; font-size: 1.6rem; margin: 0 0 8px; font-weight: 700; }
    .metric-card p { color: #dc2626 !important; font-size: 3.2rem; font-weight: 800; margin: 0; }
    .article-card {
        background: #f8fafc !important; border-radius: 36px; padding: 36px; margin-bottom: 28px;
        border: 2px solid #e2e8f0 !important; box-shadow: 0 10px 30px rgba(0,0,0,0.12);
        transition: all 0.4s ease;
    }
    .article-card:hover { transform: translateY(-10px); border-color: #dc2626 !important; }
    .article-title { font-size: 1.8rem; font-weight: 700; color: #1f2937 !important; margin: 0 0 12px; line-height: 1.4; }
    .article-source { color: #64748b; font-size: 1rem; font-weight: 500; margin: 0 0 14px; }
    .article-summary { color: #475569; font-size: 1.15rem; line-height: 1.7; margin: 0 0 18px; }
    .stButton > button, button[kind="primary"], button[kind="secondary"] {
        background: #6b7280 !important; color: white !important; border: none !important;
        border-radius: 20px !important; height: 56px !important; font-size: 1.1rem !important;
        font-weight: 600 !important; text-transform: uppercase !important; letter-spacing: 1.2px !important;
        transition: all 0.4s ease !important; box-shadow: 0 6px 20px rgba(0,0,0,0.15) !important;
        width: 100% !important;
    }
    .stButton > button:hover { background: #4b5563 !important; transform: translateY(-4px) !important; }
    .red-btn {
        background: #dc2626 !important; color: white !important; border: none !important;
        border-radius: 20px !important; height: 56px !important; font-size: 1.1rem !important;
        font-weight: 600 !important; text-transform: uppercase !important; letter-spacing: 1.2px !important;
        transition: all 0.4s ease !important; box-shadow: 0 6px 20px rgba(220,38,38,0.3) !important;
        width: 100% !important;
    }
    .red-btn:hover { background: #b91c1c !important; transform: translateY(-4px) !important; }
    [data-testid="stSidebar"] { background: #1f2937 !important; }
    .sidebar-header { color: white !important; font-size: 1.35rem; font-weight: 700; margin-bottom: 20px; padding: 16px; background: rgba(255,255,255,0.1); border-radius: 18px; text-align: center; }
    .stTextInput > div > div > input, .stMultiSelect > div > div {
        background: #4b5563 !important; color: white !important; border: 1.5px solid #6b7280 !important; border-radius: 14px !important; padding: 12px !important; font-size: 1.1rem !important;
    }
    .chart-container {
        background: #f8fafc !important; border-radius: 32px; padding: 28px; margin: 20px 0;
        border: 2px solid #e2e8f0 !important; box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    .footer { text-align: center; padding: 32px; background: #f1f5f9; border-radius: 24px; margin-top: 50px; border: 2px solid #e2e8f0; }
    .footer p { color: #64748b !important; font-size: 1.15rem; margin: 0; font-weight: 500; }
</style>
""", unsafe_allow_html=True)

# =============================================
# 4. UTILS
# =============================================
def format_date(date_val):
    try:
        dt = pd.to_datetime(date_val, errors="coerce", utc=True)
        return dt.strftime("%b %d, %Y") if pd.notna(dt) else "Date unavailable"
    except:
        return "Date unavailable"

# =============================================
# 5. IMAGE LOADER
# =============================================
@st.cache_data(ttl=3600)
def load_image(url: str):
    if not url or "placeholder" in str(url):
        return None
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(url, timeout=12, headers=headers)
        if r.status_code == 200 and "image" in r.headers.get("Content-Type", "").lower():
            return Image.open(BytesIO(r.content))
    except:
        pass
    return None

# =============================================
# 6. ALERTS – ASK AI BUTTONS SAME AS MAIN PAGE
# =============================================
if prefs.get("notifications", False):
    user_topics = prefs.get("topics", [])
    if user_topics:
        with st.sidebar:
            st.markdown('<div class="sidebar-header">Breaking Alerts</div>', unsafe_allow_html=True)
            alert_placeholder = st.empty()
        if "last_alert_check" not in st.session_state:
            st.session_state.last_alert_check = 0
            st.session_state.alert_shown = set()
        now = time.time()
        if now - st.session_state.last_alert_check > 60:
            with st.spinner("Checking..."):
                latest = scrape_news("all", num_articles=5) if scrape_news else pd.DataFrame()
                for _, row in latest.iterrows():
                    if any(topic.lower() in row["title"].lower() for topic in user_topics):
                        alert_id = hashlib.md5(row["title"].encode()).hexdigest()
                        if alert_id not in st.session_state.alert_shown:
                            st.session_state.alert_shown.add(alert_id)
                            with alert_placeholder:
                                st.markdown(f"""
                                <div style="background:#fee2e2; border-left:6px solid #dc2626; border-radius:16px; padding:18px; margin:12px 0;">
                                    <h4 style='color:#dc2626; margin:0 0 6px;'>BREAKING: {row['title']}</h4>
                                    <p style='color:#64748b; font-size:0.9rem; margin:0 0 10px;'>
                                        {row['source']} • {format_date(row['date'])}
                                    </p>
                                    <div style="display: flex; gap: 12px;">
                                """, unsafe_allow_html=True)
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.markdown(
                                        f'<a href="{row["url"]}" target="_blank" style="text-decoration:none; flex:1;">'
                                        '<button class="red-btn" style="height:44px; font-size:0.95rem;">READ FULL</button>'
                                        '</a>',
                                        unsafe_allow_html=True
                                    )
                                with col2:
                                    if st.button("ASK AI", key=f"alert_ask_{row.name}", use_container_width=True):
                                        st.session_state.selected_article = row.to_dict()
                                        st.switch_page("pages/app.py")
                                st.markdown("</div></div>", unsafe_allow_html=True)
            st.session_state.last_alert_check = now

# =============================================
# 7. TITLE
# =============================================
st.markdown("""
<div style='text-align: center; margin-bottom: 30px;'>
    <h1 class="dashboard-title">KHBAYER DASHBOARD</h1>
    <p class="dashboard-subtitle">Real-Time News Pulse • AI-Powered Sentiment Analysis</p>
</div>
""", unsafe_allow_html=True)

# =============================================
# 8. SIDEBAR
# =============================================
with st.sidebar:
    st.markdown('<div class="sidebar-header">Filters</div>', unsafe_allow_html=True)
    query = st.text_input("Search Topic", placeholder="e.g., AI, politics", key="q")
    refresh = st.button("Refresh Data", use_container_width=True)
    sentiment_filter = st.multiselect("Sentiment", ["Positive", "Negative", "Neutral"], default=["Positive", "Negative", "Neutral"], key="s")

# =============================================
# 9. DATA
# =============================================
@st.cache_data(ttl=300)
def get_data(q: str):
    if not scrape_news: return pd.DataFrame()
    return scrape_news(q if q else "all", num_articles=40)

if refresh or "df_raw" not in st.session_state:
    with st.spinner("Fetching..."):
        st.session_state.df_raw = get_data(query)

df = st.session_state.df_raw.copy()

# Ensure sentiment
if "sentiment" not in df.columns or df["sentiment"].isna().all():
    df["sentiment"] = pd.Series([-0.5, 0.8, 0.3, -0.2, 0.6, 0.1, -0.7, 0.4, -0.1, 0.5] * 4)[:len(df)]
    df["sentiment_label"] = df["sentiment"].apply(lambda x: "Positive" if x > 0.1 else "Negative" if x < -0.1 else "Neutral")

# PINNED ARTICLE
replacement_article = {
    "title": "Amazon to cut about 14,000 corporate jobs in AI push",
    "summary": "Amazon is cutting approximately 14,000 corporate jobs to streamline operations and accelerate AI investments...",
    "url": "https://www.reuters.com/sustainability/amazon-lay-off-about-14000-roles-2025-10-28/",
    "date": "2025-10-28 10:15:00",
    "source": "Reuters",
    "image_url": "https://cloudfront-us-east-2.images.arcpublishing.com/reuters/7KX2O5Z6Q5F6XN5Y2U3W6Z7X4Y.jpg",
    "sentiment": -0.32,
    "sentiment_label": "Negative",
}
df = pd.concat([pd.DataFrame([replacement_article]), df], ignore_index=True)

# FILTERS
user_topics = prefs.get("topics", [])
if user_topics:
    pattern = "|".join(re.escape(t) for t in user_topics)
    mask = df["title"].str.contains(pattern, case=False, na=False) | df["summary"].str.contains(pattern, case=False, na=False)
    df = df[mask].copy()

if query:
    df = df[df["title"].str.contains(re.escape(query), case=False, na=False)]

if sentiment_filter:
    df = df[df["sentiment_label"].isin(sentiment_filter)]

# LIVE + SORT
@st.cache_data(ttl=300)
def url_is_live(u):
    if not u or u == "#": return False
    try: return requests.head(u, timeout=5).status_code == 200
    except: return False

df = df[df["url"].apply(url_is_live)].reset_index(drop=True)
df["date"] = pd.to_datetime(df["date"], errors="coerce", utc=True)
df = df.sort_values("date", ascending=False).reset_index(drop=True)

# =============================================
# 10. METRICS
# =============================================
col1, col2 = st.columns(2, gap="medium")
with col1:
    st.markdown(f'''
    <div class="metric-card">
        <h3>Total Articles</h3>
        <p>{len(df)}</p>
    </div>
    ''', unsafe_allow_html=True)
with col2:
    st.markdown(f'''
    <div class="metric-card">
        <h3>Positive News</h3>
        <p>{len(df[df["sentiment"] > 0.1])}</p>
    </div>
    ''', unsafe_allow_html=True)

# =============================================
# 11. RENDER ARTICLE – SAME BUTTONS
# =============================================
def render_article(row):
    sentiment_label = "Positive" if row["sentiment"] > 0.1 else "Negative" if row["sentiment"] < -0.1 else "Neutral"
    summary = row.get("summary", "")[:240] + ("..." if len(row.get("summary", "")) > 240 else "")

    st.markdown(f'''
    <div class="article-card">
        <div style="display: flex; gap: 28px; align-items: flex-start;">
            <div style="flex: 1; border-radius: 24px; overflow: hidden; box-shadow: 0 8px 20px rgba(0,0,0,0.15);">
    ''', unsafe_allow_html=True)

    img = load_image(row["image_url"])
    if img:
        st.image(img, use_container_width=True)
    else:
        st.image("https://via.placeholder.com/300x200.png?text=No+Image", use_container_width=True)

    st.markdown(f'''
            </div>
            <div style="flex: 2;">
                <div class="article-title">{sentiment_label} {row["title"]}</div>
                <p class="article-source"><strong>{row["source"]}</strong> • {format_date(row["date"])}</p>
                <p class="article-summary">{summary}</p>
                <div style="display: flex; gap: 12px; margin-top: 16px;">
                    <a href="{row["url"]}" target="_blank" style="flex:1; text-decoration:none;">
                        <button class="red-btn">READ FULL</button>
                    </a>
    ''', unsafe_allow_html=True)

    if st.button("ASK AI", key=f"ask_ai_{row.name}", use_container_width=True):
        st.session_state.selected_article = row.to_dict()
        st.switch_page("pages/app.py")

    st.markdown('''
                </div>
            </div>
        </div>
    </div>
    ''', unsafe_allow_html=True)

# =============================================
# 12. DISPLAY – BREAKING NEWS TITLE VISIBLE
# =============================================
st.markdown('<h2 class="section-title">Breaking News</h2>', unsafe_allow_html=True)
if not df.empty:
    render_article(df.iloc[0])

if len(df) > 1:
    st.markdown('<h2 class="section-title">Latest Headlines</h2>', unsafe_allow_html=True)
    for _, row in df.iloc[1:8].iterrows():
        render_article(row)

# =============================================
# 13. CHARTS
# =============================================
if not df.empty:
    st.markdown('<h2 class="section-title">Sentiment Analysis</h2>', unsafe_allow_html=True)
    col_a, col_b = st.columns(2, gap="large")

    with col_a:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        fig_line = px.line(
            df.sort_values("date"),
            x="date", y="sentiment",
            title="Sentiment Trend",
            hover_data=["title"],
            color_discrete_sequence=["#dc2626"]
        )
        fig_line.update_layout(
            height=400,
            template="plotly_white",
            plot_bgcolor="#f8fafc",
            paper_bgcolor="#f8fafc",
            margin=dict(l=20, r=20, t=50, b=20),
            font=dict(family="Inter", size=13, color="black"),
            title_font=dict(size=18, color="black"),
            xaxis=dict(tickfont=dict(color="black"), title_font=dict(color="black"), gridcolor="#e2e8f0"),
            yaxis=dict(tickfont=dict(color="black"), title_font=dict(color="black"), gridcolor="#e2e8f0")
        )
        fig_line.update_traces(line=dict(width=3))
        st.plotly_chart(fig_line, use_container_width=True, key="line_fixed")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_b:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        cnt = df["sentiment_label"].value_counts().reindex(["Positive", "Negative", "Neutral"], fill_value=0)
        labels = cnt.index.tolist()
        values = cnt.values.tolist()

        fig_pie = px.pie(
            values=values,
            names=labels,
            title="Sentiment Distribution"
        )
        colors = ["#dc2626", "#000000", "#6b7280"]
        fig_pie.update_traces(
            marker=dict(colors=colors),
            textinfo='percent+label',
            textfont_size=14
        )
        fig_pie.update_layout(
            height=400,
            template="plotly_white",
            plot_bgcolor="#f8fafc",
            paper_bgcolor="#f8fafc",
            margin=dict(l=20, r=20, t=50, b=20),
            font=dict(family="Inter", size=13, color="black"),
            title_font=dict(size=18, color="black"),
            legend=dict(font=dict(color="black"))
        )
        st.plotly_chart(fig_pie, use_container_width=True, key="pie_fixed")
        st.markdown('</div>', unsafe_allow_html=True)

# =============================================
# 14. FOOTER
# =============================================
st.markdown("""
<div class="footer">
    <p><strong>KHBAYER</strong> • Personalized News | Powered by Streamlit • Nov 11, 2025 12:50 AM CET</p>
</div>
""", unsafe_allow_html=True)