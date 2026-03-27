import streamlit as st
import math
import pandas as pd

# ============================================================
# PAGE CONFIGURATION
# ============================================================
st.set_page_config(
    page_title="ESPN Sample Projection",
    layout="wide"
)

# ============================================================
# GLOBAL COLORS & BRANDING
# ============================================================
NCDC_GREEN = "#196806"

st.markdown(f"""
<style>

/* ---- Page Background ---- */
.stApp {{
    background-color: #Ffffff;
}}

/* ---- Main Header ---- */
.main-header h1 {{
    color: {NCDC_GREEN} !important;
    font-weight: 900;
    text-align: center;
    padding-bottom: 0px;
}}

/* ---- Subheaders ---- */
h2, h3, h4, .stSubheader {{
    color: {NCDC_GREEN} !important;
    font-weight: 800 !important;
}}

/* ---- Metrics Styling ---- */
div[data-testid="stMetricValue"] {{
    color: {NCDC_GREEN} !important;
    font-weight: 900 !important;
}}

div[data-testid="stMetricLabel"] {{
    font-weight: 600 !important;
}}

div.stMetric {{
    background: white;
    padding: 10px;
    border-radius: 8px;
    border-left: 5px solid {NCDC_GREEN};
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}}

/* ---- Center logo ---- */
.center {{
    display: flex;
    justify-content: center;
    align-items: center;
}}

</style>
""", unsafe_allow_html=True)

# ============================================================
# HEADER WITH NCDC LOGO AND TITLE
# ============================================================
col_logo, col_title, col_empty = st.columns([1,4,1])

with col_logo:
    st.markdown("<div class='center'>", unsafe_allow_html=True)
    st.image("espn_logo.jpg", width=110)
    st.markdown("</div>", unsafe_allow_html=True)

with col_title:
    st.markdown("<div class='main-header'><h1>ESPN Sample Projection Dashboard</h1></div>", unsafe_allow_html=True)


# ============================================================
# INPUT AREA (COMPACT ONE-SCREEN LAYOUT)
# ============================================================
st.markdown("### Input Parameters")

months_only = ["January", "February", "March", "April", "May", "June",
               "July", "August", "September", "October", "November", "December"]

timeline = []
for y in range(2026, 2031):
    for m in months_only:
        timeline.append(f"{m} {y}")

colA, colB, colC, colD = st.columns([1.2, 1.2, 1.2, 1.2])

with colA:
    total_target = st.number_input("Total Targeted Samples", min_value=1, value=1296)
    collected = st.number_input("Samples Collected Already", min_value=0, value=288)
    start_month = st.selectbox("Start Projection Month", [m for m in timeline if "2026" in m])

with colB:
    base_sites = st.number_input("Current Active Sites", min_value=1, value=18)
    freq_label = st.selectbox("Current Sampling Frequency", ["Once", "Twice"])
    base_frequency = 1 if freq_label == "Once" else 2

with colC:
    freq_change_month = st.selectbox("Month Frequency Changes", ["None"] + timeline)
    new_freq_label = st.selectbox("New Frequency", ["Once", "Twice"])
    new_frequency = 1 if new_freq_label == "Once" else 2
with colD:
    site_change_month = st.selectbox("Month New Sites Start", ["None"] + timeline)
    added_sites = st.number_input("Additional Sites", min_value=0, value=12)


# ============================================================
# SIMULATION ENGINE
# ============================================================
def simulate_projection():

    samples_remaining = total_target - collected
    current_sites = base_sites
    current_frequency = base_frequency

    start_idx = timeline.index(start_month)
    month_idx = start_idx

    result = []

    while samples_remaining > 0:

        current_month = timeline[month_idx]

        # Apply changes when they occur
        if freq_change_month != "None" and current_month == freq_change_month:
            current_frequency = new_frequency

        if site_change_month != "None" and current_month == site_change_month:
            current_sites += added_sites

        # Monthly capacity (2 samples per visit)
        monthly_capacity = current_sites * current_frequency * 2
        samples_remaining -= monthly_capacity

        result.append({
            "Month": current_month,
            "Sites Active": current_sites,
            "Frequency": current_frequency,
            "Monthly Capacity": monthly_capacity,
            "Remaining Samples": max(samples_remaining, 0)
        })

        month_idx += 1

    return pd.DataFrame(result)


df_sim = simulate_projection()

completion_month = df_sim.iloc[-1]["Month"]
months_needed = len(df_sim)
years = months_needed // 12
extra_months = months_needed % 12


# ============================================================
# RESULTS SECTION — COMPACT AND CENTERED
# ============================================================
st.markdown("### Projection Summary")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Samples", f"{total_target:,}")

with col2:
    st.metric("Remaining Samples", f"{total_target - collected:,}")

with col3:
    st.metric("Monthly Start Capacity", f"{base_sites * base_frequency * 2} Samples")


col4, col5 = st.columns(2)

with col4:
    st.success(f"Completion Expected: **{completion_month}**")

with col5:
    st.info(f"Duration: **{months_needed} months** "
            f"({years} years {extra_months} months)")


# ============================================================
# TABLE SECTION (SEPARATED TO REDUCE SCROLLING)
# ============================================================
st.markdown("---")
st.markdown("### Month-by-Month Projection Table")
st.dataframe(df_sim, hide_index=True)

st.caption("© NCDC • ESPN Operational Planning Tool")