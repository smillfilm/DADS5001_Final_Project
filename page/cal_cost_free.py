# calc_trip_cost.py
import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import snowflake.connector
from datetime import datetime

# ---------------------------------------
# Page config - Premium Theme
# ---------------------------------------
st.set_page_config(
    page_title="Fuel Trip Calculator | Premium", 
    page_icon="⛽", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for premium look
st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --primary: #1a237e;
        --secondary: #0d47a1;
        --accent: #00b8d4;
        --success: #00c853;
        --warning: #ff9800;
        --light-bg: #f8fafc;
        --card-bg: #ffffff;
        --text-primary: #1e293b;
        --text-secondary: #64748b;
    }
    
    /* Main container */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: black;
        font-weight: 600;
    }
    
    h1 {
        background: linear-gradient(135deg, var(--primary), var(--accent));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #e2e8f0;
        margin-bottom: 1.5rem;
    }
    
    /* Cards */
    .custom-card {
        background: var(--card-bg);
        border-radius: 16px;
        padding: 1.5rem;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        transition: all 0.3s ease;
        height: 100%;
    }
    
    .custom-card:hover {
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        transform: translateY(-2px);
    }
    
    /* Metrics */
    .stMetric {
        background: linear-gradient(135deg, var(--light-bg), white);
        border-radius: 12px;
        padding: 1rem;
        border-left: 4px solid var(--accent);
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(135deg, 
            #f8fafc 0%,
            #f1f5f9 25%,
            #e2e8f0 50%,
            #f1f5f9 75%,
            #f8fafc 100%);
        color: black;
    }
    
    section[data-testid="stSidebar"] .st-emotion-cache-16txtl3 {
        padding-top: 2rem;
    }
    
    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] .st-emotion-cache-1v0mbdj {
        color: white !important;
    }
    
    section[data-testid="stSidebar"] .stSelectbox,
    section[data-testid="stSidebar"] .stMultiSelect,
    section[data-testid="stSidebar"] .stNumberInput {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        padding: 0.5rem;
        color : black ;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, var(--primary), var(--secondary));
        color: black;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(26, 35, 126, 0.3);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        background-color: var(--light-bg);
        padding: 0.5rem;
        border-radius: 12px;
        color : black ;
    }
            
    
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 500;
    }
    
    /* Dataframe */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid #e2e8f0;
    }
    
    /* Badge for cheapest */
    .cheapest-badge {
        background: linear-gradient(135deg, var(--success), #00e676);
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        display: inline-block;
        margin-left: 0.5rem;
    }
    
    /* Company tags */
    .company-tag {
        display: inline-block;
        background: var(--light-bg);
        padding: 0.25rem 0.75rem;
        border-radius: 6px;
        margin: 0.25rem;
        font-size: 0.85rem;
        border-left: 3px solid var(--accent);
    }
    
    /* Price highlight */
    .price-highlight {
        font-size: 1.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, var(--primary), var(--accent));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
    /* ตัวอักษรใน Fuel Types Selectbox */
    div[data-testid="stSelectbox"] div[data-baseweb="select"] span {
        color: #000000 !important;  /* สีดำ */
        font-weight: 500 !important;
    }
    
    /* ตัวอักษรใน Companies Multiselect */
    div[data-testid="stMultiSelect"] div[data-baseweb="select"] span {
        color: #000000 !important;  /* สีดำ */
    }
    
    /* ตัวอักษรใน Latest Data Date input */
    div[data-testid="stDateInput"] input {
        color: #000000 !important;  /* สีดำ */
        font-weight: 500 !important;
    }
    
    /* ตัวอักษรใน dropdown ทั้งหมด */
    div[role="listbox"] li {
        color: #000000 !important;  /* สีดำ */
    }
    
    /* เมื่อเลือก item ใน dropdown */
    div[role="listbox"] li[aria-selected="true"] {
        background-color: #bae6fd !important;
        color: #000000 !important;  /* สีดำ */
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------
# Premium Header
# ---------------------------------------
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <h1 style="font-size: 2.5rem; margin-bottom: 0.5rem;">⛽ Fuel Trip Calculator</h1>
        <p style="color: var(--text-secondary); font-size: 1.1rem; margin-top: 0;">
            Premium Fuel Cost Analysis & Comparison Tool
        </p>
    </div>
    """, unsafe_allow_html=True)

# ---------------------------------------
# Snowflake helpers
# ---------------------------------------
def get_connection():
    sf = st.secrets["connections"]["snowflake"]
    return snowflake.connector.connect(
        account=sf["account"], user=sf["user"], password=sf["password"],
        role=sf["role"], warehouse=sf["warehouse"],
        database=sf["database"], schema=sf["schema"]
    )

@st.cache_data(ttl=900)
def run_query(sql: str) -> pd.DataFrame:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(sql)
    df = pd.DataFrame(cur.fetchall(), columns=[d[0] for d in cur.description])
    cur.close(); conn.close()
    return df

# ---------------------------------------
# Data functions
# ---------------------------------------
@st.cache_data(ttl=900)
def get_type_names() -> list[str]:
    sql = """
    SELECT DISTINCT ty.TYPE_NAME
    FROM OIL_TRANSACTION t
    JOIN OIL_TYPE ty ON ty.TYPE_NO = t.TYPE_ID
    WHERE t.PRICE IS NOT NULL
    ORDER BY ty.TYPE_NAME
    """
    df = run_query(sql)
    return df["TYPE_NAME"].dropna().tolist()

@st.cache_data(ttl=900)
def get_latest_date() -> pd.Timestamp | None:
    df = run_query("SELECT MAX(DATE_TRANSACTION) AS MAXDATE FROM OIL_TRANSACTION")
    if df.empty or pd.isna(df.iloc[0]["MAXDATE"]):
        return None
    return pd.to_datetime(df.iloc[0]["MAXDATE"])

@st.cache_data(ttl=900)
def get_latest_prices(selected_types: list[str] | None = None) -> pd.DataFrame:
    where_type = ""
    if selected_types:
        safe = [t.replace("'", "''") for t in selected_types]
        names_sql = ", ".join(f"'{n}'" for n in safe)
        where_type = f"AND ty.TYPE_NAME IN ({names_sql})"

    sql = f"""
    WITH latest AS ( SELECT MAX(DATE_TRANSACTION) AS MAXDATE FROM OIL_TRANSACTION )
    SELECT
      t.DATE_TRANSACTION AS DATE_TRANSACTION,
      ty.TYPE_NAME       AS TYPE_NAME,
      MAX(CASE WHEN com.COMPANY_ID = 1  THEN t.PRICE END) AS PTT,
      MAX(CASE WHEN com.COMPANY_ID = 2  THEN t.PRICE END) AS BANGCHAK,
      MAX(CASE WHEN com.COMPANY_ID = 3  THEN t.PRICE END) AS SHELL,
      MAX(CASE WHEN com.COMPANY_ID = 4  THEN t.PRICE END) AS ESSO,
      MAX(CASE WHEN com.COMPANY_ID = 5  THEN t.PRICE END) AS CHEVRON,
      MAX(CASE WHEN com.COMPANY_ID = 6  THEN t.PRICE END) AS IRPC,
      MAX(CASE WHEN com.COMPANY_ID = 7  THEN t.PRICE END) AS PTG,
      MAX(CASE WHEN com.COMPANY_ID = 8  THEN t.PRICE END) AS SUSCO,
      MAX(CASE WHEN com.COMPANY_ID = 9  THEN t.PRICE END) AS PURE,
      MAX(CASE WHEN com.COMPANY_ID = 10 THEN t.PRICE END) AS SUSCO_DEALER
    FROM OIL_TRANSACTION t
    JOIN OIL_TYPE ty ON ty.TYPE_NO = t.TYPE_ID
    JOIN COMPANY com ON com.COMPANY_ID = t.COMPANY_ID
    WHERE t.DATE_TRANSACTION = (SELECT MAXDATE FROM latest)
      {where_type}
    GROUP BY t.DATE_TRANSACTION, ty.TYPE_NAME
    ORDER BY ty.TYPE_NAME
    """
    df = run_query(sql)
    df["DATE_TRANSACTION"] = pd.to_datetime(df["DATE_TRANSACTION"], errors="coerce")
    for c in ["PTT","BANGCHAK","SHELL","ESSO","CHEVRON","IRPC","PTG","SUSCO","PURE","SUSCO_DEALER"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df

def wide_to_long(df: pd.DataFrame) -> pd.DataFrame:
    brand_cols = ["PTT","BANGCHAK","SHELL","ESSO","CHEVRON","IRPC","PTG","SUSCO","PURE","SUSCO_DEALER"]
    df_long = df.melt(
        id_vars=["DATE_TRANSACTION", "TYPE_NAME"],
        value_vars=brand_cols,
        var_name="COMPANY",
        value_name="PRICE_PER_L"
    )
    df_long["PRICE_PER_L"] = pd.to_numeric(df_long["PRICE_PER_L"], errors="coerce")
    df_long = df_long.dropna(subset=["PRICE_PER_L"])
    return df_long

# ---------------------------------------
# Sidebar
# ---------------------------------------
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0; margin-bottom: 2rem;">
        <h4 style="color: black; margin-bottom: 0.5rem;">🚗 Trip Details</h4>
        <p style="color: black; font-size: 0.9rem; margin: 0;">
            Configure your journey parameters
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div>', unsafe_allow_html=True)
    distance_km = st.number_input(
        "**Distance (km)**", 
        min_value=0.0, 
        value=50.0, 
        step=1.0,
        help="Total distance of your trip"
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div>', unsafe_allow_html=True)
    km_per_l = st.number_input(
        "**Fuel Efficiency (km/L)**", 
        min_value=0.1, 
        value=12.0, 
        step=0.1,
        help="Your vehicle's fuel efficiency"
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    if km_per_l > 0:
        liters_needed = distance_km / km_per_l
        st.markdown(f"""
        <div class="custom-card" style="background: linear-gradient(135deg, rgba(0,184,212,0.1), rgba(13,71,161,0.1));">
            <div style="color: var(--text-secondary); font-size: 0.9rem;">Estimated Fuel Required</div>
            <div class="price-highlight">{liters_needed:,.2f} L</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0; margin-bottom: 1rem;">
        <h4 style="color: black; margin-bottom: 0.5rem;">🔍 Data Filters</h4>
        <p style="color: black; font-size: 0.9rem; margin: 0;">
            Customize your comparison
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    types_all = get_type_names()
    latest_date = get_latest_date()
    
    sel_types = st.multiselect(
        "**Fuel Types**", 
        options=types_all, 
        default=types_all[:6] if len(types_all) > 6 else types_all,
        help="Select fuel types to compare"
    )
    
    sel_companies = st.multiselect(
        "**Companies**", 
        options=["PTT","BANGCHAK","SHELL","ESSO","CHEVRON","IRPC","PTG","SUSCO","PURE","SUSCO_DEALER"],
        default=["PTT","BANGCHAK","SHELL","ESSO"],
        help="Select companies to include in comparison"
    )
    
    if latest_date:
        st.markdown(f"""
        <div style="background: rgba(255,255,255,0.1); padding: 0.75rem; border-radius: 8px; margin-top: 1rem;">
            <div style="color: rgba(255,255,255,0.9); font-size: 0.85rem; display: flex; align-items: center; gap: 0.5rem;">
                <span style="font-size: 1.2rem;">🔄</span>
                <div>
                    <div style="font-weight: 500;">Latest Data</div>
                    <div>{latest_date.strftime('%d %b %Y')}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ---------------------------------------
# Validation
# ---------------------------------------
if km_per_l <= 0:
    st.error("⚠️ Please enter a valid fuel efficiency (km/L) greater than 0")
    st.stop()

# ---------------------------------------
# Load and process data
# ---------------------------------------
prices_wide = get_latest_prices(selected_types=sel_types)
if prices_wide.empty:
    st.warning("📊 No fuel price data found for the selected filters. Please adjust your selections.")
    st.stop()

prices_long = wide_to_long(prices_wide)
if sel_companies:
    prices_long = prices_long[prices_long["COMPANY"].isin(sel_companies)]

# Calculate trip costs
liters_needed = distance_km / km_per_l
prices_long["LITERS_NEEDED"] = liters_needed
prices_long["TRIP_COST_BAHT"] = prices_long["PRICE_PER_L"] * liters_needed

# Find cheapest per type
min_cost_by_type = (
    prices_long.groupby("TYPE_NAME", as_index=False)["TRIP_COST_BAHT"].min()
               .rename(columns={"TRIP_COST_BAHT": "MIN_COST"})
)
prices_long = prices_long.merge(min_cost_by_type, on="TYPE_NAME", how="left")

TOL = 1e-6
prices_long["IS_CHEAPEST_IN_TYPE"] = (abs(prices_long["TRIP_COST_BAHT"] - prices_long["MIN_COST"]) <= TOL)
prices_long["RANK_IN_TYPE"] = prices_long.groupby("TYPE_NAME")["TRIP_COST_BAHT"].rank(method="min")

# ---------------------------------------
# Dashboard Overview
# ---------------------------------------
st.markdown("## 📈 Trip Cost Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="custom-card">
        <div style="color: var(--text-secondary); font-size: 0.9rem; margin-bottom: 0.5rem;">Total Distance</div>
        <div style="font-size: 1.8rem; font-weight: 700; color: var(--primary);">{distance_km:,.1f} km</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="custom-card">
        <div style="color: var(--text-secondary); font-size: 0.9rem; margin-bottom: 0.5rem;">Fuel Required</div>
        <div style="font-size: 1.8rem; font-weight: 700; color: var(--accent);">{liters_needed:,.2f} L</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    avg_cost = prices_long["TRIP_COST_BAHT"].mean()
    st.markdown(f"""
    <div class="custom-card">
        <div style="color: var(--text-secondary); font-size: 0.9rem; margin-bottom: 0.5rem;">Avg. Trip Cost</div>
        <div style="font-size: 1.8rem; font-weight: 700; color: var(--success);">฿{avg_cost:,.2f}</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    min_cost = prices_long["TRIP_COST_BAHT"].min()
    st.markdown(f"""
    <div class="custom-card">
        <div style="color: var(--text-secondary); font-size: 0.9rem; margin-bottom: 0.5rem;">Lowest Trip Cost</div>
        <div style="font-size: 1.8rem; font-weight: 700; color: #00c853;">฿{min_cost:,.2f}</div>
    </div>
    """, unsafe_allow_html=True)

# ---------------------------------------
# Best Options Section
# ---------------------------------------
st.markdown("## 🏆 Best Options Per Fuel Type")

summary_lines = []
for type_name, sub in prices_long.groupby("TYPE_NAME"):
    type_min = sub["TRIP_COST_BAHT"].min()
    cheapest_rows = sub[abs(sub["TRIP_COST_BAHT"] - type_min) <= TOL].sort_values("COMPANY")
    
    if not cheapest_rows.empty:
        companies_list = ", ".join(cheapest_rows["COMPANY"].tolist())
        price_per_l = cheapest_rows["PRICE_PER_L"].iloc[0]
        trip_cost = cheapest_rows["TRIP_COST_BAHT"].iloc[0]
        
        summary_lines.append({
            "type": type_name,
            "companies": companies_list,
            "price_per_l": price_per_l,
            "trip_cost": trip_cost
        })

# Display best options
if summary_lines:
    cols = st.columns(3)
    for idx, summary in enumerate(summary_lines):
        with cols[idx % 3]:
            st.markdown(f"""
            <div class="custom-card" style="border-top: 4px solid var(--success);">
                <div style="display: flex; justify-content: space-between; align-items: start;">
                    <h4 style="margin: 0; color: var(--primary);">{summary['type']}</h4>
                    <span class="cheapest-badge">Best</span>
                </div>
                <div style="margin: 1rem 0;">
                    <div style="color: var(--text-secondary); font-size: 0.9rem;">Best Companies</div>
                    <div style="font-weight: 500; color: var(--text-primary);">{summary['companies']}</div>
                </div>
                <div style="display: flex; justify-content: space-between; margin-top: 1rem;">
                    <div>
                        <div style="color: var(--text-secondary); font-size: 0.85rem;">Price/Liter</div>
                        <div style="font-size: 1.2rem; font-weight: 600;">฿{summary['price_per_l']:,.2f}</div>
                    </div>
                    <div style="text-align: right;">
                        <div style="color: var(--text-secondary); font-size: 0.85rem;">Trip Cost</div>
                        <div class="price-highlight">฿{summary['trip_cost']:,.2f}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

# ---------------------------------------
# Detailed Comparison Tabs
# ---------------------------------------
st.markdown("## 📊 Detailed Analysis")

# สร้าง tabs ที่นี่!
tab1, tab2, tab3 = st.tabs(["Fuel Type Comparison", "Visual Analysis", "Data Table"])

with tab1:
    st.markdown("### 🔍 Compare All Options")
    
    for type_name, sub in prices_long.groupby("TYPE_NAME"):
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            color: white;
            padding: 1rem;
            border-radius: 10px;
            margin: 1rem 0;
        ">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div style="font-size: 1.2rem; font-weight: bold;">
                    ⛽ {type_name}
                </div>
                <div style="font-size: 0.9rem; opacity: 0.9;">
                    {len(sub)} options
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        sub_sorted = sub.sort_values("TRIP_COST_BAHT")
        
        for _, row in sub_sorted.iterrows():
            is_cheapest = bool(row["IS_CHEAPEST_IN_TYPE"])
            
            col1, col2, col3 = st.columns([2, 3, 1])
            
            with col1:
                st.markdown(f"**{row['COMPANY']}**")
                if is_cheapest:
                    st.markdown('<span style="color: green; font-weight: bold; font-size: 0.8rem;">✓ BEST</span>', 
                              unsafe_allow_html=True)
            
            with col2:
                min_price = sub_sorted['TRIP_COST_BAHT'].min()
                max_price = sub_sorted['TRIP_COST_BAHT'].max()
                price_range = max_price - min_price
                if price_range > 0:
                    position = (row['TRIP_COST_BAHT'] - min_price) / price_range
                    bar_width = 100 - (position * 50)
                else:
                    bar_width = 100
                
                st.markdown(f"""
                <div style="margin: 0.3rem 0;">
                    <div style="display: flex; justify-content: space-between;">
                        <span style="font-size: 1.1rem; font-weight: 600; color: var(--accent);">
                            ฿{row['TRIP_COST_BAHT']:,.2f}
                        </span>
                        <span style="font-size: 0.9rem; color: #666;">
                            {row['PRICE_PER_L']:,.2f} ฿/L
                        </span>
                    </div>
                    <div style="
                        height: 8px;
                        background: {'linear-gradient(90deg, #4CAF50, #8BC34A)' if is_cheapest else 'linear-gradient(90deg, #90CAF9, #E3F2FD)'};
                        border-radius: 4px;
                        margin-top: 0.3rem;
                        width: {bar_width}%;
                    "></div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div style="
                    background: {'#E8F5E9' if is_cheapest else '#F5F5F5'};
                    padding: 0.3rem 0.8rem;
                    border-radius: 12px;
                    text-align: center;
                ">
                    <strong>#{int(row['RANK_IN_TYPE'])}</strong>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("---")

with tab2:
    st.markdown("### 📈 Visual Comparison")
    
    type_for_chart = st.selectbox(
        "Select Fuel Type for Visualization", 
        options=sorted(prices_long["TYPE_NAME"].unique().tolist()),
        key="chart_type"
    )
    
    chart_df = prices_long[prices_long["TYPE_NAME"] == type_for_chart].copy()
    chart_df["LABEL"] = chart_df["COMPANY"]
    
    bar = alt.Chart(chart_df).mark_bar(
        cornerRadiusTopLeft=4,
        cornerRadiusTopRight=4
    ).encode(
        x=alt.X("LABEL:N", 
                title="Company",
                axis=alt.Axis(labelAngle=0),
                sort=list(chart_df.sort_values("TRIP_COST_BAHT")["LABEL"])),
        y=alt.Y("TRIP_COST_BAHT:Q", 
                title="Trip Cost (THB)",
                scale=alt.Scale(zero=False)),
        color=alt.Color("IS_CHEAPEST_IN_TYPE:N", 
                       title="Best Option",
                       scale=alt.Scale(domain=[False, True], range=["#90CAF9", "#00c853"]),
                       legend=None),
        tooltip=[
            alt.Tooltip("COMPANY:N", title="Company"),
            alt.Tooltip("PRICE_PER_L:Q", title="Price/Liter", format=".2f"),
            alt.Tooltip("TRIP_COST_BAHT:Q", title="Trip Cost", format=".2f"),
            alt.Tooltip("RANK_IN_TYPE:Q", title="Rank"),
        ]
    ).properties(
        height=400,
        title=f"Trip Cost Comparison for {type_for_chart}"
    )
    
    text = bar.mark_text(
        align='center',
        baseline='bottom',
        dy=-5,
        fontSize=12,
        fontWeight='bold'
    ).encode(
        text=alt.Text('TRIP_COST_BAHT:Q', format='.2f')
    )
    
    st.altair_chart(bar + text, use_container_width=True)

with tab3:
    st.markdown("### 📋 Detailed Data Table")
    
    table_df = prices_long[[
        "TYPE_NAME", "COMPANY", "PRICE_PER_L", 
        "LITERS_NEEDED", "TRIP_COST_BAHT", "RANK_IN_TYPE"
    ]].sort_values(["TYPE_NAME", "TRIP_COST_BAHT", "COMPANY"])
    
    display_df = table_df.copy()
    display_df["PRICE_PER_L"] = display_df["PRICE_PER_L"].map(lambda x: f"฿{x:,.2f}")
    display_df["TRIP_COST_BAHT"] = display_df["TRIP_COST_BAHT"].map(lambda x: f"฿{x:,.2f}")
    display_df["LITERS_NEEDED"] = display_df["LITERS_NEEDED"].map(lambda x: f"{x:,.2f} L")
    display_df["RANK_IN_TYPE"] = display_df["RANK_IN_TYPE"].astype(int)
    
    st.dataframe(
        display_df,
        use_container_width=True,
        column_config={
            "TYPE_NAME": "Fuel Type",
            "COMPANY": "Company",
            "PRICE_PER_L": "Price/Liter",
            "LITERS_NEEDED": "Fuel Required",
            "TRIP_COST_BAHT": "Trip Cost",
            "RANK_IN_TYPE": "Rank"
        },
        hide_index=True
    )

# ---------------------------------------
# Download Section
# ---------------------------------------
st.markdown("---")
col1, col2 = st.columns([3, 1])

with col1:
    st.markdown("### 💾 Export Results")
    st.markdown("""
    <div style="color: var(--text-secondary);">
        Download the complete analysis for offline review or further processing.
        The CSV file contains all calculated trip costs with detailed breakdown.
    </div>
    """, unsafe_allow_html=True)

with col2:
    csv_data = table_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download CSV Report",
        data=csv_data,
        file_name=f"fuel_trip_analysis_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        mime="text/csv",
        type="primary",
        use_container_width=True
    )

# ---------------------------------------
# Footer
# ---------------------------------------
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: var(--text-secondary); padding: 2rem 0;">
    <div style="font-size: 0.9rem; margin-bottom: 0.5rem;">
        ⛽ Fuel Trip Calculator Premium Edition • Data Source: PROJECT_5001.OIL_PRICE
    </div>
    <div style="font-size: 0.8rem; opacity: 0.7;">
        Last updated: {date} • Calculations based on latest available pricing data
    </div>
</div>
""".format(date=latest_date.strftime('%d %B %Y') if latest_date else "N/A"), 
unsafe_allow_html=True)