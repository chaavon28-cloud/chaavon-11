import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import re
from datetime import datetime
import streamlit as st
import pandas as pd
from supabase import create_client
from src.screening import clean_name, match_name, calculate_risk  # ✅ import from src
from src.pdf_generator import generate_pdf

SUPABASE_URL = "https://guqjmtgqaxperzxfsmel.supabase.co"
SUPABASE_KEY = "sb_publishable_SMWNZub4TscXI1SMEOaOww_HQ3sYELO"

st.set_page_config(
    page_title="Vessel Sanctions Screening",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    :root {
        --bank-bg: #000000;
        --bank-card: #111111;
        --bank-green: #00FF9C;
        --bank-text: #FFFFFF;
        --bank-muted: #B9C7C0;
        --bank-yellow: #FFD166;
        --bank-red: #FF4B4B;
    }

    .stApp {
        background: var(--bank-bg);
        color: var(--bank-text);
    }

    h1, h2, h3, .stMarkdown, label {
        color: var(--bank-text) !important;
    }

    h1 {
        font-weight: 800 !important;
        letter-spacing: 0;
        padding: 1rem 0 0.5rem 0;
    }

    .stMarkdown p {
        color: var(--bank-muted);
    }

    div[data-testid="stTextInput"] input,
    div[data-testid="stNumberInput"] input {
        background: #111111;
        color: #FFFFFF;
        border: 1px solid rgba(0, 255, 156, 0.55);
        border-radius: 12px;
        padding: 0.75rem;
    }

    div[data-testid="stTextInput"] input:focus,
    div[data-testid="stNumberInput"] input:focus {
        border-color: var(--bank-green);
        box-shadow: 0 0 0 1px var(--bank-green);
    }

    .stButton > button {
        background: var(--bank-green);
        color: #000000;
        border: 1px solid var(--bank-green);
        border-radius: 12px;
        font-weight: 800;
        padding: 0.65rem 1.2rem;
    }

    .stButton > button:hover {
        background: #33FFB1;
        border-color: #33FFB1;
        color: #000000;
    }

    .result-card {
        margin-top: 1.5rem;
        padding: 1.25rem;
        border: 1px solid var(--bank-green);
        border-radius: 12px;
        background: var(--bank-card);
    }

    .result-card h3 {
        margin: 0 0 0.75rem 0;
        color: var(--bank-text);
        font-weight: 800;
    }

    .status-match {
        color: var(--bank-red);
        font-weight: 800;
    }

    .status-clear {
        color: var(--bank-green);
        font-weight: 800;
    }

    .risk-row {
        margin-top: 1rem;
    }

    .risk-label {
        display: flex;
        justify-content: space-between;
        color: var(--bank-text);
        font-weight: 700;
        margin-bottom: 0.45rem;
    }

    .risk-track {
        width: 100%;
        height: 16px;
        border-radius: 999px;
        background: #242424;
        overflow: hidden;
        border: 1px solid #303030;
    }

    .risk-fill {
        height: 100%;
        border-radius: 999px;
        transition: width 0.9s ease;
        animation: riskPulse 1.1s ease-out;
    }

    @keyframes riskPulse {
        from {
            width: 0%;
        }
    }

    .report-section {
        min-height: 170px;
        padding: 1.1rem;
        border: 1px solid rgba(0, 255, 156, 0.45);
        border-radius: 12px;
        background: #111111;
    }

    .section-title {
        margin: 0 0 0.85rem 0;
        color: #FFFFFF;
        font-size: 1.05rem;
        font-weight: 800;
    }

    .badge {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        border-radius: 999px;
        color: #000000;
        font-size: 0.8rem;
        font-weight: 800;
    }

    .badge-low {
        background: var(--bank-green);
    }

    .badge-medium {
        background: var(--bank-yellow);
    }

    .badge-high {
        background: var(--bank-red);
        color: #FFFFFF;
    }

    .report-line {
        margin: 0.35rem 0;
        color: var(--bank-muted);
    }

    .report-line strong {
        color: var(--bank-text);
    }

    .access-card {
        padding: 1rem;
        border: 1px solid #00FF9C;
        border-radius: 12px;
        background: #111111;
        margin: 1rem 0;
    }

    .access-card h3 {
        color: #00FF9C !important;
        margin-top: 0;
    }

    .status-hero {
        font-size: 1.7rem;
        font-weight: 900;
        margin: 0 0 0.75rem 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

try:
    test = supabase.table("users_access").select("*").limit(1).execute()
    st.success("Supabase connected")
except Exception as e:
    st.error(f"Supabase connection failed: {e}")
    st.stop()

for key, default in {
    "authenticated": False,
    "checked_access": False,
    "user_email": "",
    "user": {},
    "expiry_display": "Not specified",
}.items():
    if key not in st.session_state:
        st.session_state[key] = default


def show_support_info():
    st.info("If you believe this is a mistake, contact support.")


def format_expiry(end_date):
    if not end_date:
        return "Not specified", None

    try:
        expiry = datetime.fromisoformat(str(end_date).replace("Z", ""))
    except Exception:
        return None, None

    return expiry.strftime("%Y-%m-%d %H:%M UTC"), expiry


def show_subscription_card():
    st.markdown("""
    <div class="access-card">
    <h3>Subscription Access</h3>

    <p><b>Price:</b> $1198 USD / 28 days</p>

    <p>
    After payment, access will be manually activated within 12 hours.<br>
    Subscription validity: <b>28 days from activation</b>.
    </p>

    <a href="https://www.paypal.com/ncp/payment/URXM2BPFFLHXC" target="_blank">
    <button style="
    background:#00FF9C;
    color:#000;
    padding:10px 16px;
    border:none;
    border-radius:10px;
    font-weight:800;
    cursor:pointer;
    ">
    Activate Access
    </button>
    </a>
    </div>
    """, unsafe_allow_html=True)


if not st.session_state.authenticated:
    st.title("Secure Access")
    show_subscription_card()

    user_email_input = st.text_input("Enter your registered email to access the platform")

    if st.button("Access Platform"):
        user_email_input = user_email_input.strip().lower()

        if not user_email_input:
            st.warning("Please enter your email to continue")
            show_support_info()
            st.stop()

        if not re.match(r"[^@]+@[^@]+\.[^@]+", user_email_input):
            st.error("Enter a valid email address")
            show_support_info()
            st.stop()

        with st.spinner("Validating access..."):
            try:
                response = supabase.table("users_access").select("*").eq("email", user_email_input).execute()
            except Exception:
                st.error("System temporarily unavailable. Try again shortly.")
                show_support_info()
                st.stop()

        st.session_state.checked_access = True

        if not response or not hasattr(response, "data") or not response.data:
            st.error("Access denied. Email not registered.")
            show_support_info()
            st.stop()

        user = response.data[0]
        approved = user.get("approved", False)
        end_date = user.get("end_date", None)

        if not approved:
            st.error("Access not approved yet.")
            show_support_info()
            st.stop()

        expiry_display, expiry = format_expiry(end_date)
        if expiry_display is None:
            st.error("Invalid account configuration. Contact support.")
            show_support_info()
            st.stop()

        if expiry and expiry < datetime.utcnow():
            st.error("Your access has expired.")
            show_support_info()
            st.stop()

        st.session_state.user_email = user_email_input
        st.session_state.user = user
        st.session_state.expiry_display = expiry_display
        st.session_state.authenticated = True
        st.rerun()

    st.stop()

if not st.session_state.get("authenticated"):
    st.stop()

user_email = st.session_state.user_email
user = st.session_state.user
expiry_display = st.session_state.expiry_display


@st.cache_data
def load_sdn_data():
    import pandas as pd
    import os
    if not os.path.exists("data/sdn.csv"):
        st.error("SDN file not found. Place it in /data/sdn.csv")
        st.stop()
    df = pd.read_csv("data/sdn.csv", header=None, encoding="latin-1")
    vessels = df[df[2] == 'vessel'][[1]]
    vessels.columns = ['name']
    vessels['name'] = vessels['name'].str.upper().str.strip()
    return vessels


@st.cache_data
def load_alt_names():
    import pandas as pd
    import os
    if not os.path.exists("data/alt.csv"):
        st.error("ALT file not found. Place it in /data/alt.csv")
        st.stop()
    alt = pd.read_csv("data/alt.csv", header=None, encoding="latin-1")
    alt = alt[[2]]
    alt.columns = ['name']
    alt['name'] = alt['name'].str.upper().str.strip()
    return alt


top_left, top_right = st.columns([4, 1])
with top_left:
    st.success(f"Access granted for {user_email}")
with top_right:
    if st.button("Reset Session"):
        st.session_state.clear()
        st.rerun()

st.markdown(f"""
<div style="
padding:0.8rem;
border:1px solid #00FF9C;
border-radius:10px;
background:#0c0c0c;
margin-bottom:1rem;
">
<p><b>Account:</b> {user_email}</p>
<p><b>Status:</b> {"APPROVED" if user.get("approved", False) else "NOT APPROVED"}</p>
<p><b>Expiry:</b> {expiry_display}</p>
</div>
""", unsafe_allow_html=True)

# --- Streamlit UI ---
st.title("Vessel Sanctions Screening for Crude Cargo")

st.write("Enter a vessel name to screen against the OFAC list.")

vessel_name = st.text_input("Enter Vessel Name")

ais_gap = st.number_input("AIS Gap (hours)", min_value=0, max_value=720, value=0)

run_check = st.button("Run Screening")

try:
    sdn = load_sdn_data()
    alt = load_alt_names()
    sanctions_df = pd.concat([sdn, alt], ignore_index=True)
    sanctions_df = sanctions_df.dropna().drop_duplicates()
    sanctions_df["clean_name"] = sanctions_df["name"].astype(str).apply(clean_name)
    sanctions_list = sanctions_df["clean_name"].tolist()
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
    risk_badge = "badge-low"
    recommendation = "Proceed with standard compliance review."
    if risk >= 70:
        risk_level = "High"
        risk_badge = "badge-high"
        risk_color = "#FF4B4B"
        recommendation = "Escalate for immediate compliance review before proceeding."
    elif risk >= 40:
        risk_level = "Medium"
        risk_badge = "badge-medium"
        risk_color = "#FFD166"
        recommendation = "Review supporting vessel activity and sanctions context."
    else:
        risk_color = "#00FF9C"

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
    except:
        pass

    st.markdown('<div class="result-card">', unsafe_allow_html=True)
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
                <p class="report-line"><strong>Risk Level:</strong> <span class="badge {risk_badge}">{risk_level}</span></p>
                <p class="report-line"><strong>Score:</strong> {risk}/100</p>
                <p class="report-line"><strong>Recommendation:</strong> {recommendation}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with screening_col:
        match_status = "Yes" if flag else "No"
        match_badge = "badge-high" if flag else "badge-low"
        confidence = score if flag else 0
        matched_entity = match if flag else "None"
        st.markdown(
            f"""
            <div class="report-section">
                <div class="section-title">Sanctions Screening</div>
                <p class="report-line"><strong>Match:</strong> <span class="badge {match_badge}">{match_status}</span></p>
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
                <div class="risk-fill" style="width: {risk_width}%; background: {risk_color};"></div>
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
        label="📄 Download Compliance Report",
        data=pdf_bytes,
        file_name=f"compliance_report_{vessel_name}.pdf",
        mime="application/pdf"
    )

    st.markdown("</div>", unsafe_allow_html=True)
