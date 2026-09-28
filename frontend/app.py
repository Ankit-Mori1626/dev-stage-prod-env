import streamlit as st
import requests
import os
import json
import time
import pandas as pd
from datetime import datetime

# --- Configure Streamlit Page ---
st.set_page_config(
    page_title="CloudNexus Enterprise | 3-Tier Cloud Platform",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Environment & API Configuration ---
BACKEND_URL = os.getenv("BACKEND_URL", "http://backend-service:5000").rstrip("/")
TASKS_API = f"{BACKEND_URL}/api/tasks"
JOBS_API = f"{BACKEND_URL}/api/jobs"
APPLICATIONS_API = f"{BACKEND_URL}/api/applications"
INQUIRIES_API = f"{BACKEND_URL}/api/inquiries"
HEALTH_API = f"{BACKEND_URL}/ready"
LIVENESS_API = f"{BACKEND_URL}/healthz"
METRICS_API = f"{BACKEND_URL}/metrics"
INGRESS_INFO_API = f"{BACKEND_URL}/api/ingress-info"

# Session State Initialization for Admin Authentication
if "is_admin_authenticated" not in st.session_state:
    st.session_state["is_admin_authenticated"] = False
if "admin_token" not in st.session_state:
    st.session_state["admin_token"] = ""

# --- Custom Styling & Aesthetics (Crisp High-Contrast Dark SaaS Theme) ---
st.markdown("""
    <style>
    /* Main Background & Base Typography */
    .stApp {
        background-color: #0b0f19 !important;
        color: #e2e8f0 !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Headers & Text Elements */
    h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em;
    }
    p, span, label {
        color: #cbd5e1 !important;
    }
    .stCaption, small {
        color: #94a3b8 !important;
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #0f172a !important;
        border-right: 1px solid #1e293b !important;
    }
    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3 {
        color: #ffffff !important;
    }
    
    /* Metrics Top Bar */
    [data-testid="stMetricValue"] {
        color: #38bdf8 !important;
        font-weight: 800 !important;
        font-size: 1.6rem !important;
    }
    [data-testid="stMetricLabel"] {
        color: #94a3b8 !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        font-size: 0.75rem !important;
        letter-spacing: 0.05em;
    }
    
    /* Cards & Containers */
    .corporate-card {
        background: #1e293b !important;
        border: 1px solid #334155 !important;
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 16px;
        box-shadow: 0 4px 12px -1px rgba(0, 0, 0, 0.25);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .corporate-card:hover {
        border-color: #3b82f6 !important;
        transform: translateY(-2px);
    }
    .auth-lock-card {
        background: #1e293b !important;
        border: 2px solid #ef4444 !important;
        border-radius: 16px;
        padding: 32px;
        text-align: center;
        box-shadow: 0 8px 24px rgba(239, 68, 68, 0.15);
        max-width: 600px;
        margin: 20px auto;
    }
    .service-badge {
        display: inline-block;
        background: rgba(59, 130, 246, 0.15);
        color: #60a5fa;
        border: 1px solid rgba(59, 130, 246, 0.3);
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-right: 6px;
        margin-bottom: 6px;
    }
    .hero-banner {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155;
        border-radius: 16px;
        padding: 36px;
        margin-bottom: 24px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
    }
    .path-card {
        background: #1e293b !important;
        border: 1px solid #334155 !important;
        border-left: 4px solid #3b82f6 !important;
        padding: 16px;
        border-radius: 8px;
        margin-bottom: 12px;
    }
    .path-card code {
        background: #0f172a !important;
        color: #38bdf8 !important;
        padding: 2px 6px;
        border-radius: 4px;
        border: 1px solid #334155;
    }
    
    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #0f172a;
        padding: 8px;
        border-radius: 10px;
        border: 1px solid #1e293b;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #1e293b !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
        padding: 10px 20px !important;
        color: #cbd5e1 !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        transition: all 0.2s ease;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #334155 !important;
        color: #ffffff !important;
        border-color: #60a5fa !important;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #2563eb, #1d4ed8) !important;
        color: #ffffff !important;
        border-color: #3b82f6 !important;
        box-shadow: 0 4px 14px rgba(37, 99, 235, 0.4) !important;
    }
    
    /* Form Inputs & Selects */
    .stTextInput input, .stTextArea textarea, .stSelectbox select {
        background-color: #1e293b !important;
        color: #ffffff !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
    }
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2) !important;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #2563eb, #1d4ed8) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 8px 16px !important;
        transition: all 0.2s ease;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #1d4ed8, #1e40af) !important;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.4) !important;
        transform: translateY(-1px);
    }
    </style>
""", unsafe_allow_html=True)

# --- Backend Communication Helpers ---
@st.cache_data(ttl=3)
def get_backend_health():
    try:
        t0 = time.time()
        res = requests.get(HEALTH_API, timeout=3)
        latency = round((time.time() - t0) * 1000, 2)
        if res.status_code == 200:
            data = res.json()
            data["latency_ms"] = latency
            return data
        return {"status": "UNHEALTHY", "error": f"HTTP {res.status_code}", "latency_ms": latency}
    except Exception as e:
        return {"status": "OFFLINE", "error": str(e), "latency_ms": 0}

@st.cache_data(ttl=2)
def fetch_jobs():
    try:
        res = requests.get(JOBS_API, timeout=4)
        if res.status_code == 200:
            return res.json().get("data", [])
        return []
    except Exception:
        return []

# Authenticated APIs for Internal Admin Portal
def fetch_applications(admin_key):
    try:
        headers = {"x-admin-key": admin_key}
        res = requests.get(APPLICATIONS_API, headers=headers, timeout=4)
        if res.status_code == 200:
            return {"success": True, "data": res.json().get("data", [])}
        elif res.status_code in [401, 403]:
            return {"success": False, "error": "Invalid Admin Credentials or Session Expired."}
        return {"success": False, "error": f"HTTP {res.status_code}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def fetch_inquiries(admin_key):
    try:
        headers = {"x-admin-key": admin_key}
        res = requests.get(INQUIRIES_API, headers=headers, timeout=4)
        if res.status_code == 200:
            return {"success": True, "data": res.json().get("data", [])}
        elif res.status_code in [401, 403]:
            return {"success": False, "error": "Invalid Admin Credentials or Session Expired."}
        return {"success": False, "error": f"HTTP {res.status_code}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@st.cache_data(ttl=2)
def fetch_tasks():
    try:
        res = requests.get(TASKS_API, timeout=4)
        if res.status_code == 200:
            return res.json()
        return {"success": False, "data": [], "error": f"HTTP {res.status_code}"}
    except Exception as e:
        return {"success": False, "data": [], "error": str(e)}

def submit_job_application(job_id, job_title, name, email, phone, experience, portfolio, cover_note):
    try:
        payload = {
            "job_id": job_id,
            "job_title": job_title,
            "candidate_name": name,
            "email": email,
            "phone": phone,
            "experience_years": experience,
            "portfolio_url": portfolio,
            "cover_note": cover_note
        }
        res = requests.post(APPLICATIONS_API, json=payload, timeout=5)
        return res.status_code in [200, 201]
    except Exception as e:
        st.error(f"Application submission failed: {e}")
        return False

def submit_service_inquiry(name, email, company, service, budget, message):
    try:
        payload = {
            "client_name": name,
            "email": email,
            "company_name": company,
            "service_required": service,
            "budget": budget,
            "message": message
        }
        res = requests.post(INQUIRIES_API, json=payload, timeout=5)
        return res.status_code in [200, 201]
    except Exception as e:
        st.error(f"Inquiry submission failed: {e}")
        return False

def create_task(title, description, priority, status):
    try:
        payload = {"title": title, "description": description, "priority": priority, "status": status}
        res = requests.post(TASKS_API, json=payload, timeout=4)
        return res.status_code in [200, 201]
    except Exception as e:
        st.error(f"Error creating task: {e}")
        return False

# --- Fetch Initial Data ---
health_data = get_backend_health()
tasks_response = fetch_tasks()
tasks_list = tasks_response.get("data", [])
jobs_list = fetch_jobs()
env_name = tasks_response.get("environment", health_data.get("environment", "DEV")).upper()
pod_name = tasks_response.get("pod_name", health_data.get("pod", "local-pod"))
node_name = tasks_response.get("node_name", "local-node")

# --- Sidebar ---
with st.sidebar:
    st.title("🏢 CloudNexus Hub")
    st.caption("Enterprise Cloud & Multi-Cluster Platform")
    st.markdown("---")
    
    st.markdown(f"**Cluster Environment:** `{env_name}`")
    if health_data.get("status") == "READY":
        st.success(f"🟢 **API & DB**: READY ({health_data.get('latency_ms')} ms)")
    else:
        st.error("🔴 **Backend API**: Offline")
        
    st.markdown("---")
    st.subheader("🛡️ Security & Ingress Model")
    st.markdown("""
    - **Public Ingress Routes**:
      - `/` ➡️ Web UI
      - `/api/jobs` ➡️ Active Listings
      - `/api/inquiries` ➡️ POST Quote
      - `/api/applications` ➡️ POST Apply
    - **Protected Internal Routes**:
      - `GET /api/applications` 🔒 *(Admin Auth)*
      - `GET /api/inquiries` 🔒 *(Admin Auth)*
    """)
    
    st.markdown("---")
    if st.session_state["is_admin_authenticated"]:
        st.success("🔓 **Admin Mode**: Authenticated")
        if st.button("🚪 Logout Admin Session", use_container_width=True):
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
    st.metric(label="ACTIVE CLUSTER", value=f"{env_name}", delta=f"Node: {node_name}")

# Metrics Top Bar
m1, m2, m3, m4 = st.columns(4)
m1.metric(label="Open Careers", value=len(jobs_list) if jobs_list else "4 Active")
m2.metric(label="Client SLA", value="99.999%")
m3.metric(label="Cluster Workloads", value=len(tasks_list))
m4.metric(label="API Latency", value=f"{health_data.get('latency_ms', 0)} ms")

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
    st.markdown("""
    <div class="hero-banner">
        <h2>Empowering Global Enterprises with Resilient Multi-Cluster Cloud Platforms</h2>
        <p style="font-size: 1.1rem; color: #cbd5e1; margin-top: 12px; line-height: 1.6;">
            <strong>CloudNexus Solutions</strong> is a premier DevOps, Cloud Infrastructure, and Site Reliability Engineering firm. 
            We design, automate, and manage mission-critical 3-tier architectures across baremetal Kubernetes (Kubeadm), 
            AWS (EKS, ALB Ingress), Hybrid Clouds, and automated Declarative CI/CD pipelines.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col_a1, col_a2, col_a3 = st.columns(3)
    with col_a1:
        st.markdown("""
        <div class="corporate-card">
            <h3 style="color: #60a5fa;">🎯 Our Mission</h3>
            <p>To eliminate deployment downtime and cloud complexity through automated GitOps pipelines, resilient Ingress architectures, and zero-trust security postures.</p>
        </div>
        """, unsafe_allow_html=True)
    with col_a2:
        st.markdown("""
        <div class="corporate-card">
            <h3 style="color: #38bdf8;">🌐 Global Multi-Cluster Scale</h3>
            <p>Operating across 12 global cloud regions and on-prem data centers with automated failover, MetalLB load balancing, and AWS Application Load Balancers.</p>
        </div>
        """, unsafe_allow_html=True)
    with col_a3:
        st.markdown("""
        <div class="corporate-card">
            <h3 style="color: #34d399;">🛡️ Enterprise Security</h3>
            <p>End-to-end vulnerability scanning with Trivy, Kubernetes NetworkPolicies, automated TLS termination, and role-based access controls.</p>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("### 🏆 Company Core Milestones & Stats")
    s1, s2, s3, s4 = st.columns(4)
    s1.metric("Production Clusters", "500+", "Multi-region")
    s2.metric("Enterprise Clients", "150+", "Fortune 500 & Startups")
    s3.metric("Deployments / Day", "2,400+", "Zero Downtime")
    s4.metric("Security Compliance", "SOC2 & ISO", "Certified")

# ==============================================================================
# TAB 2: OUR SERVICES
# ==============================================================================
with tab_services:
    st.subheader("💼 Enterprise Cloud & DevOps Solutions")
    st.caption("We offer comprehensive engineering and managed services tailored for high-scale enterprise systems.")
    
    col_s1, col_s2 = st.columns(2, gap="large")
    
    with col_s1:
        st.markdown("""
        <div class="corporate-card">
            <h3 style="color: #60a5fa;">☸️ 1. Kubernetes Multi-Cluster Engineering</h3>
            <p>Full lifecycle design for baremetal Kubeadm, EKS, and GKE. Production setup of Calico CNI, MetalLB, CoreDNS, and stateful PostgreSQL clusters.</p>
            <div style="margin-top: 10px;">
                <span class="service-badge">Kubeadm</span>
                <span class="service-badge">Calico CNI</span>
                <span class="service-badge">MetalLB</span>
                <span class="service-badge">Helm</span>
            </div>
        </div>
        
        <div class="corporate-card">
            <h3 style="color: #38bdf8;">🌐 2. Layer-7 Ingress & AWS ALB Solutions</h3>
            <p>Advanced routing, SSL/TLS termination, path-based routing, target group bindings, rate limiting, and web application firewalls (WAF).</p>
            <div style="margin-top: 10px;">
                <span class="service-badge">NGINX Ingress</span>
                <span class="service-badge">AWS ALB Controller</span>
                <span class="service-badge">Cert-Manager</span>
                <span class="service-badge">Let's Encrypt</span>
            </div>
        </div>
        
        <div class="corporate-card">
            <h3 style="color: #a78bfa;">🔄 3. Multi-Branch CI/CD & GitOps Automation</h3>
            <p>Declarative Jenkins Multi-Branch pipelines, Docker security hardening, automated Trivy scanning, and environment promotion gates (Dev ➡️ Stage ➡️ Prod).</p>
            <div style="margin-top: 10px;">
                <span class="service-badge">Jenkins Declarative</span>
                <span class="service-badge">Docker</span>
                <span class="service-badge">Trivy</span>
                <span class="service-badge">Kustomize</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    with col_s2:
        st.markdown("""
        <div class="corporate-card">
            <h3 style="color: #34d399;">📈 4. 24x7 SRE & Observability Platforms</h3>
            <p>Full-stack monitoring with Prometheus metric scraping, Grafana dashboards, Kubernetes Probes (Liveness & Readiness), and automated incident alerts.</p>
            <div style="margin-top: 10px;">
                <span class="service-badge">Prometheus</span>
                <span class="service-badge">Grafana</span>
                <span class="service-badge">Alertmanager</span>
                <span class="service-badge">Probes</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Interactive Service Quote Request Form
        st.markdown("### 📩 Request a Consultation / Project Quote")
        with st.form("inquiry_form", clear_on_submit=True):
            inq_name = st.text_input("Your Name *", placeholder="e.g., Alex Johnson")
            inq_email = st.text_input("Work Email *", placeholder="alex@company.com")
            
            c_comp, c_budget = st.columns(2)
            with c_comp:
                inq_company = st.text_input("Company Name", placeholder="Acme Corp")
            with c_budget:
                inq_budget = st.selectbox("Estimated Budget", ["< $10,000", "$10,000 - $50,000", "$50,000 - $150,000", "$150,000+"])
                
            inq_service = st.selectbox("Select Service Required *", [
                "Kubernetes Multi-Cluster & Ingress Setup",
                "AWS ALB & Cloud Migration",
                "DevOps & Jenkins CI/CD Automation",
                "SRE & Observability Framework",
                "End-to-End Enterprise Architecture"
            ])
            
            inq_message = st.text_area("Project Scope & Requirements *", placeholder="Describe your architecture requirements...")
            
            inq_submit = st.form_submit_button("🚀 Submit Consultation Request", use_container_width=True)
            if inq_submit:
                if not inq_name or not inq_email or not inq_message:
                    st.warning("Please fill all required fields (*).")
                else:
                    if submit_service_inquiry(inq_name, inq_email, inq_company, inq_service, inq_budget, inq_message):
                        st.success("Thank you! Your request has been securely submitted to our Client Success team.")
                        st.cache_data.clear()
                        st.rerun()

# ==============================================================================
# TAB 3: CAREERS & HIRING
# ==============================================================================
with tab_careers:
    st.subheader("🚀 Careers at CloudNexus")
    st.markdown("Join our globally distributed engineering team building high-performance Kubernetes, Cloud, and SRE platforms.")
    
    col_jobs, col_apply = st.columns([3, 2], gap="large")
    
    with col_jobs:
        st.markdown("### 💼 Open Engineering Positions")
        if not jobs_list:
            st.info("Loading open positions from database...")
        else:
            for job in jobs_list:
                with st.container():
                    st.markdown(f"""
                    <div class="corporate-card">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <h3 style="color: #60a5fa; margin: 0;">{job.get('title')}</h3>
                            <span style="background: #0f172a; padding: 4px 10px; border-radius: 6px; font-weight: 600; color: #38bdf8; border: 1px solid #334155;">{job.get('salary_range', '')}</span>
                        </div>
                        <p style="margin: 8px 0; color: #94a3b8;">📍 <strong>Location:</strong> {job.get('location')} | 🏢 <strong>Dept:</strong> {job.get('department')} | ⏳ <strong>Exp:</strong> {job.get('experience')}</p>
                        <p style="color: #cbd5e1; margin-bottom: 12px;">{job.get('description')}</p>
                        <div>
                            {' '.join([f'<span class="service-badge">{skill}</span>' for skill in job.get('skills', [])])}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
    with col_apply:
        st.markdown("### 📝 Apply for a Position")
        st.caption("🔒 Candidate submissions are confidential and stored securely in PostgreSQL.")
        
        job_titles = [j.get("title") for j in jobs_list] if jobs_list else ["Senior DevOps Engineer"]
        
        with st.form("job_application_form", clear_on_submit=True):
            selected_job_title = st.selectbox("Select Position Applying For *", job_titles)
            cand_name = st.text_input("Full Name *", placeholder="John Doe")
            cand_email = st.text_input("Email Address *", placeholder="john@example.com")
            
            c_p, c_exp = st.columns(2)
            with c_p:
                cand_phone = st.text_input("Phone Number", placeholder="+91 9876543210")
            with c_exp:
                cand_exp = st.selectbox("Years of Experience", ["1-3 Years", "3-5 Years", "5-8 Years", "8+ Years"])
                
            cand_portfolio = st.text_input("GitHub / LinkedIn URL", placeholder="https://github.com/yourhandle")
            cand_notes = st.text_area("Why are you a good fit? (Cover Note)", placeholder="Tell us about your Kubernetes, DevOps or Cloud projects...")
            
            app_submit = st.form_submit_button("📤 Submit Confidential Application", use_container_width=True)
            if app_submit:
                if not cand_name or not cand_email:
                    st.warning("Please provide your Name and Email.")
                else:
                    selected_job_obj = next((j for j in jobs_list if j.get("title") == selected_job_title), None)
                    job_id = selected_job_obj.get("id") if selected_job_obj else None
                    if submit_job_application(job_id, selected_job_title, cand_name, cand_email, cand_phone, cand_exp, cand_portfolio, cand_notes):
                        st.success("🎉 Application submitted successfully! Our Talent Acquisition team will review your application confidentially.")
                        st.cache_data.clear()
                        st.rerun()

# ==============================================================================
# TAB 4: INGRESS & AWS ALB ROUTING
# ==============================================================================
with tab_ingress:
    st.subheader("🌐 Kubernetes Ingress & AWS ALB Routing Architecture")
    st.markdown("""
    Ingress controllers expose HTTP/HTTPS routes from outside the cluster to services within the cluster.
    Below is how our corporate platform routes traffic across tiers and endpoints.
    """)
    
    col_p1, col_p2, col_p3 = st.columns(3)
    with col_p1:
        st.markdown("""
        <div class="path-card">
            <h4>🌐 Path: <code>/</code></h4>
            <p><strong>Target:</strong> <code>frontend-service:80</code></p>
            <p><strong>Service:</strong> Corporate Web Application UI</p>
        </div>
        """, unsafe_allow_html=True)
    with col_p2:
        st.markdown("""
        <div class="path-card">
            <h4>⚙️ Path: <code>/api/*</code></h4>
            <p><strong>Target:</strong> <code>backend-service:5000</code></p>
            <p><strong>Service:</strong> Public Careers & Lead Submissions</p>
        </div>
        """, unsafe_allow_html=True)
    with col_p3:
        st.markdown("""
        <div class="path-card">
            <h4>🛡️ Protected Admin APIs</h4>
            <p><strong>Target:</strong> <code>GET /api/applications</code></p>
            <p><strong>Security:</strong> Header Token & Ingress Policy</p>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("---")
    
    # Live Route Tester
    st.subheader("🧪 Live Ingress Route & Header Inspector")
    c_test_select, c_test_action = st.columns([3, 1])
    with c_test_select:
        test_endpoint = st.selectbox("Select Endpoint to Test", [
            "/api/ingress-info (Header & Ingress Inspector)",
            "/api/jobs (Active Job Openings API)",
            "/api/tasks (Public Telemetry Workloads)",
            "/ready (K8s Readiness Probe)",
            "/healthz (K8s Liveness Probe)",
            "/metrics (Prometheus Metric Scrape)",
            "/api/applications (Protected: Without Auth Token -> 401)",
            "/api/inquiries (Protected: Without Auth Token -> 401)"
        ])
    with c_test_action:
        st.write("")
        st.write("")
        trigger_test = st.button("🚀 Send Test Request", use_container_width=True)
        
    endpoint_path = test_endpoint.split(" ")[0]
    target_url = f"{BACKEND_URL}{endpoint_path}"
    st.code(f"curl -X GET {target_url}", language="bash")
    
    try:
        t_start = time.time()
        resp = requests.get(target_url, timeout=4)
        t_elapsed = round((time.time() - t_start) * 1000, 2)
        
        res_c1, res_c2, res_c3 = st.columns(3)
        res_c1.metric("HTTP Status", f"{resp.status_code} {'OK' if resp.status_code == 200 else ('AUTH REQUIRED' if resp.status_code in [401, 403] else 'ERR')}")
        res_c2.metric("Response Time", f"{t_elapsed} ms")
        res_c3.metric("Payload Size", f"{len(resp.content)} bytes")
        
        st.markdown("#### 📥 Response Payload:")
        try:
            json_data = resp.json()
            st.json(json_data)
            
            if endpoint_path == "/api/ingress-info":
                st.markdown("#### 🛡️ Ingress Header Analysis:")
                headers_dict = json_data.get("headers", {})
                df_headers = pd.DataFrame([{"Header Name": k, "Received Value": str(v)} for k, v in headers_dict.items()])
                st.dataframe(df_headers, use_container_width=True)
                st.info(f"🔎 **Detected Routing Layer**: `{json_data.get('ingress_type_detected', 'Direct Access')}`")
        except Exception:
            st.text(resp.text[:1000])
    except Exception as e:
        st.error(f"Failed to reach endpoint {target_url}: {e}")

# ==============================================================================
# TAB 5: INTERNAL ADMIN & TALENT PORTAL (AUTHENTICATED & RESTRICTED)
# ==============================================================================
with tab_admin:
    st.subheader("🔐 Internal Admin & Talent Operations Portal")
    st.markdown("Confidential area strictly restricted to authorized Corporate Administrators, HR Recruiters, and DevOps Engineers.")
    
    # Check if admin is authenticated
    if not st.session_state["is_admin_authenticated"]:
        st.markdown("""
        <div class="auth-lock-card">
            <h2 style="color: #ef4444; margin-top: 0;">🔒 Restricted Access Gateway</h2>
            <p style="color: #cbd5e1;">Candidate resumes, personal contact details, and client project inquiries are protected under data privacy standards.</p>
        </div>
        """, unsafe_allow_html=True)
        
        col_auth_center = st.columns([1, 2, 1])[1]
        with col_auth_center:
            with st.form("admin_login_form"):
                admin_key_input = st.text_input("Enter Admin Security Passkey *", type="password", placeholder="Enter admin key (Default: admin-cloudnexus-sec2026)")
                login_btn = st.form_submit_button("🔓 Authenticate & Unlock Portal", use_container_width=True)
                
                if login_btn:
                    if admin_key_input.strip() == "admin-cloudnexus-sec2026":
                        st.session_state["is_admin_authenticated"] = True
                        st.session_state["admin_token"] = admin_key_input.strip()
                        st.success("✅ Authentication successful!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid Admin Security Passkey! Access Denied.")
    else:
        # Authenticated Admin Dashboard
        admin_auth_col1, admin_auth_col2 = st.columns([3, 1])
        with admin_auth_col1:
            st.success("🔓 **Authenticated Session Active** | Role: `Enterprise Administrator`")
        with admin_auth_col2:
            if st.button("🚪 Logout Admin", key="logout_tab_btn", use_container_width=True):
                st.session_state["is_admin_authenticated"] = False
                st.session_state["admin_token"] = ""
                st.rerun()
                
        subtab1, subtab2, subtab3 = st.tabs([
            "📝 Confidential Candidate Resumes",
            "📩 Private Client Inquiries & Leads",
            "⚡ Infrastructure Workloads"
        ])
        
        with subtab1:
            res_apps = fetch_applications(st.session_state["admin_token"])
            if not res_apps.get("success"):
                st.error(f"Failed to fetch candidate records: {res_apps.get('error')}")
            else:
                apps_data = res_apps.get("data", [])
                if not apps_data:
                    st.info("No applications received yet.")
                else:
                    st.markdown(f"**Total Applications Received:** `{len(apps_data)}`")
                    for a in apps_data:
                        with st.container():
                            st.markdown(f"""
                            <div class="corporate-card">
                                <div style="display: flex; justify-content: space-between;">
                                    <h4 style="color: #38bdf8; margin: 0;">👤 {a.get('candidate_name')} - <span style="color: #ffffff;">{a.get('job_title')}</span></h4>
                                    <span style="color: #10b981; font-weight: 600;">{a.get('status')}</span>
                                </div>
                                <p style="margin: 6px 0;">📧 <strong>Email:</strong> {a.get('email')} | 📞 <strong>Phone:</strong> {a.get('phone')} | ⏳ <strong>Exp:</strong> {a.get('experience_years')}</p>
                                {f"<p>🔗 <a href='{a.get('portfolio_url')}' target='_blank' style='color: #60a5fa;'>{a.get('portfolio_url')}</a></p>" if a.get('portfolio_url') else ""}
                                <p style="color: #cbd5e1; background: #0f172a; padding: 8px 12px; border-radius: 6px; border: 1px solid #334155;"><em>\"{a.get('cover_note', 'No cover note provided')}\"</em></p>
                                <small style="color: #64748b;">Applied on: {str(a.get('created_at', ''))[:19]}</small>
                            </div>
                            """, unsafe_allow_html=True)
                            
        with subtab2:
            res_inqs = fetch_inquiries(st.session_state["admin_token"])
            if not res_inqs.get("success"):
                st.error(f"Failed to fetch client inquiries: {res_inqs.get('error')}")
            else:
                inqs_data = res_inqs.get("data", [])
                if not inqs_data:
                    st.info("No service inquiries received yet.")
                else:
                    st.markdown(f"**Total Leads / Inquiries:** `{len(inqs_data)}`")
                    for inq in inqs_data:
                        with st.container():
                            st.markdown(f"""
                            <div class="corporate-card">
                                <div style="display: flex; justify-content: space-between;">
                                    <h4 style="color: #60a5fa; margin: 0;">🏢 {inq.get('company_name', 'Client')} - <span style="color: #ffffff;">{inq.get('service_required')}</span></h4>
                                    <span style="color: #f59e0b; font-weight: 600;">{inq.get('budget')}</span>
                                </div>
                                <p style="margin: 6px 0;">👤 <strong>Contact:</strong> {inq.get('client_name')} (📧 {inq.get('email')})</p>
                                <p style="color: #cbd5e1; background: #0f172a; padding: 8px 12px; border-radius: 6px; border: 1px solid #334155;">{inq.get('message')}</p>
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
st.caption("🏢 CloudNexus Solutions Inc. | 3-Tier Enterprise Cloud Platform | Kubeadm Kubernetes & Ingress Controller")
