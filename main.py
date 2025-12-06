import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
import seaborn as sns
import pydeck as pdk
from matplotlib import rcParams
import os
from datetime import datetime
from scipy import stats
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# ============================================================================
# 1. Configuration and Setup
# ============================================================================
st.set_page_config(
    page_title="OilSophang - ระบบวิเคราะห์ราคาน้ำมัน",
    page_icon="🛢️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom CSS
st.markdown("""
<style>
    /* Main styling */
    .main {
        padding: 1rem;
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(90deg, #FF6B6B 0%, #1B3C53 100%);
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* Card styling */
    .card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }
    
    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, #1B3C53 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin: 0.5rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    /* Insight cards */
    .insight-card {
        background: linear-gradient(135deg, #FFD166 0%, #06D6A0 100%);
        color: #333;
        padding: 1.2rem;
        border-radius: 10px;
        margin: 0.8rem 0;
        box-shadow: 0 3px 5px rgba(0, 0, 0, 0.1);
        border-left: 5px solid #EF476F;
    }
    
    /* Warning cards */
    .warning-card {
        background: linear-gradient(135deg, #FF9E6D 0%, #FF6B6B 100%);
        color: white;
        padding: 1.2rem;
        border-radius: 10px;
        margin: 0.8rem 0;
        box-shadow: 0 3px 5px rgba(0, 0, 0, 0.1);
        border-left: 5px solid #EF476F;
    }
    
    /* Success cards */
    .success-card {
        background: linear-gradient(135deg, #06D6A0 0%, #118AB2 100%);
        color: white;
        padding: 1.2rem;
        border-radius: 10px;
        margin: 0.8rem 0;
        box-shadow: 0 3px 5px rgba(0, 0, 0, 0.1);
        border-left: 5px solid #073B4C;
    }
    
    /* Custom button */
    .stButton>button {
        background: linear-gradient(90deg, #FF6B6B 0%, #4ECDC4 100%);
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    
    /* Dataframe styling */
    .dataframe {
        border-radius: 10px !important;
        overflow: hidden !important;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1) !important;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
        padding: 0 1rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #427A76;
        border-radius: 5px 5px 0px 0px;
        padding: 10px 20px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #e0e2e6;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .main-header h1 {
            font-size: 24px !important;
        }
        .metric-card h3 {
            font-size: 14px !important;
        }
    }
    
    /* Custom metric value */
    .metric-value {
        font-size: 24px;
        font-weight: bold;
        margin: 10px 0;
    }
    
    /* Custom metric label */
    .metric-label {
        font-size: 14px;
        opacity: 0.9;
    }
</style>
""", unsafe_allow_html=True)

# Set font
rcParams['font.family'] = 'Tahoma'

# ============================================================================
# 2. Caching Functions for Performance
# ============================================================================
@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_oil_data():
    """Load and preprocess oil price data"""
    try:
        df = pd.read_csv("Price_Oil.csv")
        df['Date'] = pd.to_datetime(df['Date'])
        
        # Clean numeric columns - แปลงคอลัมน์ราคาให้เป็น numeric
        price_columns = ['PTT', 'BANGCHAK', 'SHELL', 'ESSO', 'CHEVRON', 
                        'IRPC', 'PTG', 'SUSCO', 'PURE', 'SUSCO DEALER']
        
        for col in price_columns:
            if col in df.columns:
                # แปลง string เป็น numeric, แทนที่ค่าไม่ถูกต้องด้วย NaN
                df[col] = pd.to_numeric(df[col], errors='coerce')
                # แปลง 0 เป็น NaN เพื่อไม่ให้รบกวนการคำนวณ
                df[col] = df[col].replace(0, np.nan)
                
        return df
    except Exception as e:
        st.error(f"Error loading oil data: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=3600)
def load_tariff_data():
    """Load and preprocess tariff data"""
    try:
        if os.path.exists("tariff.csv"):
            tariff = pd.read_csv("tariff.csv")
            tariff.columns = tariff.columns.str.strip().str.lower()
            tariff = tariff.rename(columns={"longtitude": "longitude"})
            
            # Clean coordinates
            tariff['latitude'] = pd.to_numeric(tariff['latitude'], errors='coerce')
            tariff['longitude'] = pd.to_numeric(tariff['longitude'], errors='coerce')
            tariff = tariff.dropna(subset=['latitude', 'longitude'])
            
            return tariff
    except Exception as e:
        st.error(f"Error loading tariff data: {e}")
    return None

# ============================================================================
# 3. Helper Functions for Data Processing
# ============================================================================
def safe_numeric_conversion(value):
    """Safely convert value to numeric, handling errors"""
    try:
        if pd.isna(value):
            return np.nan
        if isinstance(value, str) and value.strip() == '':
            return np.nan
        return float(value)
    except (ValueError, TypeError):
        return np.nan

def get_price_change(current_df, previous_df, company):
    """Get price change safely handling NaN and string values"""
    try:
        if company in current_df.columns and not current_df.empty:
            current_raw = current_df[company].iloc[0] if len(current_df[company]) > 0 else np.nan
            current = safe_numeric_conversion(current_raw)
        else:
            current = np.nan
        
        if company in previous_df.columns and not previous_df.empty:
            previous_raw = previous_df[company].iloc[0] if len(previous_df[company]) > 0 else np.nan
            previous = safe_numeric_conversion(previous_raw)
        else:
            previous = np.nan
        
        if pd.notna(current) and pd.notna(previous):
            change = current - previous
            percent_change = (change / previous) * 100 if previous != 0 else np.nan
            return {
                'current': current,
                'previous': previous,
                'change': change,
                'percent': percent_change,
                'is_valid': True
            }
        else:
            return {
                'current': current,
                'previous': previous,
                'change': np.nan,
                'percent': np.nan,
                'is_valid': False
            }
    except Exception as e:
        return {
            'current': np.nan,
            'previous': np.nan,
            'change': np.nan,
            'percent': np.nan,
            'is_valid': False
        }

def highlight_selected_date(row, selected_date):
    """Highlight selected date in dataframe"""
    if row.name == selected_date:
        return ['background-color: #4ECDC4; color: white; font-weight: bold;'] * len(row)
    return [''] * len(row)

def get_company_colors():
    """Define colors and styles for each company"""
    return {
        "PTT":      {"color": "#1f77b4", "marker": "o", "linestyle": "-", "emoji": "⛽"},
        "BANGCHAK": {"color": "#2ca02c", "marker": "s", "linestyle": "--", "emoji": "🌱"},
        "SHELL":    {"color": "#ff7f0e", "marker": "^", "linestyle": ":", "emoji": "🐚"},
        "ESSO":     {"color": "#9467bd", "marker": "D", "linestyle": "-.", "emoji": "💧"},
        "CHEVRON":  {"color": "#8c564b", "marker": "x", "linestyle": "-", "emoji": "🔷"},
        "IRPC":     {"color": "#e377c2", "marker": "*", "linestyle": "--", "emoji": "🏭"},
        "PTG":      {"color": "#7f7f7f", "marker": "P", "linestyle": ":", "emoji": "🚗"},
        "SUSCO":    {"color": "#bcbd22", "marker": "h", "linestyle": "-.", "emoji": "⚡"},
        "PURE":     {"color": "#17becf", "marker": "+", "linestyle": "-", "emoji": "✨"},
        "SUSCO DEALER": {"color": "#d62728", "marker": "v", "linestyle": "--", "emoji": "🏪"}
    }

# ============================================================================
# 4. Advanced Analysis Functions
# ============================================================================
def analyze_price_trends(df, fuel_type, selected_companies, days=30):
    """วิเคราะห์แนวโน้มราคาและให้ insight"""
    insights = []
    
    # ข้อมูล 30 วันล่าสุด
    end_date = df['Date'].max()
    start_date = end_date - pd.Timedelta(days=days)
    recent_data = df[(df['Date'] >= start_date) & 
                     (df['Date'] <= end_date) &
                     (df['FULE_TYPE'] == fuel_type)].copy()
    
    if recent_data.empty or len(selected_companies) == 0:
        return insights
    
    # วิเคราะห์สำหรับแต่ละบริษัท
    for company in selected_companies:
        if company in recent_data.columns:
            prices = recent_data[company].dropna()
            if len(prices) > 1:
                # คำนวณแนวโน้ม
                x = np.arange(len(prices))
                slope, intercept, r_value, p_value, std_err = stats.linregress(x, prices)
                
                # สร้าง insight
                trend = "เพิ่มขึ้น" if slope > 0 else "ลดลง" if slope < 0 else "คงที่"
                magnitude = abs(slope * 30)  # การเปลี่ยนแปลงใน 30 วัน
                
                if slope > 0.01:  # เพิ่มขึ้นอย่างมีนัยสำคัญ
                    insights.append({
                        'type': 'warning',
                        'title': f'⚠️ ราคา{company} แนวโน้มเพิ่มขึ้น',
                        'content': f'ราคา{company} มีแนวโน้มเพิ่มขึ้น {trend} ประมาณ {magnitude:.2f} บาท/ลิตร ใน 30 วันที่ผ่านมา',
                        'company': company,
                        'slope': slope,
                        'r_squared': r_value**2
                    })
                elif slope < -0.01:  # ลดลงอย่างมีนัยสำคัญ
                    insights.append({
                        'type': 'success',
                        'title': f'✅ ราคา{company} แนวโน้มลดลง',
                        'content': f'ราคา{company} มีแนวโน้มลดลง {trend} ประมาณ {abs(magnitude):.2f} บาท/ลิตร ใน 30 วันที่ผ่านมา',
                        'company': company,
                        'slope': slope,
                        'r_squared': r_value**2
                    })
    
    return insights

def analyze_price_volatility(df, fuel_type, selected_companies, days=30):
    """วิเคราะห์ความผันผวนของราคา"""
    insights = []
    
    end_date = df['Date'].max()
    start_date = end_date - pd.Timedelta(days=days)
    recent_data = df[(df['Date'] >= start_date) & 
                     (df['Date'] <= end_date) &
                     (df['FULE_TYPE'] == fuel_type)].copy()
    
    if recent_data.empty:
        return insights
    
    volatility_scores = {}
    for company in selected_companies:
        if company in recent_data.columns:
            prices = recent_data[company].dropna()
            if len(prices) > 5:
                returns = prices.pct_change().dropna()
                volatility = returns.std() * np.sqrt(252)  # ประมาณการต่อปี
                volatility_scores[company] = volatility
    
    if volatility_scores:
        # หาบริษัทที่มีความผันผวนสูงสุด
        max_vol_company = max(volatility_scores, key=volatility_scores.get)
        max_vol = volatility_scores[max_vol_company]
        
        # หาบริษัทที่มีความผันผวนต่ำสุด
        min_vol_company = min(volatility_scores, key=volatility_scores.get)
        min_vol = volatility_scores[min_vol_company]
        
        if max_vol > 0.3:  # ความผันผวนสูง
            insights.append({
                'type': 'warning',
                'title': '⚠️ ความผันผวนราคาสูง',
                'content': f'{max_vol_company} มีความผันผวนสูงสุด ({max_vol:.2%}) ใน 30 วันที่ผ่านมา',
                'company': max_vol_company,
                'volatility': max_vol
            })
        
        if min_vol < 0.1:  # ความผันผวนต่ำ
            insights.append({
                'type': 'success',
                'title': '✅ ราคามีเสถียรภาพ',
                'content': f'{min_vol_company} มีความผันผวนต่ำสุด ({min_vol:.2%}) ราคาค่อนข้างมีเสถียรภาพ',
                'company': min_vol_company,
                'volatility': min_vol
            })
    
    return insights

def analyze_price_spread(df, fuel_type, selected_companies, days=7):
    """วิเคราะห์ช่วงราคาระหว่างบริษัทต่างๆ"""
    insights = []
    
    end_date = df['Date'].max()
    start_date = end_date - pd.Timedelta(days=days)
    recent_data = df[(df['Date'] >= start_date) & 
                     (df['Date'] <= end_date) &
                     (df['FULE_TYPE'] == fuel_type)].copy()
    
    if recent_data.empty or len(selected_companies) < 2:
        return insights
    
    # คำนวณช่วงราคาเฉลี่ย
    daily_spreads = []
    for date in recent_data['Date'].unique():
        daily_data = recent_data[recent_data['Date'] == date]
        valid_prices = []
        for company in selected_companies:
            if company in daily_data.columns:
                price = daily_data[company].iloc[0]
                if pd.notna(price):
                    valid_prices.append(price)
        
        if len(valid_prices) >= 2:
            daily_spread = max(valid_prices) - min(valid_prices)
            daily_spreads.append(daily_spread)
    
    if daily_spreads:
        avg_spread = np.mean(daily_spreads)
        max_spread = max(daily_spreads)
        
        if avg_spread > 1.0:
            insights.append({
                'type': 'insight',
                'title': '💡 ช่วงราคาค่อนข้างกว้าง',
                'content': f'ช่วงราคาระหว่างบริษัทต่าง ๆ เฉลี่ย {avg_spread:.2f} บาท/ลิตร สูงสุด {max_spread:.2f} บาท/ลิตร',
                'avg_spread': avg_spread,
                'max_spread': max_spread
            })
        elif avg_spread < 0.3:
            insights.append({
                'type': 'success',
                'title': '✅ ราคาใกล้เคียงกัน',
                'content': f'ราคาน้ำมันระหว่างบริษัทต่าง ๆ ใกล้เคียงกันมาก เฉลี่ยเพียง {avg_spread:.2f} บาท/ลิตร',
                'avg_spread': avg_spread,
                'max_spread': max_spread
            })
    
    return insights

def find_best_deals(df, date, fuel_type, selected_companies):
    """หาปั๊มที่ราคาถูกที่สุดและแพงที่สุด"""
    insights = []
    
    daily_data = df[(df['Date'] == pd.to_datetime(date)) & 
                    (df['FULE_TYPE'] == fuel_type)]
    
    if daily_data.empty:
        return insights
    
    valid_prices = {}
    for company in selected_companies:
        if company in daily_data.columns:
            price = daily_data[company].iloc[0]
            if pd.notna(price) and price > 0:
                valid_prices[company] = price
    
    if len(valid_prices) >= 2:
        cheapest = min(valid_prices, key=valid_prices.get)
        expensive = max(valid_prices, key=valid_prices.get)
        price_diff = valid_prices[expensive] - valid_prices[cheapest]
        
        company_mapping = {
            "PTT": "⛽ PTT",
            "BANGCHAK": "🌱 Bangchak",
            "SHELL": "🐚 Shell",
            "ESSO": "💧 Esso",
            "CHEVRON": "🔷 Chevron",
            "IRPC": "🏭 IRPC",
            "PTG": "🚗 PTG",
            "SUSCO": "⚡ Susco",
            "PURE": "✨ Pure",
            "SUSCO DEALER": "🏪 Susco Dealer"
        }
        
        if price_diff > 0.5:
            insights.append({
                'type': 'insight',
                'title': '💰 โอกาสประหยัดเงิน',
                'content': f'คุณสามารถประหยัดได้ถึง {price_diff:.2f} บาท/ลิตร โดยเลือกเติมที่ {company_mapping.get(cheapest, cheapest)} ({valid_prices[cheapest]:.2f} บาท) แทน {company_mapping.get(expensive, expensive)} ({valid_prices[expensive]:.2f} บาท)',
                'cheapest': cheapest,
                'expensive': expensive,
                'price_diff': price_diff
            })
    
    return insights

def analyze_missing_data(df, fuel_type, selected_companies):
    """วิเคราะห์ข้อมูลที่หายไป"""
    insights = []
    
    # ตรวจสอบข้อมูลล่าสุด
    latest_date = df['Date'].max()
    latest_data = df[(df['Date'] == latest_date) & 
                     (df['FULE_TYPE'] == fuel_type)]
    
    if not latest_data.empty:
        missing_companies = []
        for company in selected_companies:
            if company in latest_data.columns:
                price = latest_data[company].iloc[0]
                if pd.isna(price):
                    missing_companies.append(company)
        
        if missing_companies:
            insights.append({
                'type': 'warning',
                'title': '⚠️ ข้อมูลบางส่วนขาดหาย',
                'content': f'ไม่พบข้อมูลล่าสุดสำหรับ: {", ".join(missing_companies)}',
                'missing_companies': missing_companies
            })
    
    return insights

def generate_price_forecast(df, fuel_type, company, days=7):
    """พยากรณ์ราคาล่วงหน้า"""
    try:
        # ข้อมูล 30 วันที่ผ่านมา
        end_date = df['Date'].max()
        start_date = end_date - pd.Timedelta(days=30)
        historical_data = df[(df['Date'] >= start_date) & 
                            (df['Date'] <= end_date) &
                            (df['FULE_TYPE'] == fuel_type)].copy()
        
        if historical_data.empty or company not in historical_data.columns:
            return None
        
        prices = historical_data[company].dropna()
        if len(prices) < 10:
            return None
        
        # ใช้ simple moving average สำหรับพยากรณ์
        window = min(7, len(prices))
        sma = prices.rolling(window=window).mean()
        last_sma = sma.iloc[-1]
        trend = (prices.iloc[-1] - prices.iloc[-window]) / window
        
        # พยากรณ์ 7 วันข้างหน้า
        forecast = []
        for i in range(1, days + 1):
            forecast_price = last_sma + (trend * i)
            forecast.append({
                'date': end_date + pd.Timedelta(days=i),
                'price': max(forecast_price, 0)  # ราคาต้องไม่ติดลบ
            })
        
        return {
            'company': company,
            'current_price': prices.iloc[-1],
            'trend': trend,
            'forecast': forecast,
            'confidence': min(0.8, len(prices) / 100)  # ความมั่นใจ
        }
    except:
        return None

# ============================================================================
# 5. Main Application
# ============================================================================

# Load data
df = load_oil_data()
if df.empty:
    st.error("ไม่สามารถโหลดข้อมูลราคาน้ำมันได้ กรุณาตรวจสอบไฟล์ Price_Oil.csv")
    st.stop()

tariff_df = load_tariff_data()

# Header
st.markdown("""
<div class="main-header">
    <h1>🛢️ OilSophang - ระบบวิเคราะห์และติดตามราคาน้ำมัน</h1>
    <p>"เติมก่อนประหยัดกว่า" - วิเคราะห์เชิงลึกเพื่อการตัดสินใจที่ชาญฉลาด</p>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# 6. Sidebar Configuration
# ============================================================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3174/3174837.png", width=100)
    st.title("⚙️ การตั้งค่า")
    
    # Date selection
    st.subheader("📅 เลือกวันที่")
    selected_date = st.date_input(
        "วันที่",
        value=df['Date'].max().date() if not df.empty else datetime.now().date(),
        min_value=df['Date'].min().date() if not df.empty else datetime.now().date(),
        max_value=df['Date'].max().date() if not df.empty else datetime.now().date(),
        label_visibility="collapsed"
    )
    
    # Fuel type selection
    st.subheader("⛽ ประเภทน้ำมัน")
    fuel_types = df['FULE_TYPE'].unique() if not df.empty else []
    fuel = st.selectbox(
        "เลือกประเภทน้ำมัน",
        options=fuel_types,
        index=0 if len(fuel_types) > 0 else 0,
        label_visibility="collapsed"
    ) if len(fuel_types) > 0 else st.selectbox("เลือกประเภทน้ำมัน", options=["ไม่มีข้อมูล"])
    
    # Company selection
    st.subheader("🏭 เลือกบริษัท")
    company_mapping = {
        "PTT": "⛽ PTT",
        "BANGCHAK": "🌱 Bangchak",
        "SHELL": "🐚 Shell",
        "ESSO": "💧 Esso",
        "CHEVRON": "🔷 Chevron",
        "IRPC": "🏭 IRPC",
        "PTG": "🚗 PTG",
        "SUSCO": "⚡ Susco",
        "PURE": "✨ Pure",
        "SUSCO DEALER": "🏪 Susco Dealer"
    }
    
    # Get available companies from data
    available_companies = []
    if not df.empty:
        for company in company_mapping.keys():
            if company in df.columns:
                # ตรวจสอบว่ามีข้อมูลสำหรับ fuel type นี้หรือไม่
                fuel_data = df[df['FULE_TYPE'] == fuel]
                if not fuel_data.empty and company in fuel_data.columns:
                    has_data = fuel_data[company].notna().any()
                    if has_data:
                        available_companies.append(company)
    
    if available_companies:
        selected_companies = st.multiselect(
            "เลือกบริษัทที่ต้องการวิเคราะห์",
            options=available_companies,
            default=available_companies[:3] if len(available_companies) >= 3 else available_companies,
            format_func=lambda x: company_mapping.get(x, x)
        )
    else:
        selected_companies = []
        st.warning("ไม่พบข้อมูลบริษัทสำหรับประเภทน้ำมันนี้")
    
    # Analysis settings
    st.subheader("📊 การตั้งค่าการวิเคราะห์")
    analysis_period = st.slider(
        "ช่วงเวลาที่ใช้วิเคราะห์ (วัน)",
        min_value=7,
        max_value=90,
        value=30,
        help="จำนวนวันย้อนหลังที่ใช้ในการวิเคราะห์แนวโน้ม"
    )
    
    show_forecast = st.checkbox("แสดงการพยากรณ์ราคา", value=True)
    show_advanced_stats = st.checkbox("แสดงสถิติเชิงลึก", value=True)

# ============================================================================
# 7. Main Content - Tabs
# ============================================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 ภาพรวมราคา", 
    "📈 วิเคราะห์แนวโน้ม", 
    "🔍 วิเคราะห์เชิงลึก", 
    "💡 ข้อมูลเชิงลึก (Insights)",
    "🗺️ ค้นหาปั๊มน้ำมัน"
])

# ============================================================================
# TAB 1: Price Overview
# ============================================================================
with tab1:
    st.header(f"📊 ภาพรวมราคาน้ำมันประเภท {fuel}")
    st.subheader(f"ประจำวันที่ {selected_date.strftime('%d %B %Y')}")
    
    # Filter data for selected date and fuel type
    selected_data = df[df['Date'] == pd.to_datetime(selected_date)]
    
    if selected_data.empty:
        st.warning(f"⚠️ ไม่พบข้อมูลสำหรับวันที่ {selected_date}")
        # Find nearest available date
        available_dates = df['Date'].dt.date.unique()
        if len(available_dates) > 0:
            nearest_date = min(available_dates, key=lambda x: abs((x - selected_date).days))
            st.info(f"แสดงข้อมูลวันที่ใกล้เคียงที่สุด: {nearest_date}")
            selected_data = df[df['Date'] == pd.to_datetime(nearest_date)]
            selected_date = nearest_date
        else:
            st.error("ไม่มีข้อมูลวันที่ใกล้เคียง")
            selected_data = pd.DataFrame()
    
    filtered = selected_data[selected_data['FULE_TYPE'] == fuel] if not selected_data.empty else pd.DataFrame()
    
    if filtered.empty:
        st.error(f"⚠️ ไม่พบข้อมูลน้ำมันประเภท {fuel} สำหรับวันที่เลือก")
    else:
        # แปลงคอลัมน์ราคาให้เป็น numeric
        company_cols = list(company_mapping.keys())
        for col in company_cols:
            if col in filtered.columns:
                filtered[col] = pd.to_numeric(filtered[col], errors='coerce')
        
        # Create display dataframe with emojis
        display_df = filtered[company_cols].rename(columns=company_mapping)
        
        # Calculate metrics
        valid_prices = {}
        for company in selected_companies:
            if company in filtered.columns:
                price = filtered[company].iloc[0]
                if pd.notna(price) and price > 0:
                    valid_prices[company] = price
        
        if valid_prices:
            min_price = min(valid_prices.values())
            max_price = max(valid_prices.values())
            avg_price = np.mean(list(valid_prices.values()))
            price_range = max_price - min_price
            
            min_company = [k for k, v in valid_prices.items() if v == min_price][0]
            max_company = [k for k, v in valid_prices.items() if v == max_price][0]
            
            # Display metrics in columns
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>💰 ราคาต่ำสุด</h3>
                    <div class="metric-value">{min_price:.2f}</div>
                    <div class="metric-label">{company_mapping.get(min_company, min_company)}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>📈 ราคาสูงสุด</h3>
                    <div class="metric-value">{max_price:.2f}</div>
                    <div class="metric-label">{company_mapping.get(max_company, max_company)}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>📊 ราคาเฉลี่ย</h3>
                    <div class="metric-value">{avg_price:.2f}</div>
                    <div class="metric-label">บาท/ลิตร</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>🎯 ช่วงราคา</h3>
                    <div class="metric-value">{price_range:.2f}</div>
                    <div class="metric-label">บาท/ลิตร</div>
                </div>
                """, unsafe_allow_html=True)
        
        # Display price table
        st.subheader("📋 ตารางราคาน้ำมัน")
        
        # Format dataframe with 2 decimal places
        formatted_df = display_df.copy()
        for col in formatted_df.columns:
            formatted_df[col] = formatted_df[col].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "N/A")
        
        # Highlight min and max prices
        def highlight_min_max(val):
            try:
                num_val = float(val)
                if num_val == min_price:
                    return 'background-color: #4ECDC4; color: white; font-weight: bold;'
                elif num_val == max_price:
                    return 'background-color: #FF6B6B; color: white; font-weight: bold;'
            except:
                pass
            return ''
        
        # Apply styling
        styled_df = formatted_df.style.applymap(highlight_min_max)
        
        st.dataframe(styled_df, use_container_width=True)
        
        # Price comparison with previous date
        compare_date = selected_date - pd.Timedelta(days=1)
        compare_data = df[df['Date'] == pd.to_datetime(compare_date)]
        compare_filtered = compare_data[compare_data['FULE_TYPE'] == fuel]
        
        if not compare_filtered.empty and not filtered.empty:
            st.subheader("📊 การเปลี่ยนแปลงราคาจากเมื่อวาน")
            
            price_changes = []
            for company in selected_companies:
                change_data = get_price_change(filtered, compare_filtered, company)
                
                if change_data['is_valid']:
                    price_changes.append({
                        'บริษัท': company_mapping.get(company, company),
                        'ราคาปัจจุบัน': f"{change_data['current']:.2f}",
                        'ราคาเมื่อวาน': f"{change_data['previous']:.2f}",
                        'เปลี่ยนแปลง': f"{change_data['change']:+.2f}",
                        'ร้อยละ': f"{change_data['percent']:+.2f}%" if pd.notna(change_data['percent']) else "N/A"
                    })
            
            if price_changes:
                comp_df = pd.DataFrame(price_changes)
                
                # Apply styling
                def color_change(val):
                    if isinstance(val, str):
                        if '+' in val:
                            return 'color: #FF6B6B; font-weight: bold;'  # แดงสำหรับเพิ่มขึ้น
                        elif '-' in val:
                            return 'color: #4ECDC4; font-weight: bold;'  # เขียวสำหรับลดลง
                    return ''
                
                styled_comp_df = comp_df.style.applymap(
                    color_change, 
                    subset=['เปลี่ยนแปลง', 'ร้อยละ']
                )
                
                st.dataframe(styled_comp_df, use_container_width=True)
        
        # Quick insights for today
        st.subheader("💡 ข้อมูลเบื้องต้นสำหรับวันนี้")
        
        # Find best deals
        if valid_prices and len(valid_prices) >= 2:
            cheapest = min(valid_prices, key=valid_prices.get)
            expensive = max(valid_prices, key=valid_prices.get)
            price_diff = valid_prices[expensive] - valid_prices[cheapest]
            
            if price_diff > 0:
                st.info(f"""
                **💰 เคล็ดลับประหยัดเงิน:** 
                คุณสามารถประหยัดได้ **{price_diff:.2f} บาท/ลิตร** โดยเลือกเติมที่ **{company_mapping.get(cheapest, cheapest)}** 
                แทน **{company_mapping.get(expensive, expensive)}**
                """)

# ============================================================================
# TAB 2: Trend Analysis
# ============================================================================
with tab2:
    st.header("📈 วิเคราะห์แนวโน้มราคา")
    
    if not selected_companies:
        st.warning("⚠️ กรุณาเลือกบริษัทที่ต้องการวิเคราะห์ใน sidebar")
    else:
        # Time period selection
        col1, col2 = st.columns(2)
        
        with col1:
            period = st.selectbox(
                "เลือกช่วงเวลาที่ต้องการวิเคราะห์",
                ["7 วัน", "30 วัน", "90 วัน", "1 ปี", "ทั้งหมด"],
                key="trend_period"
            )
        
        with col2:
            chart_type = st.selectbox(
                "เลือกรูปแบบกราฟ",
                ["เส้น", "แท่ง", "พื้นที่"],
                key="chart_type"
            )
        
        # Convert period to days
        period_map = {
            "7 วัน": 7,
            "30 วัน": 30,
            "90 วัน": 90,
            "1 ปี": 365,
            "ทั้งหมด": None
        }
        
        days = period_map[period]
        if days:
            start_date_trend = pd.to_datetime(selected_date) - pd.Timedelta(days=days)
            trend_data = df[(df['Date'] >= start_date_trend) & 
                           (df['Date'] <= pd.to_datetime(selected_date)) &
                           (df['FULE_TYPE'] == fuel)]
        else:
            trend_data = df[df['FULE_TYPE'] == fuel]
        
        # Clean data
        trend_data = trend_data.copy()
        for company in selected_companies:
            if company in trend_data.columns:
                trend_data[company] = pd.to_numeric(trend_data[company], errors='coerce')
        
        if not trend_data.empty and len(selected_companies) > 0:
            # Create interactive plot with plotly
            fig = go.Figure()
            
            company_colors = get_company_colors()
            
            for company in selected_companies:
                if company in trend_data.columns:
                    company_data = trend_data[['Date', company]].dropna()
                    if not company_data.empty:
                        color = company_colors.get(company, {}).get('color', '#1f77b4')
                        
                        if chart_type == "เส้น":
                            fig.add_trace(go.Scatter(
                                x=company_data['Date'],
                                y=company_data[company],
                                mode='lines+markers',
                                name=company_mapping.get(company, company),
                                line=dict(color=color, width=2),
                                marker=dict(size=6),
                                hovertemplate='<b>%{x|%d/%m/%Y}</b><br>ราคา: %{y:.2f} บาท<extra></extra>'
                            ))
                        elif chart_type == "แท่ง":
                            fig.add_trace(go.Bar(
                                x=company_data['Date'],
                                y=company_data[company],
                                name=company_mapping.get(company, company),
                                marker_color=color,
                                hovertemplate='<b>%{x|%d/%m/%Y}</b><br>ราคา: %{y:.2f} บาท<extra></extra>'
                            ))
                        elif chart_type == "พื้นที่":
                            fig.add_trace(go.Scatter(
                                x=company_data['Date'],
                                y=company_data[company],
                                mode='lines',
                                name=company_mapping.get(company, company),
                                line=dict(color=color, width=2),
                                stackgroup='one',
                                hovertemplate='<b>%{x|%d/%m/%Y}</b><br>ราคา: %{y:.2f} บาท<extra></extra>'
                            ))
            
            # Update layout
            fig.update_layout(
                title=f"แนวโน้มราคาน้ำมัน {fuel} - {period}",
                xaxis_title="วันที่",
                yaxis_title="ราคา (บาท/ลิตร)",
                hovermode="x unified",
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ),
                height=500,
                template="plotly_white"
            )
            
            # Add range slider
            fig.update_xaxes(
                rangeslider_visible=True,
                rangeselector=dict(
                    buttons=list([
                        dict(count=7, label="1w", step="day", stepmode="backward"),
                        dict(count=30, label="1m", step="day", stepmode="backward"),
                        dict(count=90, label="3m", step="day", stepmode="backward"),
                        dict(step="all")
                    ])
                )
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Statistical analysis
            if show_advanced_stats:
                st.subheader("📊 สถิติเชิงลึก")
                
                stats_data = []
                for company in selected_companies:
                    if company in trend_data.columns:
                        company_prices = trend_data[company].dropna()
                        if len(company_prices) > 1:
                            stats_data.append({
                                'บริษัท': company_mapping.get(company, company),
                                'ราคาล่าสุด': f"{company_prices.iloc[-1]:.2f}",
                                'ราคาต่ำสุด': f"{company_prices.min():.2f}",
                                'ราคาสูงสุด': f"{company_prices.max():.2f}",
                                'ค่าเฉลี่ย': f"{company_prices.mean():.2f}",
                                'ส่วนเบี่ยงเบน': f"{company_prices.std():.2f}",
                                'การเปลี่ยนแปลง': f"{(company_prices.iloc[-1] - company_prices.iloc[0]):+.2f}"
                            })
                
                if stats_data:
                    stats_df = pd.DataFrame(stats_data)
                    st.dataframe(stats_df, use_container_width=True)
            
            # Price forecast
            if show_forecast and len(selected_companies) > 0:
                st.subheader("🔮 การพยากรณ์ราคา 7 วันข้างหน้า")
                
                forecast_cols = st.columns(min(3, len(selected_companies)))
                
                for idx, company in enumerate(selected_companies[:3]):  # Limit to 3 companies
                    with forecast_cols[idx % len(forecast_cols)]:
                        forecast = generate_price_forecast(df, fuel, company, days=7)
                        
                        if forecast:
                            current_price = forecast['current_price']
                            trend_icon = "📈" if forecast['trend'] > 0 else "📉" if forecast['trend'] < 0 else "➡️"
                            trend_text = "เพิ่มขึ้น" if forecast['trend'] > 0 else "ลดลง" if forecast['trend'] < 0 else "คงที่"
                            
                            st.metric(
                                label=f"{company_mapping.get(company, company)}",
                                value=f"{current_price:.2f}",
                                delta=f"{trend_icon} แนวโน้ม{trend_text}",
                                delta_color="normal" if forecast['trend'] == 0 else "inverse" if forecast['trend'] > 0 else "normal"
                            )
                            
                            # Show forecast prices
                            with st.expander("ดูพยากรณ์รายวัน"):
                                for day_forecast in forecast['forecast']:
                                    st.write(f"{day_forecast['date'].strftime('%d/%m')}: {day_forecast['price']:.2f} บาท")
        else:
            st.warning("⚠️ ไม่มีข้อมูลสำหรับการวิเคราะห์แนวโน้ม")

# ============================================================================
# TAB 3: Deep Analysis
# ============================================================================
with tab3:
    st.header("🔍 วิเคราะห์เชิงลึก")
    
    if len(selected_companies) < 2:
        st.warning("⚠️ กรุณาเลือกอย่างน้อย 2 บริษัทเพื่อวิเคราะห์เชิงลึก")
    else:
        # Correlation analysis
        st.subheader("🔗 ความสัมพันธ์ระหว่างราคา")
        
        col1, col2 = st.columns(2)
        
        with col1:
            corr_period = st.selectbox(
                "ช่วงเวลาที่ใช้วิเคราะห์",
                ["30 วันล่าสุด", "90 วันล่าสุด", "1 ปีล่าสุด", "ทั้งหมด"],
                key="corr_period"
            )
        
        with col2:
            corr_method = st.selectbox(
                "วิธีคำนวณความสัมพันธ์",
                ["Pearson", "Spearman"],
                key="corr_method"
            )
        
        # Filter data based on period
        period_map_corr = {
            "30 วันล่าสุด": 30,
            "90 วันล่าสุด": 90,
            "1 ปีล่าสุด": 365,
            "ทั้งหมด": None
        }
        
        days_corr = period_map_corr[corr_period]
        if days_corr:
            start_date_corr = pd.to_datetime(selected_date) - pd.Timedelta(days=days_corr)
            corr_data = df[(df['Date'] >= start_date_corr) & 
                          (df['Date'] <= pd.to_datetime(selected_date)) &
                          (df['FULE_TYPE'] == fuel)]
        else:
            corr_data = df[df['FULE_TYPE'] == fuel]
        
        # Clean and prepare data
        corr_data_clean = corr_data.copy()
        for company in selected_companies:
            if company in corr_data_clean.columns:
                corr_data_clean[company] = pd.to_numeric(corr_data_clean[company], errors='coerce')
        
        # Remove rows where all selected companies have NaN
        corr_data_clean = corr_data_clean.dropna(subset=selected_companies, how='all')
        
        if len(corr_data_clean) >= 5:  # Need at least 5 data points
            # Calculate correlation
            method_map = {
                "Pearson": "pearson",
                "Spearman": "spearman"
            }
            
            try:
                corr_matrix = corr_data_clean[selected_companies].corr(method=method_map[corr_method])
                
                # Create heatmap
                fig_corr = go.Figure(data=go.Heatmap(
                    z=corr_matrix.values,
                    x=[company_mapping.get(col, col) for col in corr_matrix.columns],
                    y=[company_mapping.get(col, col) for col in corr_matrix.index],
                    colorscale='RdBu',
                    zmin=-1,
                    zmax=1,
                    text=corr_matrix.values.round(2),
                    texttemplate='%{text}',
                    textfont={"size": 10},
                    hovertemplate='<b>%{x}</b> vs <b>%{y}</b><br>Correlation: %{z:.3f}<extra></extra>'
                ))
                
                fig_corr.update_layout(
                    title=f"เมทริกซ์ความสัมพันธ์ราคาน้ำมัน<br><sup>{fuel} - {corr_period} ({corr_method})</sup>",
                    height=500,
                    xaxis_title="บริษัท",
                    yaxis_title="บริษัท",
                    template="plotly_white"
                )
                
                st.plotly_chart(fig_corr, use_container_width=True)
                
                # Interpretation
                with st.expander("📖 คำอธิบายความสัมพันธ์"):
                    st.markdown("""
                    **การตีความค่าความสัมพันธ์:**
                    - **1.00**: ความสัมพันธ์เชิงบวกสมบูรณ์ (ราคาเปลี่ยนแปลงในทิศทางเดียวกันเสมอ)
                    - **0.70 ถึง 0.99**: ความสัมพันธ์เชิงบวกสูง
                    - **0.40 ถึง 0.69**: ความสัมพันธ์เชิงบวกปานกลาง
                    - **0.00 ถึง 0.39**: ความสัมพันธ์เชิงบวกต่ำหรือไม่มี
                    - **-0.39 ถึง 0.00**: ความสัมพันธ์เชิงลบต่ำ
                    - **-0.69 ถึง -0.40**: ความสัมพันธ์เชิงลบปานกลาง
                    - **-0.99 ถึง -0.70**: ความสัมพันธ์เชิงลบสูง
                    - **-1.00**: ความสัมพันธ์เชิงลบสมบูรณ์
                    
                    **การประยุกต์ใช้:**
                    - ค่าความสัมพันธ์สูง (>0.7) บ่งชี้ว่าราคามีแนวโน้มเปลี่ยนแปลงในทิศทางเดียวกัน
                    - ค่าความสัมพันธ์ต่ำ (<0.3) บ่งชี้ว่าราคามีความเป็นอิสระต่อกัน
                    """)
                
            except Exception as e:
                st.error(f"⚠️ ไม่สามารถคำนวณความสัมพันธ์ได้: {e}")
        
        # Volatility analysis
        st.subheader("📊 การวิเคราะห์ความผันผวน")
        
        if len(corr_data_clean) >= 10:
            # Calculate volatility for each company
            volatility_data = []
            for company in selected_companies:
                if company in corr_data_clean.columns:
                    prices = corr_data_clean[company].dropna()
                    if len(prices) > 5:
                        returns = prices.pct_change().dropna()
                        volatility = returns.std() * np.sqrt(252)  # Annualized volatility
                        
                        # Classify volatility level
                        if volatility > 0.3:
                            level = "สูง"
                            color = "#FF6B6B"
                        elif volatility > 0.15:
                            level = "ปานกลาง"
                            color = "#FFD166"
                        else:
                            level = "ต่ำ"
                            color = "#06D6A0"
                        
                        volatility_data.append({
                            'company': company_mapping.get(company, company),
                            'volatility': volatility,
                            'level': level,
                            'color': color
                        })
            
            if volatility_data:
                # Create bar chart
                vol_df = pd.DataFrame(volatility_data)
                vol_df = vol_df.sort_values('volatility', ascending=False)
                
                fig_vol = go.Figure(data=[
                    go.Bar(
                        x=vol_df['company'],
                        y=vol_df['volatility'],
                        marker_color=vol_df['color'],
                        text=[f'{v:.1%}' for v in vol_df['volatility']],
                        textposition='auto',
                        hovertemplate='<b>%{x}</b><br>ความผันผวน: %{y:.2%}<br>ระดับ: %{customdata}<extra></extra>',
                        customdata=vol_df['level']
                    )
                ])
                
                fig_vol.update_layout(
                    title="ระดับความผันผวนของราคา",
                    xaxis_title="บริษัท",
                    yaxis_title="ความผันผวน (ต่อปี)",
                    height=400,
                    template="plotly_white"
                )
                
                st.plotly_chart(fig_vol, use_container_width=True)
        
        # Price spread analysis
        st.subheader("📏 การวิเคราะห์ช่วงราคา")
        
        if len(corr_data_clean) >= 5:
            # Calculate daily price spread
            daily_data = corr_data_clean.groupby('Date')[selected_companies].mean()
            
            if not daily_data.empty:
                daily_spread = daily_data.max(axis=1) - daily_data.min(axis=1)
                
                # Create spread chart
                fig_spread = go.Figure()
                
                fig_spread.add_trace(go.Scatter(
                    x=daily_spread.index,
                    y=daily_spread,
                    mode='lines',
                    name='ช่วงราคา',
                    line=dict(color='#EF476F', width=2),
                    fill='tozeroy',
                    fillcolor='rgba(239, 71, 111, 0.2)',
                    hovertemplate='<b>%{x|%d/%m/%Y}</b><br>ช่วงราคา: %{y:.2f} บาท<extra></extra>'
                ))
                
                # Add average line
                avg_spread = daily_spread.mean()
                fig_spread.add_hline(
                    y=avg_spread,
                    line_dash="dash",
                    line_color="green",
                    annotation_text=f"ค่าเฉลี่ย: {avg_spread:.2f} บาท",
                    annotation_position="bottom right"
                )
                
                fig_spread.update_layout(
                    title="ช่วงราคาน้ำมันเปลี่ยนแปลงตามเวลา",
                    xaxis_title="วันที่",
                    yaxis_title="ช่วงราคา (บาท/ลิตร)",
                    height=400,
                    template="plotly_white",
                    showlegend=True
                )
                
                st.plotly_chart(fig_spread, use_container_width=True)
                
                # Spread statistics
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("ค่าเฉลี่ยช่วงราคา", f"{avg_spread:.3f} บาท")
                with col2:
                    st.metric("ช่วงราคาสูงสุด", f"{daily_spread.max():.3f} บาท")
                with col3:
                    st.metric("ช่วงราคาต่ำสุด", f"{daily_spread.min():.3f} บาท")

# ============================================================================
# TAB 4: Insights
# ============================================================================
with tab4:
    st.header("💡 ข้อมูลเชิงลึก (Insights)")
    
    if not selected_companies:
        st.warning("⚠️ กรุณาเลือกบริษัทที่ต้องการวิเคราะห์ใน sidebar")
    else:
        # Generate insights
        with st.spinner("กำลังวิเคราะห์ข้อมูล..."):
            # 1. Price trend insights
            trend_insights = analyze_price_trends(df, fuel, selected_companies, analysis_period)
            
            # 2. Volatility insights
            volatility_insights = analyze_price_volatility(df, fuel, selected_companies, analysis_period)
            
            # 3. Price spread insights
            spread_insights = analyze_price_spread(df, fuel, selected_companies, 7)
            
            # 4. Best deals insights
            deal_insights = find_best_deals(df, selected_date, fuel, selected_companies)
            
            # 5. Missing data insights
            missing_insights = analyze_missing_data(df, fuel, selected_companies)
            
            # Combine all insights
            all_insights = (trend_insights + volatility_insights + 
                          spread_insights + deal_insights + missing_insights)
        
        if not all_insights:
            st.info("📊 ไม่พบข้อมูลเชิงลึกที่สำคัญในขณะนี้")
        else:
            # Group insights by type
            warning_insights = [i for i in all_insights if i['type'] == 'warning']
            success_insights = [i for i in all_insights if i['type'] == 'success']
            other_insights = [i for i in all_insights if i['type'] not in ['warning', 'success']]
            
            # Display warnings first
            if warning_insights:
                st.subheader("⚠️ ข้อควรระวัง")
                for insight in warning_insights:
                    st.markdown(f"""
                    <div class="warning-card">
                        <h4>{insight['title']}</h4>
                        <p>{insight['content']}</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Display successes
            if success_insights:
                st.subheader("✅ โอกาสที่ดี")
                for insight in success_insights:
                    st.markdown(f"""
                    <div class="success-card">
                        <h4>{insight['title']}</h4>
                        <p>{insight['content']}</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Display other insights
            if other_insights:
                st.subheader("💡 ข้อมูลเชิงลึก")
                for insight in other_insights:
                    st.markdown(f"""
                    <div class="insight-card">
                        <h4>{insight['title']}</h4>
                        <p>{insight['content']}</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Summary statistics
            st.subheader("📈 สรุปสถิติสำคัญ")
            
            # Get latest data for summary
            latest_data = df[df['Date'] == df['Date'].max()]
            latest_fuel_data = latest_data[latest_data['FULE_TYPE'] == fuel]
            
            if not latest_fuel_data.empty:
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    # Count of companies with data
                    companies_with_data = 0
                    for company in selected_companies:
                        if company in latest_fuel_data.columns:
                            price = latest_fuel_data[company].iloc[0]
                            if pd.notna(price) and price > 0:
                                companies_with_data += 1
                    
                    st.metric("บริษัทที่มีข้อมูล", f"{companies_with_data}/{len(selected_companies)}")
                
                with col2:
                    # Days with data
                    fuel_data = df[df['FULE_TYPE'] == fuel]
                    days_with_data = fuel_data['Date'].nunique()
                    st.metric("วันที่มีข้อมูล", days_with_data)
                
                with col3:
                    # Average price
                    valid_prices = []
                    for company in selected_companies:
                        if company in latest_fuel_data.columns:
                            price = latest_fuel_data[company].iloc[0]
                            if pd.notna(price) and price > 0:
                                valid_prices.append(price)
                    
                    if valid_prices:
                        avg_price = np.mean(valid_prices)
                        st.metric("ราคาเฉลี่ยล่าสุด", f"{avg_price:.2f} บาท")
            
            # Recommendations
            st.subheader("🎯 ข้อแนะนำ")
            
            recommendations = []
            
            # Check if there's significant price difference
            latest_valid_prices = {}
            for company in selected_companies:
                if company in latest_fuel_data.columns:
                    price = latest_fuel_data[company].iloc[0]
                    if pd.notna(price) and price > 0:
                        latest_valid_prices[company] = price
            
            if len(latest_valid_prices) >= 2:
                cheapest = min(latest_valid_prices, key=latest_valid_prices.get)
                expensive = max(latest_valid_prices, key=latest_valid_prices.get)
                price_diff = latest_valid_prices[expensive] - latest_valid_prices[cheapest]
                
                if price_diff > 0.5:
                    recommendations.append(
                        f"**เติมที่ {company_mapping.get(cheapest, cheapest)}** เพื่อประหยัด {price_diff:.2f} บาท/ลิตร"
                    )
            
            # Check price trend
            if trend_insights:
                for insight in trend_insights:
                    if insight.get('slope', 0) < -0.02:  # ถ้าราคาลดลงอย่างมีนัยสำคัญ
                        recommendations.append(
                            f"**รอเติม {insight['company']}** เพราะราคามีแนวโน้มลดลงอย่างต่อเนื่อง"
                        )
            
            # Display recommendations
            if recommendations:
                for i, rec in enumerate(recommendations, 1):
                    st.markdown(f"{i}. {rec}")
            else:
                st.info("ราคาในปัจจุบันค่อนข้างเสถียร ไม่มีข้อแนะนำพิเศษ")

# ============================================================================
# TAB 5: Station Map
# ============================================================================
with tab5:
    st.header("🗺️ ค้นหาปั๊มน้ำมัน")
    
    if tariff_df is None or tariff_df.empty:
        st.warning("⚠️ ไม่พบข้อมูลตำแหน่งปั๊มน้ำมัน กรุณาตรวจสอบไฟล์ tariff.csv")
    else:
        # Filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Brand filter
            available_brands = sorted(tariff_df['company'].dropna().unique())
            selected_brands = st.multiselect(
                "เลือกแบรนด์ปั๊ม",
                options=available_brands,
                default=available_brands[:3] if len(available_brands) > 3 else available_brands
            )
        
        with col2:
            # Province filter
            available_provinces = sorted(tariff_df['province'].dropna().unique())
            selected_province = st.selectbox(
                "เลือกจังหวัด",
                options=available_provinces,
                index=available_provinces.index('Bangkok') if 'Bangkok' in available_provinces else 0
            )
        
        with col3:
            # District filter (only for Bangkok)
            if selected_province.lower() == 'bangkok' and 'district' in tariff_df.columns:
                available_districts = sorted(tariff_df['district'].dropna().unique())
                selected_districts = st.multiselect(
                    "เลือกเขตในกรุงเทพฯ",
                    options=available_districts,
                    default=available_districts[:5] if len(available_districts) > 5 else available_districts
                )
            else:
                selected_districts = None
        
        # Apply filters
        if selected_districts and selected_brands:
            filtered_tariff = tariff_df[
                (tariff_df['company'].isin(selected_brands)) &
                (tariff_df['province'] == selected_province) &
                (tariff_df['district'].isin(selected_districts))
            ]
        elif selected_brands:
            filtered_tariff = tariff_df[
                (tariff_df['company'].isin(selected_brands)) &
                (tariff_df['province'] == selected_province)
            ]
        else:
            filtered_tariff = pd.DataFrame()
        
        if not filtered_tariff.empty:
            # Display statistics
            st.info(f"""
            **พบปั๊มน้ำมันทั้งหมด: {len(filtered_tariff)} แห่ง**
            - **แบรนด์ที่เลือก:** {', '.join(selected_brands)}
            - **จังหวัด:** {selected_province}
            {f"- **เขต:** {', '.join(selected_districts)}" if selected_districts else ""}
            """)
            
            # Create map layers with different colors for each brand
            brand_colors = {
                'PTT': [255, 0, 0, 160],        # Red
                'BANGCHAK': [0, 255, 0, 160],    # Green
                'SHELL': [255, 165, 0, 160],     # Orange
                'ESSO': [0, 0, 255, 160],        # Blue
                'CHEVRON': [255, 255, 0, 160],   # Yellow
                'IRPC': [255, 0, 255, 160],      # Magenta
                'PTG': [128, 128, 128, 160],     # Gray
                'SUSCO': [0, 255, 255, 160],     # Cyan
                'PURE': [128, 0, 128, 160],      # Purple
            }
            
            # Create layers for each brand
            layers = []
            for brand in selected_brands:
                brand_data = filtered_tariff[filtered_tariff['company'] == brand]
                if not brand_data.empty:
                    color = brand_colors.get(brand.upper(), [0, 128, 255, 160])
                    layer = pdk.Layer(
                        "ScatterplotLayer",
                        data=brand_data,
                        get_position='[longitude, latitude]',
                        get_color=color,
                        get_radius=500,
                        pickable=True,
                        auto_highlight=True
                    )
                    layers.append(layer)
            
            # Set view state
            if selected_province.lower() == 'bangkok':
                # Zoom in for Bangkok
                view_state = pdk.ViewState(
                    latitude=filtered_tariff['latitude'].mean(),
                    longitude=filtered_tariff['longitude'].mean(),
                    zoom=11,
                    pitch=50
                )
            else:
                # Show whole province
                view_state = pdk.ViewState(
                    latitude=filtered_tariff['latitude'].mean(),
                    longitude=filtered_tariff['longitude'].mean(),
                    zoom=8,
                    pitch=0
                )
            
            # Create map
            if layers:
                map_deck = pdk.Deck(
                    layers=layers,
                    initial_view_state=view_state,
                    tooltip={
                        "html": """
                        <b>{company}</b><br/>
                        {province} {district if district else ''}<br/>
                        Lat: {latitude:.4f}<br/>
                        Long: {longitude:.4f}
                        """,
                        "style": {
                            "backgroundColor": "steelblue",
                            "color": "white",
                            "fontFamily": '"Helvetica Neue", Arial',
                            "fontSize": "14px",
                            "padding": "10px"
                        }
                    }
                )
                
                # Display map
                st.pydeck_chart(map_deck)
                
                # Display station list
                st.subheader("📋 รายการปั๊มน้ำมัน")
                
                # Create display dataframe
                display_cols = ['company', 'province']
                if 'district' in filtered_tariff.columns:
                    display_cols.append('district')
                display_cols.extend(['latitude', 'longitude'])
                
                station_df = filtered_tariff[display_cols].copy()
                station_df['latitude'] = station_df['latitude'].round(4)
                station_df['longitude'] = station_df['longitude'].round(4)
                
                if 'district' in display_cols:
                    station_df.columns = ['แบรนด์', 'จังหวัด', 'เขต', 'ละติจูด', 'ลองจิจูด']
                else:
                    station_df.columns = ['แบรนด์', 'จังหวัด', 'ละติจูด', 'ลองจิจูด']
                
                st.dataframe(
                    station_df.style.background_gradient(cmap='Blues'),
                    use_container_width=True
                )
                
                # Brand distribution chart
                st.subheader("📊 การกระจายตัวของปั๊มน้ำมันตามแบรนด์")
                
                brand_counts = filtered_tariff['company'].value_counts()
                
                fig_brand = px.pie(
                    values=brand_counts.values,
                    names=brand_counts.index,
                    title=f"สัดส่วนปั๊มน้ำมันแบ่งตามแบรนด์ ({selected_province})",
                    color_discrete_sequence=px.colors.sequential.Blues_r
                )
                
                fig_brand.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig_brand, use_container_width=True)
            else:
                st.warning("⚠️ ไม่พบปั๊มน้ำมันที่ตรงกับเงื่อนไขที่เลือก")
        else:
            st.warning("⚠️ ไม่พบปั๊มน้ำมันที่ตรงกับเงื่อนไขที่เลือก")

# ============================================================================
# 8. Footer
# ============================================================================
st.markdown("---")
if not df.empty:
    last_update = df['Date'].max().strftime('%d %B %Y')
    total_days = df['Date'].nunique()
    total_fuel_types = df['FULE_TYPE'].nunique()
else:
    last_update = "ไม่ทราบวันที่"
    total_days = 0
    total_fuel_types = 0

st.markdown(f"""
<div style="text-align: center; color: #666; padding: 2rem;">
    <h3>🛢️ OilSophang - ระบบวิเคราะห์และติดตามราคาน้ำมัน</h3>
    <p>"เติมก่อนประหยัดกว่า" - วิเคราะห์เชิงลึกเพื่อการตัดสินใจที่ชาญฉลาด</p>
    <p>ข้อมูลอัปเดตล่าสุด: {last_update} | มีข้อมูล {total_days} วัน | {total_fuel_types} ประเภทน้ำมัน</p>
    <p>© 2024 OilSophang. All rights reserved.</p>
</div>
""", unsafe_allow_html=True)