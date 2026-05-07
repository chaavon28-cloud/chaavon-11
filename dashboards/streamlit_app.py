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


def reset_auth_state():
    st.session_state.authenticated = False
    st.session_state.user_email = None
    st.session_state.payment_done = False
    st.session_state.approved = False
    st.session_state.user_name = ""
    st.session_state.company_type = ""
    st.session_state.user = {}
    st.session_state.expiry_display = "Not specified"
    st.session_state.access_status = "pending"
    st.session_state.dashboard_log_written = False


def restore_session():
    payload = auth_session_payload()
    if not payload:
        return

    session_email = str(payload.get("email", "")).strip().lower()
    issued_at = payload.get("issued_at")
    if not session_email or not issued_at:
        clear_auth_session()
        return

    record = get_user_record(session_email)
    if not record:
        reset_auth_state()
        clear_auth_session()
        set_page("home")
        return

    record_last_login = record.get("last_login")
    if not record_last_login:
        reset_auth_state()
        clear_auth_session()
        set_page("home")
        return

    try:
        if parse_timestamp(record_last_login) != parse_timestamp(issued_at):
            reset_auth_state()
            clear_auth_session()
            set_page("home")
            return
    except Exception:
        reset_auth_state()
        clear_auth_session()
        set_page("home")
        return

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


def sync_access_state():
    user_email = st.session_state.user_email
    if not user_email:
        return

    record = get_user_record(user_email)
    if not record:
        st.session_state.approved = False
        st.session_state.payment_done = False
        st.session_state.access_status = "expired"
        st.session_state.user = {}
        if st.session_state.authenticated:
            set_page("payment")
        return

    st.session_state.user = record
    st.session_state.approved = bool(record.get("approved"))
    st.session_state.user_name = record.get("name") or st.session_state.user_name
    st.session_state.company_type = record.get("company_type") or st.session_state.company_type

    if record.get("end_date"):
        st.session_state.payment_done = bool(record.get("payment_done", True))
        try:
            raw_end = str(record["end_date"]).replace("Z", "")
            # Parse date and normalize to end of day UTC
            if " " in raw_end:
                end_date = datetime.fromisoformat(raw_end.split(" ")[0])
            elif "T" in raw_end:
                end_date = datetime.fromisoformat(raw_end.split("T")[0])
            else:
                end_date = datetime.fromisoformat(raw_end)
            
            # Normalize to 23:59:59 UTC of that day
            end_date = end_date.replace(hour=23, minute=59, second=59, tzinfo=timezone.utc)
            
            st.session_state.expiry_display = end_date.strftime("%Y-%m-%d")
            
            if end_date < datetime.now(timezone.utc):
                st.session_state.approved = False
                st.session_state.payment_done = False
                st.session_state.access_status = "expired"
                set_page("payment")
                save_user_record(user_email, {"approved": False, "payment_done": False})
                log_access_event(user_email, "expiry")
                return
        except Exception as e:
            st.error(f"Expiry sync error: {str(e)}")
            st.session_state.approved = False
            st.session_state.payment_done = False
            st.session_state.access_status = "expired"
            set_page("payment")
            return
    else:
        st.session_state.payment_done = bool(record.get("payment_done", False))
        st.session_state.expiry_display = "Not specified"

    if st.session_state.approved:
        st.session_state.access_status = "active"
    elif st.session_state.payment_done:
        st.session_state.access_status = "pending"
    else:
        st.session_state.access_status = "pending"


restore_session()
restore_admin_session()
sync_access_state()

requested_page = st.query_params.get("page")
if requested_page in {"home", "login", "register", "payment", "terms", "dashboard", "admin"}:
    st.session_state.page = str(requested_page)

if st.session_state.authenticated and st.session_state.page in {"login", "register"}:
    set_page("dashboard" if st.session_state.approved else "payment")


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
            if st.button("Enter Intelligence Workspace →", key="workspace_cta"):
                if st.session_state.approved:
                    set_page("dashboard")
                else:
                    set_page("payment")
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
        set_page("dashboard" if st.session_state.approved else "payment")
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
            set_page("dashboard")
        else:
            set_page("payment")
        st.rerun()


def render_payment_page():
    if st.session_state.approved:
        set_page("dashboard")
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
            set_page("dashboard")
        st.rerun()

    if st.session_state.payment_done and not st.session_state.approved:
        st.info(
            "Your account is awaiting approval. "
            "Access is activated manually after review."
        )

    st.caption("Access activated after approval")


def render_admin_panel():
    st.markdown("### Operational Control")
    st.markdown('<div class="subtitle" style="text-align: left; margin-left: 0; margin-bottom: 24px;">Manage platform access, approvals, and subscription cycles.</div>', unsafe_allow_html=True)

    col_logout, col_empty = st.columns([1, 4])
    with col_logout:
        if st.button("Logout Admin", key="admin_logout_btn", use_container_width=True):
            st.session_state.admin_authenticated = False
            clear_admin_session()
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
        return

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


def dashboard_page():
    sync_access_state()
    if not st.session_state.approved:
        set_page("payment")
        st.session_state.status_notice = "Access approval required."
        st.warning("Access approval required.")
        st.rerun()

    user_email = st.session_state.user_email
    user = st.session_state.user
    expiry_display = st.session_state.expiry_display

    top_left, top_mid, top_right = st.columns([3, 2, 1])
    with top_left:
        st.success("Access Granted")
    with top_mid:
        st.markdown(f"Valid until: {expiry_display}")
    with top_right:
        if st.button("Logout"):
            log_access_event(user_email, "logout")
            try:
                save_user_record(user_email, {"last_login": None})
            except Exception:
                pass
            clear_auth_session()
            clear_route_params()
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

    st.markdown(f"""
    <div class="panel">
    <p><b>Account:</b> {user_email}</p>
    <p><b>Status:</b> {"APPROVED" if user.get("approved", False) else "NOT APPROVED"}</p>
    <p><b>Expiry:</b> {expiry_display}</p>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.dashboard_log_written:
        log_access_event(user_email, "dashboard_access")
        st.session_state.dashboard_log_written = True

    if st.session_state.admin_authenticated:
        render_admin_panel()

    st.title("Vessel Sanctions Screening for Crude Cargo")
    st.markdown("Enter a vessel name to screen against the OFAC list.")

    vessel_name = st.text_input("Enter Vessel Name")
    ais_gap = st.number_input("AIS Gap (hours)", min_value=0, max_value=720, value=0)
    run_check = st.button("Run Screening")

    try:
        sanctions_list = load_data()
    except Exception:
        st.error("Sanctions data failed to load. Please retry.")
        st.stop()

    if not sanctions_list:
        st.error("Sanctions data is unavailable. Please retry.")
        st.stop()

    if run_check:
        if not vessel_name.strip():
            st.warning("Please enter a vessel name")
            st.stop()

        clean_vessel = clean_name(vessel_name)
        with st.spinner("Running sanctions screening..."):
            try:
                match, score, flag = match_name(clean_vessel, sanctions_list)
            except Exception:
                st.error("Screening failed. Please retry.")
                st.stop()

        try:
            risk = calculate_risk(flag, score, ais_gap)
        except Exception:
            st.error("Risk calculation failed. Please retry.")
            st.stop()

        risk_level = "Low"
        risk_badge = "badge"
        recommendation = "Proceed with standard compliance review."
        if risk >= 70:
            risk_level = "High"
            recommendation = "Escalate for immediate compliance review before proceeding."
        elif risk >= 40:
            risk_level = "Medium"
            recommendation = "Review supporting vessel activity and sanctions context."

        flags_triggered = []
        if flag:
            flags_triggered.append("Sanctions match")
        if ais_gap >= 24:
            flags_triggered.append("AIS gap >= 24 hours")
        flags_text = ", ".join(flags_triggered) if flags_triggered else "No risk flags triggered"

        try:
            supabase.table("usage_logs").insert({
                "email": user_email,
                "timestamp": datetime.utcnow().isoformat()
            }).execute()
        except Exception:
            pass

        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.header("Compliance Report")
        st.markdown(
            f"""
            <p class="status-hero {'status-match' if flag else 'status-clear'}">
                {'Sanctions Match Found' if flag else 'No Sanctions Match Found'}
            </p>
            """,
            unsafe_allow_html=True,
        )

        summary_col, screening_col, indicators_col = st.columns(3)

        with summary_col:
            st.markdown(
                f"""
                <div class="report-section">
                    <div class="section-title">Executive Summary</div>
                    <p class="report-line"><strong>Risk Level:</strong> <span class="{risk_badge}">{risk_level}</span></p>
                    <p class="report-line"><strong>Score:</strong> {risk}/100</p>
                    <p class="report-line"><strong>Recommendation:</strong> {recommendation}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with screening_col:
            match_status = "Yes" if flag else "No"
            confidence = score if flag else 0
            matched_entity = match if flag else "None"
            st.markdown(
                f"""
                <div class="report-section">
                    <div class="section-title">Sanctions Screening</div>
                    <p class="report-line"><strong>Match:</strong> <span class="badge">{match_status}</span></p>
                    <p class="report-line"><strong>Confidence:</strong> {confidence}</p>
                    <p class="report-line"><strong>Matched Vessel:</strong> {matched_entity}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with indicators_col:
            st.markdown(
                f"""
                <div class="report-section">
                    <div class="section-title">Risk Indicators</div>
                    <p class="report-line"><strong>AIS Gap:</strong> {ais_gap} hours</p>
                    <p class="report-line"><strong>Flags Triggered:</strong> {flags_text}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        risk_width = min(max(int(risk), 0), 100)
        st.markdown(
            f"""
            <div class="risk-row">
                <div class="risk-label">
                    <span>Risk Score</span>
                    <span>{risk}/100</span>
                </div>
                <div class="risk-track">
                    <div class="risk-fill" style="width: {risk_width}%;"></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.metric("Risk Score", f"{risk}/100")

        try:
            pdf_bytes = generate_pdf(vessel_name, match, score, risk)
        except Exception:
            st.error("Report generation failed. Please retry.")
            st.stop()

        st.download_button(
            label="Download Compliance Report",
            data=pdf_bytes,
            file_name=f"compliance_report_{vessel_name}.pdf",
            mime="application/pdf"
        )

        st.markdown("</div>", unsafe_allow_html=True)


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
elif page == "dashboard":
    dashboard_page()
else:
    render_landing_page()

if st.session_state.page != "dashboard":
    render_footer()
