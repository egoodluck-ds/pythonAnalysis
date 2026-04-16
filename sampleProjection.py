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
.stApp {{
    background-color: #FFFFFF;
}}

.main-header h1 {{
    color: {NCDC_GREEN};
    font-weight: 900;
    text-align: center;
}}

h2, h3, .stSubheader {{
    color: {NCDC_GREEN} !important;
    font-weight: 800;
}}

div.stMetric {{
    background: white;
    padding: 10px;
    border-radius: 8px;
    border-left: 5px solid {NCDC_GREEN};
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}}

div[data-testid="stMetricValue"] {{
    color: {NCDC_GREEN};
    font-weight: 900;
}}
</style>
""", unsafe_allow_html=True)

# ============================================================
# HEADER
# ============================================================
col_logo, col_title, _ = st.columns([1, 4, 1])

with col_logo:
    st.image("espn_logo.jpg", width=100)

with col_title:
    st.markdown(
        "<div class='main-header'><h1>ESPN Sample Projection Dashboard</h1></div>",
        unsafe_allow_html=True
    )

# ============================================================
# CONSTANTS
# ============================================================
TOTAL_TARGET = 1296
SAMPLES_PER_VISIT = 2

# ============================================================
# BUILD FULL TIMELINE (SAFE RANGE)
# ============================================================
months_only = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]

months = []
for year in range(2025, 2036):
    for m in months_only:
        months.append(f"{m} {year}")

# ============================================================
# HISTORICAL BASELINE TABLE (AUG 2025 – APR 2026)
# ============================================================
def build_historical_table():
    rows = []
    remaining = TOTAL_TARGET

    # Phase 1: Aug–Oct 2025 (15 sites)
    phase1 = ["August 2025", "September 2025", "October 2025"]
    for month in phase1:
        monthly = 15 * 1 * SAMPLES_PER_VISIT
        remaining -= monthly
        rows.append({
            "Month": month,
            "Active Sites": 15,
            "Frequency": 1,
            "Monthly Samples": monthly,
            "Remaining Samples": remaining,
            "Status": "Historical"
        })

    # Phase 2: Nov 2025–Apr 2026 (18 sites)
    phase2 = [
        "November 2025", "December 2025",
        "January 2026", "February 2026",
        "March 2026", "April 2026"
    ]
    for month in phase2:
        monthly = 18 * 1 * SAMPLES_PER_VISIT
        remaining -= monthly
        rows.append({
            "Month": month,
            "Active Sites": 18,
            "Frequency": 1,
            "Monthly Samples": monthly,
            "Remaining Samples": remaining,
            "Status": "Historical"
        })

    return pd.DataFrame(rows), remaining

hist_df, remaining_after_baseline = build_historical_table()

# ============================================================
# INPUT AREA (PROJECTIONS)
# ============================================================
st.markdown("### Scenario Inputs (From May 2026 onward)")

proj_months = months[months.index("May 2026"):]

colA, colB, colC = st.columns(3)

with colA:
    start_month = st.selectbox("Projection Start Month", proj_months)
    base_sites = st.number_input("Sites at Start Month", min_value=1, value=18)
with colB:
    freq_label = st.selectbox("Sampling Frequency", ["Once", "Twice"])
    base_frequency = 1 if freq_label == "Once" else 2
    freq_change_month = st.selectbox("Month Frequency Changes", ["None"] + proj_months)
with colC:
    site_change_month = st.selectbox("Month New Sites Start", ["None"] + proj_months)
    added_sites = st.number_input("Additional Sites", min_value=0, value=0)

# ============================================================
# PROJECTION SIMULATION
# ============================================================
def simulate_projection(start_remaining):
    remaining = start_remaining
    sites = base_sites
    freq = base_frequency

    idx = months.index(start_month)
    rows = []

    while remaining > 0 and idx < len(months):
        month = months[idx]

        if freq_change_month != "None" and month == freq_change_month:
            freq = 2

        if site_change_month != "None" and month == site_change_month:
            sites += added_sites

        monthly = sites * freq * SAMPLES_PER_VISIT
        remaining -= monthly

        rows.append({
            "Month": month,
            "Active Sites": sites,
            "Frequency": freq,
            "Monthly Samples": monthly,
            "Remaining Samples": max(remaining, 0),
            "Status": "Projected"
        })

        idx += 1

    return pd.DataFrame(rows)

proj_df = simulate_projection(remaining_after_baseline)

# ============================================================
# COMBINE TABLES
# ============================================================
full_df = pd.concat([hist_df, proj_df], ignore_index=True)

# ============================================================
# SUMMARY
# ============================================================
st.markdown("### Projection Summary")

c1, c2, c3 = st.columns(3)
c1.metric("Total Target", f"{TOTAL_TARGET:,}")
c2.metric("Baseline Collected", f"{TOTAL_TARGET - remaining_after_baseline:,}")
c3.metric("Remaining at Start", f"{remaining_after_baseline:,}")

completion_month = full_df.iloc[-1]["Month"]
st.success(f"Expected Completion: **{completion_month}**")
st.info(f"Total Duration Shown: {len(full_df)} months (Aug 2025 → completion)")

# ============================================================
# TABLE
# ============================================================
st.markdown("---")
st.markdown("### Month‑by‑Month Projection (Including History)")
st.dataframe(full_df, use_container_width=True)

st.caption("© NCDC / ESPN — Scenario‑Based Sample Projection Tool")

