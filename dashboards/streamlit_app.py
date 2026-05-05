import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import re
from datetime import datetime
import streamlit as st
from supabase import create_client
from src.screening import clean_name, match_name, calculate_risk
from src.pdf_generator import generate_pdf

SUPABASE_URL = "https://guqjmtgqaxperzxfsmel.supabase.co"
SUPABASE_KEY = "sb_publishable_SMWNZub4TscXI1SMEOaOww_HQ3sYELO"
PAYPAL_URL = "https://www.paypal.com/ncp/payment/URXM2BPFFLHXC"
LOGO_PATH = "assets/logo.png"

st.set_page_config(
    page_title="ChaAVON — Structured intelligence for high-stakes decisions.",
    page_icon="assets/logo.png",
    layout="wide",
    initial_sidebar_state="collapsed",
)

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
        background: var(--bg);
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
        box-shadow: 0 0 0 1px var(--green);
    }

    .stButton > button,
    .stDownloadButton > button,
    .stLinkButton > a {
        background: var(--green);
        color: var(--text);
        border: 1px solid var(--green);
        border-radius: 999px;
        font-weight: 800;
        padding: 0.7rem 1.35rem;
    }

    .stButton > button:hover,
    .stDownloadButton > button:hover,
    .stLinkButton > a:hover {
        background: var(--green);
        border-color: var(--green);
        color: var(--text);
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

    .hero {
        min-height: 520px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
    }

    .hero-orb {
        width: 460px;
        height: 460px;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(0, 96, 57, 0.18) 0%, rgba(0, 96, 57, 0.04) 45%, rgba(0, 0, 0, 0) 70%);
        filter: blur(12px);
        pointer-events: none;
        margin: 0 auto -360px auto;
    }

    .hero-grid {
        align-items: center;
        gap: 1rem;
    }

    .hero-column {
        display: flex;
        flex-direction: column;
        gap: 22px;
        justify-content: center;
    }

    .floating-card {
        width: 100%;
        padding: 18px 18px 16px 18px;
        background: rgba(17, 17, 17, 0.92);
        border: 1px solid rgba(0, 96, 57, 0.7);
        border-radius: 16px;
        box-shadow: 0 26px 60px rgba(0, 0, 0, 0.42);
        backdrop-filter: blur(10px);
        text-align: left;
    }

    .floating-kicker {
        font-size: 0.72rem;
        font-weight: 800;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        color: var(--green);
        margin-bottom: 0.6rem;
    }

    .floating-title {
        font-size: 1rem;
        font-weight: 700;
        color: var(--text);
        margin-bottom: 0.45rem;
    }

    .floating-copy {
        font-size: 0.92rem;
        line-height: 1.55;
        color: var(--muted);
    }

    .hero-stack {
        max-width: 760px;
        padding: 0 24px;
    }

    .hero-title {
        color: var(--text);
        font-size: 88px;
        font-weight: 700;
        line-height: 1;
        margin: 0;
        letter-spacing: -2px;
    }

    .hero-sub {
        font-size: 22px;
        text-align: center;
        color: #9CA3AF;
        margin-top: 12px;
    }

    .section-title {
        font-size: 42px;
        font-weight: 600;
        margin: 0 0 20px 0;
        color: var(--text);
    }

    .section-text {
        font-size: 18px;
        color: #9CA3AF;
        line-height: 1.8;
    }

    .premium-block {
        background: linear-gradient(180deg, rgba(17, 17, 17, 0.96) 0%, rgba(10, 10, 10, 0.98) 100%);
        border: 1px solid var(--line);
        border-radius: 28px;
        padding: 52px;
        box-shadow: 0 24px 60px rgba(0, 0, 0, 0.35);
    }

    .green-strip {
        margin-top: 36px;
        padding-top: 28px;
        border-top: 1px solid rgba(0, 96, 57, 0.5);
        color: var(--green);
        font-size: 0.95rem;
        font-weight: 800;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        line-height: 1.9;
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

    @media (max-width: 760px) {
        .navbar {
            padding: 16px 0 20px 0;
        }

        .hero-title {
            font-size: 56px;
        }

        .hero {
            min-height: 460px;
        }

        .hero-grid {
            gap: 0;
        }

        .hero-column {
            margin-top: 1rem;
        }

        .hero-stack {
            padding: 40px 0;
        }

        .premium-block {
            padding: 32px 24px;
        }

        .container {
            padding: 40px 16px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

for key, default in {
    "page": "home",
    "authenticated": False,
    "user_email": "",
    "user_name": "",
    "company_type": "",
    "user": {},
    "expiry_display": "Not specified",
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

allowed_pages = {"home", "register", "payment", "access", "terms", "app"}
page_param = st.query_params.get("page")
if page_param in allowed_pages and st.session_state.page != page_param:
    st.session_state.page = page_param


def go_to(page):
    st.session_state.page = page
    st.query_params["page"] = page
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


def render_top_nav():
    st.markdown(
        f"""
        <div class="navbar">
            <a class="brand-link" href="?page=home">
                <img class="logo" src="data:image/png;base64,{logo_base64()}" />
                <div class="brand">ChaAVON</div>
            </a>
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


def render_landing_page():
    render_top_nav()
    st.markdown('<div class="container">', unsafe_allow_html=True)
    left, center, right = st.columns([1, 2, 1], gap="large")

    with left:
        st.markdown('<div class="hero-column">', unsafe_allow_html=True)
        st.markdown(
            """
            <div class="floating-card">
                <div class="floating-kicker">Intelligence</div>
                <div class="floating-title">Risk Intelligence</div>
                <div class="floating-copy">Structured counterparty risk evaluation using deterministic models.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            """
            <div class="floating-card">
                <div class="floating-kicker">Controls</div>
                <div class="floating-title">Audit Integrity</div>
                <div class="floating-copy">Every decision is recorded, traceable, and defensible.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with center:
        st.markdown(
            """
            <section class="hero">
                <div class="hero-orb"></div>
                <div class="hero-stack">
                    <div class="hero-title">ChaAVON</div>
                    <div class="hero-sub">Structured intelligence for high-stakes decisions.</div>
                </div>
            </section>
            """,
            unsafe_allow_html=True,
        )
        st.markdown('<div class="cta-wrap">', unsafe_allow_html=True)
        _, cta_col, _ = st.columns([1.2, 1, 1.2])
        with cta_col:
            if st.button("Join Now", key="hero_join", use_container_width=True):
                go_to("register")
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown('<div class="hero-column">', unsafe_allow_html=True)
        st.markdown(
            """
            <div class="floating-card">
                <div class="floating-kicker">Exposure</div>
                <div class="floating-title">Counterparty Controls</div>
                <div class="floating-copy">Entity matching, jurisdiction exposure, and behavioral risk signals.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            """
            <div class="floating-card">
                <div class="floating-kicker">Platform</div>
                <div class="floating-title">Controlled Access</div>
                <div class="floating-copy">Approval-gated platform with enforced subscription lifecycle.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(
        """
        <div class="container">
            <div class="divider"></div>
            <div class="section-title">What We Do</div>
            <div class="premium-block">
                <div class="section-text">
                    <p>ChaAVON provides institutional-grade intelligence infrastructure for maritime compliance, sanctions screening, and counterparty risk analysis.</p>
                    <p>We replace fragmented workflows with a unified system that enforces verification, standardizes decision-making, and preserves auditability across every interaction.</p>
                    <p>Each screening output is generated through deterministic scoring models, ensuring consistency, transparency, and repeatability across jurisdictions and datasets.</p>
                    <p>Our platform is designed for environments where errors are unacceptable, oversight is mandatory, and every decision must be defensible under scrutiny.</p>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="container">
            <div class="divider"></div>
            <div class="section-title">Execution Guarantees</div>
            <div class="premium-block">
                <div class="section-text">
                    <p>Matching is deterministic. Assignments are produced by explicit scoring logic, not opaque recommendation systems.</p>
                    <p>Payments are escrow-first. Funds are committed before work begins and released only through verified completion paths.</p>
                    <p>Execution is dispute-locked. Active disputes suspend resolution, payout, and closure until formally resolved.</p>
                    <p>Audit trails are immutable. Every action, transition, and decision is recorded and preserved.</p>
                </div>
                <div class="green-strip">
                    ALL ACTIONS ARE LOGGED.<br>
                    ALL EXECUTION PATHS ARE BOUNDED.<br>
                    ALL OUTCOMES ARE REVIEWABLE.
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_registration_page():
    render_top_nav()
    st.markdown('<div class="compact-panel panel">', unsafe_allow_html=True)
    st.title("Request Access")
    st.markdown(
        '<div class="form-note">Submit your registration details to request controlled platform access. Access is reviewed manually and activated only after approval.</div>',
        unsafe_allow_html=True,
    )
    name = st.text_input("Full Name", value=st.session_state.get("user_name", ""))
    email = st.text_input("Email", value=st.session_state.get("user_email", ""))
    password = st.text_input("Password", type="password")
    company_options = ["Trading Firm", "Broker", "Bank", "Other"]
    default_company = st.session_state.get("company_type", company_options[0])
    company_index = company_options.index(default_company) if default_company in company_options else 0
    company = st.selectbox("Company Type", company_options, index=company_index)

    if st.button("Continue"):
        name = name.strip()
        email = email.strip().lower()
        password = password.strip()

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
                existing = supabase.table("users_access").select(
                    "email, approved, end_date, is_active, expiry_date, start_date"
                ).eq("email", email).execute()
                if existing and hasattr(existing, "data") and existing.data:
                    existing_approved = existing.data[0].get("approved", False)
                    existing_end_date = existing.data[0].get("end_date")
                    is_active = existing.data[0].get("is_active", False)
                    expiry_date = existing.data[0].get("expiry_date")
                    start_date = existing.data[0].get("start_date")
                else:
                    is_active = False
                    expiry_date = None
                    start_date = None

                # The live users_access table currently supports access fields only.
                payload = {
                    "email": email,
                    "is_active": is_active,
                    "expiry_date": expiry_date,
                    "approved": existing_approved,
                    "start_date": start_date,
                    "end_date": existing_end_date,
                }
                supabase.table("users_access").upsert(payload, on_conflict="email").execute()
            except Exception:
                st.error("Registration could not be saved. Please retry.")
                st.stop()

        st.session_state.user_name = name
        st.session_state.user_email = email
        st.session_state.company_type = company
        go_to("payment")

    st.markdown("</div>", unsafe_allow_html=True)


def render_payment_page():
    render_top_nav()
    st.markdown('<div class="compact-panel panel">', unsafe_allow_html=True)
    st.title("Subscription Access")
    st.markdown(
        """
        <p><strong>Plan:</strong> Vessel Sanctions Intelligence Platform</p>
        <p><strong>Price:</strong> $1198 USD / month</p>
        """,
        unsafe_allow_html=True,
    )
    st.link_button("Pay Now", PAYPAL_URL)
    st.markdown("Access activated after approval")

    if st.button("I Have Paid"):
        go_to("access")

    st.markdown("</div>", unsafe_allow_html=True)


def render_access_check_page():
    render_top_nav()
    st.markdown('<div class="compact-panel panel">', unsafe_allow_html=True)
    st.title("Access Check")
    user_email = st.text_input("Email", value=st.session_state.get("user_email", ""))

    if st.button("Check Access"):
        user_email = user_email.strip().lower()

        if not is_valid_email(user_email):
            st.error("Enter a valid email address")
            st.stop()

        with st.spinner("Validating access..."):
            try:
                response = supabase.table("users_access").select("*").eq("email", user_email).execute()
            except Exception:
                st.error("System temporarily unavailable. Try again shortly.")
                st.stop()

        if not response or not hasattr(response, "data") or not response.data:
            st.warning("Access pending approval")
            st.stop()

        user = response.data[0]
        approved = user.get("approved", False)
        end_date = user.get("end_date", None)
        expiry_display, expiry = format_expiry(end_date)

        if expiry_display is None:
            st.warning("Access pending approval")
            st.stop()

        if approved and expiry >= datetime.utcnow():
            st.session_state.user_email = user_email
            st.session_state.user = user
            st.session_state.expiry_display = expiry_display
            st.session_state.authenticated = True
            go_to("app")

        st.warning("Access pending approval")
        st.markdown(f"Valid until: {expiry_display}")

    st.markdown("</div>", unsafe_allow_html=True)


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


def render_main_app():
    if not st.session_state.get("authenticated"):
        st.session_state.page = "home"
        st.query_params["page"] = "home"
        st.stop()

    user_email = st.session_state.user_email
    user = st.session_state.user
    expiry_display = st.session_state.expiry_display

    top_left, top_mid, top_right = st.columns([3, 2, 1])
    with top_left:
        st.success(f"Access granted for {user_email}")
    with top_mid:
        st.markdown(f"Valid until: {expiry_display}")
    with top_right:
        if st.button("Logout"):
            st.session_state.clear()
            st.rerun()

    st.markdown(f"""
    <div class="panel">
    <p><b>Account:</b> {user_email}</p>
    <p><b>Status:</b> {"APPROVED" if user.get("approved", False) else "NOT APPROVED"}</p>
    <p><b>Expiry:</b> {expiry_display}</p>
    </div>
    """, unsafe_allow_html=True)

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
elif page == "register":
    render_registration_page()
elif page == "payment":
    render_payment_page()
elif page == "access":
    render_access_check_page()
elif page == "terms":
    terms_page()
elif page == "app":
    render_main_app()
else:
    st.session_state.page = "home"
    st.query_params["page"] = "home"
    st.rerun()

if st.session_state.page != "app":
    render_footer()
