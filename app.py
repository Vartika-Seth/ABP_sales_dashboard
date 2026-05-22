import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# =====================================================
# DEMO USER DATABASE
# =====================================================

users = {
    "admin": {
        "password": "admin123",
        "role": "Admin",
        "region": "All"
    },

    "north_mgr": {
        "password": "north123",
        "role": "Manager",
        "region": "North-Corp"
    },

    "south_mgr": {
        "password": "south123",
        "role": "Manager",
        "region": "South"
    }
}

# =====================================================
# LOGIN SYSTEM
# =====================================================

st.sidebar.title("🔐 Login")

username = st.sidebar.text_input("Username")
password = st.sidebar.text_input(
    "Password",
    type="password"
)

login_button = st.sidebar.button("Login")

# SESSION STATE
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# LOGIN LOGIC
if login_button:

    if username in users:

        if password == users[username]["password"]:

            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.role = users[username]["role"]
            st.session_state.region = users[username]["region"]

        else:
            st.sidebar.error("Wrong password")

    else:
        st.sidebar.error("User not found")

# STOP APP IF NOT LOGGED IN
if not st.session_state.logged_in:

    st.warning("Please login first")
    st.stop()

# =====================================================
# USER INFO
# =====================================================

st.sidebar.success(
    f"Logged in as: {st.session_state.role}"
)

st.sidebar.write(
    f"Region Access: {st.session_state.region}"
)

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="ABP Sales Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# THEME TOGGLE
# =====================================================

st.sidebar.title("⚙ Dashboard Settings")

mode = st.sidebar.toggle("Dark Mode")

if mode:
    background = "#0E1117"
    text_color = "white"
    card_color = "#1E1E1E"
else:
    background = "#F7F9FC"
    text_color = "black"
    card_color = "white"

st.markdown(f"""
<style>
.stApp {{
    background-color: {background};
    color: {text_color};
}}

.kpi-card {{
    background-color: {card_color};
    padding: 20px;
    border-radius: 15px;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.1);
    text-align: center;
}}
</style>
""", unsafe_allow_html=True)

# =====================================================
# TITLE
# =====================================================

st.title("📊 ABP Sales Dashboard")
st.markdown("### Dynamic Sales Intelligence & Performance Monitoring")

# =====================================================
# LOAD DATA
# =====================================================

@st.cache_data

def load_data():
    df = pd.read_excel("sales_data.xlsx")
    return df

_df = load_data()

# =====================================================
# DATA CLEANING
# =====================================================

numeric_cols = [
    "Target",
    "MTD",
    "LY",
    "Confirmed Revenue",
    "Likely Conversions",
    "Pipeline",
    "Sales Visibility"
]

for col in numeric_cols:
    if col in _df.columns:
        _df[col] = pd.to_numeric(_df[col], errors="coerce").fillna(0)

# =====================================================
# SIDEBAR FILTERS
# =====================================================

st.sidebar.header("📌 Filters")

month_filter = st.sidebar.multiselect(
    "Select Month",
    options=_df["Month"].unique(),
    default=_df["Month"].unique()
)

stream_filter = st.sidebar.multiselect(
    "Select Stream",
    options=_df["Stream"].unique(),
    default=_df["Stream"].unique()
)

vertical_filter = st.sidebar.multiselect(
    "Select Vertical",
    options=_df["Vertical"].unique(),
    default=_df["Vertical"].unique()
)

revtype_filter = st.sidebar.multiselect(
    "Select Revenue Type",
    options=_df["RevType"].unique(),
    default=_df["RevType"].unique()
)

# =====================================================
# REGION ACCESS CONTROL
# =====================================================

if st.session_state.role == "Admin":

    region_filter = st.sidebar.multiselect(
        "Select Region",
        options=_df["Region"].unique(),
        default=_df["Region"].unique()
    )

else:

    region_filter = [st.session_state.region]

# =====================================================
# APPLY FILTERS
# =====================================================

filtered_df = _df[
    (_df["Month"].isin(month_filter)) &
    (_df["Stream"].isin(stream_filter)) &
    (_df["Vertical"].isin(vertical_filter)) &
    (_df["RevType"].isin(revtype_filter)) &
    (_df["Region"].isin(region_filter))
]
# =====================================================
# KPI CALCULATIONS
# =====================================================

mtd_target = filtered_df["Target"].sum()

mtd_actual = filtered_df["MTD"].sum()

ly_total = filtered_df["LY"].sum()

achievement = (
    (mtd_actual / mtd_target) * 100
    if mtd_target > 0 else 0
)

growth = (
    ((mtd_actual - ly_total) / ly_total) * 100
    if ly_total > 0 else 0
)

confirmed_rev = filtered_df["Confirmed Revenue"].sum()

likely_conversion = filtered_df["Likely Conversions"].sum()

pipeline = filtered_df["Pipeline"].sum()

visibility = filtered_df["Sales Visibility"].sum()

coverage = (
    (visibility / mtd_target) * 100
    if mtd_target > 0 else 0
)
# =====================================================
# KPI SECTION
# =====================================================

st.markdown("## 📈 Performance KPIs")

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("MTD Target", f"₹ {mtd_target:,.0f}")
col2.metric("MTD Actual", f"₹ {mtd_actual:,.0f}")
col3.metric("Achievement %", f"{achievement:.1f}%")
col4.metric("Growth vs LY", f"{growth:.1f}%")
col5.metric("Visibility %", f"{coverage:.1f}%")

# =====================================================
# PIPELINE KPI ROW
# =====================================================

st.markdown("## 🚀 Pipeline & Visibility")

p1, p2, p3, p4 = st.columns(4)

p1.metric("Confirmed Revenue", f"₹ {confirmed_rev:,.0f}")
p2.metric("Likely Conversion", f"₹ {likely_conversion:,.0f}")
p3.metric("Pipeline", f"₹ {pipeline:,.0f}")
p4.metric("Sales Visibility", f"₹ {visibility:,.0f}")

# =====================================================
# CHART SECTION
# =====================================================

chart1, chart2 = st.columns(2)

# -----------------------------------------------------
# STREAM SPLIT PIE CHART
# -----------------------------------------------------

stream_fig = px.pie(
    filtered_df,
    names="Stream",
    values="MTD",
    title="Stream Split"
)

chart1.plotly_chart(stream_fig, use_container_width=True)
# -----------------------------------------------------
st.markdown("## 🔻 Sales Pipeline Funnel")

funnel_df = pd.DataFrame({
    "Stage": ["MTD", "Confirmed Rev", "Likely Conversion", "Pipeline"],
    "Value": [mtd_actual, confirmed_rev, likely_conversion, pipeline]
})

funnel_fig = px.funnel(
    funnel_df,
    x="Value",
    y="Stage"
)

st.plotly_chart(funnel_fig, use_container_width=True)

# =====================================================
# DYNAMIC ALERTS & INSIGHTS
# =====================================================

st.markdown("## 🚨 Dynamic Insights & Alerts")

alerts = []

if achievement < 70:
    alerts.append("⚠ Achievement below 70%")

if growth < 0:
    alerts.append("📉 Negative growth vs LY")

if coverage < 100:
    alerts.append("🚨 Visibility coverage below 100%")

if pipeline < confirmed_rev:
    alerts.append("⚠ Pipeline lower than confirmed revenue")

if len(alerts) == 0:
    st.success("✅ All business metrics are healthy")
else:
    for alert in alerts:
        st.warning(alert)
# =====================================================
# DATA TABLE
# =====================================================

st.markdown("## 📄 Detailed Sales Data")

st.dataframe(filtered_df, use_container_width=True)

# =====================================================
# RBAC PLACEHOLDER
# =====================================================

# Example Future Logic
# if user_role == "Employee":
#     filtered_df = filtered_df[
#         filtered_df["Employee"] == current_user
#     ]

# if user_role == "Manager":
#     filtered_df = filtered_df[
#         filtered_df["Region"] == assigned_region
#     ]