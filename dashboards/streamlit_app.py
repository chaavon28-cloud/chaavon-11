import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import date, datetime
import streamlit as st
import pandas as pd
from dotenv import load_dotenv
from supabase import create_client
from src.screening import clean_name, match_name, calculate_risk  # ✅ import from src
from src.pdf_generator import generate_pdf

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
    </style>
    """,
    unsafe_allow_html=True,
)

load_dotenv()
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

if not supabase_url or not supabase_key:
    st.error("Supabase environment variables are not configured.")
    st.stop()

supabase = create_client(supabase_url, supabase_key)


def parse_expiry_date(expiry_date):
    if isinstance(expiry_date, date):
        return expiry_date
    return datetime.fromisoformat(str(expiry_date).replace("Z", "+00:00")).date()


def validate_user_access(user_email):
    response = (
        supabase.table("users_access")
        .select("is_active, expiry_date")
        .eq("email", user_email)
        .limit(1)
        .execute()
    )

    if not response.data:
        st.error("Access denied.")
        st.stop()

    access = response.data[0]

    if not access.get("is_active"):
        st.error("Access inactive.")
        st.stop()

    expiry_date = parse_expiry_date(access.get("expiry_date"))
    if expiry_date < date.today():
        st.error("Access expired.")
        st.stop()

    return access


if "user" not in st.session_state:
    st.session_state["user"] = None

if not st.session_state["user"]:
    st.subheader("Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Sign In"):
        try:
            auth_response = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password,
            })
            st.session_state["user"] = auth_response.user
            st.rerun()
        except Exception as exc:
            st.error(f"Login failed: {exc}")

    st.stop()

user_email = st.session_state["user"].email
user_data = validate_user_access(user_email)

st.markdown(f"""
<div style="
padding:0.8rem;
border:1px solid #00FF9C;
border-radius:10px;
background:#0c0c0c;
margin-bottom:1rem;
">
<p><b>Account:</b> {user_email}</p>
<p><b>Status:</b> {"ACTIVE" if user_data["is_active"] else "INACTIVE"}</p>
<p><b>Expiry:</b> {user_data["expiry_date"]}</p>
</div>
""", unsafe_allow_html=True)


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


# --- Streamlit UI ---
st.title("Vessel Sanctions Screening for Crude Cargo")

st.markdown("""
<div style="
padding: 1rem;
border: 1px solid #00FF9C;
border-radius: 12px;
background: #111111;
margin-bottom: 1rem;
">
<h3 style="color:#00FF9C;">Subscription Access</h3>

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

st.write("Enter a vessel name to screen against the OFAC list.")

vessel_name = st.text_input("Enter Vessel Name")

ais_gap = st.number_input("AIS Gap (hours)", min_value=0, max_value=720, value=0)

run_check = st.button("Run Screening")

sdn = load_sdn_data()
alt = load_alt_names()
sanctions_df = pd.concat([sdn, alt], ignore_index=True)
sanctions_df = sanctions_df.dropna().drop_duplicates()
sanctions_df["clean_name"] = sanctions_df["name"].astype(str).apply(clean_name)
sanctions_list = sanctions_df["clean_name"].tolist()

if run_check:
    if not vessel_name.strip():
        st.warning("Please enter a vessel name")
        st.stop()

    clean_vessel = clean_name(vessel_name)
    match, score, flag = match_name(clean_vessel, sanctions_list)

    risk = calculate_risk(flag, score, ais_gap)
    risk_level = "Low"
    risk_badge = "badge-low"
    recommendation = "Proceed with standard compliance review."
    if risk >= 70:
        risk_level = "High"
        risk_badge = "badge-high"
        recommendation = "Escalate for immediate compliance review before proceeding."
    elif risk >= 40:
        risk_level = "Medium"
        risk_badge = "badge-medium"
        recommendation = "Review supporting vessel activity and sanctions context."

    flags_triggered = []
    if flag:
        flags_triggered.append("Sanctions match")
    if ais_gap >= 24:
        flags_triggered.append("AIS gap >= 24 hours")
    flags_text = ", ".join(flags_triggered) if flags_triggered else "No risk flags triggered"

    st.markdown('<div class="result-card">', unsafe_allow_html=True)
    st.header("Compliance Report")

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
                <p class="report-line"><strong>Matched Entity:</strong> {matched_entity}</p>
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

    st.markdown("### Risk Score")
    st.progress(min(max(int(risk), 0), 100))
    st.metric("Risk Score", f"{risk}/100")

    pdf_bytes = generate_pdf(vessel_name, match, score, risk)

    st.download_button(
        label="📄 Download Compliance Report",
        data=pdf_bytes,
        file_name=f"compliance_report_{vessel_name}.pdf",
        mime="application/pdf"
    )

    st.markdown("</div>", unsafe_allow_html=True)
