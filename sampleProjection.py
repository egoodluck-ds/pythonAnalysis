
import streamlit as st
import pandas as pd

# ============================================================
# PAGE CONFIGURATION
# ============================================================
st.set_page_config(
    page_title="ESPN Sample Projection Dashboard",
    layout="wide"
)

# ============================================================
# BRANDING & STYLING
# ============================================================
NCDC_GREEN = "#196806"

st.markdown(f"""
<style>

/* Page background */
.stApp {{
    background-color: #FFFFFF;
}}

/* Main title */
.main-header h1 {{
    color: {NCDC_GREEN};
    font-weight: 900;
    text-align: center;
}}

/* Subheadings */
h2, h3, .stSubheader {{
    color: {NCDC_GREEN} !important;
    font-weight: 800;
}}

/* Metric cards */
div.stMetric {{
    background: #FFFFFF;
    padding: 10px;
    border-radius: 8px;
    border-left: 5px solid {NCDC_GREEN};
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}}

div[data-testid="stMetricValue"] {{
    color: {NCDC_GREEN};
    font-weight: 900;
}}

.center {{
    display: flex;
    justify-content: center;
}}

</style>
""", unsafe_allow_html=True)

# ============================================================
# HEADER
# ============================================================
col_logo, col_title, _ = st.columns([1, 4, 1])

with col_logo:
    st.image("espn_logo.jpg", width=110)

with col_title:
    st.markdown(
        "<div class='main-header'><h1>ESPN Sample Projection Dashboard</h1></div>",
        unsafe_allow_html=True
    )

# ============================================================
# HISTORICAL BASELINE (LOCKED)
# ============================================================
TOTAL_TARGET = 1296
SAMPLES_PER_VISIT = 2

# Phase 1: Aug–Oct 2025 (15 sites)
PHASE1_SITES = 15
PHASE1_MONTHS = 3
PHASE1_COLLECTED = PHASE1_SITES * 1 * SAMPLES_PER_VISIT * PHASE1_MONTHS

# Phase 2: Nov 2025–Apr 2026 (18 sites)
PHASE2_SITES = 18
PHASE2_MONTHS = 6
PHASE2_COLLECTED = PHASE2_SITES * 1 * SAMPLES_PER_VISIT * PHASE2_MONTHS

BASELINE_COLLECTED = PHASE1_COLLECTED + PHASE2_COLLECTED
REMAINING_SAMPLES = TOTAL_TARGET - BASELINE_COLLECTED

# ============================================================
# INPUT AREA
# ============================================================
st.markdown("### Input Parameters")

months = [
    "May 2026", "June 2026", "July 2026", "August 2026", "September 2026",
    "October 2026", "November 2026", "December 2026",
    "January 2027", "February 2027", "March 2027", "April 2027",
    "May 2027", "June 2027", "July 2027", "August 2027"
]

colA, colB, colC, colD = st.columns(4)

with colA:
    st.metric("Baseline Collected (Aug 2025–Apr 2026)", f"{BASELINE_COLLECTED:,}")
    start_month = st.selectbox("Projection Start Month", months)

with colB:
    base_sites = st.number_input("Sites Active from Start Month", min_value=1, value=18)
    freq_label = st.selectbox("Current Frequency", ["Once", "Twice"])
    base_frequency = 1 if freq_label == "Once" else 2

with colC:
    freq_change_month = st.selectbox("Month Frequency Changes", ["None"] + months)
    new_freq_label = st.selectbox("New Frequency", ["Once", "Twice"])
    new_frequency = 1 if new_freq_label == "Once" else 2

with colD:
    site_change_month = st.selectbox("Month New Sites Start", ["None"] + months)
    added_sites = st.number_input("Additional Sites", min_value=0, value=0)

# ============================================================
# SIMULATION ENGINE
# ============================================================
def simulate():
    remaining = REMAINING_SAMPLES
    sites = base_sites
    freq = base_frequency

    start_idx = months.index(start_month)
    idx = start_idx
    rows = []

    while remaining > 0:
        month = months[idx]

        if freq_change_month != "None" and month == freq_change_month:
            freq = new_frequency

        if site_change_month != "None" and month == site_change_month:
            sites += added_sites

        monthly_capacity = sites * freq * SAMPLES_PER_VISIT
        remaining -= monthly_capacity

        rows.append({
            "Month": month,
            "Active Sites": sites,
            "Frequency": freq,
            "Monthly Samples": monthly_capacity,
            "Remaining Samples": max(remaining, 0)
        })

        idx += 1

    return pd.DataFrame(rows)

df = simulate()

# ============================================================
# RESULTS SUMMARY
# ============================================================
st.markdown("### Projection Summary")

c1, c2, c3 = st.columns(3)
c1.metric("Total Target", f"{TOTAL_TARGET:,}")
c2.metric("Remaining at Start", f"{REMAINING_SAMPLES:,}")
c3.metric("Start Monthly Capacity", f"{base_sites * base_frequency * 2}")

st.success(f"**Completion Expected: {df.iloc[-1]['Month']}**")
st.info(f"**Duration:** {len(df)} months from {start_month}")

# ============================================================
# TABLE
# ============================================================
st.markdown("---")
st.markdown("### Month‑by‑Month Projection")
st.dataframe(df, use_container_width=True)

st.caption("© NCDC / ESPN — Scenario‑Based Sample Projection Tool")
