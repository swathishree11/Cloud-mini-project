import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.set_page_config(
    page_title="Sales Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .stApp { background-color: #0f1117; }
    div[data-testid="metric-container"] {
        background: linear-gradient(135deg, #1e2130 0%, #252a3a 100%);
        border: 1px solid #2e3452; border-radius: 12px; padding: 16px 20px;
    }
    div[data-testid="metric-container"] label {
        color: #8b92a5 !important; font-size: 13px !important;
        text-transform: uppercase; letter-spacing: 0.8px;
    }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        color: #e8eaf0 !important; font-size: 28px !important; font-weight: 700 !important;
    }
    section[data-testid="stSidebar"] {
        background-color: #151823; border-right: 1px solid #2e3452;
    }
    h1 { color: #e8eaf0 !important; font-weight: 800 !important; }
    h2, h3 { color: #c5c9d6 !important; }
    hr { border-color: #2e3452 !important; }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def generate_data():
    np.random.seed(42)
    n = 500
    start = datetime(2023, 1, 1)
    dates = [start + timedelta(days=i % 365) for i in range(n)]
    categories = ["Electronics", "Clothing", "Food", "Sports", "Home"]
    products = {
        "Electronics": ["Laptop", "Phone", "Tablet", "Watch"],
        "Clothing":    ["Shirt", "Pants", "Jacket", "Shoes"],
        "Food":        ["Snacks", "Beverages", "Dairy", "Bakery"],
        "Sports":      ["Gym Equipment", "Outdoor", "Team Sports", "Yoga"],
        "Home":        ["Furniture", "Decor", "Kitchen", "Cleaning"],
    }
    cat_col  = np.random.choice(categories, n)
    prod_col = [np.random.choice(products[c]) for c in cat_col]
    df = pd.DataFrame({
        "Date":            dates,
        "Region":          np.random.choice(["North","South","East","West","Central"], n),
        "Category":        cat_col,
        "Product":         prod_col,
        "Sales":           np.random.randint(500, 15000, n),
        "Units":           np.random.randint(1, 200, n),
        "Profit":          np.random.randint(50, 4000, n),
        "Customer_Rating": np.round(np.random.uniform(3.0, 5.0, n), 1),
    })
    df["Month"]     = pd.to_datetime(df["Date"]).dt.strftime("%b")
    df["Month_Num"] = pd.to_datetime(df["Date"]).dt.month
    return df

df_full = generate_data()

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font_color="#c5c9d6", font_family="Inter, sans-serif",
    margin=dict(l=10, r=10, t=40, b=10),
    legend=dict(bgcolor="rgba(0,0,0,0)"),
    xaxis=dict(gridcolor="#2e3452"), yaxis=dict(gridcolor="#2e3452"),
)
COLOR_SEQ = px.colors.qualitative.Vivid

# ── Sidebar Filters ──────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎛️ Filters")
    st.markdown("---")
    regions    = st.multiselect("Region",   sorted(df_full["Region"].unique()),
                                default=sorted(df_full["Region"].unique()))
    categories = st.multiselect("Category", sorted(df_full["Category"].unique()),
                                default=sorted(df_full["Category"].unique()))
    sales_min  = st.slider("Min Sales ($)", 0, int(df_full["Sales"].max()), 0, step=500)
    st.markdown("---")
    MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    months = st.select_slider("Month Range", options=MONTHS, value=("Jan","Dec"))
    month_map = {m: i+1 for i, m in enumerate(MONTHS)}
    m_start, m_end = month_map[months[0]], month_map[months[1]]

df = df_full[
    df_full["Region"].isin(regions) &
    df_full["Category"].isin(categories) &
    (df_full["Sales"] >= sales_min) &
    (df_full["Month_Num"].between(m_start, m_end))
].copy()

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown("# 📊 Sales Analytics Dashboard")
st.markdown(f"Showing **{len(df):,}** of {len(df_full):,} transactions")
st.markdown("---")

# ── KPI Cards ────────────────────────────────────────────────────────────────
c1,c2,c3,c4,c5 = st.columns(5)
ts = df["Sales"].sum(); tp = df["Profit"].sum(); tu = df["Units"].sum()
ar = df["Customer_Rating"].mean() if len(df) else 0
mp = (tp/ts*100) if ts else 0
c1.metric("💰 Total Sales",   f"${ts:,.0f}", "+12.4%")
c2.metric("📈 Total Profit",  f"${tp:,.0f}", "+8.7%")
c3.metric("📦 Units Sold",    f"{tu:,}",      "+5.2%")
c4.metric("⭐ Avg Rating",    f"{ar:.2f}/5",  "+0.3")
c5.metric("🎯 Profit Margin", f"{mp:.1f}%",   "+1.1%")

# ── Row 1: Line + Donut ───────────────────────────────────────────────────────
r1a, r1b = st.columns([2,1])
with r1a:
    st.markdown("### 📅 Monthly Sales Trend")
    monthly = df.groupby(["Month_Num","Month","Category"])["Sales"].sum().reset_index().sort_values("Month_Num")
    fig = px.line(monthly, x="Month", y="Sales", color="Category",
                  markers=True, color_discrete_sequence=COLOR_SEQ)
    fig.update_traces(line_width=2.5, marker_size=6)
    fig.update_layout(**PLOTLY_LAYOUT, height=320)
    st.plotly_chart(fig, use_container_width=True)
with r1b:
    st.markdown("### 🥧 By Category")
    fig = px.pie(df.groupby("Category")["Sales"].sum().reset_index(),
                 names="Category", values="Sales", hole=0.55,
                 color_discrete_sequence=COLOR_SEQ)
    fig.update_layout(**PLOTLY_LAYOUT, height=320)
    st.plotly_chart(fig, use_container_width=True)

# ── Row 2: Bar + Scatter ──────────────────────────────────────────────────────
r2a, r2b = st.columns(2)
with r2a:
    st.markdown("### 🌍 Sales & Profit by Region")
    rd = df.groupby("Region")[["Sales","Profit"]].sum().reset_index()
    fig = go.Figure([
        go.Bar(name="Sales",  x=rd["Region"], y=rd["Sales"],  marker_color="#7c83fd"),
        go.Bar(name="Profit", x=rd["Region"], y=rd["Profit"], marker_color="#fd7c83"),
    ])
    fig.update_layout(**PLOTLY_LAYOUT, barmode="group", height=300)
    st.plotly_chart(fig, use_container_width=True)
with r2b:
    st.markdown("### 🔵 Units vs Sales")
    fig = px.scatter(df, x="Units", y="Sales", color="Category", size="Profit",
                     hover_data=["Product","Region"],
                     color_discrete_sequence=COLOR_SEQ, opacity=0.75)
    fig.update_layout(**PLOTLY_LAYOUT, height=300)
    st.plotly_chart(fig, use_container_width=True)

# ── Row 3: Heatmap + Top Products ────────────────────────────────────────────
r3a, r3b = st.columns(2)
with r3a:
    st.markdown("### 🔥 Heatmap — Region × Category")
    pivot = df.pivot_table("Sales", "Region", "Category", aggfunc="sum", fill_value=0)
    fig = px.imshow(pivot, color_continuous_scale="Viridis", text_auto=".2s", aspect="auto")
    fig.update_layout(**PLOTLY_LAYOUT, height=300, coloraxis_showscale=False)
    fig.update_traces(textfont_color="white")
    st.plotly_chart(fig, use_container_width=True)
with r3b:
    st.markdown("### 🏆 Top 10 Products")
    top = df.groupby("Product")["Sales"].sum().nlargest(10).reset_index().sort_values("Sales")
    fig = px.bar(top, x="Sales", y="Product", orientation="h",
                 color="Sales", color_continuous_scale="Plasma")
    fig.update_layout(**PLOTLY_LAYOUT, height=300, coloraxis_showscale=False,
                      yaxis=dict(gridcolor="rgba(0,0,0,0)"))
    st.plotly_chart(fig, use_container_width=True)

# ── Raw Data ──────────────────────────────────────────────────────────────────
st.markdown("---")
with st.expander("🗃️ View Raw Data"):
    st.dataframe(df.sort_values("Sales", ascending=False).reset_index(drop=True),
                 use_container_width=True, height=300)
    st.download_button("⬇️ Download CSV", df.to_csv(index=False).encode(), "data.csv", "text/csv")
