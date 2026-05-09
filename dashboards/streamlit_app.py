import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import bcrypt
import json
import re
from datetime import datetime, timedelta, timezone
from textwrap import dedent
import streamlit as st
from streamlit_cookies_manager import EncryptedCookieManager
from supabase import create_client
from src.screening import clean_name, match_name, calculate_risk
from src.pdf_generator import generate_pdf

SUPABASE_URL = "https://guqjmtgqaxperzxfsmel.supabase.co"
SUPABASE_KEY = "sb_publishable_SMWNZub4TscXI1SMEOaOww_HQ3sYELO"
PAYPAL_URL = "https://www.paypal.com/ncp/payment/URXM2BPFFLHXC"
PAYMENT_URL = PAYPAL_URL
LOGO_PATH = "assets/logo.png"
ADMIN_ACCESS_HASH = "$2b$12$Pq7uISXnhxLocZunA1i0M.BPE9YcMGGQC37anS0wl1qQRC2QQQfp2"
AUTH_COOKIE_NAME = "chaavon_auth_session"
ADMIN_COOKIE_NAME = "chaavon_admin_session"
AUTH_COOKIE_TTL_DAYS = 30

st.set_page_config(
    page_title="ChaAVON — Structured intelligence for high-stakes decisions.",
    page_icon="assets/logo.png",
    layout="wide",
    initial_sidebar_state="collapsed",
)

cookie_manager = EncryptedCookieManager(
    prefix="chaavon_prod/",
    password=f"{SUPABASE_KEY}:chaavon-auth-v1",
)

if not cookie_manager.ready():
    st.stop()

st.markdown(
    """
    <style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    [data-testid="stToolbar"] {display: none;}
    [data-testid="stDecoration"] {display: none;}
    [data-testid="stStatusWidget"] {display: none;}
    [data-testid="stSidebar"] {display: none;}
    [data-testid="stHeader"] {display: none;}
    [data-testid="stAppDeployButton"] {display: none;}
    [data-testid="stAppViewContainer"] > .main {padding-top: 0;}
    [data-testid="stAppHeader"] {display: none;}
    [data-testid="stHeaderActionElements"] {display: none;}
    button[kind="header"] {display: none;}

    :root {
        --bg: #000000;
        --card: #111111;
        --green: #006039;
        --text: #FFFFFF;
        --muted: rgba(255, 255, 255, 0.68);
        --line: rgba(255, 255, 255, 0.12);
        --danger: #FF4D4D;
    }

    html, body, [class*="css"], .stApp {
        background: #000000;
        color: var(--text);
        font-family: -apple-system, BlinkMacSystemFont, "San Francisco", sans-serif;
    }

    header[data-testid="stHeader"] {
        background: transparent;
    }

    div.block-container {
        max-width: 1200px;
        padding: 0 24px 60px 24px;
    }

    h1, h2, h3, label, .stMarkdown {
        color: var(--text) !important;
        letter-spacing: 0;
    }

    h1 {
        font-weight: 900 !important;
    }

    .stMarkdown p {
        color: var(--muted);
    }

    .container {
        max-width: 1200px;
        margin: auto;
        padding: 60px 24px;
    }

    div[data-testid="stTextInput"] input,
    div[data-testid="stNumberInput"] input {
        background: var(--card);
        color: var(--text);
        border: 1px solid var(--green);
        border-radius: 10px;
        padding: 0.75rem;
    }

    div[data-testid="stTextInput"] input:focus,
    div[data-testid="stNumberInput"] input:focus {
        border-color: var(--green);
        box-shadow: none;
    }

    button:focus {
        outline: none !important;
        box-shadow: none !important;
    }

    .stButton > button,
    .stDownloadButton > button,
    .stLinkButton > a {
        background: var(--green);
        color: #FFFFFF;
        border: none;
        border-radius: 12px;
        font-weight: 600;
        padding: 12px 26px;
    }

    .stButton > button:hover,
    .stDownloadButton > button:hover,
    .stLinkButton > a:hover {
        background: #0b7448;
        color: #FFFFFF;
    }

    .navbar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 20px 40px;
        border-bottom: 1px solid var(--line);
    }

    .brand-lockup {
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .brand-link {
        display: inline-flex;
        align-items: center;
        gap: 12px;
        text-decoration: none;
    }

    .logo {
        width: 44px;
        height: 44px;
        border-radius: 50%;
        object-fit: cover;
        display: block;
    }

    .brand {
        font-size: 18px;
        font-weight: 600;
        letter-spacing: 0.5px;
        color: var(--text);
    }

    .nav-status {
        font-size: 11px;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        font-weight: 700;
    }

    .status-active {
        color: #006039;
    }

    .status-pending {
        color: #d1a646;
    }

    .status-expired {
        color: #b65b5b;
    }

    .landing-shell {
        max-width: 1180px;
        margin: 0 auto;
        padding: 0 24px 28px 24px;
    }

    .landing-hero-grid {
        padding: 86px 0 76px 0;
        align-items: center;
    }

    .landing-hero-grid div[data-testid="stHorizontalBlock"] {
        align-items: center;
    }

    div[data-testid="stHorizontalBlock"]:has(.main-title) {
        align-items: center;
    }

    .main-title {
        font-size: 72px;
        font-weight: 700;
        letter-spacing: -1px;
        text-align: center;
        color: var(--text);
        margin: 0;
        line-height: 1;
    }

    .subtitle {
        font-size: 18px;
        color: #9CA3AF;
        text-align: center;
        margin-top: 8px;
        max-width: 600px;
        margin-left: auto;
        margin-right: auto;
        opacity: 0.7;
    }

    .cta-wrapper {
        text-align: center;
        margin-top: 20px;
    }

    .cta-text {
        display: inline-block;
        font-size: 16px;
        color: #006039;
        cursor: pointer;
        text-decoration: none;
    }

    .folder {
        position: relative;
        margin-bottom: 40px;
        transition: all 0.25s ease;
    }

    .folder-tilt-a { transform: rotate(-1deg); }
    .folder-tilt-b { transform: rotate(1.5deg); }
    .folder-tilt-c { transform: rotate(-2deg); }
    .folder-tilt-d { transform: rotate(1deg); }

    .folder:hover {
        transform: translateY(-6px) scale(1.01);
    }

    .folder-tab {
        width: 42%;
        height: 12px;
        background: #121212;
        border: 1px solid rgba(0,96,57,0.35);
        border-bottom: none;
        border-radius: 8px 8px 0 0;
        margin-left: 6px;
    }

    .folder-body {
        background: #0f0f0f;
        border: 1px solid rgba(0,96,57,0.4);
        border-radius: 0 12px 12px 12px;
        padding: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.6), 0 0 0 1px rgba(0,96,57,0.15) inset;
    }

    .folder-title {
        font-size: 16px;
        font-weight: 600;
        color: #FFFFFF;
    }

    .folder-text {
        margin-top: 8px;
        color: #9CA3AF;
        font-size: 14px;
        line-height: 1.6;
    }

    .landing-section {
        padding: 76px 0;
    }

    .landing-section.offset {
        padding-left: clamp(0px, 8vw, 96px);
    }

    .landing-section.compact {
        padding-top: 62px;
    }

    .section-kicker {
        color: var(--green);
        font-size: 0.78rem;
        font-weight: 900;
        letter-spacing: 0.16em;
        text-transform: uppercase;
        margin-bottom: 18px;
    }

    .section-title {
        font-size: clamp(36px, 4vw, 56px);
        font-weight: 760;
        line-height: 1.08;
        margin: 0 0 28px 0;
        color: var(--text);
        letter-spacing: 0;
    }

    .section-text {
        max-width: 760px;
        font-size: 18px;
        color: #9CA3AF;
        line-height: 1.85;
    }

    .section-text p {
        margin: 0 0 1.25rem 0;
    }

    .method-grid {
        display: grid;
        grid-template-columns: minmax(0, 0.9fr) minmax(0, 1.1fr);
        gap: clamp(48px, 8vw, 108px);
        align-items: start;
    }

    .method-list {
        display: grid;
        gap: 24px;
        margin-top: 8px;
    }

    .signal-block {
        margin-top: 40px;
        line-height: 2;
    }

    .signal-block div {
        color: #006039;
        font-size: 13px;
        letter-spacing: 1.2px;
        text-transform: uppercase;
        opacity: 0.9;
    }

    .method-item {
        padding: 0 0 24px 0;
        border-bottom: 1px solid rgba(255, 255, 255, 0.09);
    }

    .method-item:last-child {
        border-bottom: none;
    }

    .method-title {
        color: var(--text);
        font-size: 1.05rem;
        font-weight: 800;
        margin-bottom: 0.45rem;
    }

    .method-copy {
        color: var(--muted);
        font-size: 1rem;
        line-height: 1.7;
    }

    .terms-panel {
        max-width: 900px;
        margin-left: auto;
        padding: 46px 0 0 0;
        box-shadow: 0 -1px 0 rgba(0, 96, 57, 0.45);
    }

    .green {
        color: var(--green);
    }

    .cta-wrap {
        margin: 34px auto 0 auto;
        display: flex;
        justify-content: center;
    }

    .divider {
        border-top: 1px solid #1F2937;
        margin: 100px 0;
    }

    .panel {
        background: var(--card);
        border: 1px solid var(--green);
        border-radius: 12px;
        padding: 1.25rem;
        margin: 1rem 0;
    }

    .compact-panel {
        max-width: 620px;
        margin: 3rem auto 0 auto;
    }

    .form-note {
        color: var(--muted);
        font-size: 0.98rem;
        line-height: 1.7;
        margin-bottom: 1.5rem;
    }

    .page-shell {
        max-width: 840px;
        margin: 0 auto;
        padding: 52px 0 0 0;
    }

    .footer-shell {
        margin-top: 120px;
        padding: 56px 0 24px 0;
        border-top: 1px solid var(--line);
    }

    .footer-brand {
        font-size: 2rem;
        font-weight: 700;
        color: var(--text);
        margin-bottom: 1rem;
    }

    .footer-copy,
    .footer-meta,
    .footer-link-text {
        color: var(--muted);
        font-size: 1rem;
        line-height: 1.8;
    }

    .footer-heading {
        color: var(--text);
        font-size: 1.25rem;
        font-weight: 700;
        margin-bottom: 1rem;
    }

    .footer-list {
        display: flex;
        flex-direction: column;
        gap: 0.85rem;
    }

    .footer-shell .stButton > button {
        background: transparent;
        border: none;
        padding: 0;
        border-radius: 0;
        color: var(--muted);
        font-weight: 500;
        justify-content: flex-start;
        min-height: auto;
        box-shadow: none;
    }

    .footer-shell .stButton > button:hover {
        background: transparent;
        color: var(--text);
        border: none;
    }

    .report-section {
        min-height: 170px;
        padding: 1.1rem;
        border: 1px solid var(--green);
        border-radius: 12px;
        background: var(--card);
    }

    .report-section .section-title {
        margin: 0 0 0.85rem 0;
        color: var(--text);
        font-size: 1.05rem;
        font-weight: 900;
    }

    .report-line {
        margin: 0.35rem 0;
        color: var(--muted);
    }

    .report-line strong {
        color: var(--text);
    }

    .badge {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        border-radius: 999px;
        background: var(--green);
        color: var(--text);
        font-size: 0.8rem;
        font-weight: 900;
    }

    .status-hero {
        font-size: 1.7rem;
        font-weight: 950;
        margin: 0 0 0.75rem 0;
    }

    .status-clear {
        color: var(--green);
    }

    .status-match {
        color: var(--danger);
    }

    .risk-row {
        margin-top: 1rem;
    }

    .risk-label {
        display: flex;
        justify-content: space-between;
        color: var(--text);
        font-weight: 800;
        margin-bottom: 0.45rem;
    }

    .risk-track {
        width: 100%;
        height: 16px;
        border-radius: 999px;
        background: var(--card);
        overflow: hidden;
        border: 1px solid var(--line);
    }

    .risk-fill {
        height: 100%;
        border-radius: 999px;
        background: var(--green);
        transition: width 0.9s ease;
        animation: riskPulse 1.1s ease-out;
    }

    @keyframes riskPulse {
        from { width: 0%; }
    }

    .admin-container {
        background: #0B0B0B;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        margin-top: 24px;
        overflow-x: auto;
    }

    .admin-table {
        width: 100%;
        border-collapse: collapse;
        min-width: 1000px;
    }

    .admin-table th {
        text-align: left;
        padding: 16px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        color: var(--muted);
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 700;
    }

    .admin-table td {
        padding: 16px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.04);
        vertical-align: middle;
        font-size: 14px;
        color: var(--text);
    }

    .admin-table tr:last-child td {
        border-bottom: none;
    }

    .admin-actions {
        display: flex;
        gap: 8px;
        align-items: center;
    }

    .admin-actions .stButton > button {
        padding: 6px 14px;
        font-size: 13px;
        border-radius: 8px;
        min-height: auto;
        width: auto;
    }

    .admin-actions .stButton {
        width: auto;
    }

    @media (max-width: 760px) {
        .navbar {
            padding: 16px 0 20px 0;
        }

        .hero-title {
            font-size: 56px;
        }

        .main-title {
            font-size: 56px;
        }

        .container {
            padding: 40px 16px;
        }

        .landing-shell {
            padding: 0 18px 20px 18px;
        }

        .landing-hero-grid {
            padding: 52px 0 48px 0;
        }

        .landing-hero-grid div[data-testid="stHorizontalBlock"] {
            display: flex;
            flex-wrap: nowrap;
            gap: 0.75rem;
        }

        div[data-testid="stHorizontalBlock"]:has(.main-title) {
            display: flex;
            flex-direction: row;
            flex-wrap: nowrap;
            align-items: center;
            gap: 0.75rem;
        }

        .landing-hero-grid div[data-testid="column"] {
            min-width: 0;
            flex: 1 1 0;
        }

        div[data-testid="stHorizontalBlock"]:has(.main-title) > div[data-testid="column"] {
            min-width: 0;
            width: auto;
            flex: 1 1 0;
        }

        .landing-hero-grid div[data-testid="column"]:nth-child(2) {
            flex: 2 1 0;
        }

        div[data-testid="stHorizontalBlock"]:has(.main-title) > div[data-testid="column"]:nth-child(2) {
            flex: 2 1 0;
        }

        .landing-hero-grid .folder {
            margin-bottom: 24px;
        }

        .landing-hero-grid .folder-body {
            padding: 14px;
            border-radius: 12px;
        }

        .landing-hero-grid .folder-title {
            font-size: 13px;
        }

        .landing-hero-grid .folder-text {
            font-size: 12px;
            line-height: 1.45;
        }

        .landing-section,
        .landing-section.compact {
            padding: 64px 0;
        }

        .landing-section.offset {
            padding-left: 0;
        }

        .method-grid {
            grid-template-columns: 1fr;
            gap: 36px;
        }

        .terms-panel {
            margin-left: 0;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

if "page" not in st.session_state:
    st.session_state.page = "home"
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "admin_authenticated" not in st.session_state:
    st.session_state.admin_authenticated = False
if "user_email" not in st.session_state:
    st.session_state.user_email = None
if "payment_done" not in st.session_state:
    st.session_state.payment_done = False
if "approved" not in st.session_state:
    st.session_state.approved = False
if "user_name" not in st.session_state:
    st.session_state.user_name = ""
if "company_type" not in st.session_state:
    st.session_state.company_type = ""
if "user" not in st.session_state:
    st.session_state.user = {}
if "expiry_display" not in st.session_state:
    st.session_state.expiry_display = "Not specified"
if "access_status" not in st.session_state:
    st.session_state.access_status = "pending"
if "status_notice" not in st.session_state:
    st.session_state.status_notice = ""
if "dashboard_log_written" not in st.session_state:
    st.session_state.dashboard_log_written = False


def set_page(page):
    st.session_state.page = page
    if page == "home":
        clear_route_params()
    else:
        st.query_params["page"] = page


def clear_route_params():
    if "page" in st.query_params:
        del st.query_params["page"]


def parse_timestamp(value):
    if not value:
        return None
    parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def auth_session_payload():
    raw = cookie_manager.get(AUTH_COOKIE_NAME)
    if not raw:
        return None
    try:
        payload = json.loads(raw)
        expires_at = parse_timestamp(payload.get("expires_at"))
        if not expires_at or expires_at < datetime.now(timezone.utc):
            clear_auth_session()
            return None
        return payload
    except Exception:
        clear_auth_session()
        return None


def persist_auth_session(email, issued_at):
    payload = {
        "email": str(email).strip().lower(),
        "issued_at": issued_at,
        "expires_at": (datetime.now(timezone.utc) + timedelta(days=AUTH_COOKIE_TTL_DAYS)).isoformat(),
    }
    cookie_manager[AUTH_COOKIE_NAME] = json.dumps(payload)
    cookie_manager.save()


def clear_auth_session():
    if AUTH_COOKIE_NAME in cookie_manager:
        del cookie_manager[AUTH_COOKIE_NAME]
        cookie_manager.save()


def persist_admin_session():
    payload = {
        "admin_authenticated": True,
        "expires_at": (datetime.now(timezone.utc) + timedelta(days=AUTH_COOKIE_TTL_DAYS)).isoformat(),
    }
    cookie_manager[ADMIN_COOKIE_NAME] = json.dumps(payload)
    cookie_manager.save()


def clear_admin_session():
    if ADMIN_COOKIE_NAME in cookie_manager:
        del cookie_manager[ADMIN_COOKIE_NAME]
        cookie_manager.save()


def restore_admin_session():
    raw = cookie_manager.get(ADMIN_COOKIE_NAME)
    if not raw:
        return
    try:
        payload = json.loads(raw)
        expires_at = parse_timestamp(payload.get("expires_at"))
        if expires_at and expires_at > datetime.now(timezone.utc):
            st.session_state.admin_authenticated = True
        else:
            clear_admin_session()
    except Exception:
        clear_admin_session()


def clear_all_auth_state():
    # Clear session state
    st.session_state.authenticated = False
    st.session_state.admin_authenticated = False
    st.session_state.user_email = None
    st.session_state.payment_done = False
    st.session_state.approved = False
    st.session_state.user_name = ""
    st.session_state.company_type = ""
    st.session_state.user = {}
    st.session_state.expiry_display = "Not specified"
    st.session_state.access_status = "pending"
    st.session_state.dashboard_log_written = False
    
    # Clear cookies
    clear_auth_session()
    clear_admin_session()
    
    # Clear route params
    clear_route_params()


def reset_auth_state():
    clear_all_auth_state()


def restore_session():
    payload = auth_session_payload()
    if not payload:
        return

    session_email = str(payload.get("email", "")).strip().lower()
    issued_at = payload.get("issued_at")
    if not session_email or not issued_at:
        clear_all_auth_state()
        return

    record = get_user_record(session_email)
    if not record:
        clear_all_auth_state()
        set_page("home")
        st.rerun()

    record_last_login = record.get("last_login")
    if not record_last_login:
        clear_all_auth_state()
        set_page("home")
        st.rerun()

    try:
        if parse_timestamp(record_last_login) != parse_timestamp(issued_at):
            clear_all_auth_state()
            set_page("home")
            st.rerun()
    except Exception:
        clear_all_auth_state()
        set_page("home")
        st.rerun()

    st.session_state.user_email = session_email
    st.session_state.authenticated = True
    st.session_state.user = record
    st.session_state.user_name = record.get("name") or ""
    st.session_state.company_type = record.get("company_type") or ""
    st.session_state.approved = bool(record.get("approved"))
    st.session_state.payment_done = bool(record.get("payment_done", False))
    _, expiry = format_expiry(record.get("end_date"))
    st.session_state.expiry_display = expiry.strftime("%Y-%m-%d") if expiry else "Not specified"
    st.session_state.access_status = "active" if st.session_state.approved else ("pending" if st.session_state.payment_done else "pending")


def go_to(page):
    set_page(page)
    st.rerun()


def is_valid_email(email):
    return bool(re.match(r"[^@]+@[^@]+\.[^@]+", email))


def format_expiry(end_date):
    if not end_date:
        return None, None

    try:
        expiry = datetime.fromisoformat(str(end_date).replace("Z", ""))
    except Exception:
        return None, None

    return expiry.strftime("%Y-%m-%d"), expiry


def log_access_event(email, event):
    if not email:
        return

    try:
        supabase.table("access_logs").insert({
            "email": email,
            "event": event,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }).execute()
    except Exception:
        pass


def get_user_record(email):
    if not email:
        return None

    try:
        email = str(email).strip().lower()
        response = supabase.table("users_access").select("*").eq("email", email).execute()
        if response and hasattr(response, "data") and response.data:
            return response.data[0]
        return None
    except Exception:
        return None


def save_user_record(email, payload):
    try:
        email = str(email).strip().lower()
        res = supabase.table("users_access").update(payload).eq("email", email).execute()
        
        # If update returns data, use it. Otherwise re-fetch to confirm.
        if hasattr(res, "data") and res.data:
            return res.data[0]
        
        # Fallback: re-fetch to verify persistence
        return get_user_record(email)
    except Exception as e:
        st.error(f"Database error: {str(e)}")
        return None


def get_status_markup():
    if not st.session_state.authenticated:
        return ""

    status = st.session_state.access_status
    label_map = {
        "active": "● ACCESS ACTIVE",
        "pending": "● APPROVAL PENDING",
        "expired": "● ACCESS EXPIRED",
    }
    class_map = {
        "active": "status-active",
        "pending": "status-pending",
        "expired": "status-expired",
    }
    return f'<div class="nav-status {class_map.get(status, "status-pending")}">{label_map.get(status, "● APPROVAL PENDING")}</div>'


BUILD_VERSION = "workspace-rebuild-v1"

def get_access_state(record):
    """
    Unified source of truth for user access.
    """
    if not record:
        return {
            "authenticated": False,
            "approved": False,
            "payment_done": False,
            "is_active": False,
            "expired": False,
            "has_workspace_access": False,
            "status": "public"
        }
    
    approved = bool(record.get("approved"))
    payment_done = bool(record.get("payment_done"))
    is_active = bool(record.get("is_active", True)) # Default to True if not present
    
    # Check expiry
    expired = False
    if record.get("end_date"):
        try:
            raw_end = str(record["end_date"]).replace("Z", "")
            if " " in raw_end:
                end_date = datetime.fromisoformat(raw_end.split(" ")[0])
            elif "T" in raw_end:
                end_date = datetime.fromisoformat(raw_end.split("T")[0])
            else:
                end_date = datetime.fromisoformat(raw_end)
            
            # Normalize to 23:59:59 UTC
            end_date = end_date.replace(hour=23, minute=59, second=59, tzinfo=timezone.utc)
            if end_date < datetime.now(timezone.utc):
                expired = True
                is_active = False
        except Exception:
            expired = True
            is_active = False

    # Logic: must be approved, active, and not expired
    has_workspace_access = approved and is_active and not expired
    
    # Status determination
    if expired:
        status = "expired"
    elif not is_active:
        status = "revoked"
    elif approved:
        status = "approved"
    elif payment_done:
        status = "pending"
    else:
        status = "authenticated"

    return {
        "authenticated": True,
        "approved": approved,
        "payment_done": payment_done,
        "is_active": is_active,
        "expired": expired,
        "has_workspace_access": has_workspace_access,
        "status": status
    }


def sync_access_state():
    user_email = st.session_state.user_email
    if not user_email:
        return

    record = get_user_record(user_email)
    if not record:
        clear_all_auth_state()
        set_page("home")
        st.rerun()

    state = get_access_state(record)
    
    # Sync to session state
    st.session_state.user = record
    st.session_state.authenticated = state["authenticated"]
    st.session_state.approved = state["approved"]
    st.session_state.payment_done = state["payment_done"]
    st.session_state.access_status = state["status"]
    
    if record.get("end_date"):
        st.session_state.expiry_display = record["end_date"].split("T")[0] if "T" in record["end_date"] else record["end_date"]
    else:
        st.session_state.expiry_display = "Not specified"

    # Gating enforcement for Workspace
    if st.session_state.page == "workspace" and not state["has_workspace_access"]:
        set_page("payment")
        st.rerun()
    
    # Auto-redirect to workspace if approved and on payment
    if st.session_state.page == "payment" and state["has_workspace_access"]:
        set_page("workspace")
        st.rerun()


# Final enforcement: if on workspace but not approved, redirect
if st.session_state.page == "workspace" and not st.session_state.approved:
    st.session_state.page = "payment"
    st.query_params["page"] = "payment"
    st.rerun()


restore_session()
restore_admin_session()
sync_access_state()

requested_page = st.query_params.get("page")
if requested_page in {"home", "login", "register", "payment", "terms", "dashboard", "workspace", "admin"}:
    st.session_state.page = "workspace" if str(requested_page) == "dashboard" else str(requested_page)

if st.session_state.authenticated and st.session_state.page in {"login", "register"}:
    # Use computed state for routing
    record = get_user_record(st.session_state.user_email)
    state = get_access_state(record)
    set_page("workspace" if state["has_workspace_access"] else "payment")


def render_top_nav():
    status_markup = get_status_markup()
    st.markdown(
        f"""
        <div class="navbar">
            <div class="brand-link">
                <img class="logo" src="data:image/png;base64,{logo_base64()}" />
                <div class="brand">ChaAVON</div>
            </div>
            {status_markup}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_footer():
    st.markdown('<div class="footer-shell">', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns([1.5, 1, 1, 1])

    with col1:
        st.markdown('<div class="footer-brand">ChaAVON</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="footer-copy">Structured intelligence for high-stakes decisions.</div>',
            unsafe_allow_html=True,
        )
        st.markdown('<div style="height:48px"></div>', unsafe_allow_html=True)
        st.markdown('<div class="footer-meta">© 2026 ChaAVON Inc.</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="footer-heading">Product</div>', unsafe_allow_html=True)
        st.markdown(
            """
            <div class="footer-list">
                <div class="footer-link-text">Risk Intelligence</div>
                <div class="footer-link-text">Compliance Intelligence</div>
                <div class="footer-link-text">Auditability</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown('<div class="footer-heading">Company</div>', unsafe_allow_html=True)
        st.markdown(
            """
            <div class="footer-list">
                <div class="footer-link-text">About</div>
                <div class="footer-link-text">Security</div>
                <div class="footer-link-text">Contact</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col4:
        st.markdown('<div class="footer-heading">Legal</div>', unsafe_allow_html=True)
        st.markdown('<div class="footer-link-text">Privacy</div>', unsafe_allow_html=True)
        if st.button("Terms", key=f"footer_terms_{st.session_state.page}"):
            go_to("terms")
        st.markdown('<div class="footer-link-text">Cookie Policy</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


def terms_page():
    render_top_nav()
    st.markdown('<div class="page-shell">', unsafe_allow_html=True)
    st.title("Terms of Use")
    st.markdown(
        """
        ChaAVON provides access to compliance intelligence, sanctions screening tools, and structured decision systems for professional users operating in regulated and high-scrutiny environments. By accessing or using the platform, you agree to the terms below, which govern subscription access, permissible use, and allocation of responsibility.

        ### 1. Use of Services
        The Services may be used only for lawful, professional, and business purposes. You may not misuse the platform, interfere with its operation, or use it in a manner inconsistent with applicable laws, regulations, or internal compliance obligations.

        ### 2. Data & Accuracy
        Data, screening outputs, and supporting intelligence are provided on an "as is" and "as available" basis. ChaAVON does not guarantee completeness, accuracy, timeliness, or fitness for any specific purpose, and no output should be interpreted as legal advice or a final regulatory determination.

        ### 3. Access & Subscription
        Access is limited to approved users with an active subscription period recorded in the platform. Access may be suspended, restricted, or terminated when approval is withdrawn, subscription periods expire, or operational or compliance concerns require further review.

        ### 4. User Responsibilities
        You remain solely responsible for reviewing outputs, applying internal judgment, and making final operational, commercial, or compliance decisions. You are also responsible for maintaining the confidentiality of account information submitted through the registration and access workflow.

        ### 5. Intellectual Property
        The platform, its models, interface design, output structures, data presentation methods, and supporting systems are owned exclusively by ChaAVON and protected by applicable intellectual property laws.

        ### 6. Restrictions
        You may not copy, resell, redistribute, reverse engineer, scrape, or create derivative systems from the platform or its outputs without prior written authorization from ChaAVON. Automated extraction or external republication of data is prohibited.

        ### 7. Liability Disclaimer
        To the maximum extent permitted by law, ChaAVON disclaims liability for direct, indirect, incidental, consequential, regulatory, commercial, or reputational losses arising from use of, or reliance on, the Services or any output generated through the platform.

        ### 8. Availability & Access
        ChaAVON does not guarantee uninterrupted availability, continuous uptime, or error-free performance. Access may be modified, paused, or revoked when operational maintenance, security reviews, data integrity concerns, or policy enforcement actions require it.

        ### 9. Governing Law
        These terms are governed by the laws applicable to the jurisdiction designated by ChaAVON for the service relationship. Continued use of the platform after updates to these terms constitutes acceptance of the revised terms.
        """
    )
    st.markdown("</div>", unsafe_allow_html=True)


@st.cache_data
def logo_base64():
    import base64
    with open(LOGO_PATH, "rb") as logo_file:
        return base64.b64encode(logo_file.read()).decode("utf-8")


def folder(title, text, extra_class=""):
    return f"""
    <div class="folder {extra_class}">
        <div class="folder-tab"></div>
        <div class="folder-body">
            <div class="folder-title">{title}</div>
            <div class="folder-text">{text}</div>
        </div>
    </div>
    """


def render_landing_page():
    render_top_nav()
    st.markdown('<div class="landing-shell">', unsafe_allow_html=True)
    st.markdown('<div class="landing-hero-grid">', unsafe_allow_html=True)
    left, center, right = st.columns([1, 2, 1], gap="large")

    with left:
        st.markdown("<div style='margin-left:-60px; margin-top:20px;'>", unsafe_allow_html=True)
        st.markdown(
            folder(
                "Risk Intelligence",
                "Structured counterparty risk evaluation using deterministic models.",
                "folder-tilt-a",
            ),
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<div style='margin-left:40px; margin-top:60px;'>", unsafe_allow_html=True)
        st.markdown(
            folder(
                "Audit Integrity",
                "Every decision is recorded, traceable, and defensible.",
                "folder-tilt-b",
            ),
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with center:
        st.markdown("<h1 class='main-title'>ChaAVON</h1>", unsafe_allow_html=True)
        st.markdown(
            "<div class='subtitle'>Structured intelligence for high-stakes decisions.</div>",
            unsafe_allow_html=True,
        )
        st.markdown("<div class='cta-wrapper'>", unsafe_allow_html=True)
        
        if st.session_state.authenticated:
            # Lifecycle-aware CTAs
            record = get_user_record(st.session_state.user_email)
            state = get_access_state(record)
            
            if state["has_workspace_access"]:
                cta_label = "Enter Intelligence Workspace →"
                target_page = "workspace"
            elif state["status"] == "expired":
                cta_label = "Renew Access →"
                target_page = "payment"
            elif state["status"] == "pending":
                cta_label = "Approval Pending..."
                target_page = "payment"
            else:
                cta_label = "Complete Access Setup →"
                target_page = "payment"
            
            if st.button(cta_label, key="workspace_cta"):
                set_page(target_page)
                st.rerun()
        else:
            cta_col, login_col = st.columns(2, gap="small")
            with cta_col:
                if st.button("Join Now", key="cta_link"):
                    set_page("register")
                    st.rerun()
            with login_col:
                if st.button("Login", key="login_link"):
                    set_page("login")
                    st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown("<div style='margin-right:-60px; margin-top:0px;'>", unsafe_allow_html=True)
        st.markdown(
            folder(
                "Counterparty Controls",
                "Entity matching, jurisdiction exposure, and behavioral risk signals.",
                "folder-tilt-c",
            ),
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<div style='margin-top:80px;'>", unsafe_allow_html=True)
        st.markdown(
            folder(
                "Controlled Access",
                "Approval-gated platform with enforced subscription lifecycle.",
                "folder-tilt-d",
            ),
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown(
        dedent(
        """
            <div class="landing-section offset">
                <div class="section-kicker">What We Do</div>
                <div class="section-title">Compliance intelligence built for accountable decisions.</div>
                <div class="section-text">
                    <p>ChaAVON provides structured intelligence infrastructure for maritime compliance, sanctions screening, and counterparty risk review. The platform converts fragmented checks into a consistent decision environment for regulated and high-scrutiny work.</p>
                    <p>It exists to reduce ambiguity where manual review, incomplete records, and inconsistent screening logic create operational and regulatory risk. ChaAVON gives teams a controlled way to evaluate exposure, document outcomes, and preserve the reasoning behind each decision.</p>
                    <p>The result is not a recommendation layer or a marketing dashboard. It is a disciplined system for producing reviewable compliance outputs when accuracy, traceability, and governance matter.</p>
                </div>
            </div>

            <div class="landing-section compact">
                <div class="method-grid">
                    <div>
                        <div class="section-kicker">How We Do It</div>
                        <div class="section-title">Structured review, deterministic logic, defensible records.</div>
                        <div class="signal-block">
                            <div>Deterministic models</div>
                            <div>Structured outputs</div>
                            <div>Auditability</div>
                            <div>Controlled workflows</div>
                        </div>
                    </div>
                    <div class="method-list">
                        <div class="section-text">
                            <p>Screening outcomes are produced through explicit scoring logic and defined thresholds, reducing the variance that comes from ad hoc manual interpretation.</p>
                            <p>Each result is organized into consistent fields so teams can compare entities, review exposure, and understand the basis for the decision without reconstructing the process.</p>
                            <p>Review activity, screening results, and decision context are preserved in a format designed for oversight, escalation, and post-event review.</p>
                            <p>Access, subscription status, and operational pathways are governed through approval checks so the platform remains bounded to authorized professional use.</p>
                        </div>
                    </div>
                </div>
            </div>

            <div class="landing-section">
                <div class="terms-panel">
                    <div class="section-kicker">Terms</div>
                    <div class="section-title">Use is professional, controlled, and subject to review.</div>
                    <div class="section-text">
                        <p>ChaAVON is provided for lawful business and compliance purposes by approved users. Access may be limited, suspended, or withdrawn when account status, payment status, operational integrity, or compliance concerns require review.</p>
                        <p>Users remain responsible for the decisions they make from platform outputs. Screening results, risk indicators, and generated reports support professional review, but they do not replace independent judgment, legal advice, or final regulatory determinations.</p>
                        <p>The platform and its outputs are provided on an as-available basis. ChaAVON does not guarantee that external datasets are complete, current, or error-free, and disclaims liability for commercial, regulatory, reputational, or operational losses arising from reliance on the service.</p>
                        <p>Users may not copy, resell, scrape, reverse engineer, or redistribute the platform, its interface, models, reports, or data presentation methods without prior written authorization from ChaAVON.</p>
                    </div>
                </div>
            </div>
        """,
        ).replace("\n        ", "\n").strip().replace("\n", " "),
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)


def render_registration_page():
    if st.session_state.authenticated:
        set_page("payment")
        st.rerun()

    render_top_nav()
    st.title("Request Access")
    st.markdown(
        '<div class="form-note">Submit your registration details to request controlled platform access. Access is reviewed manually and activated only after approval.</div>',
        unsafe_allow_html=True,
    )
    company_options = ["Trading Firm", "Broker", "Other"]
    default_company = st.session_state.get("company_type", company_options[0])
    company_index = company_options.index(default_company) if default_company in company_options else 0

    with st.form("register_form"):
        name = st.text_input("Full Name", value=st.session_state.get("user_name", ""))
        email = st.text_input("Email", value=st.session_state.get("user_email") or "")
        password = st.text_input("Password", type="password")
        company = st.selectbox("Company Type", company_options, index=company_index)
        submit = st.form_submit_button("Continue")

    if submit:
        name = name.strip()
        email = email.strip().lower()
        password = password.strip()
        issued_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()

        if not name:
            st.error("Enter your full name")
            st.stop()
        if not is_valid_email(email):
            st.error("Enter a valid email address")
            st.stop()
        if not password:
            st.error("Enter a password")
            st.stop()

        existing_approved = False
        existing_end_date = None

        with st.spinner("Saving registration..."):
            try:
                existing = get_user_record(email)
                if existing and existing.get("password_hash"):
                    st.error("Email already registered. Please log in.")
                    st.stop()

                if existing:
                    existing_approved = existing.get("approved", False)
                    existing_end_date = existing.get("end_date")
                    is_active = existing.get("is_active", False)
                    expiry_date = existing.get("expiry_date")
                    start_date = existing.get("start_date")
                    payment_done = bool(existing.get("payment_done", False))
                else:
                    is_active = False
                    expiry_date = None
                    start_date = None
                    payment_done = False

                hashed_password = bcrypt.hashpw(
                    password.encode(),
                    bcrypt.gensalt()
                ).decode()

                payload = {
                    "name": name,
                    "email": email,
                    "password_hash": hashed_password,
                    "company_type": company,
                    "is_active": is_active,
                    "expiry_date": expiry_date,
                    "approved": existing_approved,
                    "start_date": start_date,
                    "end_date": existing_end_date,
                    "payment_done": payment_done,
                    "last_login": issued_at,
                }
                supabase.table("users_access").upsert(payload, on_conflict="email").execute()
                log_access_event(email, "register")
            except Exception:
                st.error("Registration could not be saved. Please retry.")
                st.stop()

        st.session_state.user_name = name
        st.session_state.user_email = email
        st.session_state.company_type = company
        st.session_state.authenticated = True
        st.session_state.payment_done = False
        st.session_state.approved = existing_approved
        st.session_state.dashboard_log_written = False
        persist_auth_session(email, issued_at)
        set_page("payment")
        st.rerun()


def render_login_page():
    if st.session_state.authenticated:
        set_page("workspace" if st.session_state.approved else "payment")
        st.rerun()

    render_top_nav()
    st.title("Login")
    st.markdown(
        '<div class="form-note">Sign in to restore your account session and continue with your access workflow.</div>',
        unsafe_allow_html=True,
    )

    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")

    if submit:
        email = email.strip().lower()
        password = password.strip()
        issued_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()

        if not is_valid_email(email):
            st.error("Enter a valid email address")
            st.stop()
        if not password:
            st.error("Enter your password")
            st.stop()

        record = get_user_record(email)
        stored_hash = record.get("password_hash") if record else None
        if not record or not stored_hash:
            st.error("Invalid email or password.")
            st.stop()

        try:
            valid_password = bcrypt.checkpw(
                password.encode(),
                stored_hash.encode()
            )
        except Exception:
            valid_password = False

        if not valid_password:
            st.error("Invalid email or password.")
            st.stop()

        try:
            save_user_record(email, {"last_login": issued_at})
        except Exception:
            pass

        log_access_event(email, "login")
        st.session_state.user_email = email
        st.session_state.user_name = record.get("name") or ""
        st.session_state.company_type = record.get("company_type") or ""
        st.session_state.authenticated = True
        st.session_state.dashboard_log_written = False
        persist_auth_session(email, issued_at)
        sync_access_state()
        if st.session_state.approved:
            set_page("workspace")
        else:
            set_page("payment")
        st.rerun()


def render_payment_page():
    if st.session_state.approved:
        set_page("workspace")
        st.rerun()

    render_top_nav()
    st.markdown("## Subscription Access")
    st.markdown("Plan: Vessel Sanctions Intelligence Platform")
    st.markdown("Price: $1198 USD / month")

    if st.session_state.status_notice:
        st.warning(st.session_state.status_notice)
        st.session_state.status_notice = ""

    st.link_button("Pay Now", PAYMENT_URL, use_container_width=False)
    st.caption("After completing payment, return and click: \"I Completed Payment\"")

    if st.button("I Completed Payment"):
        try:
            save_user_record(st.session_state.user_email, {"payment_done": True})
        except Exception:
            st.error("Payment confirmation could not be saved. Please retry.")
            st.stop()
        st.session_state.payment_done = True
        log_access_event(st.session_state.user_email, "payment_submit")
        st.success("Payment submitted. Access activates after compliance approval.")
        sync_access_state()
        if st.session_state.approved:
            set_page("workspace")
        st.rerun()

    if st.session_state.payment_done and not st.session_state.approved:
        st.info(
            "Your account is awaiting approval. "
            "Access is activated manually after review."
        )

    st.caption("Access activated after approval")


def render_admin_panel():
    st.markdown("### Operational Control")
    
    # Initialize report_path to avoid UnboundLocalError
    report_path = None
    
    tab_users, tab_requests, tab_archived = st.tabs(["User Access", "Intelligence Requests", "Archived Requests"])

    with tab_users:
        st.markdown('<div class="subtitle" style="text-align: left; margin-left: 0; margin-bottom: 24px;">Manage platform access, approvals, and subscription cycles.</div>', unsafe_allow_html=True)

        col_logout, col_empty = st.columns([1, 4])
        with col_logout:
            if st.button("Logout Admin", key="admin_logout_btn", use_container_width=True):
                print("[AUTH] Admin logged out.")
                clear_all_auth_state()
                st.rerun()

        try:
            response = supabase.table("users_access").select(
                "name, email, company_type, payment_done, approved, start_date, end_date"
            ).order("created_at", desc=True).execute()
            users = response.data or []
        except Exception:
            st.error("Operational data is temporarily unavailable.")
            return

        if not users:
            st.info("No registered users found.")
        else:
            # [DIAGNOSTIC] Admin Diagnostic Panel
            with st.expander("🛠️ System Diagnostics", expanded=False):
                diag_cols = st.columns(3)
                with diag_cols[0]:
                    st.write(f"**Build:** `{BUILD_VERSION}`")
                    st.write(f"**Route:** `{st.session_state.page}`")
                with diag_cols[1]:
                    st.write(f"**Email:** `{st.session_state.user_email}`")
                    st.write(f"**Auth:** `{st.session_state.authenticated}`")
                with diag_cols[2]:
                    st.write(f"**Approved:** `{st.session_state.approved}`")
                    st.write(f"**Paid:** `{st.session_state.payment_done}`")

            # Table Header with specific styling
            st.markdown('<div style="background: #0B0B0B; border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 20px;">', unsafe_allow_html=True)
            
            # Header row
            h_cols = st.columns([1.5, 2.2, 1.2, 0.8, 1, 1.2, 1.2, 3.5])
            labels = ["Name", "Email", "Company", "Paid", "Approved", "Start", "End", "Actions"]
            for col, label in zip(h_cols, labels):
                col.markdown(f'<p style="color: rgba(255,255,255,0.6); font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px;">{label}</p>', unsafe_allow_html=True)
            
            st.markdown('<div style="height: 1px; background: rgba(255,255,255,0.08); margin-bottom: 16px;"></div>', unsafe_allow_html=True)

            today = datetime.now(timezone.utc)
            for idx, record in enumerate(users):
                row_cols = st.columns([1.5, 2.2, 1.2, 0.8, 1, 1.2, 1.2, 3.5])
                email = record.get("email")
                
                with row_cols[0]:
                    st.markdown(f'<p style="font-size: 14px; margin-top: 8px;">{record.get("name") or "-"}</p>', unsafe_allow_html=True)
                with row_cols[1]:
                    st.markdown(f'<p style="font-size: 14px; margin-top: 8px; color: rgba(255,255,255,0.8);">{email or "-"}</p>', unsafe_allow_html=True)
                with row_cols[2]:
                    st.markdown(f'<p style="font-size: 14px; margin-top: 8px;">{record.get("company_type") or "-"}</p>', unsafe_allow_html=True)
                with row_cols[3]:
                    status_paid = "Yes" if record.get("payment_done") else "No"
                    st.markdown(f'<p style="font-size: 14px; margin-top: 8px;">{status_paid}</p>', unsafe_allow_html=True)
                with row_cols[4]:
                    status_app = "Yes" if record.get("approved") else "No"
                    st.markdown(f'<p style="font-size: 14px; margin-top: 8px;">{status_app}</p>', unsafe_allow_html=True)
                with row_cols[5]:
                    st.markdown(f'<p style="font-size: 14px; margin-top: 8px;">{record.get("start_date") or "-"}</p>', unsafe_allow_html=True)
                with row_cols[6]:
                    st.markdown(f'<p style="font-size: 14px; margin-top: 8px;">{record.get("end_date") or "-"}</p>', unsafe_allow_html=True)
                
                with row_cols[7]:
                    # Action buttons in a horizontal row
                    btn_cols = st.columns([1, 1, 1.4])
                    
                    with btn_cols[0]:
                        if st.button("Approve", key=f"approve_{idx}", use_container_width=True):
                            start_date = today.date().isoformat()
                            end_date = (today + timedelta(days=28)).date().isoformat()
                            payload = {
                                "approved": True,
                                "payment_done": True,
                                "start_date": start_date,
                                "end_date": end_date,
                                "is_active": True,
                            }
                            updated = save_user_record(email, payload)
                            if updated and updated.get("approved") is True:
                                log_access_event(email, "approval")
                                st.success(f"Successfully approved {email}")
                                st.rerun()
                            else:
                                st.error(f"Failed to approve {email}. Persistence failed.")

                    with btn_cols[1]:
                        if st.button("Revoke", key=f"revoke_{idx}", use_container_width=True):
                            payload = {"approved": False, "is_active": False}
                            updated = save_user_record(email, payload)
                            if updated and updated.get("approved") is False:
                                log_access_event(email, "revoke")
                                st.success(f"Successfully revoked {email}")
                                st.rerun()
                            else:
                                st.error(f"Failed to revoke {email}. Persistence failed.")

                    with btn_cols[2]:
                        if st.button("Extend 28d", key=f"extend_{idx}", use_container_width=True):
                            current_end = record.get("end_date")
                            if current_end:
                                try:
                                    parsed_end = datetime.fromisoformat(str(current_end).replace("Z", "+00:00"))
                                    if parsed_end.tzinfo is None:
                                        parsed_end = parsed_end.replace(tzinfo=timezone.utc)
                                except Exception:
                                    parsed_end = today
                            else:
                                parsed_end = today
                            new_end = (parsed_end + timedelta(days=28)).date().isoformat()
                            payload = {
                                "end_date": new_end,
                                "approved": True,
                                "payment_done": True,
                            }
                            updated = save_user_record(email, payload)
                            if updated and str(updated.get("end_date")) == new_end:
                                log_access_event(email, "extend_access")
                                st.success(f"Successfully extended {email} to {new_end}")
                                st.rerun()
                            else:
                                st.error(f"Failed to extend {email}. Persistence failed.")
                
                st.markdown('<div style="height: 1px; background: rgba(255,255,255,0.04); margin: 8px 0;"></div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)

    with tab_requests:
        st.markdown("### Maritime Intelligence Queue")
        
        try:
            res = supabase.table("intelligence_requests").select("*").eq("archived", False).order("created_at", desc=True).execute()
            all_reqs = res.data or []
        except Exception:
            # Fallback for when column doesn't exist yet
            try:
                res = supabase.table("intelligence_requests").select("*").order("created_at", desc=True).execute()
                all_reqs = res.data or []
            except Exception as e:
                st.error(f"Could not load intelligence queue: {str(e)}")
                all_reqs = []

        if not all_reqs:
            st.info("No active intelligence requests pending.")
        else:
            for req in all_reqs:
                # ... existing logic ...
                # Add Archive button for Delivered requests
                if req.get("status") == "Delivered":
                    if st.button("Archive Request", key=f"archive_{req.get('id')}", use_container_width=True):
                        try:
                            supabase.table("intelligence_requests").update({
                                "archived": True,
                                "archived_at": datetime.now(timezone.utc).isoformat()
                            }).eq("id", req.get("id")).execute()
                            st.success("Request archived.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Archive failed: {str(e)}")

    with tab_archived:
        st.markdown("### Institutional Archive")
        try:
            res = supabase.table("intelligence_requests").select("*").eq("archived", True).order("archived_at", desc=True).execute()
            archived_reqs = res.data or []
        except Exception:
            archived_reqs = []

        if not archived_reqs:
            st.info("No archived requests.")
        else:
            for req in archived_reqs:
                with st.expander(f"📦 {req.get('vessel_name')} (Archived: {req.get('archived_at', '')[:10]})", expanded=False):
                    st.write(f"**ID:** `{req.get('id')}` | **User:** {req.get('submitted_by')}")
                    if st.button("Restore to Active Queue", key=f"restore_{req.get('id')}", use_container_width=True):
                        try:
                            supabase.table("intelligence_requests").update({
                                "archived": False,
                                "archived_at": None
                            }).eq("id", req.get("id")).execute()
                            st.success("Request restored.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Restore failed: {str(e)}")
                    
                    # Also show download link in archive
                    report_path = req.get("report_path")
                    report_storage_url = req.get("report_storage_url")
                    if report_storage_url:
                        st.link_button("Download Report (Cloud)", report_storage_url, use_container_width=True)
                    elif report_path and os.path.exists(report_path):
                        with open(report_path, "rb") as f:
                            st.download_button(
                                label="Download Local Report",
                                data=f.read(),
                                file_name=os.path.basename(report_path),
                                mime="application/pdf",
                                key=f"dl_admin_archived_{req.get('id')}",
                                use_container_width=True
                            )
                    else:
                        st.warning("Archived report file unavailable on current instance")
                # SLA and Request Age
                created_at_raw = req.get("created_at")
                if created_at_raw:
                    try:
                        created_at = datetime.fromisoformat(created_at_raw.replace("Z", "+00:00"))
                        age = datetime.now(timezone.utc) - created_at
                        age_str = f"{age.days}d {age.seconds // 3600}h"
                    except Exception:
                        age_str = "N/A"
                else:
                    age_str = "N/A"
                
                status_color = {
                    "Pending Review": "🔴",
                    "Under Investigation": "🟡",
                    "Awaiting Analyst Input": "🟠",
                    "Analyst Review": "🔵",
                    "Ready for Delivery": "🟢",
                    "Delivered": "⚪"
                }.get(req.get("status"), "⚪")

                with st.expander(f"{status_color} {req.get('vessel_name')} ({req.get('status')}) — Age: {age_str}", expanded=False):
                    st.markdown(f"**Request ID:** `{req.get('id')}` | **User:** {req.get('submitted_by')}")
                    v_col1, v_col2 = st.columns(2)
                    with v_col1:
                        st.write(f"**Vessel:** {req.get('vessel_name')}")
                        st.write(f"**IMO:** {req.get('imo_number') or 'N/A'}")
                        st.write(f"**Flag:** {req.get('flag_state') or 'N/A'}")
                    with v_col2:
                        st.write(f"**Owner:** {req.get('owner') or 'N/A'}")
                        st.write(f"**Charterer:** {req.get('charterer') or 'N/A'}")
                        st.write(f"**Jurisdiction:** {req.get('jurisdiction') or 'N/A'}")
                    
                    st.write(f"**User Notes:** {req.get('operational_notes') or 'None'}")
                    
                    st.markdown("---")
                    st.markdown("#### Analyst Workspace & Enrichment")
                    
                    # --- ENRICHMENT TABS ---
                    enrich_tabs = st.tabs(["Status", "Timeline", "Citations", "Port Calls", "Ownership", "Evidence", "Sign-off"])
                    
                    with enrich_tabs[0]:
                        with st.form(f"status_form_{req.get('id')}"):
                            new_status = st.selectbox("Update Status", 
                                ["Pending Review", "Under Investigation", "Awaiting Analyst Input", "Analyst Review", "Ready for Delivery", "Delivered"],
                                index=["Pending Review", "Under Investigation", "Awaiting Analyst Input", "Analyst Review", "Ready for Delivery", "Delivered"].index(req.get("status", "Pending Review"))
                            )
                            risk_lvl = st.selectbox("Risk Level", ["Low", "Medium", "High"], 
                                index=["Low", "Medium", "High"].index(req.get("risk_level", "Medium"))
                            )
                            analyst_notes = st.text_area("Internal Analyst Notes", value=req.get("analyst_notes") or "")
                            
                            if st.form_submit_button("Update Status"):
                                try:
                                    supabase.table("intelligence_requests").update({
                                        "status": new_status,
                                        "risk_level": risk_lvl,
                                        "analyst_notes": analyst_notes,
                                        "delivered_at": datetime.now(timezone.utc).isoformat() if new_status == "Delivered" else req.get("delivered_at"),
                                        "archived": False # Reset archive if status changes
                                    }).eq("id", req.get("id")).execute()
                                    st.success("Status updated.")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Update failed: {str(e)}")

                    with enrich_tabs[1]:
                        st.write("**Vessel Timeline**")
                        timeline = req.get("timeline_events") or []
                        for i, item in enumerate(timeline):
                            st.write(f"{item.get('date')} - {item.get('event')} ({item.get('jurisdiction')})")
                        
                        with st.form(f"timeline_form_{req.get('id')}"):
                            t_date = st.date_input("Date")
                            t_event = st.text_input("Event (e.g., Flag Change, AIS Blackout)")
                            t_juris = st.text_input("Jurisdiction")
                            t_notes = st.text_area("Notes")
                            if st.form_submit_button("Add Timeline Entry"):
                                timeline.append({
                                    "date": t_date.isoformat(),
                                    "event": t_event,
                                    "jurisdiction": t_juris,
                                    "notes": t_notes
                                })
                                supabase.table("intelligence_requests").update({"timeline_events": timeline}).eq("id", req.get("id")).execute()
                                st.rerun()

                    with enrich_tabs[2]:
                        st.write("**Sanctions Source Citations**")
                        citations = req.get("citations") or []
                        for c in citations:
                            st.write(f"[{c.get('source')}]({c.get('url')}) - {c.get('observation')}")
                        
                        with st.form(f"citation_form_{req.get('id')}"):
                            c_source = st.text_input("Source Name")
                            c_url = st.text_input("Source URL")
                            c_obs = st.text_area("Observation")
                            if st.form_submit_button("Add Citation"):
                                citations.append({
                                    "source": c_source,
                                    "url": c_url,
                                    "observation": c_obs,
                                    "access_date": datetime.now(timezone.utc).isoformat()
                                })
                                supabase.table("intelligence_requests").update({"citations": citations}).eq("id", req.get("id")).execute()
                                st.rerun()

                    with enrich_tabs[3]:
                        st.write("**Port Call Chronology**")
                        port_calls = req.get("port_calls") or []
                        for p in port_calls:
                            st.write(f"{p.get('port')} ({p.get('arrival')} to {p.get('departure')})")
                        
                        with st.form(f"port_form_{req.get('id')}"):
                            p_name = st.text_input("Port Name")
                            p_arr = st.date_input("Arrival Date")
                            p_dep = st.date_input("Departure Date")
                            p_risk = st.text_input("Risk Observation")
                            p_notes = st.text_area("Activity Notes")
                            if st.form_submit_button("Add Port Call"):
                                port_calls.append({
                                    "port": p_name,
                                    "arrival": p_arr.isoformat(),
                                    "departure": p_dep.isoformat(),
                                    "risk": p_risk,
                                    "notes": p_notes
                                })
                                supabase.table("intelligence_requests").update({"port_calls": port_calls}).eq("id", req.get("id")).execute()
                                st.rerun()

                    with enrich_tabs[4]:
                        st.write("**Ownership History**")
                        ownership = req.get("ownership_history") or []
                        for o in ownership:
                            st.write(f"{o.get('company')} ({o.get('jurisdiction')})")
                        
                        with st.form(f"owner_form_{req.get('id')}"):
                            o_comp = st.text_input("Company Name")
                            o_juris = st.text_input("Jurisdiction")
                            o_start = st.date_input("Start Date")
                            o_end = st.date_input("End Date (leave if current)")
                            o_notes = st.text_area("Ownership Notes")
                            if st.form_submit_button("Add Ownership Entry"):
                                ownership.append({
                                    "company": o_comp,
                                    "jurisdiction": o_juris,
                                    "start": o_start.isoformat(),
                                    "end": o_end.isoformat() if o_end else None,
                                    "notes": o_notes
                                })
                                supabase.table("intelligence_requests").update({"ownership_history": ownership}).eq("id", req.get("id")).execute()
                                st.rerun()

                    with enrich_tabs[5]:
                        st.write("**Evidence Appendix**")
                        evidence = req.get("evidence_attachments") or []
                        for e in evidence:
                            st.write(f"- {e.get('name')} ({e.get('type')})")
                        
                        with st.form(f"evidence_form_{req.get('id')}"):
                            e_name = st.text_input("Evidence Title")
                            e_type = st.selectbox("Type", ["Screenshot", "PDF Extract", "Registry Document", "Analyst Note"])
                            e_desc = st.text_area("Description / Analyst Observations")
                            if st.form_submit_button("Add Evidence Reference"):
                                evidence.append({
                                    "name": e_name,
                                    "type": e_type,
                                    "description": e_desc,
                                    "added_at": datetime.now(timezone.utc).isoformat()
                                })
                                supabase.table("intelligence_requests").update({"evidence_attachments": evidence}).eq("id", req.get("id")).execute()
                                st.rerun()

                    with enrich_tabs[6]:
                        st.write("**Analyst Sign-off**")
                        with st.form(f"signoff_form_{req.get('id')}"):
                            a_name = st.text_input("Analyst Name", value=req.get("analyst_name") or "")
                            conf_lvl = st.select_slider("Confidence Level", options=["Low", "Medium", "High"], value=req.get("confidence_level", "Medium"))
                            rec_lvl = st.select_slider("Recommendation Level", options=["Standard Due Diligence", "Enhanced Due Diligence", "Escalation Recommended"], value=req.get("recommendation_level", "Standard Due Diligence"))
                            
                            if st.form_submit_button("Sign Off & Finalize"):
                                try:
                                    supabase.table("intelligence_requests").update({
                                        "analyst_name": a_name,
                                        "confidence_level": conf_lvl,
                                        "recommendation_level": rec_lvl,
                                        "analyst_timestamp": datetime.now(timezone.utc).isoformat(),
                                        "status": "Ready for Delivery"
                                    }).eq("id", req.get("id")).execute()
                                    st.success("Sign-off complete. Report marked as Ready for Delivery.")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Sign-off failed: {str(e)}")

                    st.markdown("---")
                    st.markdown("#### Report Generation")
                    gen_col1, gen_col2 = st.columns(2)
                    with gen_col1:
                        if st.button("Generate Institutional Report", key=f"gen_{req.get('id')}"):
                            with st.spinner("Generating 10+ page intelligence report..."):
                                try:
                                    import os
                                    # Versioning
                                    current_version = int(req.get("report_version") or 0) + 1
                                    
                                    # Generate PDF
                                    pdf_bytes = generate_pdf(req, req) 
                                    
                                    # Archival
                                    if not os.path.exists("generated_reports"):
                                        os.makedirs("generated_reports")
                                    
                                    v_name = (req.get('vessel_name') or 'Unknown').replace(' ', '_')
                                    imo = req.get('imo_number') or 'NOIMO'
                                    filename = f"ChaAVON_Report_{v_name}_{imo}_v{current_version}.pdf"
                                    filepath = os.path.join("generated_reports", filename)
                                    
                                    with open(filepath, "wb") as f:
                                        f.write(pdf_bytes)
                                    
                                    # Cloud Storage Upload
                                    storage_url = None
                                    try:
                                        bucket_name = "generated-reports"
                                        # Ensure unique cloud filename
                                        cloud_filename = f"{req.get('id')}_{filename}"
                                        
                                        # Simple binary upload
                                        supabase.storage.from_(bucket_name).upload(
                                            path=cloud_filename,
                                            file=pdf_bytes,
                                            file_options={"content-type": "application/pdf"}
                                        )
                                        
                                        # Get public URL
                                        res_url = supabase.storage.from_(bucket_name).get_public_url(cloud_filename)
                                        if res_url:
                                            storage_url = res_url
                                    except Exception as e:
                                        print(f"[STORAGE] Upload failed: {str(e)}")
                                    
                                    # Update Supabase
                                    update_payload = {
                                        "report_version": current_version,
                                        "report_path": filepath,
                                        "updated_at": datetime.now(timezone.utc).isoformat()
                                    }
                                    if storage_url:
                                        update_payload["report_storage_url"] = storage_url

                                    supabase.table("intelligence_requests").update(update_payload).eq("id", req.get("id")).execute()
                                    
                                    st.success(f"Report v{current_version} generated and archived (Cloud: {'Yes' if storage_url else 'Local Only'}).")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Generation failed: {str(e)}")

                    with gen_col2:
                        report_path = req.get("report_path")
                        if report_path:
                            st.write(f"Current Version: v{req.get('report_version')}")
                            if os.path.exists(report_path):
                                with open(report_path, "rb") as f:
                                    st.download_button(
                                        label="Download Archived Report",
                                        data=f.read(),
                                        file_name=os.path.basename(report_path),
                                        mime="application/pdf",
                                        use_container_width=True
                                    )
                            else:
                                st.info("Archived report file is not available on this instance yet. Regenerate the report to restore local download access.")
                        else:
                            st.info("No report generated for this request yet.")


def render_admin_page():
    render_top_nav()

    if not st.session_state.admin_authenticated:
        st.markdown('<div class="compact-panel">', unsafe_allow_html=True)
        st.title("Administrative Access")
        st.markdown('<div class="subtitle" style="text-align: left; margin-left: 0;">Authorized operational access only.</div>', unsafe_allow_html=True)
        st.markdown('<div style="height: 24px;"></div>', unsafe_allow_html=True)

        with st.form("admin_gate_form"):
            entered_pw = st.text_input("Enter Administrative Access Key", type="password")
            submit = st.form_submit_button("Access Control Panel")

            if submit:
                if bcrypt.checkpw(entered_pw.encode(), ADMIN_ACCESS_HASH.encode()):
                    st.session_state.admin_authenticated = True
                    persist_admin_session()
                    st.rerun()
                else:
                    st.error("Invalid access key.")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    render_admin_panel()


@st.cache_data
def load_data():
    import pandas as pd
    import os
    if not os.path.exists("data/sdn.csv"):
        st.error("SDN file not found. Place it in /data/sdn.csv")
        st.stop()
    if not os.path.exists("data/alt.csv"):
        st.error("ALT file not found. Place it in /data/alt.csv")
        st.stop()

    df = pd.read_csv("data/sdn.csv", header=None, encoding="latin-1")
    sdn = df[df[2] == 'vessel'][[1]]
    sdn.columns = ['name']
    sdn['name'] = sdn['name'].str.upper().str.strip()

    alt = pd.read_csv("data/alt.csv", header=None, encoding="latin-1")
    alt = alt[[2]]
    alt.columns = ['name']
    alt['name'] = alt['name'].str.upper().str.strip()

    sanctions_df = pd.concat([sdn, alt], ignore_index=True)
    sanctions_df = sanctions_df.dropna().drop_duplicates()
    sanctions_df["clean_name"] = sanctions_df["name"].astype(str).apply(clean_name)
    return sanctions_df["clean_name"].tolist()


def render_workspace_page():
    sync_access_state()
    
    user_email = st.session_state.user_email
    user = st.session_state.get("user") or {}
    expiry_display = st.session_state.get("expiry_display", "Not specified")

    # Top Navigation / Workspace Header
    st.markdown("## Vessel Intelligence Workspace")
    
    col_info, col_logout = st.columns([4, 1])
    with col_info:
        st.markdown(f"**Account:** {user_email} | **Company:** {user.get('company_type', 'N/A')} | **Access until:** {expiry_display}")
    with col_logout:
        if st.button("Logout Session", use_container_width=True):
            clear_all_auth_state()
            st.rerun()

    st.markdown("---")

    left_col, right_col = st.columns([1, 1.2], gap="large")

    with left_col:
        st.markdown("### Intelligence Request Submission")
        st.markdown('<div class="form-note">Submit target details for analyst-led maritime risk intelligence and deep-dive screening.</div>', unsafe_allow_html=True)
        
        with st.form("submission_form", clear_on_submit=True):
            v_name = st.text_input("Vessel Name")
            v_imo = st.text_input("IMO Number")
            v_flag = st.text_input("Flag State")
            v_cp = st.text_input("Charterer / Counterparty")
            v_owner = st.text_input("Beneficial Owner")
            v_juris = st.text_input("Primary Jurisdiction")
            v_notes = st.text_area("Operational Context / Special Instructions")
            
            submit_req = st.form_submit_button("Submit Intelligence Request")

        if submit_req:
            if not v_name.strip():
                st.warning("Vessel name is required.")
            else:
                try:
                    payload = {
                        "submitted_by": user_email,
                        "vessel_name": v_name.strip(),
                        "imo_number": v_imo.strip(),
                        "flag_state": v_flag.strip(),
                        "owner": v_owner.strip(),
                        "charterer": v_cp.strip(),
                        "jurisdiction": v_juris.strip(),
                        "operational_notes": v_notes.strip(),
                        "status": "Pending Review",
                        "created_at": datetime.now(timezone.utc).isoformat(),
                        "timeline_events": [],
                        "citations": [],
                        "port_calls": [],
                        "ownership_history": [],
                        "evidence_attachments": [],
                        "report_version": 0
                    }
                    supabase.table("intelligence_requests").insert(payload).execute()
                    st.success("Request submitted successfully. An analyst will begin investigation shortly.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Submission failed: {str(e)}")

    with right_col:
        active_tab, archive_tab = st.tabs(["Active Requests", "Archived Reports"])
        
        with active_tab:
            try:
                res = supabase.table("intelligence_requests").select("*").eq("submitted_by", user_email).neq("status", "Delivered").order("created_at", desc=True).execute()
                active_reqs = res.data or []
            except Exception:
                active_reqs = []
                st.error("Could not load active requests.")

            if not active_reqs:
                st.markdown('<div style="opacity: 0.5; text-align: center; padding-top: 50px;">No active requests.</div>', unsafe_allow_html=True)
            else:
                for r in active_reqs:
                    with st.expander(f"{r.get('vessel_name')} — {r.get('status')}", expanded=False):
                        st.write(f"**Submitted:** {r.get('created_at', '')[:10]}")
                        st.write(f"**IMO:** {r.get('imo_number') or 'N/A'}")
                        st.write(f"**Status:** {r.get('status')}")
                        if r.get("status") == "Under Investigation":
                            st.info("Analysts are currently enriching vessel information and AIS patterns.")
                        elif r.get("status") == "Ready for Delivery":
                            st.success("Analyst review complete. Finalizing delivery.")
                        else:
                            st.info("Request is in the global analyst queue.")

        with archive_tab:
            try:
                res = supabase.table("intelligence_requests").select("*").eq("submitted_by", user_email).eq("status", "Delivered").order("delivered_at", desc=True).execute()
                archived_reqs = res.data or []
            except Exception:
                archived_reqs = []
                st.error("Could not load archived reports.")

            if not archived_reqs:
                st.markdown('<div style="opacity: 0.5; text-align: center; padding-top: 50px;">No archived reports found.</div>', unsafe_allow_html=True)
            else:
                for r in archived_reqs:
                    with st.expander(f"📄 {r.get('vessel_name')} — Report v{r.get('report_version', 1)}", expanded=False):
                        st.write(f"**Delivered:** {r.get('delivered_at', '')[:10]}")
                        st.write(f"**IMO:** {r.get('imo_number') or 'N/A'}")
                        
                        report_path = r.get("report_path")
                        report_storage_url = r.get("report_storage_url")

                        if report_storage_url:
                            st.link_button("Download Intelligence Report (Cloud)", report_storage_url, use_container_width=True)
                        elif report_path and os.path.exists(report_path):
                            with open(report_path, "rb") as f:
                                st.download_button(
                                    label=f"Download Intelligence Report (PDF)",
                                    data=f.read(),
                                    file_name=os.path.basename(report_path),
                                    mime="application/pdf",
                                    key=f"dl_user_{r.get('id')}",
                                    use_container_width=True
                                )
                        else:
                            try:
                                pdf_bytes = generate_pdf(r, r)
                                st.download_button(
                                    label=f"Regenerate & Download (PDF)",
                                    data=pdf_bytes,
                                    file_name=f"ChaAVON_Intel_{r.get('vessel_name').replace(' ', '_')}.pdf",
                                    mime="application/pdf",
                                    key=f"dl_user_fallback_{r.get('id')}",
                                    use_container_width=True
                                )
                            except Exception as e:
                                st.error(f"Report generation error: {str(e)}")

    # Footer build version
    st.markdown(f'<div style="position: fixed; bottom: 10px; right: 20px; font-size: 10px; color: rgba(255,255,255,0.3);">Build {BUILD_VERSION}</div>', unsafe_allow_html=True)


page = st.session_state.page
if page == "home":
    render_landing_page()
elif page == "login":
    render_login_page()
elif page == "register":
    render_registration_page()
elif page == "payment":
    render_payment_page()
elif page == "terms":
    terms_page()
elif page == "admin":
    render_admin_page()
elif page == "workspace":
    render_workspace_page()
elif page == "dashboard":
    render_workspace_page()
else:
    render_landing_page()

if st.session_state.page != "workspace":
    render_footer()
