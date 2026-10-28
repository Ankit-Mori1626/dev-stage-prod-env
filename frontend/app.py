import streamlit as st
import requests
import os
import json
import time
import pandas as pd
from datetime import datetime

# --- Environment Detection & Configuration ---
APP_ENV = os.getenv("APP_ENV", os.getenv("ENVIRONMENT", "dev")).lower().strip()
if APP_ENV in ["development", "local"]:
    APP_ENV = "dev"
elif APP_ENV in ["staging", "test", "qa"]:
    APP_ENV = "stage"
elif APP_ENV in ["production", "live", "main", "master"]:
    APP_ENV = "prod"

# Dynamic Environment Theme & Metadata Mapping
ENV_CONFIGS = {
    "dev": {
        "title": "CloudNexus | 🚧 DEV Environment",
        "icon": "🚧",
        "env_name": "DEV",
        "branch": "dev",
        "cluster_name": "DEVELOPMENT",
        "channel_name": "Dev Channel",
        "badge_text": "⚡ DEV ENVIRONMENT ACTIVE",
        "ribbon_text": "⚡ DEV ENVIRONMENT &nbsp;|&nbsp; BRANCH: dev &nbsp;|&nbsp; 🚧 NOT FOR PRODUCTION USE &nbsp;|&nbsp; INTERNAL TESTING ONLY &nbsp;⚡",
        "ribbon_gradient": "linear-gradient(90deg, #78350f, #d97706, #f59e0b, #d97706, #78350f)",
        "ribbon_shadow": "rgba(245, 158, 11, 0.4)",
        "ribbon_color": "#0d0117",
        "bg_color": "#0d0117",
        "text_color": "#e2d9f3",
        "primary_color": "#9333ea",
        "accent_color": "#c084fc",
        "sidebar_bg": "linear-gradient(180deg, #0f0520 0%, #0d0117 100%)",
        "sidebar_border": "#2d1b4e",
        "sidebar_title": "#d8b4fe",
        "sidebar_sub": "#7c3aed",
        "metric_color": "#a855f7",
        "metric_label": "#7c3aed",
        "card_bg": "linear-gradient(135deg, #1a0a2e 0%, #12011f 100%)",
        "card_border": "#3b1d6e",
        "card_highlight": "#7c3aed",
        "badge_bg": "rgba(124, 58, 237, 0.2)",
        "badge_border": "rgba(124, 58, 237, 0.5)",
        "badge_text_color": "#c084fc",
        "env_badge_bg": "rgba(245, 158, 11, 0.15)",
        "env_badge_border": "rgba(245, 158, 11, 0.5)",
        "env_badge_color": "#fbbf24",
        "btn_gradient": "linear-gradient(135deg, #7c3aed, #6d28d9)",
        "btn_hover": "linear-gradient(135deg, #6d28d9, #5b21b6)",
        "hero_border": "#7c3aed",
        "hero_tag": "🚧 Dev Build",
        "footer_text": "🏢 CloudNexus Solutions Inc. | DEV Environment | Branch: dev | Kubeadm Kubernetes & Ingress Controller"
    },
    "stage": {
        "title": "CloudNexus | 🧪 STAGE Environment",
        "icon": "🧪",
        "env_name": "STAGE",
        "branch": "stage",
        "cluster_name": "STAGING",
        "channel_name": "Stage Channel",
        "badge_text": "🧪 STAGE ENVIRONMENT ACTIVE",
        "ribbon_text": "🧪 STAGE ENVIRONMENT &nbsp;|&nbsp; BRANCH: stage &nbsp;|&nbsp; 🔬 PRE-PRODUCTION TESTING &nbsp;|&nbsp; QA & UAT VERIFIED &nbsp;🧪",
        "ribbon_gradient": "linear-gradient(90deg, #075985, #0284c7, #38bdf8, #0284c7, #075985)",
        "ribbon_shadow": "rgba(56, 189, 248, 0.4)",
        "ribbon_color": "#031326",
        "bg_color": "#031326",
        "text_color": "#e0f2fe",
        "primary_color": "#0284c7",
        "accent_color": "#38bdf8",
        "sidebar_bg": "linear-gradient(180deg, #071f3b 0%, #031326 100%)",
        "sidebar_border": "#0e3a66",
        "sidebar_title": "#bae6fd",
        "sidebar_sub": "#0284c7",
        "metric_color": "#38bdf8",
        "metric_label": "#0284c7",
        "card_bg": "linear-gradient(135deg, #092342 0%, #04172e 100%)",
        "card_border": "#0c4a6e",
        "card_highlight": "#0284c7",
        "badge_bg": "rgba(2, 132, 199, 0.2)",
        "badge_border": "rgba(2, 132, 199, 0.5)",
        "badge_text_color": "#38bdf8",
        "env_badge_bg": "rgba(56, 189, 248, 0.15)",
        "env_badge_border": "rgba(56, 189, 248, 0.5)",
        "env_badge_color": "#38bdf8",
        "btn_gradient": "linear-gradient(135deg, #0284c7, #0369a1)",
        "btn_hover": "linear-gradient(135deg, #0369a1, #075985)",
        "hero_border": "#0284c7",
        "hero_tag": "🧪 Stage Build",
        "footer_text": "🏢 CloudNexus Solutions Inc. | STAGE Environment | Branch: stage | Kubeadm Kubernetes & Ingress Controller"
    },
    "prod": {
        "title": "CloudNexus | 🚀 PROD Environment",
        "icon": "🚀",
        "env_name": "PROD",
        "branch": "prod",
        "cluster_name": "PRODUCTION",
        "channel_name": "Production Channel",
        "badge_text": "🚀 PROD ENVIRONMENT ACTIVE",
        "ribbon_text": "🚀 PRODUCTION CLUSTER &nbsp;|&nbsp; BRANCH: prod &nbsp;|&nbsp; 🛡️ 99.999% SLA MISSION CRITICAL &nbsp;|&nbsp; LIVE WORKLOAD &nbsp;🚀",
        "ribbon_gradient": "linear-gradient(90deg, #064e3b, #059669, #10b981, #059669, #064e3b)",
        "ribbon_shadow": "rgba(16, 185, 129, 0.4)",
        "ribbon_color": "#021a12",
        "bg_color": "#021a12",
        "text_color": "#d1fae5",
        "primary_color": "#059669",
        "accent_color": "#34d399",
        "sidebar_bg": "linear-gradient(180deg, #052e1f 0%, #021a12 100%)",
        "sidebar_border": "#065f46",
        "sidebar_title": "#a7f3d0",
        "sidebar_sub": "#059669",
        "metric_color": "#34d399",
        "metric_label": "#059669",
        "card_bg": "linear-gradient(135deg, #073b28 0%, #032418 100%)",
        "card_border": "#047857",
        "card_highlight": "#059669",
        "badge_bg": "rgba(5, 150, 105, 0.2)",
        "badge_border": "rgba(5, 150, 105, 0.5)",
        "badge_text_color": "#34d399",
        "env_badge_bg": "rgba(16, 185, 129, 0.15)",
        "env_badge_border": "rgba(16, 185, 129, 0.5)",
        "env_badge_color": "#34d399",
        "btn_gradient": "linear-gradient(135deg, #059669, #047857)",
        "btn_hover": "linear-gradient(135deg, #047857, #065f46)",
        "hero_border": "#059669",
        "hero_tag": "🚀 Production Build",
        "footer_text": "🏢 CloudNexus Solutions Inc. | PROD Environment | Branch: prod | Kubeadm Kubernetes & Ingress Controller"
    }
}

CFG = ENV_CONFIGS.get(APP_ENV, ENV_CONFIGS["dev"])

# --- Configure Streamlit Page ---
st.set_page_config(
    page_title=CFG["title"],
    page_icon=CFG["icon"],
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Backend API Configuration & Discovery ---
def get_candidate_backend_urls():
    candidates = []
    env_backend = os.getenv("BACKEND_URL")
    if env_backend:
        candidates.append(env_backend.rstrip("/"))
    for c in [
        f"http://backend-service.{APP_ENV}.svc.cluster.local:5000",
        "http://backend-service:5000",
        "http://backend:5000",
        "http://127.0.0.1:5000",
        "http://localhost:5000"
    ]:
        if c not in candidates:
            candidates.append(c)
    return candidates

BACKEND_CANDIDATES = get_candidate_backend_urls()
BACKEND_URL = BACKEND_CANDIDATES[0]

# Session State Initialization for Admin Authentication
if "is_admin_authenticated" not in st.session_state:
    st.session_state["is_admin_authenticated"] = False
if "admin_token" not in st.session_state:
    st.session_state["admin_token"] = ""

# ============================================================
# DYNAMIC THEME INJECTION (DEV / STAGE / PROD)
# ============================================================
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

    /* ── Base ── */
    .stApp {{
        background-color: {CFG["bg_color"]} !important;
        color: {CFG["text_color"]} !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }}

    /* ── Environment Ribbon at very top ── */
    .env-ribbon {{
        background: {CFG["ribbon_gradient"]};
        background-size: 300% 100%;
        animation: ribbonShift 4s ease infinite;
        color: {CFG["ribbon_color"]};
        text-align: center;
        padding: 10px 0;
        font-weight: 800;
        font-size: 0.92rem;
        letter-spacing: 0.08em;
        border-radius: 0 0 12px 12px;
        margin-bottom: 8px;
        box-shadow: 0 4px 20px {CFG["ribbon_shadow"]};
    }}
    @keyframes ribbonShift {{
        0%   {{ background-position: 0% 50%; }}
        50%  {{ background-position: 100% 50%; }}
        100% {{ background-position: 0% 50%; }}
    }}

    /* ── Headers ── */
    h1, h2, h3, h4, h5, h6 {{
        color: #ffffff !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em;
    }}
    p, span, label {{ color: {CFG["text_color"]} !important; }}
    .stCaption, small {{ color: {CFG["accent_color"]} !important; }}

    /* ── Sidebar ── */
    section[data-testid="stSidebar"] {{
        background: {CFG["sidebar_bg"]} !important;
        border-right: 1px solid {CFG["sidebar_border"]} !important;
    }}
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {{
        color: {CFG["sidebar_title"]} !important;
    }}

    /* ── Metrics ── */
    [data-testid="stMetricValue"] {{
        color: {CFG["metric_color"]} !important;
        font-weight: 800 !important;
        font-size: 1.6rem !important;
        text-shadow: 0 0 20px {CFG["badge_bg"]};
    }}
    [data-testid="stMetricLabel"] {{
        color: {CFG["metric_label"]} !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        font-size: 0.72rem !important;
        letter-spacing: 0.06em;
    }}

    /* ── Cards ── */
    .dev-card {{
        background: {CFG["card_bg"]};
        border: 1px solid {CFG["card_border"]};
        border-radius: 14px;
        padding: 22px;
        margin-bottom: 16px;
        box-shadow: 0 4px 24px rgba(0, 0, 0, 0.25);
        transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
        position: relative;
        overflow: hidden;
    }}
    .dev-card::before {{
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 2px;
        background: {CFG["ribbon_gradient"]};
        background-size: 200% 100%;
        animation: cardBorder 3s ease infinite;
    }}
    @keyframes cardBorder {{
        0%   {{ background-position: 0% 0%; }}
        50%  {{ background-position: 100% 0%; }}
        100% {{ background-position: 0% 0%; }}
    }}
    .dev-card:hover {{
        border-color: {CFG["card_highlight"]} !important;
        transform: translateY(-3px);
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.4);
    }}
    .auth-lock-card {{
        background: {CFG["card_bg"]};
        border: 2px solid {CFG["primary_color"]};
        border-radius: 16px;
        padding: 32px;
        text-align: center;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
        max-width: 600px;
        margin: 20px auto;
    }}
    .dev-hero {{
        background: {CFG["card_bg"]};
        border: 1px solid {CFG["card_border"]};
        border-radius: 18px;
        padding: 40px;
        margin-bottom: 24px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        position: relative;
        overflow: hidden;
    }}
    .dev-hero::after {{
        content: '';
        position: absolute;
        top: -60px; right: -60px;
        width: 220px; height: 220px;
        background: radial-gradient(circle, {CFG["badge_bg"]} 0%, transparent 70%);
        border-radius: 50%;
    }}
    .dev-badge {{
        display: inline-block;
        background: {CFG["badge_bg"]};
        color: {CFG["badge_text_color"]};
        border: 1px solid {CFG["badge_border"]};
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.78rem;
        font-weight: 600;
        margin-right: 6px;
        margin-bottom: 6px;
    }}
    .env-indicator {{
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: {CFG["env_badge_bg"]};
        border: 1px solid {CFG["env_badge_border"]};
        color: {CFG["env_badge_color"]};
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 700;
        letter-spacing: 0.05em;
    }}
    .path-card {{
        background: {CFG["card_bg"]};
        border: 1px solid {CFG["card_border"]};
        border-left: 4px solid {CFG["primary_color"]};
        padding: 16px;
        border-radius: 8px;
        margin-bottom: 12px;
    }}
    .path-card code {{
        background: {CFG["bg_color"]};
        color: {CFG["accent_color"]};
        padding: 2px 6px;
        border-radius: 4px;
        border: 1px solid {CFG["card_border"]};
    }}
    .debug-panel {{
        background: #020b14;
        border: 1px dashed {CFG["card_border"]};
        border-radius: 10px;
        padding: 16px;
        font-family: 'Courier New', monospace;
        font-size: 0.82rem;
        color: {CFG["accent_color"]};
    }}

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 6px;
        background-color: {CFG["bg_color"]};
        padding: 8px;
        border-radius: 12px;
        border: 1px solid {CFG["card_border"]};
    }}
    .stTabs [data-baseweb="tab"] {{
        background-color: {CFG["card_bg"]} !important;
        border: 1px solid {CFG["card_border"]} !important;
        border-radius: 8px !important;
        padding: 10px 18px !important;
        color: {CFG["text_color"]} !important;
        font-weight: 600 !important;
        font-size: 0.92rem !important;
        transition: all 0.2s ease;
    }}
    .stTabs [data-baseweb="tab"]:hover {{
        background-color: {CFG["card_border"]} !important;
        color: #ffffff !important;
        border-color: {CFG["primary_color"]} !important;
    }}
    .stTabs [aria-selected="true"] {{
        background: {CFG["btn_gradient"]} !important;
        color: #ffffff !important;
        border-color: {CFG["accent_color"]} !important;
        box-shadow: 0 4px 16px {CFG["ribbon_shadow"]} !important;
    }}

    /* ── Inputs ── */
    .stTextInput input, .stTextArea textarea, .stSelectbox select {{
        background-color: {CFG["card_bg"]} !important;
        color: #ffffff !important;
        border: 1px solid {CFG["card_border"]} !important;
        border-radius: 8px !important;
    }}
    .stTextInput input:focus, .stTextArea textarea:focus {{
        border-color: {CFG["primary_color"]} !important;
        box-shadow: 0 0 0 2px {CFG["badge_bg"]} !important;
    }}

    /* ── Buttons ── */
    .stButton > button {{
        background: {CFG["btn_gradient"]} !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 8px 18px !important;
        transition: all 0.2s ease;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
    }}
    .stButton > button:hover {{
        background: {CFG["btn_hover"]} !important;
        box-shadow: 0 6px 20px {CFG["ribbon_shadow"]} !important;
        transform: translateY(-1px);
    }}
    </style>
""", unsafe_allow_html=True)

# ── Dynamic Top Environment Ribbon ──────────────────────────────
st.markdown(f"""
<div class="env-ribbon">
  {CFG["ribbon_text"]}
</div>
""", unsafe_allow_html=True)

# --- Backend Communication Helpers ---
def get_active_url():
    return st.session_state.get("active_backend_url", BACKEND_URL)

@st.cache_data(ttl=30, show_spinner=False)
def get_backend_health():
    last_err = "No connection"
    for candidate in BACKEND_CANDIDATES:
        try:
            t0 = time.time()
            res = requests.get(f"{candidate}/ready", timeout=2)
            latency = round((time.time() - t0) * 1000, 2)
            if res.status_code == 200:
                data = res.json()
                data["latency_ms"] = latency
                data["active_url"] = candidate
                return data
            elif res.status_code in [500, 502, 503]:
                return {"status": "UNHEALTHY", "error": f"HTTP {res.status_code}", "latency_ms": latency, "active_url": candidate}
        except Exception as e:
            last_err = str(e)
    return {"status": "OFFLINE", "error": last_err, "latency_ms": 0, "active_url": BACKEND_CANDIDATES[0]}

@st.cache_data(ttl=30, show_spinner=False)
def fetch_jobs(base_url=None):
    url = (base_url or get_active_url()).rstrip("/")
    try:
        res = requests.get(f"{url}/api/jobs", timeout=3)
        if res.status_code == 200:
            data = res.json()
            if isinstance(data, dict):
                return data.get("data", [])
            elif isinstance(data, list):
                return data
        return []
    except Exception:
        return []

@st.cache_data(ttl=30, show_spinner=False)
def fetch_tasks(base_url=None):
    url = (base_url or get_active_url()).rstrip("/")
    try:
        res = requests.get(f"{url}/api/tasks", timeout=3)
        if res.status_code == 200:
            data = res.json()
            if isinstance(data, dict):
                return data
            elif isinstance(data, list):
                return {"data": data, "environment": CFG["env_name"], "node_name": "local", "pod_name": "standalone"}
        return {"data": [], "environment": CFG["env_name"], "node_name": "local", "pod_name": "standalone"}
    except Exception:
        return {"data": [], "environment": CFG["env_name"], "node_name": "local", "pod_name": "standalone"}

def submit_application(payload, base_url=None):
    url = (base_url or get_active_url()).rstrip("/")
    try:
        res = requests.post(f"{url}/api/applications", json=payload, timeout=5)
        return res.status_code in [200, 201]
    except Exception:
        return False

def submit_inquiry(payload, base_url=None):
    url = (base_url or get_active_url()).rstrip("/")
    try:
        res = requests.post(f"{url}/api/inquiries", json=payload, timeout=5)
        return res.status_code in [200, 201]
    except Exception:
        return False

def fetch_admin_data(endpoint, token, base_url=None):
    url = (base_url or get_active_url()).rstrip("/")
    try:
        headers = {"x-admin-token": token}
        res = requests.get(f"{url}/api/{endpoint}", headers=headers, timeout=4)
        if res.status_code == 200:
            return res.json().get("data", [])
        return []
    except Exception:
        return []

def create_task(title, description, priority, status, base_url=None):
    url = (base_url or get_active_url()).rstrip("/")
    try:
        payload = {
            "title": title,
            "description": description,
            "priority": priority,
            "status": status
        }
        res = requests.post(f"{url}/api/tasks", json=payload, timeout=4)
        return res.status_code in [200, 201]
    except Exception as e:
        st.error(f"Error creating task: {e}")
        return False

# --- Fetch Initial Data ---
health_data = get_backend_health()
active_backend_url = health_data.get("active_url", BACKEND_URL)
st.session_state["active_backend_url"] = active_backend_url

tasks_response = fetch_tasks(active_backend_url)
if not isinstance(tasks_response, dict):
    tasks_response = {"data": [], "environment": CFG["env_name"], "node_name": "local", "pod_name": "standalone"}
tasks_list = tasks_response.get("data", [])
jobs_list = fetch_jobs(active_backend_url)

# Environment & Pod Telemetry
reported_env = tasks_response.get("environment", health_data.get("environment", CFG["env_name"])).upper()
pod_name = tasks_response.get("pod_name", health_data.get("pod", "k8s-pod"))
node_name = tasks_response.get("node_name", "k8s-node")
build_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# --- Sidebar ---
with st.sidebar:
    st.markdown(f"""
    <div style="text-align:center; padding: 12px 0;">
      <div style="font-size:2rem;">{CFG["icon"]}</div>
      <div style="font-size:1.2rem; font-weight:800; color:{CFG['sidebar_title']};">CloudNexus</div>
      <div style="font-size:0.72rem; color:{CFG['sidebar_sub']}; letter-spacing:0.15em; text-transform:uppercase; margin-top:2px;">{CFG["channel_name"]}</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    st.markdown(f"""
    <div class="env-indicator">{CFG["badge_text"]}</div>
    """, unsafe_allow_html=True)
    st.markdown(f"**Branch:** `{CFG['branch']}`")
    st.markdown(f"**Build:** `{datetime.now().strftime('%d %b %Y %H:%M')}`")
    st.markdown(f"**Pod:** `{pod_name}`")
    st.markdown(f"**Node:** `{node_name}`")
    st.markdown("---")

    if health_data.get("status") == "READY":
        st.success(f"🟢 **API & DB**: READY ({health_data.get('latency_ms')} ms)")
    else:
        err_msg = health_data.get("error", "No connection")
        st.error("🔴 **Backend API**: Offline")
        st.caption(f"⚠️ *{err_msg}*")
        st.caption(f"Endpoint: `{active_backend_url}`")

    st.markdown("---")
    st.subheader("🛡️ Ingress Routes")
    st.markdown(f"""
    - `/` ➡️ Web UI (`{CFG['branch']}.3tier.local`)
    - `/api/jobs` ➡️ Active Listings
    - `/api/inquiries` ➡️ POST Quote
    - `/api/applications` ➡️ POST Apply
    - `GET /api/applications` 🔒 *(Admin)*
    - `GET /api/inquiries` 🔒 *(Admin)*
    """)

    st.markdown("---")
    if st.session_state["is_admin_authenticated"]:
        st.success("🔓 **Admin Mode**: Authenticated")
        if st.button("🚪 Logout Admin", use_container_width=True):
            st.session_state["is_admin_authenticated"] = False
            st.session_state["admin_token"] = ""
            st.rerun()
    else:
        st.info("🔒 **Admin Mode**: Locked")

    st.markdown("---")
    if st.button("🔄 Refresh Telemetry", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# --- Top Banner & Metrics ---
col_head1, col_head2 = st.columns([3, 1])
with col_head1:
    st.title("CloudNexus Solutions Inc.")
    st.markdown("🚀 *Next-Generation Cloud Architecture, Kubernetes Management & DevSecOps Engineering*")
with col_head2:
    st.metric(label="ACTIVE CLUSTER", value=f"{CFG['cluster_name']}", delta=f"Node: {node_name}")

# Metrics Top Bar
m1, m2, m3, m4 = st.columns(4)
m1.metric(label="Open Careers", value=len(jobs_list) if jobs_list else "4 Active")
m2.metric(label="Client SLA", value="99.999%")
m3.metric(label="Cluster Workloads", value=len(tasks_list))
m4.metric(label="API Latency", value=f"{health_data.get('latency_ms', 0)} ms")

st.markdown("---")

# ── Dynamic Environment Debug Panel ─────────────────────────────────
with st.expander(f"🔬 {CFG['env_name']} Debug Panel — Real-time Cluster Info", expanded=False):
    st.markdown(f"""
    <div class="debug-panel">
    🌿 Branch         : {CFG['branch']}<br>
    🏷️  Environment    : {reported_env}<br>
    🖥️  Pod Name       : {pod_name}<br>
    🗂️  Node           : {node_name}<br>
    🔗 Active Backend : {active_backend_url}<br>
    🕐 Render Time    : {build_time}<br>
    📶 API Status     : {health_data.get('status', 'UNKNOWN')}<br>
    ⚠️ Error Message  : {health_data.get('error', 'None')}<br>
    ⚡ API Latency    : {health_data.get('latency_ms', 0)} ms<br>
    📦 Tasks in DB    : {len(tasks_list)}<br>
    💼 Jobs in DB     : {len(jobs_list)}<br>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ==============================================================================
# --- MAIN TABS ---
# ==============================================================================
tab_about, tab_services, tab_careers, tab_ingress, tab_admin = st.tabs([
    "🏢 About Company",
    "💼 Our Services",
    "🚀 Careers & Hiring",
    "🌐 Ingress & AWS ALB Routing",
    "🔐 Internal Admin Portal"
])

# ==============================================================================
# TAB 1: ABOUT COMPANY
# ==============================================================================
with tab_about:
    st.markdown(f"""
    <div class="dev-hero">
        <h2 style="background: {CFG['ribbon_gradient']}; -webkit-background-clip:text; -webkit-text-fill-color:transparent; font-size:1.7rem;">
            Empowering Global Enterprises with Resilient Multi-Cluster Cloud Platforms
        </h2>
        <p style="font-size: 1.05rem; color: {CFG['text_color']}; margin-top: 12px; line-height: 1.7;">
            <strong style="color:{CFG['accent_color']};">CloudNexus Solutions</strong> is a premier DevOps, Cloud Infrastructure, and Site Reliability Engineering firm.
            We design, automate, and manage mission-critical 3-tier architectures across baremetal Kubernetes (Kubeadm),
            AWS (EKS, ALB Ingress), Hybrid Clouds, and automated Declarative CI/CD pipelines.
        </p>
        <br>
        <span class="dev-badge">{CFG['hero_tag']}</span>
        <span class="dev-badge">Branch: {CFG['branch']}</span>
        <span class="dev-badge">Kubeadm</span>
        <span class="dev-badge">K8s v1.29</span>
    </div>
    """, unsafe_allow_html=True)
    
    col_a1, col_a2, col_a3 = st.columns(3)
    with col_a1:
        st.markdown(f"""
        <div class="dev-card">
            <h3 style="color: {CFG['accent_color']};">🎯 Our Mission</h3>
            <p>To eliminate deployment downtime and cloud complexity through automated GitOps pipelines, resilient Ingress architectures, and zero-trust security postures.</p>
        </div>
        """, unsafe_allow_html=True)
    with col_a2:
        st.markdown(f"""
        <div class="dev-card">
            <h3 style="color: {CFG['accent_color']};">⚡ High Availability</h3>
            <p>Our multi-branch delivery topology guarantees seamless zero-downtime rolling updates across Dev, Staging, and Production clusters with automated rollback triggers.</p>
        </div>
        """, unsafe_allow_html=True)
    with col_a3:
        st.markdown(f"""
        <div class="dev-card">
            <h3 style="color: {CFG['accent_color']};">🔒 Enterprise DevSecOps</h3>
            <p>Continuous vulnerability scanning (Trivy), secret rotation, least-privilege RBAC policies, and real-time pod telemetry integrated natively into our delivery lifecycle.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("### 🏆 Core Engineering Highlights")
    ch1, ch2, ch3, ch4 = st.columns(4)
    ch1.info("**Multi-Cluster Isolation**\nSeparate control planes for Dev, Stage & Prod.")
    ch2.info("**Layer 7 Ingress Routing**\nPath & Host-based routing via NGINX & AWS ALB.")
    ch3.info("**Declarative GitOps**\nKustomize overlays managing zero-drift deployments.")
    ch4.info("**Multi-Branch CI/CD**\nAutomated Jenkins pipelines with security gates.")

# ==============================================================================
# TAB 2: OUR SERVICES & INSTANT QUOTE
# ==============================================================================
with tab_services:
    st.markdown("### 🛠️ Enterprise Cloud & Infrastructure Solutions")
    st.write("Explore our specialized managed engineering offerings or request an instant architecture quote below.")
    
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.markdown(f"""
        <div class="dev-card">
            <h3 style="color: {CFG['accent_color']};">☸️ Kubernetes & Kubeadm Architecture</h3>
            <p>Production-grade baremetal and cloud Kubernetes provisioning, Calico CNI networking, MetalLB Layer-2 Load Balancing, and High-Availability etcd clustering.</p>
            <span class="dev-badge">Kubeadm</span>
            <span class="dev-badge">Calico CNI</span>
            <span class="dev-badge">MetalLB</span>
            <span class="dev-badge">EKS</span>
        </div>
        <div class="dev-card">
            <h3 style="color: {CFG['accent_color']};">🚀 CI/CD Pipeline Automation</h3>
            <p>Declarative Jenkins Multi-Branch pipelines, Docker security hardening, automated Trivy scanning, and environment promotion gates (Dev ➡️ Stage ➡️ Prod).</p>
            <span class="dev-badge">Jenkins</span>
            <span class="dev-badge">Docker</span>
            <span class="dev-badge">Trivy</span>
            <span class="dev-badge">GitOps</span>
        </div>
        """, unsafe_allow_html=True)
    with col_s2:
        st.markdown(f"""
        <div class="dev-card">
            <h3 style="color: {CFG['accent_color']};">☁️ AWS Infrastructure & ALB Ingress</h3>
            <p>Cloud architecture design with Terraform IAC, AWS Application Load Balancers, Route53 DNS management, and multi-tier VPC network isolation.</p>
            <span class="dev-badge">Terraform</span>
            <span class="dev-badge">AWS ALB</span>
            <span class="dev-badge">Route53</span>
            <span class="dev-badge">VPC Peering</span>
        </div>
        <div class="dev-card">
            <h3 style="color: {CFG['accent_color']};">📊 SRE & Observability Engineering</h3>
            <p>End-to-end monitoring with Prometheus, Grafana dashboards, automated alerting, log aggregation, and real-time SLA tracking.</p>
            <span class="dev-badge">Prometheus</span>
            <span class="dev-badge">Grafana</span>
            <span class="dev-badge">Loki</span>
            <span class="dev-badge">99.999% SLA</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📝 Request a Consultation / Project Quote")
    
    with st.form("inquiry_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            inq_client = st.text_input("Your Full Name *", placeholder="Ankit Mori")
            inq_email = st.text_input("Work Email *", placeholder="ankit@company.com")
            inq_company = st.text_input("Company / Organization Name *", placeholder="CloudNexus Enterprise Inc.")
        with c2:
            inq_service = st.selectbox("Service Required *", [
                "Kubernetes & Kubeadm Architecture",
                "CI/CD Pipeline Automation (Jenkins/GitOps)",
                "AWS Cloud & ALB Ingress Setup",
                "SRE & 24/7 Observability Setup",
                "Complete 3-Tier Multi-Cluster Modernization"
            ])
            inq_budget = st.selectbox("Estimated Budget Range", [
                "$5,000 - $15,000",
                "$15,000 - $50,000",
                "$50,000 - $150,000",
                "Enterprise Custom Quote"
            ])
            inq_msg = st.text_area("Project Scope & Requirements *", placeholder="Describe your current infrastructure, timeline, and deliverables...")
            
        submit_quote = st.form_submit_button("📩 Submit Architecture Inquiry")
        if submit_quote:
            if not inq_client or not inq_email or not inq_msg:
                st.error("⚠️ Please fill in all required fields marked with *.")
            else:
                payload = {
                    "client_name": inq_client,
                    "email": inq_email,
                    "company_name": inq_company,
                    "service_required": inq_service,
                    "budget": inq_budget,
                    "message": inq_msg
                }
                if submit_inquiry(payload):
                    st.success("🎉 Thank you! Your inquiry has been submitted successfully to CloudNexus Architecture Team.")
                else:
                    st.error("Failed to connect to backend service. Please check API readiness.")

# ==============================================================================
# TAB 3: CAREERS & HIRING PORTAL
# ==============================================================================
with tab_careers:
    st.markdown("### 🚀 Join Our Engineering Team")
    st.write("We are actively hiring top-tier DevOps, Cloud, and Kubernetes talent. Apply directly below.")
    
    if not jobs_list:
        st.info("ℹ️ No active job openings posted currently. Check back soon!")
    else:
        for job in jobs_list:
            skills_html = " ".join([f'<span class="dev-badge">{s}</span>' for s in job.get("skills", [])])
            st.markdown(f"""
            <div class="dev-card">
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                    <div>
                        <h3 style="color: {CFG['accent_color']}; margin-bottom: 4px;">{job.get('title')}</h3>
                        <p style="margin: 0; color: #94a3b8; font-size: 0.9rem;">
                            🏢 <strong>Department:</strong> {job.get('department')} &nbsp;|&nbsp; 
                            📍 <strong>Location:</strong> {job.get('location')} &nbsp;|&nbsp; 
                            💼 <strong>Experience:</strong> {job.get('experience')}
                        </p>
                    </div>
                    <div style="text-align: right;">
                        <span style="font-size: 1.1rem; font-weight: 700; color: #10b981;">{job.get('salary_range')}</span>
                    </div>
                </div>
                <p style="margin-top: 12px; color: {CFG['text_color']}; font-size: 0.95rem;">{job.get('description')}</p>
                <div style="margin-top: 10px;">{skills_html}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📄 Submit Your Job Application")
    with st.form("application_form", clear_on_submit=True):
        col_j1, col_j2 = st.columns(2)
        with col_j1:
            app_name = st.text_input("Candidate Full Name *", placeholder="Priya Sharma")
            app_email = st.text_input("Candidate Email *", placeholder="priya.sharma@gmail.com")
            app_phone = st.text_input("Phone Number", placeholder="+91 9876543210")
            
            job_options = {j["id"]: f"{j['title']} ({j['department']})" for j in jobs_list} if jobs_list else {0: "General DevOps Application"}
            selected_job_id = st.selectbox("Select Role to Apply *", options=list(job_options.keys()), format_func=lambda x: job_options[x])
            selected_job_title = job_options[selected_job_id]

        with col_j2:
            app_exp = st.selectbox("Relevant Experience *", ["1-3 Years", "3-5 Years", "5-8 Years", "8+ Years (Lead / Principal)"])
            app_portfolio = st.text_input("GitHub / LinkedIn / Portfolio URL *", placeholder="https://github.com/your-username")
            app_note = st.text_area("Cover Note / Summary of DevOps Achievements *", placeholder="Describe your experience with Kubeadm, Jenkins Multi-Branch pipelines, and Docker...")
            
        submit_app = st.form_submit_button("🚀 Submit Application")
        if submit_app:
            if not app_name or not app_email or not app_portfolio:
                st.error("⚠️ Please fill in all required fields (Name, Email, Portfolio URL).")
            else:
                payload = {
                    "job_id": selected_job_id if selected_job_id != 0 else None,
                    "job_title": selected_job_title,
                    "candidate_name": app_name,
                    "email": app_email,
                    "phone": app_phone,
                    "experience_years": app_exp,
                    "portfolio_url": app_portfolio,
                    "cover_note": app_note
                }
                if submit_application(payload):
                    st.success("🎉 Application submitted successfully! Our recruiting team will review your profile.")
                else:
                    st.error("Failed to connect to backend service. Please check API status.")

# ==============================================================================
# TAB 4: INGRESS & AWS ALB ROUTING MAP
# ==============================================================================
with tab_ingress:
    st.markdown("### 🌐 Application Ingress & AWS ALB Routing Architecture")
    st.write("This 3-tier application uses path-based and host-based routing across NGINX Ingress and AWS ALB.")
    
    col_i1, col_i2 = st.columns(2)
    with col_i1:
        st.markdown(f"""
        <div class="path-card">
            <h4 style="color: {CFG['accent_color']}; margin: 0 0 6px 0;">🌍 Route <code>/</code> ➡️ Frontend Service</h4>
            <p style="margin: 0; font-size: 0.9rem;">Renders this dynamic Streamlit User Interface. Directs to <code>frontend-service:80</code> (Port 8501 inside container).</p>
        </div>
        <div class="path-card">
            <h4 style="color: {CFG['accent_color']}; margin: 0 0 6px 0;">💼 Route <code>/api/jobs</code> ➡️ Careers API</h4>
            <p style="margin: 0; font-size: 0.9rem;">Fetches active job listings from PostgreSQL. Directs to <code>backend-service:5000</code>.</p>
        </div>
        <div class="path-card">
            <h4 style="color: {CFG['accent_color']}; margin: 0 0 6px 0;">📩 Route <code>/api/inquiries</code> ➡️ Quotes API</h4>
            <p style="margin: 0; font-size: 0.9rem;">Accepts enterprise architecture quotes and persists leads into PostgreSQL database.</p>
        </div>
        """, unsafe_allow_html=True)
    with col_i2:
        st.markdown(f"""
        <div class="path-card">
            <h4 style="color: {CFG['accent_color']}; margin: 0 0 6px 0;">📄 Route <code>/api/applications</code> ➡️ Candidate Portal</h4>
            <p style="margin: 0; font-size: 0.9rem;">Receives candidate applications and resumes with relational job ID foreign keys.</p>
        </div>
        <div class="path-card">
            <h4 style="color: {CFG['accent_color']}; margin: 0 0 6px 0;">⚡ Route <code>/ready</code> & <code>/healthz</code> ➡️ Probes</h4>
            <p style="margin: 0; font-size: 0.9rem;">Kubernetes Liveness and Readiness probes to guarantee zero-downtime rolling deploys.</p>
        </div>
        <div class="path-card">
            <h4 style="color: {CFG['accent_color']}; margin: 0 0 6px 0;">🔐 Route <code>/api/admin/*</code> ➡️ Protected APIs</h4>
            <p style="margin: 0; font-size: 0.9rem;">Role-based admin access protected via <code>x-admin-token</code> header verification.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("#### 🧭 Ingress Host Routing Table")
    ingress_df = pd.DataFrame([
        {"Environment": "DEV", "Host Header": "dev.3tier.local", "Target Service": "frontend-service.dev.svc.cluster.local:80", "Status": "Active"},
        {"Environment": "STAGE", "Host Header": "stage.3tier.local", "Target Service": "frontend-service.stage.svc.cluster.local:80", "Status": "Active"},
        {"Environment": "PROD", "Host Header": "prod.3tier.local", "Target Service": "frontend-service.prod.svc.cluster.local:80", "Status": "Active"}
    ])
    st.dataframe(ingress_df, use_container_width=True, hide_index=True)

# ==============================================================================
# TAB 5: INTERNAL ADMIN PORTAL (SECURE)
# ==============================================================================
with tab_admin:
    st.markdown("### 🔐 CloudNexus Internal Management Portal")
    
    if not st.session_state["is_admin_authenticated"]:
        st.markdown("""
        <div class="auth-lock-card">
            <div style="font-size: 3rem; margin-bottom: 12px;">🛡️</div>
            <h3 style="color: #ffffff; margin-bottom: 6px;">Admin Authentication Required</h3>
            <p style="color: #94a3b8; font-size: 0.92rem;">Please enter your administrative access token to view submitted candidate applications and client quote leads.</p>
        </div>
        """, unsafe_allow_html=True)
        
        col_c1, col_c2, col_c3 = st.columns([1, 2, 1])
        with col_c2:
            admin_pass = st.text_input("Enter Admin Token", type="password", placeholder="Default token: devops-admin-secret-2026")
            if st.button("🔓 Authenticate & Unlock Portal", use_container_width=True):
                if admin_pass in ["devops-admin-secret-2026", "cloudnexus-admin", "admin"]:
                    st.session_state["is_admin_authenticated"] = True
                    st.session_state["admin_token"] = admin_pass
                    st.success("Authenticated successfully!")
                    st.rerun()
                else:
                    st.error("Invalid token. Please enter the correct administrative secret.")
    else:
        st.markdown(f"**Status:** 🔓 Logged in as `CloudNexus Lead Administrator` (Environment: `{CFG['env_name']}`)")
        
        subtab1, subtab2, subtab3 = st.tabs(["📄 Job Applications Received", "📩 Client Quote Inquiries", "➕ Schedule Cluster Workload"])
        
        with subtab1:
            st.markdown("#### 📋 Candidate Job Applications")
            applications = fetch_admin_data("applications", st.session_state["admin_token"])
            if not applications:
                st.info("No job applications received yet in this database.")
            else:
                for app in applications:
                    st.markdown(f"""
                    <div class="dev-card">
                        <div style="display: flex; justify-content: space-between;">
                            <h4 style="color: {CFG['accent_color']}; margin: 0;">👤 {app.get('candidate_name')} - <span style="color: #ffffff;">{app.get('job_title')}</span></h4>
                            <span class="dev-badge">{app.get('status', 'Under Review')}</span>
                        </div>
                        <p style="margin: 6px 0;">📧 <strong>Email:</strong> {app.get('email')} &nbsp;|&nbsp; 📞 <strong>Phone:</strong> {app.get('phone', 'N/A')} &nbsp;|&nbsp; 💼 <strong>Exp:</strong> {app.get('experience_years')}</p>
                        <p style="margin: 4px 0;">🌐 <strong>Portfolio:</strong> <a href="{app.get('portfolio_url')}" target="_blank" style="color:{CFG['accent_color']};">{app.get('portfolio_url')}</a></p>
                        <p style="color: {CFG['text_color']}; background: {CFG['bg_color']}; padding: 8px 12px; border-radius: 6px; border: 1px solid {CFG['card_border']};">{app.get('cover_note')}</p>
                        <small style="color: #64748b;">Submitted at: {str(app.get('created_at', ''))[:19]}</small>
                    </div>
                    """, unsafe_allow_html=True)
                    
        with subtab2:
            st.markdown("#### 💼 Client Inquiries & Architecture Quotes")
            inquiries = fetch_admin_data("inquiries", st.session_state["admin_token"])
            if not inquiries:
                st.info("No customer inquiries logged yet in this database.")
            else:
                for inq in inquiries:
                    st.markdown(f"""
                    <div class="dev-card">
                        <div style="display: flex; justify-content: space-between;">
                            <h4 style="color: {CFG['accent_color']}; margin: 0;">🏢 {inq.get('company_name', 'Client')} - <span style="color: #ffffff;">{inq.get('service_required')}</span></h4>
                            <span style="color: #f59e0b; font-weight: 600;">{inq.get('budget')}</span>
                        </div>
                        <p style="margin: 6px 0;">👤 <strong>Contact:</strong> {inq.get('client_name')} (📧 {inq.get('email')})</p>
                        <p style="color: {CFG['text_color']}; background: {CFG['bg_color']}; padding: 8px 12px; border-radius: 6px; border: 1px solid {CFG['card_border']};">{inq.get('message')}</p>
                        <small style="color: #64748b;">Received on: {str(inq.get('created_at', ''))[:19]}</small>
                    </div>
                    """, unsafe_allow_html=True)
                    
        with subtab3:
            st.markdown("#### 📋 Active Infrastructure Workloads")
            with st.form("admin_task_form", clear_on_submit=True):
                t_title = st.text_input("Workload / Maintenance Title", placeholder="e.g., Renew Ingress TLS Certificate")
                t_desc = st.text_area("Details", placeholder="Operational steps...")
                t_sub = st.form_submit_button("➕ Schedule Cluster Task")
                if t_sub and t_title.strip():
                    if create_task(t_title, t_desc, "High", "Pending"):
                        st.success("Task scheduled!")
                        st.cache_data.clear()
                        st.rerun()

st.markdown("---")
st.caption(CFG["footer_text"])
