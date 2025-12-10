# settrade_demo_fixed.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import requests
import json
from typing import Dict, List, Optional
import base64
from io import BytesIO

# -------------------------------------------------
# Page Config
# -------------------------------------------------
st.set_page_config(
    page_title="Settrade Trading Platform",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------------------------
# Settrade API Configuration
# -------------------------------------------------
class SettradeConfig:
    """การตั้งค่า Settrade API"""
    
    # API Endpoints
    SANDBOX_URL = "https://api.settrade.com/api"
    PRODUCTION_URL = "https://api.settrade.com/api"
    
    # ใช้ Sandbox สำหรับทดสอบ
    BASE_URL = SANDBOX_URL
    
    # API Version
    VERSION = "v2"
    
    # API Paths
    PATHS = {
        "auth": "/oauth/token",
        "stock_quote": "/market/v2/quote/",
        "stock_intraday": "/market/v2/intraday/",
        "stock_historical": "/market/v2/historical/",
        "stock_info": "/market/v2/company/",
        "portfolio": "/v2/portfolio/",
        "account_info": "/v2/account/info",
        "place_order": "/v2/orders",
        "order_status": "/v2/orders/",
        "market_status": "/market/v2/market-status",
        "market_index": "/market/v2/index",
        "market_sector": "/market/v2/sector",
    }

# -------------------------------------------------
# Session State Management
# -------------------------------------------------
class SessionManager:
    """จัดการ Session State"""
    
    @staticmethod
    def init_session():
        """เริ่มต้น session state"""
        if 'logged_in' not in st.session_state:
            st.session_state.logged_in = False
        if 'demo_mode' not in st.session_state:
            st.session_state.demo_mode = False
        if 'access_token' not in st.session_state:
            st.session_state.access_token = None
        if 'account_info' not in st.session_state:
            st.session_state.account_info = None
        if 'portfolio' not in st.session_state:
            st.session_state.portfolio = None
        if 'market_data' not in st.session_state:
            st.session_state.market_data = {}
        if 'last_update' not in st.session_state:
            st.session_state.last_update = datetime.now()
        if 'orders' not in st.session_state:
            st.session_state.orders = []
        if 'login_attempted' not in st.session_state:
            st.session_state.login_attempted = False

# -------------------------------------------------
# Settrade API Client
# -------------------------------------------------
class SettradeAPIClient:
    """Client สำหรับเชื่อมต่อกับ Settrade API"""
    
    def __init__(self, app_id: str, app_secret: str, broker_id: str, app_code: str):
        self.app_id = app_id
        self.app_secret = app_secret
        self.broker_id = broker_id
        self.app_code = app_code
        self.base_url = SettradeConfig.BASE_URL
        self.access_token = None
        self.headers = {}
        
    def authenticate(self) -> bool:
        """การยืนยันตัวตนกับ Settrade API"""
        try:
            # สร้าง Basic Auth
            auth_string = f"{self.app_id}:{self.app_secret}"
            encoded_auth = base64.b64encode(auth_string.encode()).decode()
            
            # Headers สำหรับ authentication
            auth_headers = {
                "Authorization": f"Basic {encoded_auth}",
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            # Request body
            auth_data = {
                "grant_type": "client_credentials",
                "scope": "default"
            }
            
            # ทำ request
            response = requests.post(
                f"{self.base_url}{SettradeConfig.PATHS['auth']}",
                headers=auth_headers,
                data=auth_data,
                timeout=10
            )
            
            if response.status_code == 200:
                auth_result = response.json()
                self.access_token = auth_result.get("access_token")
                self.headers = {
                    "Authorization": f"Bearer {self.access_token}",
                    "Content-Type": "application/json",
                    "Broker-Id": self.broker_id,
                    "App-Code": self.app_code
                }
                return True
            else:
                st.error(f"Authentication failed: {response.status_code}")
                return False
                
        except Exception as e:
            st.error(f"Authentication error: {str(e)}")
            return False
    
    def get_stock_quote(self, symbol: str) -> Optional[Dict]:
        """ดึงข้อมูลราคาหุ้นล่าสุด"""
        try:
            response = requests.get(
                f"{self.base_url}{SettradeConfig.PATHS['stock_quote']}{symbol}",
                headers=self.headers,
                timeout=5
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
                
        except Exception:
            return None
    
    def get_historical_data(self, symbol: str, period: str = "1M") -> Optional[pd.DataFrame]:
        """ดึงข้อมูลราคาย้อนหลัง"""
        try:
            # Map period to API parameters
            period_map = {
                "1D": "1",
                "1W": "7",
                "1M": "30",
                "3M": "90",
                "6M": "180",
                "1Y": "365"
            }
            
            days = period_map.get(period, "30")
            
            response = requests.get(
                f"{self.base_url}{SettradeConfig.PATHS['stock_historical']}{symbol}/{days}",
                headers=self.headers,
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'ohlcv' in data:
                    df = pd.DataFrame(data['ohlcv'])
                    df['datetime'] = pd.to_datetime(df['datetime'])
                    df.set_index('datetime', inplace=True)
                    return df
            return None
            
        except Exception:
            return None

# -------------------------------------------------
# Demo Data Generator
# -------------------------------------------------
class DemoDataGenerator:
    """สร้างข้อมูล Demo สำหรับทดสอบ"""
    
    @staticmethod
    def get_stock_list() -> List[Dict]:
        """รายการหุ้นตัวอย่าง"""
        return [
            {"symbol": "AOT", "name": "ท่าอากาศยานไทย", "sector": "บริการ"},
            {"symbol": "PTT", "name": "ปตท.", "sector": "พลังงาน"},
            {"symbol": "ADVANC", "name": "เอไอเอส", "sector": "โทรคมนาคม"},
            {"symbol": "CPALL", "name": "ซีพีออลล์", "sector": "ค้าปลีก"},
            {"symbol": "KBANK", "name": "กรุงไทย", "sector": "การเงิน"},
            {"symbol": "SCB", "name": "ไทยพาณิชย์", "sector": "การเงิน"},
            {"symbol": "TRUE", "name": "ทรูคอร์ป", "sector": "โทรคมนาคม"},
            {"symbol": "GULF", "name": "กัลฟ์", "sector": "พลังงาน"},
            {"symbol": "EA", "name": "พลังงานบริสุทธิ์", "sector": "พลังงาน"},
            {"symbol": "IVL", "name": "อินโดรามา", "sector": "ปิโตรเคมี"},
            {"symbol": "DELTA", "name": "เดลต้า", "sector": "เทคโนโลยี"},
            {"symbol": "HANA", "name": "หาญเอเชีย", "sector": "เทคโนโลยี"},
            {"symbol": "AWC", "name": "แอสเซทเวิลด์", "sector": "อสังหาริมทรัพย์"},
            {"symbol": "LH", "name": "แลนด์ แอนด์ เฮ้าส์", "sector": "อสังหาริมทรัพย์"},
            {"symbol": "MINT", "name": "ไมเนอร์", "sector": "บริการ"},
            {"symbol": "CENTEL", "name": "เซ็นทราล", "sector": "บริการ"},
            {"symbol": "BBL", "name": "กรุงเทพ", "sector": "การเงิน"},
            {"symbol": "KTB", "name": "กรุงไทย", "sector": "การเงิน"},
            {"symbol": "BAY", "name": "กรุงศรี", "sector": "การเงิน"},
            {"symbol": "TMB", "name": "ธนชาต", "sector": "การเงิน"}
        ]
    
    @staticmethod
    def generate_stock_quote(symbol: str) -> Dict:
        """สร้างข้อมูลหุ้นตัวอย่าง"""
        stock_list = DemoDataGenerator.get_stock_list()
        stock_info = next((s for s in stock_list if s["symbol"] == symbol), None)
        
        if not stock_info:
            return None
        
        # สร้างราคาสุ่ม
        np.random.seed(hash(symbol) % 10000)
        base_price = np.random.uniform(10, 500)
        change = np.random.uniform(-5, 5)
        percent_change = (change / base_price) * 100
        
        return {
            "symbol": symbol,
            "name": stock_info["name"],
            "last_price": round(base_price, 2),
            "change": round(change, 2),
            "percent_change": round(percent_change, 2),
            "high_price": round(base_price * 1.03, 2),
            "low_price": round(base_price * 0.98, 2),
            "open_price": round(base_price * 0.995, 2),
            "previous_close": round(base_price * 0.99, 2),
            "volume": np.random.randint(1000000, 10000000),
            "value": np.random.randint(50000000, 500000000),
            "bid": round(base_price - 0.25, 2),
            "ask": round(base_price + 0.25, 2),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    @staticmethod
    def generate_historical_data(symbol: str, period: str = "1M") -> pd.DataFrame:
        """สร้างข้อมูลย้อนหลัง"""
        days_map = {"1D": 1, "1W": 7, "1M": 30, "3M": 90, "6M": 180, "1Y": 365}
        days = days_map.get(period, 30)
        
        # สร้างวันที่
        dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
        
        # สร้างราคาแบบ random walk
        np.random.seed(hash(symbol) % 10000)
        returns = np.random.normal(0.0005, 0.02, days)
        prices = 100 * (1 + returns).cumprod()
        
        # สร้าง DataFrame
        df = pd.DataFrame(index=dates)
        df['open'] = prices * (1 + np.random.uniform(-0.01, 0.01, days))
        df['high'] = df['open'] * (1 + np.random.uniform(0, 0.02, days))
        df['low'] = df['open'] * (1 + np.random.uniform(-0.02, 0, days))
        df['close'] = prices
        df['volume'] = np.random.randint(1000000, 5000000, days)
        
        return df

# -------------------------------------------------
# UI Components
# -------------------------------------------------
class UIComponents:
    """คอมโพเนนต์ UI"""
    
    @staticmethod
    def create_login_section():
        """ส่วนเข้าสู่ระบบ"""
        with st.sidebar:
            st.title("🔐 Settrade Login")
            
            # ฟอร์มเข้าสู่ระบบ
            with st.form("login_form"):
                st.write("**กรุณากรอกข้อมูล Settrade API:**")
                
                app_id = st.text_input("App ID", value="SANDBOX")
                app_secret = st.text_input("App Secret", type="password", value="SANDBOX")
                broker_id = st.text_input("Broker ID", value="SANDBOX")
                app_code = st.text_input("App Code", value="SANDBOX")
                
                submitted = st.form_submit_button("เข้าสู่ระบบ", type="primary")
                
                if submitted:
                    st.session_state.login_attempted = True
                    with st.spinner("กำลังเชื่อมต่อกับ Settrade..."):
                        try:
                            # สร้าง client
                            client = SettradeAPIClient(app_id, app_secret, broker_id, app_code)
                            
                            # ทำ authentication
                            if client.authenticate():
                                st.session_state.logged_in = True
                                st.session_state.demo_mode = False
                                st.session_state.access_token = client.access_token
                                st.session_state.client = client
                                st.success("✅ เข้าสู่ระบบสำเร็จ!")
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error("❌ ไม่สามารถเชื่อมต่อกับ Settrade ได้")
                        except Exception as e:
                            st.error(f"❌ เกิดข้อผิดพลาด: {str(e)}")
            
            # ปุ่ม Demo Mode (อยู่นอก form)
            st.divider()
            st.write("**หรือทดสอบด้วย Demo Mode:**")
            
            if st.button("🎮 ใช้ Demo Mode", use_container_width=True):
                st.session_state.logged_in = True
                st.session_state.demo_mode = True
                st.success("✅ เปิดใช้งาน Demo Mode สำเร็จ!")
                time.sleep(1)
                st.rerun()
            
            # Demo instructions
            if not st.session_state.logged_in:
                with st.expander("ℹ️ วิธีการใช้งาน", expanded=True):
                    st.write("""
                    ### สำหรับทดสอบ:
                    1. ใช้ **Demo Mode** สำหรับทดสอบฟรี
                    2. หรือใช้ข้อมูล **SANDBOX** สำหรับทั้ง 4 ช่อง
                    
                    ### สำหรับใช้งานจริง:
                    1. ไปที่ [Settrade Developer Portal](https://developer.settrade.com/)
                    2. สร้างแอปพลิเคชันและรับข้อมูล API
                    3. ใส่ข้อมูลในฟอร์มด้านบน
                    """)
    
    @staticmethod
    def create_market_overview():
        """ภาพรวมตลาด"""
        st.header("📊 ภาพรวมตลาด")
        
        # Market indices
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("SET Index", "1,450.12", "+12.34 (+0.86%)")
        
        with col2:
            st.metric("SET50 Index", "1,234.56", "+8.90 (+0.73%)")
        
        with col3:
            st.metric("SET100 Index", "1,678.90", "+15.67 (+0.94%)")
        
        st.divider()
        
        # Top movers
        st.subheader("🚀 หุ้นเด่นประจำวัน")
        
        # สร้างข้อมูลหุ้นตัวอย่าง
        top_stocks = ["AOT", "PTT", "ADVANC", "CPALL", "KBANK", "SCB", "TRUE", "GULF"]
        
        cols = st.columns(4)
        for idx, symbol in enumerate(top_stocks):
            with cols[idx % 4]:
                if st.session_state.get('demo_mode', True):
                    quote = DemoDataGenerator.generate_stock_quote(symbol)
                else:
                    if 'client' in st.session_state:
                        quote = st.session_state.client.get_stock_quote(symbol)
                    else:
                        quote = DemoDataGenerator.generate_stock_quote(symbol)
                
                if quote:
                    UIComponents.display_stock_card(quote)
        
        st.divider()
        
        # Market chart
        st.subheader("📈 กราฟตลาดหุ้น")
        UIComponents.create_market_chart()
    
    @staticmethod
    def display_stock_card(quote: Dict):
        """แสดงการ์ดข้อมูลหุ้น"""
        st.metric(
            label=f"{quote['symbol']} - {quote.get('name', '')}",
            value=f"{quote.get('last_price', 0):,.2f}",
            delta=f"{quote.get('change', 0):+,.2f} ({quote.get('percent_change', 0):+,.2f}%)"
        )
    
    @staticmethod
    def create_market_chart():
        """สร้างกราฟตลาด"""
        # สร้างข้อมูลตัวอย่าง
        dates = pd.date_range(end=datetime.now(), periods=60, freq='D')
        prices = 1400 + np.cumsum(np.random.randn(60)) * 10
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dates,
            y=prices,
            mode='lines',
            name='SET Index',
            line=dict(color='#1f77b4', width=3)
        ))
        
        fig.update_layout(
            title="SET Index - 60 วันย้อนหลัง",
            xaxis_title="วันที่",
            yaxis_title="จุด",
            height=400,
            template="plotly_white",
            hovermode="x unified"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    @staticmethod
    def create_stock_analysis():
        """วิเคราะห์หุ้น"""
        st.header("📈 วิเคราะห์หุ้น")
        
        # เลือกหุ้น
        stock_list = DemoDataGenerator.get_stock_list()
        symbol_options = [f"{s['symbol']} - {s['name']}" for s in stock_list]
        
        col1, col2 = st.columns(2)
        with col1:
            selected = st.selectbox("เลือกหุ้น", symbol_options, index=0)
            symbol = selected.split(" - ")[0]
        
        with col2:
            period = st.selectbox("ช่วงเวลา", ["1D", "1W", "1M", "3M", "6M", "1Y"], index=2)
        
        if symbol:
            # แสดงข้อมูลหุ้น
            UIComponents.display_stock_detail(symbol, period)
    
    @staticmethod
    def display_stock_detail(symbol: str, period: str):
        """แสดงรายละเอียดหุ้น"""
        # ดึงข้อมูล
        if st.session_state.get('demo_mode', True):
            quote = DemoDataGenerator.generate_stock_quote(symbol)
            hist_data = DemoDataGenerator.generate_historical_data(symbol, period)
        else:
            if 'client' in st.session_state:
                quote = st.session_state.client.get_stock_quote(symbol)
                hist_data = st.session_state.client.get_historical_data(symbol, period)
            else:
                quote = DemoDataGenerator.generate_stock_quote(symbol)
                hist_data = DemoDataGenerator.generate_historical_data(symbol, period)
        
        if quote:
            # แสดงข้อมูลพื้นฐาน
            st.subheader(f"📊 {quote.get('name', '')} ({symbol})")
            
            # Metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "ราคาล่าสุด",
                    f"{quote.get('last_price', 0):,.2f}",
                    f"{quote.get('change', 0):+,.2f} ({quote.get('percent_change', 0):+,.2f}%)"
                )
            
            with col2:
                st.metric(
                    "เสนอซื้อ/เสนอขาย",
                    f"{quote.get('bid', 0):,.2f} / {quote.get('ask', 0):,.2f}"
                )
            
            with col3:
                st.metric(
                    "สูง/ต่ำ วันนี้",
                    f"{quote.get('high_price', 0):,.2f} / {quote.get('low_price', 0):,.2f}"
                )
            
            with col4:
                st.metric("ปริมาณ", f"{quote.get('volume', 0):,}")
            
            st.divider()
            
            # กราฟราคา
            st.subheader("📈 กราฟราคาย้อนหลัง")
            
            if hist_data is not None:
                # เลือกประเภทกราฟ
                chart_type = st.radio("ประเภทกราฟ", ["เส้น", "แท่งเทียน"], horizontal=True)
                
                if chart_type == "แท่งเทียน":
                    fig = go.Figure(data=[
                        go.Candlestick(
                            x=hist_data.index,
                            open=hist_data['open'],
                            high=hist_data['high'],
                            low=hist_data['low'],
                            close=hist_data['close'],
                            name=symbol
                        )
                    ])
                else:
                    fig = go.Figure(data=[
                        go.Scatter(
                            x=hist_data.index,
                            y=hist_data['close'],
                            mode='lines',
                            name='ราคาปิด',
                            line=dict(color='blue', width=2)
                        )
                    ])
                
                fig.update_layout(
                    title=f"{symbol} - {period}",
                    yaxis_title="ราคา (บาท)",
                    xaxis_title="วันที่",
                    height=500,
                    template="plotly_white"
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # สถิติ
                st.subheader("📊 สถิติ")
                
                stat_cols = st.columns(4)
                
                with stat_cols[0]:
                    current = hist_data['close'].iloc[-1]
                    st.metric("ราคาปัจจุบัน", f"{current:,.2f}")
                
                with stat_cols[1]:
                    high = hist_data['high'].max()
                    st.metric("สูงสุด", f"{high:,.2f}")
                
                with stat_cols[2]:
                    low = hist_data['low'].min()
                    st.metric("ต่ำสุด", f"{low:,.2f}")
                
                with stat_cols[3]:
                    avg = hist_data['close'].mean()
                    st.metric("เฉลี่ย", f"{avg:,.2f}")
    
    @staticmethod
    def create_portfolio_view():
        """แสดงพอร์ตโฟลิโอ"""
        st.header("💼 พอร์ตโฟลิโอ")
        
        # สร้างข้อมูลพอร์ตตัวอย่าง
        portfolio_data = [
            {"symbol": "AOT", "name": "ท่าอากาศยานไทย", "qty": 1000, "avg_price": 65.50, "current_price": 68.50},
            {"symbol": "PTT", "name": "ปตท.", "qty": 2000, "avg_price": 34.25, "current_price": 35.25},
            {"symbol": "ADVANC", "name": "เอไอเอส", "qty": 1500, "avg_price": 41.80, "current_price": 42.75},
            {"symbol": "KBANK", "name": "กรุงไทย", "qty": 500, "avg_price": 150.25, "current_price": 152.00},
        ]
        
        # คำนวณมูลค่า
        for item in portfolio_data:
            item['market_value'] = item['qty'] * item['current_price']
            item['cost'] = item['qty'] * item['avg_price']
            item['pnl'] = item['market_value'] - item['cost']
            item['pnl_percent'] = (item['pnl'] / item['cost']) * 100 if item['cost'] > 0 else 0
        
        # สรุปพอร์ต
        total_cost = sum(item['cost'] for item in portfolio_data)
        total_value = sum(item['market_value'] for item in portfolio_data)
        total_pnl = total_value - total_cost
        total_pnl_percent = (total_pnl / total_cost) * 100 if total_cost > 0 else 0
        
        # Display summary
        st.subheader("📈 สรุปพอร์ต")
        
        summary_cols = st.columns(4)
        summary_cols[0].metric("มูลค่าพอร์ต", f"฿{total_value:,.2f}")
        summary_cols[1].metric("เงินลงทุน", f"฿{total_cost:,.2f}")
        summary_cols[2].metric("กำไร/ขาดทุน", f"฿{total_pnl:+,.2f}")
        summary_cols[3].metric("% กำไร/ขาดทุน", f"{total_pnl_percent:+.2f}%")
        
        st.divider()
        
        # ตารางพอร์ต
        st.subheader("📋 หลักทรัพย์ในพอร์ต")
        
        # สร้าง DataFrame
        df = pd.DataFrame(portfolio_data)
        df['weight'] = (df['market_value'] / total_value * 100).round(2)
        
        # จัดรูปแบบแสดงผล
        display_df = df.copy()
        display_df['avg_price'] = display_df['avg_price'].apply(lambda x: f"฿{x:,.2f}")
        display_df['current_price'] = display_df['current_price'].apply(lambda x: f"฿{x:,.2f}")
        display_df['market_value'] = display_df['market_value'].apply(lambda x: f"฿{x:,.2f}")
        display_df['pnl'] = display_df['pnl'].apply(lambda x: f"฿{x:+,.2f}")
        display_df['pnl_percent'] = display_df['pnl_percent'].apply(lambda x: f"{x:+.2f}%")
        display_df['weight'] = display_df['weight'].apply(lambda x: f"{x:.2f}%")
        
        st.dataframe(
            display_df,
            column_config={
                "symbol": "สัญลักษณ์",
                "name": "ชื่อ",
                "qty": "จำนวน",
                "avg_price": "ราคาเฉลี่ย",
                "current_price": "ราคาปัจจุบัน",
                "market_value": "มูลค่าตลาด",
                "pnl": "กำไร/ขาดทุน",
                "pnl_percent": "% กำไร/ขาดทุน",
                "weight": "สัดส่วน"
            },
            use_container_width=True,
            hide_index=True
        )
        
        # กราฟพอร์ต
        st.subheader("📊 การกระจายพอร์ต")
        
        fig = go.Figure(data=[go.Pie(
            labels=df['symbol'],
            values=df['market_value'],
            hole=0.3,
            textinfo='label+percent'
        )])
        
        fig.update_layout(
            title="สัดส่วนการลงทุนในพอร์ต",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    @staticmethod
    def create_trading_platform():
        """แพลตฟอร์มซื้อขาย"""
        st.header("🎯 แพลตฟอร์มซื้อขาย")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📤 ส่งคำสั่งซื้อขาย")
            
            # เลือกหุ้น
            stock_list = DemoDataGenerator.get_stock_list()
            symbol_options = [f"{s['symbol']} - {s['name']}" for s in stock_list]
            selected_symbol = st.selectbox("เลือกหุ้น", symbol_options, key="order_symbol")
            symbol = selected_symbol.split(" - ")[0]
            
            # ประเภทคำสั่ง
            side = st.radio("ประเภทคำสั่ง", ["ซื้อ", "ขาย"], horizontal=True, key="order_side")
            
            # จำนวนและราคา
            col_qty, col_price = st.columns(2)
            
            with col_qty:
                quantity = st.number_input(
                    "จำนวนหุ้น",
                    min_value=1,
                    value=100,
                    step=100,
                    key="order_qty"
                )
            
            with col_price:
                price_type = st.selectbox("ประเภทราคา", ["ตลาด", "กำหนดราคา"], key="price_type")
                
                if price_type == "กำหนดราคา":
                    price = st.number_input(
                        "ราคาที่ต้องการ",
                        min_value=0.0,
                        value=0.0,
                        step=0.01,
                        format="%.2f",
                        key="order_price"
                    )
                else:
                    price = None
            
            # PIN
            pin = st.text_input("PIN การซื้อขาย", type="password", value="000000", key="order_pin")
            
            # ปุ่มส่ง (อยู่นอก form)
            if st.button("📤 ส่งคำสั่ง", type="primary", use_container_width=True, key="submit_order"):
                # ดึงราคาปัจจุบัน
                if st.session_state.get('demo_mode', True):
                    quote = DemoDataGenerator.generate_stock_quote(symbol)
                else:
                    if 'client' in st.session_state:
                        quote = st.session_state.client.get_stock_quote(symbol)
                    else:
                        quote = DemoDataGenerator.generate_stock_quote(symbol)
                
                if quote:
                    # คำนวณราคา
                    if price_type == "ตลาด" or price is None or price <= 0:
                        exec_price = quote['ask'] if side == "ซื้อ" else quote['bid']
                        price_type_display = "ตลาด"
                    else:
                        exec_price = price
                        price_type_display = "กำหนดราคา"
                    
                    order_value = quantity * exec_price
                    
                    # สร้างข้อมูลคำสั่ง
                    order_data = {
                        "order_id": f"ORD{int(time.time())}",
                        "symbol": symbol,
                        "name": quote['name'],
                        "side": side,
                        "quantity": quantity,
                        "price": exec_price,
                        "value": order_value,
                        "type": price_type_display,
                        "status": "รอการจับคู่",
                        "timestamp": datetime.now().strftime("%H:%M:%S")
                    }
                    
                    # เพิ่มใน session state
                    if 'orders' not in st.session_state:
                        st.session_state.orders = []
                    
                    st.session_state.orders.append(order_data)
                    st.success("✅ ส่งคำสั่งสำเร็จ!")
                    
                    # แสดงรายละเอียด
                    with st.expander("📋 รายละเอียดคำสั่ง", expanded=True):
                        st.json(order_data, expanded=False)
        
        with col2:
            st.subheader("📋 คำสั่งค้างอยู่")
            
            if 'orders' in st.session_state and st.session_state.orders:
                for idx, order in enumerate(st.session_state.orders[-5:]):  # แสดง 5 คำสั่งล่าสุด
                    with st.container():
                        st.write(f"**{order['order_id']}**")
                        
                        cols = st.columns(2)
                        cols[0].write(f"**{order['symbol']}** - {order['name']}")
                        cols[1].write(f"{order['side']} {order['quantity']:,} หุ้น")
                        
                        st.write(f"ราคา: ฿{order['price']:,.2f} | มูลค่า: ฿{order['value']:,.2f}")
                        st.write(f"สถานะ: `{order['status']}` | เวลา: {order['timestamp']}")
                        
                        # ปุ่มยกเลิก
                        if st.button(f"ยกเลิกคำสั่ง", key=f"cancel_{idx}"):
                            st.session_state.orders[idx]['status'] = "ยกเลิกแล้ว"
                            st.success(f"คำสั่ง {order['order_id']} ถูกยกเลิก")
                            st.rerun()
                        
                        st.divider()
            else:
                st.info("ไม่มีคำสั่งค้างอยู่")
            
            # Quick trading
            st.subheader("⚡ ซื้อขายด่วน")
            
            quick_symbols = ["AOT", "PTT", "ADVANC", "KBANK"]
            for sym in quick_symbols:
                col_buy, col_sell = st.columns(2)
                
                with col_buy:
                    if st.button(f"🛒 ซื้อ {sym}", key=f"quick_buy_{sym}", use_container_width=True):
                        if st.session_state.get('demo_mode', True):
                            quote = DemoDataGenerator.generate_stock_quote(sym)
                        else:
                            if 'client' in st.session_state:
                                quote = st.session_state.client.get_stock_quote(sym)
                            else:
                                quote = DemoDataGenerator.generate_stock_quote(sym)
                        
                        if quote:
                            order_data = {
                                "order_id": f"Q{int(time.time())}",
                                "symbol": sym,
                                "name": quote['name'],
                                "side": "ซื้อ",
                                "quantity": 100,
                                "price": quote['ask'],
                                "value": 100 * quote['ask'],
                                "type": "ตลาด",
                                "status": "รอการจับคู่",
                                "timestamp": datetime.now().strftime("%H:%M:%S")
                            }
                            
                            if 'orders' not in st.session_state:
                                st.session_state.orders = []
                            
                            st.session_state.orders.append(order_data)
                            st.success(f"สั่งซื้อ {sym} 100 หุ้น @ ฿{quote['ask']:,.2f}")
                
                with col_sell:
                    if st.button(f"💰 ขาย {sym}", key=f"quick_sell_{sym}", use_container_width=True):
                        if st.session_state.get('demo_mode', True):
                            quote = DemoDataGenerator.generate_stock_quote(sym)
                        else:
                            if 'client' in st.session_state:
                                quote = st.session_state.client.get_stock_quote(sym)
                            else:
                                quote = DemoDataGenerator.generate_stock_quote(sym)
                        
                        if quote:
                            order_data = {
                                "order_id": f"Q{int(time.time())}",
                                "symbol": sym,
                                "name": quote['name'],
                                "side": "ขาย",
                                "quantity": 100,
                                "price": quote['bid'],
                                "value": 100 * quote['bid'],
                                "type": "ตลาด",
                                "status": "รอการจับคู่",
                                "timestamp": datetime.now().strftime("%H:%M:%S")
                            }
                            
                            if 'orders' not in st.session_state:
                                st.session_state.orders = []
                            
                            st.session_state.orders.append(order_data)
                            st.success(f"สั่งขาย {sym} 100 หุ้น @ ฿{quote['bid']:,.2f}")

# -------------------------------------------------
# Main Application
# -------------------------------------------------
class SettradeApp:
    """แอปพลิเคชันหลัก"""
    
    def __init__(self):
        SessionManager.init_session()
        self.ui = UIComponents()
    
    def run(self):
        """รันแอปพลิเคชัน"""
        # Title
        st.title("📈 Settrade Trading Platform")
        
        # Check login status
        if not st.session_state.logged_in:
            self.ui.create_login_section()
            
            # Demo instructions
            st.info("💡 **สำหรับการทดสอบ:** ใช้ **Demo Mode** หรือใช้ **SANDBOX** สำหรับทุกช่อง")
            
            # Feature preview
            with st.expander("🚀 ดูฟีเจอร์ทั้งหมด", expanded=True):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**📊 ภาพรวมตลาด**")
                    st.write("- SET Index และดัชนี")
                    st.write("- หุ้นเด่นประจำวัน")
                    st.write("- กราฟตลาด")
                
                with col2:
                    st.write("**💼 การซื้อขาย**")
                    st.write("- วิเคราะห์หุ้น")
                    st.write("- จัดการพอร์ตโฟลิโอ")
                    st.write("- ส่งคำสั่งซื้อขาย")
                
                st.write("**🎯 คุณสมบัติพิเศษ**")
                st.write("- ข้อมูลแบบเรียลไทม์")
                st.write("- กราฟแบบอินเตอร์แอคทีฟ")
                st.write("- ระบบ Demo และ Live")
            
        else:
            # Display sidebar
            self.create_sidebar()
            
            # Display selected page
            self.display_page()
            
            # Footer
            self.create_footer()
    
    def create_sidebar(self):
        """สร้าง sidebar"""
        with st.sidebar:
            st.title("📊 เมนูหลัก")
            
            # User info
            if st.session_state.get('demo_mode', True):
                st.success("✅ DEMO MODE")
                st.info("""
                **บัญชี:** DEMO-ACCOUNT
                **เงินสด:** ฿1,000,000.00
                **สถานะ:** ใช้งานได้เต็มที่
                """)
            else:
                st.success("✅ LIVE MODE")
                st.info("เชื่อมต่อกับ Settrade API")
            
            st.divider()
            
            # Navigation
            page = st.radio(
                "เลือกหน้าที่ต้องการ",
                [
                    "🏠 ภาพรวมตลาด",
                    "📈 วิเคราะห์หุ้น",
                    "💼 พอร์ตโฟลิโอ",
                    "🎯 ซื้อขายหุ้น",
                    "📰 ข่าวสาร",
                    "⚙️ การตั้งค่า"
                ],
                key="navigation"
            )
            
            st.session_state.current_page = page
            
            st.divider()
            
            # Market stats
            st.subheader("📈 สถิติตลาด")
            st.metric("SET Index", "1,450.12", "+12.34")
            st.metric("มูลค่าตลาด", "18.2 ล้านล้าน", "+0.8%")
            st.metric("หุ้นขึ้น/ลง", "342/158", None)
            
            st.divider()
            
            # Quick actions
            st.subheader("⚡ ด่วน")
            if st.button("🔄 อัปเดตข้อมูล", use_container_width=True, key="refresh_data"):
                st.session_state.last_update = datetime.now()
                st.rerun()
            
            if st.button("🚪 ออกจากระบบ", use_container_width=True, key="logout"):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()
    
    def display_page(self):
        """แสดงหน้าที่เลือก"""
        page = st.session_state.get('current_page', '🏠 ภาพรวมตลาด')
        
        if page == "🏠 ภาพรวมตลาด":
            self.ui.create_market_overview()
        elif page == "📈 วิเคราะห์หุ้น":
            self.ui.create_stock_analysis()
        elif page == "💼 พอร์ตโฟลิโอ":
            self.ui.create_portfolio_view()
        elif page == "🎯 ซื้อขายหุ้น":
            self.ui.create_trading_platform()
        elif page == "📰 ข่าวสาร":
            self.create_news_page()
        else:
            self.create_settings_page()
    
    def create_news_page(self):
        """หน้าข่าวสาร"""
        st.header("📰 ข่าวสารตลาด")
        
        # Market news
        news_items = [
            {"time": "09:30", "title": "SET Index เปิดตลาดที่ 1,450.12 จุด", "impact": "+", "symbols": "SET"},
            {"time": "10:15", "title": "PTT ได้รับสัญญาก๊าซธรรมชาติใหม่", "impact": "+", "symbols": "PTT, GULF"},
            {"time": "11:30", "title": "นักลงทุนต่างชาติซื้อสุทธิ 1,200 ล้านบาท", "impact": "+", "symbols": "KBANK, SCB"},
            {"time": "13:45", "title": "AOT เตรียมขยายท่าอากาศยาน", "impact": "+", "symbols": "AOT"},
            {"time": "14:30", "title": "ADVANC รายงานยอดใช้งาน 5G เพิ่มขึ้น", "impact": "+", "symbols": "ADVANC, TRUE"},
        ]
        
        for news in news_items:
            with st.container():
                col1, col2 = st.columns([1, 4])
                
                with col1:
                    st.write(f"**{news['time']}**")
                
                with col2:
                    if news['impact'] == "+":
                        st.success(f"📈 {news['title']}")
                    else:
                        st.error(f"📉 {news['title']}")
                    
                    st.caption(f"เกี่ยวข้องกับ: {news['symbols']}")
                
                st.divider()
        
        # Economic calendar
        st.subheader("📅 ปฏิทินเศรษฐกิจ")
        
        events = [
            {"date": "15 ม.ค.", "event": "CPI (เดือนธ.ค.)", "forecast": "0.8%", "actual": "0.9%"},
            {"date": "18 ม.ค.", "event": "อัตราดอกเบี้ยนโยบาย", "forecast": "2.50%", "actual": "2.50%"},
            {"date": "25 ม.ค.", "event": "GDP ไตรมาส 4/2023", "forecast": "3.2%", "actual": "-"},
            {"date": "30 ม.ค.", "event": "ดุลการค้า", "forecast": "1.5B USD", "actual": "-"},
        ]
        
        df_events = pd.DataFrame(events)
        st.dataframe(df_events, use_container_width=True, hide_index=True)
    
    def create_settings_page(self):
        """หน้าการตั้งค่า"""
        st.header("⚙️ การตั้งค่า")
        
        tab1, tab2, tab3 = st.tabs(["โปรไฟล์", "การแจ้งเตือน", "เกี่ยวกับ"])
        
        with tab1:
            st.subheader("👤 โปรไฟล์ผู้ใช้")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.text_input("ชื่อผู้ใช้", value="sahaphum", disabled=True, key="profile_username")
                st.text_input("อีเมล", value="sahaphum@example.com", key="profile_email")
                st.text_input("เบอร์โทรศัพท์", value="081-234-5678", key="profile_phone")
            
            with col2:
                st.text_input("บัญชีหุ้น", value="sahaphum-E", disabled=True, key="profile_account")
                st.text_input("PIN การซื้อขาย", value="******", type="password", key="profile_pin")
            
            if st.button("บันทึกการเปลี่ยนแปลง", type="primary", key="save_profile"):
                st.success("✅ บันทึกการเปลี่ยนแปลงเรียบร้อยแล้ว")
        
        with tab2:
            st.subheader("🔔 การแจ้งเตือน")
            
            st.checkbox("แจ้งเตือนเมื่อราคาเปลี่ยนแปลงเกิน 5%", value=True, key="notif_price")
            st.checkbox("แจ้งเตือนข่าวสำคัญ", value=True, key="notif_news")
            st.checkbox("แจ้งเตือนเมื่อคำสั่งถูกดำเนินการ", value=True, key="notif_order")
            st.checkbox("แจ้งเตือนเมื่อพอร์ตเปลี่ยนแปลงเกิน 10%", value=True, key="notif_portfolio")
            
            st.divider()
            
            st.subheader("📧 ช่องทางการแจ้งเตือน")
            st.checkbox("อีเมล", value=True, key="channel_email")
            st.checkbox("แจ้งเตือนบนเว็บ", value=True, key="channel_web")
            
            if st.button("บันทึกการตั้งค่า", type="primary", key="save_notifications"):
                st.success("✅ บันทึกการตั้งค่าเรียบร้อยแล้ว")
        
        with tab3:
            st.subheader("ℹ️ เกี่ยวกับ")
            
            st.write("""
            ### Settrade Trading Platform
            
            **เวอร์ชัน:** 2.0.0
            **สถานะ:** """ + ("DEMO MODE" if st.session_state.get('demo_mode', True) else "LIVE MODE") + """
            **ผู้พัฒนา:** Sahaphum Team
            
            ### คุณสมบัติ:
            - 📊 ข้อมูลตลาดหุ้นแบบเรียลไทม์
            - 💼 การจัดการพอร์ตโฟลิโอ
            - 🎯 แพลตฟอร์มซื้อขายหุ้น
            - 📰 ข่าวสารและข้อมูลตลาด
            
            ### การสนับสนุน:
            ติดต่อ: support@sahaphum-trading.com
            """)
            
            if st.session_state.get('demo_mode', True):
                st.warning("⚠️ **หมายเหตุ:** ระบบกำลังใช้งานในโหมด Demo")
            
            # System info
            with st.expander("🖥️ ข้อมูลระบบ"):
                st.write(f"**เวลาปัจจุบัน:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                st.write(f"**สถานะการเชื่อมต่อ:** {'Demo Mode' if st.session_state.get('demo_mode', True) else 'Live Mode'}")
                st.write(f"**จำนวนคำสั่ง:** {len(st.session_state.get('orders', []))}")
    
    def create_footer(self):
        """สร้าง footer"""
        st.divider()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.caption("© 2024 Settrade Trading Platform")
        
        with col2:
            mode = "Demo" if st.session_state.get('demo_mode', True) else "Live"
            st.caption(f"🔄 โหมด: {mode}")
        
        with col3:
            update_time = st.session_state.last_update.strftime("%H:%M:%S")
            st.caption(f"🕒 อัปเดต: {update_time}")

# -------------------------------------------------
# Run the application
# -------------------------------------------------
if __name__ == "__main__":
    app = SettradeApp()
    app.run()