import streamlit as st
from pathlib import Path
import base64
import pandas as pd
import folium
from streamlit_folium import st_folium
import random
from datetime import datetime
import webbrowser
import os
import plotly.express as px
import duckdb
import streamlit.components.v1 as components

# ---------------- Page Config ----------------
st.set_page_config(
    page_title="OILSOPHAENG,Co.td",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------- Light Background with Soft Gradient ----------------
def set_light_bg():
    st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, 
            #f8fafc 0%,
            #f1f5f9 25%,
            #e2e8f0 50%,
            #f1f5f9 75%,
            #f8fafc 100%);
        background-size: 400% 400%;
        animation: gradientShift 15s ease infinite;
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50% }
        50% { background-position: 100% 50% }
        100% { background-position: 0% 50% }
    }
    
    /* Modern Glass Morphism Cards */
    .main .block-container {
        background: rgba(255, 255, 255, 0.8);
        backdrop-filter: blur(20px);
        border-radius: 24px;
        border: 1px solid rgba(255, 255, 255, 0.3);
        margin: 20px;
        padding: 30px;
        box-shadow: 
            0 8px 32px rgba(0, 0, 0, 0.1),
            inset 0 1px 0 rgba(255, 255, 255, 0.8);
    }
    
    /* Text Colors for Light Background */
    h1, h2, h3, h4, h5, h6 {
        color: #1e293b !important;
        font-family: 'Inter', sans-serif;
        font-weight: 700;
    }
    
    p, div, span, label {
        color: #475569 !important;
        font-family: 'Inter', sans-serif;
    }
    
    /* Modern Card Design - Light Theme */
    .modern-card {
        background: linear-gradient(135deg, 
            rgba(255, 255, 255, 0.9) 0%,
            rgba(248, 250, 252, 0.9) 100%);
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.5);
        border-radius: 20px;
        padding: 25px;
        margin: 15px 0;
        box-shadow: 
            0 8px 32px rgba(0, 0, 0, 0.08),
            inset 0 1px 0 rgba(255, 255, 255, 0.9);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .modern-card:hover {
        transform: translateY(-5px);
        box-shadow: 
            0 20px 40px rgba(0, 0, 0, 0.12),
            inset 0 1px 0 rgba(255, 255, 255, 0.9);
        border-color: rgba(59, 130, 246, 0.3);
    }
    
    /* Gradient Text for Light Background */
    .gradient-text {
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    /* Metric Cards Enhancement */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, 
            rgba(255, 255, 255, 0.9) 0%,
            rgba(248, 250, 252, 0.9) 100%) !important;
        border: 1px solid rgba(255, 255, 255, 0.5) !important;
        border-radius: 16px !important;
        padding: 20px !important;
        backdrop-filter: blur(15px);
    }
    
    /* Custom Scrollbar for Light Theme */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(241, 245, 249, 0.8);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
        border-radius: 10px;
    }
    
    /* Hide Streamlit Default Elements */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    [data-testid="stSidebar"] {display: none;}
    
    /* Input Fields Styling */
    .stTextInput>div>div>input {
        background: rgba(255, 255, 255, 0.8) !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 12px !important;
    }
    
    /* Select Box Styling */
    .stSelectbox>div>div>div {
        background: rgba(255, 255, 255, 0.8) !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 12px !important;
    }
    
    /* Sign Up Button Styling */
    .signup-btn {
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 12px 24px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }
    
    .signup-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(59, 130, 246, 0.4) !important;
    }

    /* Link Styling */
    .custom-link {
        color: #3b82f6 !important;
        text-decoration: none;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .custom-link:hover {
        color: #1d4ed8 !important;
        text-decoration: underline;
    }
    
    /* Direct Link Button */
    .direct-link-btn {
        display: inline-block;
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
        color: white !important;
        padding: 12px 30px;
        border-radius: 12px;
        text-decoration: none;
        font-weight: 600;
        text-align: center;
        transition: all 0.3s ease;
        border: none;
        cursor: pointer;
        margin: 10px 0;
    }
    
    .direct-link-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(59, 130, 246, 0.4);
        color: white !important;
        text-decoration: none;
    }
    </style>
    """, unsafe_allow_html=True)

# Set light background
set_light_bg()

# ---------------- Enhanced Navigation ----------------
logo_path = Path("image/Logo.png")
logo_bytes = logo_path.read_bytes()
logo_base64 = base64.b64encode(logo_bytes).decode()

# ---------------- Sign Up Functionality ----------------
def redirect_to_app_main():
    """Redirect to app_main file - WORKING VERSION"""
    # วิธีที่ 1: ใช้ JavaScript redirect
    st.markdown("""
    <script>
    window.open('app_main', '_self');
    </script>
    """, unsafe_allow_html=True)
    
    # วิธีที่ 2: แสดงลิงก์ให้คลิกโดยตรง
    st.markdown("""
    <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(29, 78, 216, 0.1) 100%); border-radius: 15px; margin: 20px 0;">
        <h3 style="color: #1e293b;">🚀 Redirecting to Sign Up Page</h3>
        <p style="color: #64748b; margin: 15px 0;">If you are not redirected automatically, please click the button below:</p>
        <a href="app_main" class="direct-link-btn" style="display: inline-block;">
            📝 Go to Sign Up Page
        </a>
    </div>
    """, unsafe_allow_html=True)

# Initialize session state for sign up
if 'signup_clicked' not in st.session_state:
    st.session_state.signup_clicked = False

# Enhanced HTML with Light Theme Design
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
        
        /* Hero Section - Light Theme */
        .hero-section {{
            background: linear-gradient(135deg, 
                rgba(255, 255, 255, 0.9) 0%,
                rgba(248, 250, 252, 0.8) 50%,
                rgba(255, 255, 255, 0.9) 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            position: relative;
            overflow: hidden;
            backdrop-filter: blur(10px);
        }}
        
        .hero-section::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: 
                radial-gradient(circle at 20% 80%, rgba(59, 130, 246, 0.1) 0%, transparent 50%),
                radial-gradient(circle at 80% 20%, rgba(29, 78, 216, 0.1) 0%, transparent 50%);
            z-index: 1;
        }}
        
        .hero-content {{
            position: relative;
            z-index: 2;
            text-align: center;
        }}
        
        .hero-title {{
            font-size: 4rem;
            font-weight: 800;
            background: linear-gradient(135deg, #1e293b 0%, #475569 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 1.5rem;
            line-height: 1.1;
        }}
        
        .hero-subtitle {{
            font-size: 1.5rem;
            color: #64748b;
            margin-bottom: 2rem;
            font-weight: 400;
        }}
        
        .cta-button {{
            background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
            border: none;
            padding: 1rem 2.5rem;
            border-radius: 50px;
            color: white;
            font-weight: 600;
            font-size: 1.1rem;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
        }}
        
        .cta-button:hover {{
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(59, 130, 246, 0.4);
            color: white;
            text-decoration: none;
        }}
        
        /* Floating Elements */
        .floating {{
            animation: floating 3s ease-in-out infinite;
        }}
        
        @keyframes floating {{
            0% {{ transform: translate(0, 0px); }}
            50% {{ transform: translate(0, -15px); }}
            100% {{ transform: translate(0, 0px); }}
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
                    <li class="nav-item"><a class="nav-link" href="/settrade_sandbox" target="_top" ><i class="fas fa-chart-line me-2"></i>Market</a></li>
                    <li class="nav-item"><a class="nav-link" href="/station" target="_top" ><i class="fas fa-gas-pump me-2"></i>Stations</a></li>
                    <li class="nav-item"><a class="nav-link" href="/news" target="_top" ><i class="fas fa-newspaper me-2"></i>News</a></li>
                    <li class="nav-item"><a href="/premium_detail" target="_top" class="nav-link" ><i class="fas fa-crown me-2"></i>Premium</a></li>
                    <li class="nav-item"><a href="/app_main" target="_top" class="nav-link"><i class="fas fa-key me-2"></i>Sign up</a></li>
                </ul>
            </div>
        </div>
    </nav>

    <!-- Hero Section -->
    <section class="hero-section">
        <div class="container">
            <div class="hero-content">
                <h1 class="hero-title floating">
                    Energy Intelligence<br>Platform
                </h1>
                <p class="hero-subtitle">
                    Real-time fuel prices, market insights, and energy analytics in one powerful platform
                </p>
                <a href="app_main" class="cta-button">
                    <i class="fas fa-rocket me-2"></i>Explore Dashboard
                </a>
            </div>
        </div>
    </section>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
'''

st.components.v1.html(html_content, height=900, scrolling=False)

# ---------------- Main Content with Light Theme ----------------
st.markdown("""
<div class="modern-card">
    <div style="text-align: center; margin-bottom: 40px;">
        <h1 class="gradient-text" style="font-size: 3.5rem; margin-bottom: 20px;">
            ⚡ OILSOPHAENG
        </h1>
        <p style="font-size: 1.3rem; color: #64748b;">
            Your comprehensive energy market intelligence platform
        </p>
    </div>
</div>
""", unsafe_allow_html=True)


# ---------------- ราคาน้ำมันรายวันแบบตาราง (ตามภาพ) ----------------



# ข้อมูลราคาน้ำมันจากภาพ
conn = st.connection("snowflake", type="snowflake")

@st.cache_data
def load_oil_data():
    sql = """
        SELECT 
            DATE_TRANSACTION,
            TYPE_NAME,
            MAX(CASE WHEN COM.COMPANY_ID= 1 THEN PRICE END) AS PTT,
            MAX(CASE WHEN COM.COMPANY_ID= 2 THEN PRICE END) AS BANGCHAK,
            MAX(CASE WHEN COM.COMPANY_ID= 3 THEN PRICE END) AS SHELL,
            MAX(CASE WHEN COM.COMPANY_ID= 4 THEN PRICE END) AS ESSO,
            MAX(CASE WHEN COM.COMPANY_ID= 5 THEN PRICE END) AS CHEVRON,
            MAX(CASE WHEN COM.COMPANY_ID= 6 THEN PRICE END) AS IRPC,
            MAX(CASE WHEN COM.COMPANY_ID= 7 THEN PRICE END) AS PTG,
            MAX(CASE WHEN COM.COMPANY_ID= 8 THEN PRICE END) AS SUSCO,
            MAX(CASE WHEN COM.COMPANY_ID= 9 THEN PRICE END) AS PURE,
            MAX(CASE WHEN COM.COMPANY_ID= 10 THEN PRICE END) AS SUSCO_DEALER
        FROM OIL_TRANSACTION OT
        JOIN OIL_TYPE OTY ON OT.TYPE_ID = OTY.TYPE_NO
        JOIN COMPANY COM  ON OT.COMPANY_ID = COM.COMPANY_ID
        GROUP BY DATE_TRANSACTION, TYPE_NAME
        ORDER BY DATE_TRANSACTION, TYPE_NAME;
    """
    return pd.read_sql(sql, conn)

df = load_oil_data()

# -----------------------------
# Convert DATE_TRANSACTION to date
# -----------------------------
df['DATE_TRANSACTION'] = pd.to_datetime(df['DATE_TRANSACTION']).dt.date

# -----------------------------
# Filter วันที่ — ตัวเดียว
# -----------------------------
selected_date = st.date_input(
    "เลือกวันที่",
    value=max(df['DATE_TRANSACTION'])
)

df_filtered = df[df['DATE_TRANSACTION'] == selected_date]

st.markdown(f"""
<div class="modern-card">
    <div style="text-align: center; margin-bottom: 30px;">
        <h2 class="gradient-text" style="font-size: 2.5rem; margin-bottom: 15px;">
            ⛽ ราคาน้ำมันวันที่ {selected_date.strftime('%d/%m/%Y')}
        </h2>
        <p style="font-size: 1.2rem; color: #a0a0a0; max-width: 800px; margin: 0 auto;">
            รายงานโดยส่วนน้ำมัน สนพ. Tel 0-2612-1555 ext 567
        </p>
        <p style="font-size: 1.1rem; color: #b0b0b0; margin-top: 10px;">
            ราคาขายปลีกมาตรฐาน ในเขต กทม. นนทบุรี ปทุมธานี และสมุทรปราการ หน่วย : บาท/ลิตร
        </p>
    </div>
</div>
""", unsafe_allow_html=True)


if df_filtered.empty:
    st.warning(f"❗ ไม่มีข้อมูลสำหรับวันที่: {selected_date}")
else:
    # -----------------------------
    # HTML Table
    # -----------------------------
    oil_table_html = """
    <style>
    .oil-price-table {
        width: 100%;
        border-collapse: collapse;
        color: #37474f;
        font-family: 'Segoe UI', sans-serif;
        font-size: 0.9rem;
        background: #ffffff;
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 12px rgba(176, 224, 230, 0.3);
    }
    
    /* HEADER - แถวบนสุด */
    .oil-price-table th {
        padding: 16px 12px;
        font-weight: 600;
        border-bottom: 2px solid #e0f7fa;
    }
    
    /* คอลัมน์ที่ 1 (หัว + ข้อมูล) */
    .oil-price-table th:first-child {
        background: #e0f7fa;
        color: #00838f;
        text-align: left;
        padding-left: 24px;
        border-right: 2px solid #b2ebf2;
    }
    
    .oil-price-table td:first-child {
        background: #f4fdff;
        color: #006064;
        text-align: left;
        padding: 14px 12px 14px 24px;
        font-weight: 500;
        border-right: 2px solid #b2ebf2;
        border-bottom: 1px solid #e0f2f1;
    }
    
    /* หัวคอลัมน์อื่นๆ */
    .oil-price-table th:not(:first-child) {
        background: #f4fdff;
        color: #006064;
        text-align: center;
        border-bottom: 2px solid #cfd8dc;
    }
    
    /* ข้อมูลคอลัมน์อื่นๆ */
    .oil-price-table td:not(:first-child) {
        background: #ffffff;
        color: #455a64;
        text-align: center;
        padding: 14px 12px;
        border-bottom: 1px solid #f5f5f5;
    }
    
    /* Hover effects */
    .oil-price-table tr:hover td:first-child {
        background: #b2ebf2;
    }
    
    .oil-price-table tr:hover td:not(:first-child) {
        background: #f0f0f0;
    }
    
    /* ราคา */
    .oil-price-table .price-cell {
        font-weight: 600;
        color: #00838f;
        font-size: 0.95rem;
    }
    
    /* เส้นสุดท้ายไม่มี border */
    .oil-price-table tr:last-child td {
        border-bottom: none;
    }
    
    /* มุมโค้ง */
    .oil-price-table th:first-child {
        border-top-left-radius: 10px;
    }
    
    .oil-price-table th:last-child {
        border-top-right-radius: 10px;
    }
    
    .oil-price-table tr:last-child td:first-child {
        border-bottom-left-radius: 10px;
    }
    
    .oil-price-table tr:last-child td:last-child {
        border-bottom-right-radius: 10px;
    }
</style>

    <table class="oil-price-table">
        <thead>
            <tr>
                <th style="width: 22%;">Fuel Catagory</th>
    """

    brands = df_filtered.columns[2:]  # ['PTT', 'BANGCHAK', ...]
    for b in brands:
        oil_table_html += f'<th class="company-name">{b}</th>'
    oil_table_html += "</tr></thead><tbody>"

    for _, row in df_filtered.iterrows():
        oil_table_html += f'<tr><td class="fuel-type">{row["TYPE_NAME"]}</td>'
        for b in brands:
            val = row[b]
            if pd.isna(val):
                oil_table_html += '<td class="empty">-</td>'
            else:
                oil_table_html += f'<td class="price">{val:.2f}</td>'
        oil_table_html += "</tr>"

    oil_table_html += "</tbody></table>"
    oil_table_html += f"""
    <div style="margin-top: 20px; color: #9ca3af; font-size: 0.8rem; text-align: center;">
        มีผลตั้งแต่ (Effective Date): {selected_date.strftime('%d %b %Y')}
    </div>
    """

    st.components.v1.html(oil_table_html, height=600, scrolling=False)




# ---------------- Interactive Map Section ----------------
st.markdown("""
<div class="modern-card">
    <div style="text-align: center; margin-bottom: 30px;">
        <h2 class="gradient-text" style="font-size: 2.5rem; margin-bottom: 15px;">
            🗺️ สถานีบริการน้ำมันทั่วประเทศไทย
        </h2>
        <p style="font-size: 1.1rem; color: #64748b;">
            Petroleum stations across Thailand
        </p>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------- DuckDB Connection ----------------
con = duckdb.connect('dads5001.duckdb')  # หรือ ':memory:' ถ้า in-memory

# Load station data from DuckDB
# สมมติ table ชื่อ PIN มี columns: company, latitude, longitude, price
sql = """
SELECT company, latitude, longitude
FROM PIN
"""
df_stations = con.execute(sql).fetchdf()

# ---------------- Folium Map ----------------
m = folium.Map(
    location=[13.7367, 100.5231],
    zoom_start=12,
    tiles='CartoDB positron',
    width='100%',
    height='1000px'
)

# Drop rows with missing coordinates
df_stations_clean = df_stations.dropna(subset=['latitude', 'longitude'])

# Add markers
for _, station in df_stations_clean.iterrows():
    # สร้าง URL ของ Google Maps ก่อน
    google_maps_url = f"https://www.google.com/maps/search/?api=1&query={station['latitude']},{station['longitude']}"
    
    folium.Marker(
        location=[station['latitude'], station['longitude']],
        popup=f"""
        <div style='min-width: 200px;'>
            <h4 style='color: #1f2937; margin-bottom: 10px;'>{station['company']}</h4>
            <p style='color: #6b7280; margin: 5px 0;'><strong>Type:</strong> Oil</p>
            <p style='color: #6b7280; margin: 5px 0;'><strong>Latitude:</strong> {station['latitude']}</p>
            <p style='color: #6b7280; margin: 5px 0;'><strong>Longitude:</strong> {station['longitude']}</p>
            <a href="{google_maps_url}" target="_blank">
                <button style="padding:5px 10px; background-color:#2563eb; color:white; border:none; border-radius:4px; cursor:pointer;">
                    Link to Google Map
                </button>
            </a>
        </div>
        """,
        tooltip=station['company'],
        icon=folium.Icon(
            color='blue' if station['company'] == 'PTT' 
                  else 'green' if station['company'] == 'BCP'
                  else 'red' if station['company'] == 'Susco' 
                  else 'yellow' if station['company'] == 'Shell'
                  else 'darkgreen' if station['company'] == 'PTG'  
                  else 'gray',
            icon='gas-pump',
            prefix='fa'
        )
    ).add_to(m)


# ---------------- Display Map ----------------
st_folium(m, width=None, height=1000, use_container_width=True)


# ---------------- Real-time Market Overview ----------------
st.markdown("""
<div class="modern-card">
    <div style="text-align: center; margin-bottom: 30px;">
        <h2 class="gradient-text" style="font-size: 2.8rem; margin-bottom: 15px;">
            📊 Market Overview
        </h2>
        <p style="font-size: 1.2rem; color: #64748b;">
            Live market data and energy insights
        </p>
    </div>
</div>
""", unsafe_allow_html=True)

# Market Metrics in 3 Columns
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <a href='/oilprice_board' target="_top" style="text-decoration: none;">
        <div class="modern-card">
            <div style="text-align: center;">
                <div style="font-size: 2.5rem; color: #3b82f6; margin-bottom: 10px;">⛽</div>
                <h3 style="color: #1e293b; margin-bottom: 10px;">Fuel Prices</h3>
                <p style="color: #64748b; font-size: 0.9rem;">Real-time updates</p>
            </div>
        </div>
    </a>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <a href='https://ทองคําราคา.com/#google_vignette' style="text-decoration: none;">
        <div class="modern-card">
            <div style="text-align: center;">
                <div style="font-size: 2.5rem; color: #f59e0b; margin-bottom: 10px;">🥇</div>
                <h3 style="color: #1e293b; margin-bottom: 10px;">Gold Market</h3>
                <p style="color: #64748b; font-size: 0.9rem;">Live trading data</p>
            </div>
        </div>
    </a>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <a href='/settrade_sandbox' style="text-decoration: none;">
        <div class="modern-card">
            <div style="text-align: center;">
                <div style="font-size: 2.5rem; color: #10b981; margin-bottom: 10px;">📈</div>
                <h3 style="color: #1e293b; margin-bottom: 10px;">Stock Market</h3>
                <p style="color: #64748b; font-size: 0.9rem;">SET Index & more</p>
            </div>
        </div>
    </a>
    """, unsafe_allow_html=True)

# ---------------- News Section ----------------
st.markdown("""
<div class="modern-card">
    <div style="text-align: center; margin-bottom: 30px;">
        <h2 class="gradient-text" style="font-size: 2.5rem; margin-bottom: 15px;">
            📰 Market News
        </h2>
        <p style="font-size: 1.1rem; color: #64748b;">
            Latest updates from the energy sector
        </p>
    </div>
</div>
""", unsafe_allow_html=True)

# News cards
news_col1, news_col2 = st.columns(2)

news_items = [
    {
        "title": "Oil Prices Surge Amid Supply Concerns",
        "category": "Energy",
        "time": "2 hours ago",
        "color": "#3b82f6",
        "icon": "⛽"
    },
    {
        "title": "Gold Hits Record High on Economic Uncertainty",
        "category": "Commodities", 
        "time": "4 hours ago",
        "color": "#f59e0b",
        "icon": "🥇"
    },
    {
        "title": "Renewable Energy Investments Reach New Peak",
        "category": "Sustainability",
        "time": "6 hours ago", 
        "color": "#10b981",
        "icon": "🌱"
    },
    {
        "title": "Stock Market Shows Strong Recovery Signs",
        "category": "Markets",
        "time": "8 hours ago",
        "color": "#8b5cf6",
        "icon": "📈"
    }
]

for i, news in enumerate(news_items):
    col = news_col1 if i % 2 == 0 else news_col2
    with col:
        st.markdown(f"""
        <div class="modern-card">
            <div style="display: flex; align-items: start; gap: 15px;">
                <div style="font-size: 2rem;">{news['icon']}</div>
                <div style="flex: 1;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <span style="background: {news['color']}20; color: {news['color']}; padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: 600; border: 1px solid {news['color']}40;">
                            {news['category']}
                        </span>
                        <span style="color: #64748b; font-size: 0.8rem;">{news['time']}</span>
                    </div>
                    <h4 style="color: #1e293b; margin: 0; line-height: 1.4;">{news['title']}</h4>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ---------------- Bottom Sign Up Section ----------------
st.markdown("""
<div class="modern-card">
    <div style="text-align: center; padding: 40px 20px; background: linear-gradient(135deg, rgba(59, 130, 246, 0.05) 0%, rgba(29, 78, 216, 0.05) 100%); border-radius: 20px;">
        <h2 class="gradient-text" style="font-size: 2.5rem; margin-bottom: 20px;">
            Ready to Transform Your Energy Insights?
        </h2>
        <p style="font-size: 1.2rem; color: #64748b; margin-bottom: 30px; max-width: 700px; margin-left: auto; margin-right: auto;">
            Join OILSOPHAENG today and get access to real-time market data, advanced analytics, and comprehensive energy intelligence tools.
        </p>
""", unsafe_allow_html=True)

# Bottom Sign Up Button - ใช้ลิงก์โดยตรง
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("""
    <div style="text-align: center; margin: 20px 0;">
        <a href="app_main" class="direct-link-btn" style="display: inline-block; width: 100%; font-size: 1.1rem;">
            🌟 Get Started - Sign Up Now
        </a>
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-top: 30px;">
            <div style="text-align: center;">
                <div style="font-size: 2rem; color: #3b82f6; margin-bottom: 10px;">🚀</div>
                <div style="color: #1e293b; font-weight: 600;">Instant Access</div>
                <div style="color: #64748b; font-size: 0.9rem;">Get started immediately</div>
            </div>
            <div style="text-align: center;">
                <div style="font-size: 2rem; color: #10b981; margin-bottom: 10px;">💡</div>
                <div style="color: #1e293b; font-weight: 600;">Smart Analytics</div>
                <div style="color: #64748b; font-size: 0.9rem;">AI-powered insights</div>
            </div>
            <div style="text-align: center;">
                <div style="font-size: 2rem; color: #f59e0b; margin-bottom: 10px;">📈</div>
                <div style="color: #1e293b; font-weight: 600;">Live Updates</div>
                <div style="color: #64748b; font-size: 0.9rem;">Real-time data feeds</div>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------- Footer ----------------
st.markdown("""
<div class="modern-card">
    <div style="text-align: center; padding: 40px 20px;">
        <h3 class="gradient-text" style="margin-bottom: 20px;">
            OILSOPHAENG
        </h3>
        <p style="color: #64748b; margin-bottom: 20px;">
            Advanced energy intelligence for modern businesses
        </p>
        <div style="display: flex; justify-content: center; gap: 20px; margin-bottom: 20px;">
            <a href="#" style="color: #64748b; text-decoration: none; transition: color 0.3s;">About</a>
            <a href="#" style="color: #64748b; text-decoration: none; transition: color 0.3s;">Features</a>
            <a href="#" style="color: #64748b; text-decoration: none; transition: color 0.3s;">Pricing</a>
            <a href="#" style="color: #64748b; text-decoration: none; transition: color 0.3s;">Contact</a>
        </div>
        <p style="color: #94a3b8; font-size: 0.9rem;">
            © 2025 OILSOPHAENG. All rights reserved.<br>
            Last updated: {}
        </p>
    </div>
</div>
""".format(datetime.now().strftime("%d/%m/%Y %H:%M")), unsafe_allow_html=True)

# ---------------- Handle Sign Up Redirection ----------------
if st.session_state.signup_clicked:
    redirect_to_app_main()



#----------------------------------------------------------

import streamlit as st
import random
import time

# ตั้งค่าหน้า
st.set_page_config(
    page_title="OILSOPHANG",
    page_icon="⛽",
    layout="wide"
)

# ตั้งค่า session state
if "chat_open" not in st.session_state:
    st.session_state.chat_open = False
if "messages" not in st.session_state:
    st.session_state.messages = []

# ฟังก์ชันเปิดแชท
def open_chat():
    st.session_state.chat_open = True
    st.rerun()

# ฟังก์ชันปิดแชท
def close_chat():
    st.session_state.chat_open = False
    st.rerun()

# ฟังก์ชันส่งข้อความ
def send_message():
    if st.session_state.get("chat_input", "").strip():
        # เพิ่มข้อความผู้ใช้
        st.session_state.messages.append({
            "role": "user",
            "content": st.session_state.chat_input,
            "time": time.strftime("%H:%M")
        })
        
        # คำตอบ AI
        responses = [
            "สวัสดีครับ! ผม OilSophia AI สามารถช่วยอะไรคุณได้บ้างเกี่ยวกับน้ำมันและพลังงาน?",
            "ราคาน้ำมันวันนี้: เบนซิน 95 = 45.50 บาท, ดีเซล = 32.25 บาท",
            "ต้องการข้อมูลเกี่ยวกับราคาน้ำมันประเภทไหนเป็นพิเศษไหมครับ?",
            "ผมสามารถช่วยวิเคราะห์แนวโน้มราคาได้",
            "OilSophia AI พร้อมให้บริการครับ!"
        ]
        
        ai_response = random.choice(responses)
        st.session_state.messages.append({
            "role": "assistant",
            "content": ai_response,
            "time": time.strftime("%H:%M")
        })
        
        # เคลียร์ input
        st.session_state.chat_input = ""
        st.rerun()

# ============================================
# ส่วนที่ 1: CSS สำหรับปุ่มและแชท
# ============================================
st.markdown("""
<style>
    /* ปุ่มลอยที่มองเห็นได้แน่นอน */
    #chat-float-button {
        position: fixed !important;
        bottom: 30px !important;
        right: 30px !important;
        width: 70px !important;
        height: 70px !important;
        background: linear-gradient(135deg, #101f59 0%, #6453e6 100%) !important;
        border-radius: 50% !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        color: white !important;
        font-size: 30px !important;
        cursor: pointer !important;
        box-shadow: 0 5px 20px rgba(0, 0, 113, 0.5) !important;
        border: 3px solid white !important;
        z-index: 9999 !important;
        animation: pulse 2s infinite !important;
    }
    
    #chat-float-button:hover {
        transform: scale(1.1) !important;
        box-shadow: 0 8px 25px rgba(239, 68, 68, 0.7) !important;
    }
    
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7); }
        70% { box-shadow: 0 0 0 15px rgba(239, 68, 68, 0); }
        100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }
    }
    
    /* กล่องแชท */
    .chat-box {
        position: fixed !important;
        bottom: 120px !important;
        right: 30px !important;
        width: 400px !important;
        height: 500px !important;
        background: white !important;
        border-radius: 15px !important;
        box-shadow: 0 15px 50px rgba(0,0,0,0.2) !important;
        z-index: 10000 !important;
        border: 2px solid #e2e8f0 !important;
        display: flex;
        flex-direction: column;
    }
    
    /* ปรับปรุง Streamlit elements */
    .stButton > button {
        border: 2px solid #ef4444;
    }
    
    .stTextInput > div > div > input {
        border: 1px solid #dc2626;
    }
    
    /* ทำให้เนื้อหาหลักอยู่ห่างจากขอบ */
    .main .block-container {
        padding-bottom: 100px;
    }
</style>
""", unsafe_allow_html=True)




# ============================================
# ส่วนที่ 4: ใช้ JavaScript สร้างปุ่มลอย
# ============================================
st.markdown("""
<div id="chat-float-button" onclick="document.getElementById('hidden-chat-trigger').click()">💬</div>

<script>
// ตรวจสอบว่ามีปุ่มลอยหรือไม่ ถ้าไม่มีให้สร้าง
function ensureFloatButton() {
    let floatBtn = document.getElementById('chat-float-button');
    
    if (!floatBtn) {
        floatBtn = document.createElement('div');
        floatBtn.id = 'chat-float-button';
        floatBtn.innerHTML = '💬';
        floatBtn.onclick = function() {
            // ส่ง event ไปเปิดแชท
            window.parent.postMessage({
                type: 'OPEN_CHAT',
                value: 'open'
            }, '*');
        };
        document.body.appendChild(floatBtn);
    }
}

// รันเมื่อหน้าโหลดเสร็จ
document.addEventListener('DOMContentLoaded', ensureFloatButton);

// รันใหม่ทุก 2 วินาทีเพื่อความแน่นอน
setInterval(ensureFloatButton, 2000);
</script>
""", unsafe_allow_html=True)


# ============================================
# ส่วนที่ 6: แสดงกล่องแชท
# ============================================
if st.session_state.chat_open:
    # สร้างกล่องแชท
    st.markdown("""
    <div class="chat-box">
        <!-- Header -->
        <div style="
            background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
            color: white;
            padding: 20px;
            border-radius: 15px 15px 0 0;
        ">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h3 style="margin: 0; font-size: 18px;">⛽ OilSopha AI</h3>
                    <p style="margin: 5px 0 0 0; font-size: 12px; opacity: 0.9;">พร้อมให้บริการ 24/7</p>
                </div>
                <div style="
                    cursor: pointer;
                    font-size: 24px;
                    width: 36px;
                    height: 36px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    border-radius: 50%;
                    background: rgba(255,255,255,0.2);
                " onclick="window.location.reload()">×</div>
            </div>
        </div>
        
        <!-- Messages Area -->
        <div style="
            flex: 1;
            padding: 20px;
            overflow-y: auto;
            background: #f8fafc;
            display: flex;
            flex-direction: column;
            gap: 10px;
        ">
    """, unsafe_allow_html=True)
    
    # แสดงข้อความ
    if not st.session_state.messages:
        st.markdown("""
        <div style="
            background: white;
            padding: 15px;
            border-radius: 15px;
            border: 1px solid #e2e8f0;
            max-width: 85%;
            align-self: flex-start;
        ">
            <div style="font-weight: bold; color: #ef4444; margin-bottom: 5px;">OilSopha AI:</div>
            <div>สวัสดีครับ! ผม OilSophia AI สามารถช่วยอะไรคุณได้บ้างเกี่ยวกับน้ำมันและพลังงาน? 😊</div>
            <div style="font-size: 11px; color: #94a3b8; margin-top: 5px;">แชทถูกเปิดเมื่อสักครู่</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
                    color: white;
                    padding: 12px 16px;
                    border-radius: 18px;
                    margin-left: auto;
                    max-width: 85%;
                    border-bottom-right-radius: 5px;
                ">
                    <div style="font-weight: bold; margin-bottom: 3px;">คุณ:</div>
                    <div>{msg["content"]}</div>
                    <div style="font-size: 11px; opacity: 0.8; margin-top: 5px;">{msg["time"]}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="
                    background: white;
                    padding: 12px 16px;
                    border-radius: 18px;
                    border: 1px solid #e2e8f0;
                    max-width: 85%;
                    align-self: flex-start;
                    border-bottom-left-radius: 5px;
                ">
                    <div style="font-weight: bold; color: #ef4444; margin-bottom: 3px;">OilSopha AI:</div>
                    <div>{msg["content"]}</div>
                    <div style="font-size: 11px; color: #94a3b8; margin-top: 5px;">{msg["time"]}</div>
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown("""
        </div>
        
        <!-- Input Area -->
        <div style="
            padding: 20px;
            border-top: 1px solid #e2e8f0;
            background: white;
        ">
    """, unsafe_allow_html=True)
    
    # Input field และปุ่มส่ง
    input_col, btn_col = st.columns([3, 1])
    with input_col:
        st.text_input(
            "พิมพ์ข้อความ...",
            key="chat_input",
            label_visibility="collapsed",
            placeholder="พิมพ์ข้อความที่นี่..."
        )
    with btn_col:
        if st.button("ส่ง", key="send_button_chat", use_container_width=True, type="primary"):
            send_message()
    
    st.markdown("""
        </div>
    </div>
    
    <script>
    // Auto scroll ลงล่าง
    setTimeout(function() {
        const chatArea = document.querySelector('[style*="flex: 1; padding: 20px; overflow-y: auto"]');
        if (chatArea) {
            chatArea.scrollTop = chatArea.scrollHeight;
        }
    }, 100);
    </script>
    """, unsafe_allow_html=True)
    
    # ปุ่มปิดแชทแบบ Streamlit
    st.markdown('<div style="height: 20px;"></div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("ปิดแชท", key="close_chat_button", type="secondary", use_container_width=True):
            close_chat()


# ============================================
# ส่วนที่ 11: JavaScript สำหรับจัดการเพิ่มเติม
# ============================================
st.markdown("""
<script>
// ตรวจสอบและสร้างปุ่มลอยทุกครั้ง
setInterval(function() {
    let floatBtn = document.getElementById('chat-float-button');
    if (!floatBtn) {
        console.log('Creating float button...');
        floatBtn = document.createElement('div');
        floatBtn.id = 'chat-float-button';
        floatBtn.innerHTML = '💬';
        floatBtn.style.cssText = `
            position: fixed !important;
            bottom: 30px !important;
            right: 30px !important;
            width: 70px !important;
            height: 70px !important;
            background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%) !important;
            border-radius: 50% !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            color: white !important;
            font-size: 30px !important;
            cursor: pointer !important;
            box-shadow: 0 5px 20px rgba(239, 68, 68, 0.5) !important;
            border: 3px solid white !important;
            z-index: 9999 !important;
            animation: pulse 2s infinite !important;
        `;
        
        floatBtn.onclick = function() {
            // คลิกปุ่ม Streamlit ที่ซ่อนอยู่
            const hiddenBtn = document.querySelector('button[id*="hidden_chat_trigger"]');
            if (hiddenBtn) hiddenBtn.click();
        };
        
        document.body.appendChild(floatBtn);
    }
}, 1000);

// ใส่ style สำหรับ pulse animation
const style = document.createElement('style');
style.textContent = `
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7); }
        70% { box-shadow: 0 0 0 15px rgba(239, 68, 68, 0); }
        100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }
    }
`;
document.head.appendChild(style);
</script>
""", unsafe_allow_html=True)