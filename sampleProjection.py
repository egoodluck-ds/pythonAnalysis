from calendar import month

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
# ASSUMPTIONS (FIXED / READ-ONLY)
# ============================================================
TOTAL_TARGET = 1296
SAMPLES_PER_VISIT = 2
PROJECTION_START_MONTH = "May 2026"
ACTIVE_SITES_AT_START = 18

# Sampling frequency after change (fixed)
NEW_FREQUENCY = 2  # Twice monthly

# ============================================================
# BUILD FULL TIMELINE (SAFE, EXTENDED)
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
# HISTORICAL BASELINE (AUG 2025 – APR 2026)
# ============================================================
def build_historical_table():
    rows = []
    remaining = TOTAL_TARGET

    # Aug–Oct 2025: 15 sites
    for month in ["August 2025", "September 2025", "October 2025"]:
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

    # Nov 2025–Apr 2026: 18 sites
    for month in [
        "November 2025", "December 2025",
        "January 2026", "February 2026",
        "March 2026", "April 2026"
    ]:
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
# EXPECTATIONS (READ-ONLY)
# ============================================================
st.markdown("### Initial Plan (Investment Document)")

e1, e2, e3 = st.columns(3)
e1.metric("Targeted Total", f"{TOTAL_TARGET:,}")
e2.metric("Sampling Frequency", "Twice Monthly")
e3.metric("Number of States (Sites)", "7 (30)")
st.markdown("**Note:** Sample counts assume 2 samples per visit (1 Grab | **1 Moore swabs**).")
# ============================================================
# CURRENT IMPLEMENTATION (READ-ONLY)
# ============================================================
st.markdown("### Implementation Details (Baseline)")

b1, b2, b3, b4 = st.columns(4)
b1.metric("Samples Collected", f"{TOTAL_TARGET - remaining_after_baseline:,}")
b2.metric("Sampling Frequency", "Once Monthly")
b3.metric("Number of States (Sites)", "4 (18)")
b4.metric("Samples Remaining", f"{remaining_after_baseline:,}")

st.markdown("""
**Note:**
- August – October 2025: Samples were collected from **15 sites**
- November 2025 – April 2026: Samples were collected from **18 sites**
- Sampling frequency during this period was **once monthly** """)

# ============================================================
# SCENARIO CHANGES (EDITABLE)
# ============================================================
st.markdown("### Scenario Changes (What‑If Analysis)")

proj_months = months[months.index(PROJECTION_START_MONTH):]

c1, c2 , c3= st.columns(3)

with c1:
    freq_change_month = st.selectbox(
        "Month Sampling Frequency Increases (Once → Twice)",
        ["None"] + proj_months
    )
    st.caption("Sampling remains once monthly until the selected month.")

with c2:
    site_change_month = st.selectbox(
        "Month New Sites Start",
        ["None"] + proj_months
    )
with c3:
    added_sites = st.number_input(
        "Additional Sites",
        min_value=0,
        value=0
    )
# ============================================================
# PROJECTION SIMULATION
# ============================================================

def simulate_projection(start_remaining):
    remaining = start_remaining
    sites = ACTIVE_SITES_AT_START
    freq = 1  # Always start Once Monthly

    idx = months.index(PROJECTION_START_MONTH)
    rows = []

    while remaining > 0 and idx < len(months):
        month = months[idx]

        if freq_change_month != "None" and month == freq_change_month:
            freq = NEW_FREQUENCY

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

completion_month = full_df.iloc[-1]["Month"]
duration_months = len(full_df)

m1, m2 = st.columns(2)

with m1:
    st.metric(
        label="Expected Completion Month",
        value=completion_month
    )

with m2:
    st.metric(
        label="Total Duration",
        value=f"{duration_months} months",
        delta="Aug 2025 → " + completion_month
    )

# ============================================================
# TABLE
# ============================================================
st.markdown("---")
st.markdown("### Month‑by‑Month Projection (Including History)")
st.dataframe(full_df, width='stretch')

st.caption("© NCDC / ESPN — Scenario‑Based Sample Projection Tool")