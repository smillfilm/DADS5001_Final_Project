
# oilprice_change_board.py
import streamlit as st
import pandas as pd
import snowflake.connector
import altair as alt
from datetime import datetime

# ---------------------------
# Page config - Premium Theme
# ---------------------------
st.set_page_config(
    page_title="Oil Price Dashboard | Premium", 
    page_icon="📊", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for premium look - Matching the trip calculator style
st.markdown("""
<style>
    /* Main theme colors - Consistent with trip calculator */
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
        color: var(--primary);
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
    
    /* Premium Cards */
    .premium-card {
        background: var(--card-bg);
        border-radius: 16px;
        padding: 1.5rem;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        transition: all 0.3s ease;
        height: 100%;
    }
    
    .premium-card:hover {
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        transform: translateY(-2px);
    }
    
/* Price Cards - New Design */
.price-card {
    background: black;
    border-radius: 12px;
    padding: 1.25rem;
    margin-bottom: 1rem;
    border: 1px solid #e2e8f0;
    transition: all 0.3s ease;
    color: white; /* เพื่อให้ข้อความอ่านง่ายบนพื้นหลังดำ */
}

.price-card:hover {
    border-color: var(--accent);
    box-shadow: 0 4px 12px rgba(0, 184, 212, 0.15);
}

.price-card.up {
    border-left: 4px solid #ef5350;
    background: linear-gradient(135deg, #FFEBEE, #ffffff);
    color: black; /* ข้อความสีดำบนพื้นหลังอ่อน */
}

.price-card.down {
    border-left: 4px solid #66BB6A;
    background: linear-gradient(135deg, #E8F5E9, #ffffff);
    color: black; /* ข้อความสีดำบนพื้นหลังอ่อน */
}

.price-card.neutral {
    border-left: 4px solid #90CAF9;
    background: linear-gradient(135deg, #1B5E20, #388E3C, #66BB6A); /* พื้นหลังสีเขียวไล่ระดับ */
    color: white; /* ข้อความสีขาวเพื่อความคมชัด */
}
    
    .card-title {
        font-weight: 600;
        color: black;
        margin-bottom: 0.5rem;
        font-size: 1rem;
    }
    
    .card-price {
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--text-primary);
        margin: 0.5rem 0;
    }
    
    .card-diff {
        font-size: 0.9rem;
        font-weight: 600;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        display: inline-block;
    }
    
    .diff-up {
        background: linear-gradient(135deg, #FFEBEE, #FFCDD2);
        color: #d32f2f;
    }
    
    .diff-down {
        background: linear-gradient(135deg, #E8F5E9, #C8E6C9);
        color: #2E7D32;
    }
    
    .diff-neutral {
        background: #F5F5F5;
        color: #666;
    }
    
    .card-meta {
        font-size: 0.8rem;
        color: var(--text-secondary);
        margin-top: 0.75rem;
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
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        background-color: var(--light-bg);
        color : black;
        padding: 0.5rem;
        border-radius: 12px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 0.5rem 1rem;
        color : black;
        font-weight: 500;
    }
    
    /* Stats Cards */
    .stat-card {
        background: linear-gradient(135deg, var(--light-bg), white);
        border-radius: 12px;
        padding: 1.25rem;
        border-left: 4px solid var(--accent);
    }
    
    .stat-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: var(--primary);
        line-height: 1;
    }
    
    .stat-label {
        color: var(--text-secondary);
        font-size: 0.9rem;
        margin-top: 0.5rem;
    }
    
    /* Badges */
    .badge {
        background: linear-gradient(135deg, var(--accent), #00acc1);
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        display: inline-block;
    }
    
    /* Company Tags */
    .company-tag {
        display: inline-block;
        background: var(--light-bg);
        padding: 0.25rem 0.75rem;
        border-radius: 6px;
        margin: 0.25rem;
        font-size: 0.85rem;
        border-left: 3px solid var(--accent);
    }
    
    /* Footer */
    .footer {
        text-align: center;
        color: var(--text-secondary);
        padding: 2rem 0;
        border-top: 1px solid #e2e8f0;
        margin-top: 2rem;
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



# ---------------------------
# Premium Header
# ---------------------------
html_content = f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EnergyHub Pro</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Inter', sans-serif;
            background: transparent;
            color: #1e293b;
            overflow-x: hidden;
        }}
        
        /* Modern Navigation - Light Theme */
        .navbar {{
            background: rgba(255, 255, 255, 0.95) !important;
            backdrop-filter: blur(20px);
            border-bottom: 1px solid rgba(226, 232, 240, 0.8);
            padding: 1rem 0;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        }}
        
        .navbar-brand img {{
            height: 40px;
            transition: all 0.3s ease;
            filter: brightness(0.8);
        }}
        
        .nav-link {{
            color: #64748b !important;
            font-weight: 500;
            margin: 0 0.5rem;
            padding: 0.75rem 1.5rem !important;
            border-radius: 50px;
            transition: all 0.3s ease;
            position: relative;
            background: transparent;
        }}
        
        .nav-link:hover {{
            color: #1e293b !important;
            background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(29, 78, 216, 0.1) 100%);
            transform: translateY(-2px);
        }}
        
        .nav-link.active {{
            background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
            color: white !important;
            box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
        }}
        
    </style>
</head>
<body>
    <!-- Modern Navigation -->
    <nav class="navbar navbar-expand-lg navbar-light fixed-top">
        <div class="container">
           <h3>OILSOPHAENG</h3>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item"><a class="nav-link active" href="#"><i class="fas fa-home me-2"></i>Home</a></li>
                    <li class="nav-item"><a class="nav-link" href="#"><i class="fas fa-chart-line me-2"></i>Market</a></li>
                    <li class="nav-item"><a class="nav-link" href="#"><i class="fas fa-gas-pump me-2"></i>Stations</a></li>
                    <li class="nav-item"><a class="nav-link" href="#"><i class="fas fa-newspaper me-2"></i>News</a></li>
                    <li class="nav-item"><a href="/premium_detail" target="_top" class="nav-link" ><i class="fas fa-crown me-2"></i>Premium</a></li>
                    <li class="nav-item"><a href="/app_main" target="_top" class="nav-link"><i class="fas fa-key me-2"></i>Sign up</a></li>
                </ul>
            </div>
        </div>
    </nav>


    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
'''

st.components.v1.html(html_content, height=100, scrolling=False)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <h1 style="font-size: 2.5rem; margin-bottom: 0.5rem;">📊 Oil Price Dashboard</h1>
        <p style="color: var(--text-secondary); font-size: 1.1rem; margin-top: 0;">
            Real-time Fuel Price Monitoring & Analysis
        </p>
    </div>
    """, unsafe_allow_html=True)

# ---------------------------
# Snowflake connection helpers
# ---------------------------
sf = st.secrets["connections"]["snowflake"]

def get_connection():
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

# ---------------------------
# SQL Query (unchanged)
# ---------------------------
SQL_LAST_TWO_CHANGES = """
WITH system_max_date AS (
  SELECT MAX(DATE_TRANSACTION) AS MAX_DATE
  FROM OIL_TRANSACTION
  WHERE PRICE IS NOT NULL
),
active_types AS (
  SELECT DISTINCT t.TYPE_ID
  FROM OIL_TRANSACTION t
  CROSS JOIN system_max_date smd
  WHERE t.PRICE IS NOT NULL
    AND t.DATE_TRANSACTION >= DATEADD('month', -3, smd.MAX_DATE)
),
base AS (
  SELECT
    t.DATE_TRANSACTION,
    t.TYPE_ID,
    ty.TYPE_NAME,
    t.COMPANY_ID,
    com.COMPANY_NAME,
    t.PRICE,
    LAG(t.PRICE) OVER (
      PARTITION BY t.TYPE_ID, t.COMPANY_ID
      ORDER BY t.DATE_TRANSACTION
    ) AS prev_price
  FROM OIL_TRANSACTION t
  JOIN OIL_TYPE ty ON ty.TYPE_NO = t.TYPE_ID
  JOIN COMPANY com ON com.COMPANY_ID = t.COMPANY_ID
  WHERE t.PRICE IS NOT NULL
    AND t.TYPE_ID IN (SELECT TYPE_ID FROM active_types)
),
changes AS (
  SELECT
    DATE_TRANSACTION,
    TYPE_ID,
    TYPE_NAME,
    COMPANY_ID,
    COMPANY_NAME,
    PRICE,
    CASE WHEN prev_price IS NULL OR PRICE <> prev_price THEN 1 ELSE 0 END AS is_change
  FROM base
),
last2 AS (
  SELECT
    *,
    ROW_NUMBER() OVER (
      PARTITION BY TYPE_ID, COMPANY_ID
      ORDER BY DATE_TRANSACTION DESC
    ) AS rn
  FROM changes
  WHERE is_change = 1
),
last_change AS (
  SELECT
    TYPE_ID, TYPE_NAME, COMPANY_ID, COMPANY_NAME,
    DATE_TRANSACTION AS DATE_LAST_CHANGE,
    PRICE AS PRICE_LAST
  FROM last2 WHERE rn = 1
),
prev_change AS (
  SELECT
    TYPE_ID, TYPE_NAME, COMPANY_ID, COMPANY_NAME,
    DATE_TRANSACTION AS DATE_PREV_CHANGE,
    PRICE AS PRICE_PREV
  FROM last2 WHERE rn = 2
),
final AS (
  SELECT
    lc.TYPE_ID, lc.TYPE_NAME, lc.COMPANY_ID, lc.COMPANY_NAME,
    lc.DATE_LAST_CHANGE, lc.PRICE_LAST,
    pc.DATE_PREV_CHANGE, pc.PRICE_PREV
  FROM last_change lc
  LEFT JOIN prev_change pc
    ON pc.TYPE_ID = lc.TYPE_ID
   AND pc.COMPANY_ID = lc.COMPANY_ID
)
SELECT
  TYPE_ID, TYPE_NAME, COMPANY_ID, COMPANY_NAME,
  DATE_LAST_CHANGE, PRICE_LAST,
  DATE_PREV_CHANGE, PRICE_PREV
FROM final
ORDER BY COMPANY_NAME, TYPE_NAME;
"""

df = run_query(SQL_LAST_TWO_CHANGES)

# Process data
df["DATE_LAST_CHANGE"] = pd.to_datetime(df["DATE_LAST_CHANGE"], errors="coerce")
df["DATE_PREV_CHANGE"] = pd.to_datetime(df["DATE_PREV_CHANGE"], errors="coerce")
df["PRICE_LAST"] = pd.to_numeric(df["PRICE_LAST"], errors="coerce")
df["PRICE_PREV"] = pd.to_numeric(df["PRICE_PREV"], errors="coerce")
df["DIFF_FROM_PREV_CHANGE"] = df["PRICE_LAST"] - df["PRICE_PREV"]

# Get max date
max_date_sql = "SELECT MAX(DATE_TRANSACTION) AS MAX_DATE FROM OIL_TRANSACTION"
max_date_df = run_query(max_date_sql)
max_date = pd.to_datetime(max_date_df.iloc[0]["MAX_DATE"]) if not max_date_df.empty else None

# ---------------------------
# Premium Sidebar Design
# ---------------------------
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0; margin-bottom: 2rem;">
        <h2 style="color: white; margin-bottom: 0.5rem;">⚙️ Dashboard Settings</h2>
        <p style="color: rgba(255,255,255,0.8); font-size: 0.9rem; margin: 0;">
            Configure your view settings
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    companies_avail = sorted(df["COMPANY_NAME"].dropna().unique().tolist())
    types_avail = sorted(df["TYPE_NAME"].dropna().unique().tolist())
    
    st.markdown('<div class="premium-card">', unsafe_allow_html=True)
    selected_companies = st.multiselect(
        "**Select Companies**", 
        options=companies_avail,
        default=companies_avail[:3] if companies_avail else [],
        help="Choose companies to display"
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="premium-card">', unsafe_allow_html=True)
    selected_types = st.multiselect(
        "**Select Fuel Types**", 
        options=types_avail,
        default=types_avail[:6] if types_avail else [],
        help="Choose fuel types to display"
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="premium-card">', unsafe_allow_html=True)
    sort_by = st.selectbox(
        "**Sort Fuel Types By**", 
        ["Type Name", "Latest Price"], 
        index=0
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Data freshness indicator
    if max_date:
        st.markdown(f"""
        <div style="background: rgba(255,255,255,0.1); padding: 0.75rem; border-radius: 8px; margin-top: 1rem;">
            <div style="color: rgba(255,255,255,0.9); font-size: 0.85rem; display: flex; align-items: center; gap: 0.5rem;">
                <span style="font-size: 1.2rem;">🔄</span>
                <div>
                    <div style="font-weight: 500;">Latest Data</div>
                    <div>{max_date.strftime('%d %b %Y')}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ---------------------------
# Dashboard Header with Stats
# ---------------------------
st.markdown("## 📈 Market Overview")

# Filter data
df_filtered = df.copy()
if selected_companies:
    df_filtered = df_filtered[df_filtered["COMPANY_NAME"].isin(selected_companies)]
if selected_types:
    df_filtered = df_filtered[df_filtered["TYPE_NAME"].isin(selected_types)]

if df_filtered.empty:
    st.warning("No data available for selected filters. Please adjust your selection.")
    st.stop()

# Calculate statistics
total_companies = df_filtered["COMPANY_NAME"].nunique()
total_types = df_filtered["TYPE_NAME"].nunique()
avg_price = df_filtered["PRICE_LAST"].mean()
price_changes = df_filtered["DIFF_FROM_PREV_CHANGE"].notna().sum()

# Display stats in cards
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-value">{total_companies}</div>
        <div class="stat-label">Companies</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-value">{total_types}</div>
        <div class="stat-label">Fuel Types</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-value">฿{avg_price:,.2f}</div>
        <div class="stat-label">Avg. Price</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-value">{price_changes}</div>
        <div class="stat-label">Price Changes</div>
    </div>
    """, unsafe_allow_html=True)

# Data freshness info
st.markdown(f"""
<div style="background: linear-gradient(135deg, #E3F2FD, #BBDEFB); 
            padding: 1rem; 
            border-radius: 10px; 
            margin: 1.5rem 0;">
    <div style="display: flex; align-items: center; gap: 1rem;">
        <div style="font-size: 1.5rem;">📅</div>
        <div>
            <div style="font-weight: 600; color: var(--primary);">
                Latest System Date: {max_date.date() if pd.notna(max_date) else 'N/A'}
            </div>
            <div style="color: var(--text-secondary); font-size: 0.9rem;">
                Price differences calculated from latest price change date compared to previous change date
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("## ⛽ Fuel Price Comparison")

# Create tabs for different views
tab1, tab2, tab3 = st.tabs(["Company View", "Fuel Type View", "Price Analysis"])

with tab1:
    st.markdown("### 📊 Prices by Company")
    
    # Group by company
    for company_name in (selected_companies if selected_companies else companies_avail):
        company_data = df_filtered[df_filtered["COMPANY_NAME"] == company_name].copy()
        
        if company_data.empty or company_data["DATE_PREV_CHANGE"].notna().any():
            # Header for company
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, var(--primary), var(--secondary)); 
                        color: white; 
                        padding: 1rem; 
                        border-radius: 10px; 
                        margin: 1rem 0;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div style="font-size: 1.2rem; font-weight: bold;">🏢 {company_name}</div>
                    <div style="font-size: 0.9rem; opacity: 0.9;">
                        {len(company_data)} fuel types
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Sort data
            if sort_by == "Latest Price":
                company_data = company_data.sort_values(["PRICE_LAST", "TYPE_NAME"])
            else:
                company_data = company_data.sort_values("TYPE_NAME")
            
            # Display price cards in grid
            cols = st.columns(3)
            for idx, (_, row) in enumerate(company_data.iterrows()):
                with cols[idx % 3]:
                    typ = row["TYPE_NAME"]
                    price = row["PRICE_LAST"]
                    d_last = row["DATE_LAST_CHANGE"]
                    d_prev = row["DATE_PREV_CHANGE"]
                    diff = row["DIFF_FROM_PREV_CHANGE"]
                    
                    # Determine card style and diff display
                    if pd.notna(diff):
                        if diff > 0:
                            card_class = "up"
                            diff_class = "diff-up"
                            diff_symbol = "▲"
                            diff_display = f"+{diff:.2f}"
                        elif diff < 0:
                            card_class = "down"
                            diff_class = "diff-down"
                            diff_symbol = "▼"
                            diff_display = f"{diff:.2f}"
                        else:
                            card_class = "neutral"
                            diff_class = "diff-neutral"
                            diff_symbol = "—"
                            diff_display = "0.00"
                    else:
                        card_class = "neutral"
                        diff_class = "diff-neutral"
                        diff_symbol = "—"
                        diff_display = "N/A"
                    
                    # Render price card
                    st.markdown(f"""
                    <div class="price-card {card_class}">
                        <div class="card-title">{typ}</div>
                        <div class="card-price">฿{price:,.2f}</div>
                        <div class="{diff_class} card-diff">
                            {diff_symbol} {diff_display}
                        </div>
                        <div class="card-meta">
                            Updated: {d_last.date() if pd.notna(d_last) else 'N/A'}<br>
                            Prev: {d_prev.date() if pd.notna(d_prev) else '—'}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Add spacing between companies
            st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

with tab2:
    st.markdown("### 🔍 Prices by Fuel Type")
    
    # Group by fuel type
    fuel_types = sorted(df_filtered["TYPE_NAME"].unique())
    
    for fuel_type in fuel_types:
        type_data = df_filtered[df_filtered["TYPE_NAME"] == fuel_type].copy()
        
        if type_data.empty:
            continue
            
        # Header for fuel type
        st.markdown(f"#### ⛽ {fuel_type}")
        st.caption(f"{len(type_data)} companies available")
        
        # Sort by price
        type_data = type_data.sort_values("PRICE_LAST")
        
        # Find cheapest option
        cheapest = type_data["PRICE_LAST"].min()
        
        # Display company prices in a clean grid
        num_items = len(type_data)
        num_cols = 4
        
        # Create grid layout
        grid = st.columns(num_cols)
        
        for idx in range(num_items):
            row = type_data.iloc[idx]
            company = row["COMPANY_NAME"]
            price = row["PRICE_LAST"]
            diff = row["DIFF_FROM_PREV_CHANGE"]
            d_last = row["DATE_LAST_CHANGE"]
            d_prev = row["DATE_PREV_CHANGE"]
            
            # Determine column
            col_idx = idx % num_cols
            col = grid[col_idx]
            
            with col:
                # Determine styling
                is_cheapest = price == cheapest
                
                
                # Format dates
                last_date = d_last.strftime('%Y-%m-%d') if pd.notna(d_last) else 'N/A'
                prev_date = d_prev.strftime('%Y-%m-%d') if pd.notna(d_prev) else '—'


                                # Create card using container
                with st.container():
                    # Determine card class based on price change
                    if pd.notna(diff):
                      if diff > 0:
                        card_class = "up"
                        diff_class = "diff-up"
                        diff_symbol = "▲"
                        diff_display = f"+{diff:.2f}"
                      elif diff < 0:
                        card_class = "down"
                        diff_class = "diff-down"
                        diff_symbol = "▼"
                        diff_display = f"{diff:.2f}"
                      else:
                        card_class = "neutral"
                        diff_class = "diff-neutral"
                        diff_symbol = "—"
                        diff_display = "0.00"
                    else:
                        card_class = "neutral"
                        diff_class = "diff-neutral"
                        diff_symbol = "—"
                        diff_display = "N/A"
                    
                    # Add best badge to company name if cheapest
                    company_display = f"{company} {'<span class="best-badge">★ Best</span>' if is_cheapest else ''}"
                    
                    # Render price card
                    st.markdown(f"""
                    <div class="price-card {card_class}">
                        <div class="card-title">{typ}</div>
                        <div class="card-price">฿{price:,.2f}</div>
                        <div class="{diff_class} card-diff">
                            {diff_symbol} {diff_display}
                        </div>
                        <div class="card-meta">
                            Updated: {d_last.date() if pd.notna(d_last) else 'N/A'}<br>
                            Prev: {d_prev.date() if pd.notna(d_prev) else '—'}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                                


with tab3:
    st.markdown("### 📈 Price Analysis")
    
    # Summary table
    st.markdown("#### 📋 Price Change Summary")
    
    # Calculate summary statistics
    summary_df = df_filtered.copy()
    summary_df["Change Status"] = summary_df["DIFF_FROM_PREV_CHANGE"].apply(
        lambda x: "Increased" if pd.notna(x) and x > 0 else 
                  "Decreased" if pd.notna(x) and x < 0 else 
                  "Unchanged" if pd.notna(x) and x == 0 else "No Previous"
    )
    # Price range analysis
    st.markdown("#### 📊 Price Range Analysis")
    
    if not summary_df.empty:
        # Create price distribution chart
        chart = alt.Chart(summary_df).mark_bar(
            cornerRadiusTopLeft=4,
            cornerRadiusTopRight=4
        ).encode(
            x=alt.X("PRICE_LAST:Q", 
                   title="Price (THB/Liter)",
                   bin=alt.Bin(maxbins=20)),
            y=alt.Y("count():Q", title="Count"),
            color=alt.Color("Change Status:N", 
                          scale=alt.Scale(
                              domain=["Increased", "Decreased", "Unchanged", "No Previous"],
                              range=["#ef5350", "#66BB6A", "#90CAF9", "#BDBDBD"]
                          ),
                          title="Price Change")
        ).properties(
            height=300,
            title="Price Distribution by Change Status"
        )
        
        st.altair_chart(chart, use_container_width=True)

# ---------------------------
# Detailed Data Table
# ---------------------------
st.markdown("## 📋 Detailed Price Data")

# Format table for display
display_df = df_filtered.copy()
display_df = display_df.rename(columns={
    "TYPE_NAME": "Fuel Type",
    "COMPANY_NAME": "Company",
    "DIFF_FROM_PREV_CHANGE": "Price Change",
    "DATE_LAST_CHANGE": "Last Change Date", 
    "PRICE_LAST": "Latest Price",
    "DATE_PREV_CHANGE": "Previous Change Date", 
    "PRICE_PREV": "Previous Price"
})

# Format columns
display_df["Latest Price"] = display_df["Latest Price"].map(lambda x: f"฿{x:,.2f}" if pd.notna(x) else "N/A")
display_df["Previous Price"] = display_df["Previous Price"].map(lambda x: f"฿{x:,.2f}" if pd.notna(x) else "N/A")
display_df["Price Change"] = display_df["Price Change"].apply(
    lambda x: f"▲ +{x:,.2f}" if pd.notna(x) and x > 0 else 
              f"▼ {x:,.2f}" if pd.notna(x) and x < 0 else 
              "— 0.00" if pd.notna(x) else "N/A"
)
# Define colors
COLOR_UP = "#ef5350"    # Red
COLOR_DOWN = "#66BB6A"  # Green
COLOR_NEUTRAL = "#757575" # Gray
COLOR_NA = "#9e9e9e"    # Light Gray

def color_price_change(val):
    if isinstance(val, str):
        if "▲" in val:
            return f"color: {COLOR_UP}; font-weight: 600;"
        elif "▼" in val:
            return f"color: {COLOR_DOWN}; font-weight: 600;"
        elif "—" in val:
            return f"color: {COLOR_NEUTRAL};"
    return ""

# Apply styling
styled_df = display_df[["Fuel Type", "Company", "Latest Price", "Price Change", 
                       "Last Change Date", "Previous Change Date", "Previous Price"]]\
    .style.applymap(color_price_change, subset=["Price Change"])

st.dataframe(
    styled_df,
    use_container_width=True,
    hide_index=True
)

# Add color explanation
st.caption("Legend: ▲ Red = Price increase, ▼ Green = Price decrease, — Gray = No change")

# แก้ไขส่วน Historical Price Chart ที่มีปัญหา

# ---------------------------
# Historical Price Chart - แก้ไขส่วนนี้
# ---------------------------
st.markdown("## 📈 Historical Price Trends")

col1, col2 = st.columns(2)
with col1:
    hist_type = st.selectbox(
        "Select Fuel Type", 
        options=sorted(df_filtered["TYPE_NAME"].unique().tolist()),
        key="hist_type"
    )
with col2:
    hist_company = st.selectbox(
        "Select Company", 
        options=sorted(df_filtered[df_filtered["TYPE_NAME"] == hist_type]["COMPANY_NAME"].unique().tolist()),
        key="hist_company"
    )

# Query historical data
HIST_SQL = f"""
SELECT t.DATE_TRANSACTION, ty.TYPE_NAME, com.COMPANY_NAME, t.PRICE
FROM OIL_TRANSACTION t
JOIN OIL_TYPE ty ON ty.TYPE_NO = t.TYPE_ID
JOIN COMPANY com ON com.COMPANY_ID = t.COMPANY_ID
WHERE ty.TYPE_NAME = '{hist_type}'
  AND com.COMPANY_NAME = '{hist_company}'
  AND t.DATE_TRANSACTION >= DATEADD('day', -30, (SELECT MAX(DATE_TRANSACTION) FROM OIL_TRANSACTION))
ORDER BY t.DATE_TRANSACTION
"""

hist = run_query(HIST_SQL)

if not hist.empty:
    hist["DATE_TRANSACTION"] = pd.to_datetime(hist["DATE_TRANSACTION"], errors="coerce")
    hist["PRICE"] = pd.to_numeric(hist["PRICE"], errors="coerce")
    
    # แก้ไขตรงนี้: ใช้ค่าสีโดยตรงแทน var() function
    chart = alt.Chart(hist).mark_line(
        point=True,
        color="#00b8d4",  # ใช้ค่าสีของ --accent โดยตรง
        strokeWidth=3
    ).encode(
        x=alt.X("DATE_TRANSACTION:T", title="Date"),
        y=alt.Y("PRICE:Q", title="Price (THB/Liter)"),
        tooltip=[
            alt.Tooltip("DATE_TRANSACTION:T", title="Date", format="%Y-%m-%d"),
            alt.Tooltip("PRICE:Q", title="Price", format=".2f"),
            alt.Tooltip("TYPE_NAME:N", title="Fuel Type"),
            alt.Tooltip("COMPANY_NAME:N", title="Company"),
        ],
    ).properties(
        height=400,
        title=f"30-Day Price Trend: {hist_type} - {hist_company}"
    )
    
    st.altair_chart(chart, use_container_width=True)
    
    # Optional: Add summary statistics
    col1, col2, col3 = st.columns(3)
    with col1:
        avg_price = hist["PRICE"].mean()
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #E3F2FD, #BBDEFB); 
                    padding: 1rem; 
                    border-radius: 10px;">
            <div style="font-size: 0.9rem; color: #1976D2;">Average Price</div>
            <div style="font-size: 1.5rem; font-weight: 700; color: var(--primary);">
                ฿{avg_price:,.2f}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        min_price = hist["PRICE"].min()
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #E8F5E9, #C8E6C9); 
                    padding: 1rem; 
                    border-radius: 10px;">
            <div style="font-size: 0.9rem; color: #2E7D32;">Lowest Price</div>
            <div style="font-size: 1.5rem; font-weight: 700; color: #2E7D32;">
                ฿{min_price:,.2f}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        max_price = hist["PRICE"].max()
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #FFEBEE, #FFCDD2); 
                    padding: 1rem; 
                    border-radius: 10px;">
            <div style="font-size: 0.9rem; color: #d32f2f;">Highest Price</div>
            <div style="font-size: 1.5rem; font-weight: 700; color: #d32f2f;">
                ฿{max_price:,.2f}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Optional: Add data table
    with st.expander("View Historical Data"):
        hist_display = hist.copy()
        hist_display["DATE_TRANSACTION"] = hist_display["DATE_TRANSACTION"].dt.strftime('%Y-%m-%d')
        hist_display["PRICE"] = hist_display["PRICE"].map(lambda x: f"฿{x:,.2f}")
        st.dataframe(
            hist_display[["DATE_TRANSACTION", "PRICE"]],
            column_config={
                "DATE_TRANSACTION": "Date",
                "PRICE": "Price (THB/Liter)"
            },
            hide_index=True,
            use_container_width=True
        )
        
else:
    st.info("📊 No historical data available for the selected combination.")
    
    # Show available options
    st.markdown("#### Available Data Options:")
    available_data = df_filtered[["TYPE_NAME", "COMPANY_NAME"]].drop_duplicates()
    available_data = available_data.sort_values(["TYPE_NAME", "COMPANY_NAME"])
    
    for _, row in available_data.iterrows():
        st.markdown(f"- **{row['TYPE_NAME']}** - {row['COMPANY_NAME']}")

# ---------------------------
# Footer
# ---------------------------
st.markdown("---")
st.markdown("""
<div class="footer">
    <div style="font-size: 0.9rem; margin-bottom: 0.5rem;">
        📊 Oil Price Dashboard Premium • Data Source: PROJECT_5001.OIL_PRICE
    </div>
    <div style="font-size: 0.8rem; opacity: 0.7;">
        Last updated: {date} • Real-time price monitoring system
    </div>
</div>
""".format(date=datetime.now().strftime('%d %B %Y, %H:%M')), 
unsafe_allow_html=True)