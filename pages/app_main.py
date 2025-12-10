import string
import streamlit as st
import snowflake.connector
import requests
import json
from datetime import datetime,timedelta
import time
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from prophet import Prophet
from prophet.plot import plot_plotly, plot_components_plotly
from prophet.diagnostics import cross_validation, performance_metrics
import re
import uuid
import altair as alt
import random
import boto3
import pandas as pd
from data_utils import get_oilprice_long




# ==============================
# 1. PAGE CONFIG & CUSTOM CSS
# ==============================
st.set_page_config(
    page_title="OILSOPHAENG | Oil Analytics Platform",
    page_icon="⛽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Light Blue Premium CSS Styling
st.markdown("""
<style>
    /* Light Blue Theme */
    :root {
        --primary: #1e88e5;
        --primary-light: #6ab7ff;
        --primary-dark: #005cb2;
        --secondary: #00acc1;
        --secondary-light: #5ddef4;
        --secondary-dark: #007c91;
        --accent: #29b6f6;
        --success: #00c853;
        --warning: #ff9100;
        --danger: #ff5252;
        --light-blue: #e3f2fd;
        --blue-50: #e3f2fd;
        --blue-100: #bbdefb;
        --blue-200: #90caf9;
        --blue-300: #64b5f6;
        --blue-400: #42a5f5;
        --gradient-primary: linear-gradient(135deg, #1e88e5 0%, #1976d2 100%);
        --gradient-secondary: linear-gradient(135deg, #00acc1 0%, #00838f 100%);
        --gradient-accent: linear-gradient(135deg, #29b6f6 0%, #0288d1 100%);
        --gradient-light: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
    }
    
    /* Main Container */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Headers */
    h1, h2, h3 {
        font-family: 'Segoe UI', 'SF Pro Display', -apple-system, BlinkMacSystemFont, sans-serif;
        font-weight: 600;
        color: var(--primary-dark);
        margin-bottom: 1.5rem;
    }
    
    h1 {
        background: linear-gradient(90deg, var(--primary), var(--secondary));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
        font-size: 2.5rem;
    }
    
    /* Premium Cards */
    .premium-card {
        background: white;
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 8px 30px rgba(30, 136, 229, 0.08);
        border: 1px solid var(--blue-100);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        margin-bottom: 1.5rem;
        position: relative;
        overflow: hidden;
    }
    
    .premium-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 4px;
        background: var(--gradient-primary);
    }
    
    .premium-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 20px 40px rgba(30, 136, 229, 0.15);
    }
    
    /* Glass Card */
    .glass-card {
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 8px 32px rgba(31, 38, 135, 0.1);
        padding: 2rem;
        margin-bottom: 1.5rem;
    }
    
    /* Chat Bubbles */
    .user-bubble {
        background: var(--gradient-primary);
        color: white;
        padding: 1.2rem 1.8rem;
        border-radius: 24px 24px 8px 24px;
        margin: 1rem 0;
        max-width: 80%;
        margin-left: auto;
        box-shadow: 0 6px 20px rgba(30, 136, 229, 0.2);
        position: relative;
    }
    
    .ai-bubble {
        background: white;
        color: var(--primary-dark);
        padding: 1.2rem 1.8rem;
        border-radius: 24px 24px 24px 8px;
        margin: 1rem 0;
        max-width: 80%;
        border-left: 6px solid var(--accent);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.06);
        position: relative;
    }
    
    .ai-bubble::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(135deg, rgba(41, 182, 246, 0.03) 0%, rgba(30, 136, 229, 0.03) 100%);
        z-index: -1;
        border-radius: inherit;
    }
    
    /* Buttons */
    .stButton > button {
        border-radius: 16px !important;
        padding: 0.85rem 2.5rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        border: none !important;
        font-size: 1rem !important;
        position: relative;
        overflow: hidden;
    }
    
    .stButton > button::after {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 5px;
        height: 5px;
        background: rgba(255, 255, 255, 0.5);
        opacity: 0;
        border-radius: 100%;
        transform: scale(1, 1) translate(-50%);
        transform-origin: 50% 50%;
    }
    
    .stButton > button:focus:not(:active)::after {
        animation: ripple 1s ease-out;
    }
    
    .primary-btn {
        background: var(--gradient-primary) !important;
        color: white !important;
    }
    
    .secondary-btn {
        background: var(--gradient-secondary) !important;
        color: white !important;
    }
    
    .light-btn {
        background: var(--gradient-light) !important;
        color: var(--primary-dark) !important;
        border: 2px solid var(--blue-200) !important;
    }
    
    /* Sidebar - Light Blue Theme */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #e3f2fd 0%, #bbdefb 100%);
        color: var(--primary-dark) !important;
        border-right: 1px solid var(--blue-200);
    }
    
    section[data-testid="stSidebar"] .stButton > button {
        background: rgba(255, 255, 255, 0.7) !important;
        color: var(--primary-dark) !important;
        border: 2px solid rgba(30, 136, 229, 0.1) !important;
        backdrop-filter: blur(10px);
        width: 100% !important;
        margin: 0.5rem 0 !important;
    }
    
    section[data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(255, 255, 255, 0.9) !important;
        border: 2px solid var(--primary-light) !important;
        transform: translateX(5px);
    }
    
    /* Input Fields */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        border-radius: 14px !important;
        border: 2px solid var(--blue-200) !important;
        padding: 1rem !important;
        transition: all 0.3s ease !important;
        background: white !important;
        font-size: 1rem !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 4px rgba(30, 136, 229, 0.15) !important;
        outline: none !important;
    }
    
    /* Badges */
    .badge {
        display: inline-block;
        padding: 0.5em 1.2em;
        font-size: 0.8em;
        font-weight: 700;
        line-height: 1;
        text-align: center;
        white-space: nowrap;
        vertical-align: baseline;
        border-radius: 50rem;
        letter-spacing: 0.5px;
    }
    
    .badge-premium {
        background: var(--gradient-secondary);
        color: white;
        box-shadow: 0 4px 15px rgba(0, 172, 193, 0.3);
    }
    
    .badge-free {
        background: var(--gradient-accent);
        color: white;
        box-shadow: 0 4px 15px rgba(41, 182, 246, 0.3);
    }
    
    /* Metrics */
    .metric-card {
        background: white;
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 8px 25px rgba(30, 136, 229, 0.08);
        text-align: center;
        border-top: 6px solid var(--primary);
        transition: transform 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
    }
    
    .metric-value {
        font-size: 2.8rem;
        font-weight: 700;
        background: linear-gradient(90deg, var(--primary), var(--secondary));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0.5rem 0;
        line-height: 1;
    }
    
    .metric-label {
        font-size: 0.95rem;
        color: var(--primary-dark);
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 600;
        opacity: 0.8;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
        border-bottom: 2px solid var(--blue-100);
        padding-bottom: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 60px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 16px;
        gap: 1rem;
        padding: 1rem 2rem;
        font-weight: 600;
        color: var(--primary-dark);
        transition: all 0.3s ease;
        border: 2px solid transparent;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: var(--blue-50);
        border-color: var(--blue-200);
    }
    
    .stTabs [aria-selected="true"] {
        background: var(--gradient-primary) !important;
        color: white !important;
        border-color: var(--primary) !important;
    }
    
    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(30px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }
    
    @keyframes ripple {
        0% { transform: scale(0, 0); opacity: 1; }
        20% { transform: scale(25, 25); opacity: 1; }
        100% { opacity: 0; transform: scale(40, 40); }
    }
    
    @keyframes shimmer {
        0% { background-position: -1000px 0; }
        100% { background-position: 1000px 0; }
    }
    
    .fade-in {
        animation: fadeIn 0.6s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .float-animation {
        animation: float 3s ease-in-out infinite;
    }
    
    /* Loading Animation */
    .loading-dots::after {
        content: '⠋';
        animation: dots 1.5s steps(5, end) infinite;
        display: inline-block;
        width: 1em;
        text-align: left;
    }
    
    @keyframes dots {
        0%, 20% { content: '⠋'; }
        40% { content: '⠙'; }
        60% { content: '⠹'; }
        80% { content: '⠸'; }
        100% { content: '⠼'; }
    }
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--blue-50);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--primary-light);
        border-radius: 10px;
        border: 2px solid var(--blue-50);
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--primary);
    }
    
    /* Selection Color */
    ::selection {
        background-color: var(--primary-light);
        color: white;
    }
    
    /* Form Styling */
    .stForm {
        background: white;
        padding: 2.5rem;
        border-radius: 24px;
        box-shadow: 0 10px 40px rgba(30, 136, 229, 0.1);
        border: 1px solid var(--blue-100);
    }
    
    /* Divider */
    .divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, var(--blue-200), transparent);
        margin: 2rem 0;
    }
    
    /* Tag/Pill */
    .pill {
        display: inline-block;
        padding: 0.5rem 1.2rem;
        background: var(--blue-50);
        color: var(--primary-dark);
        border-radius: 50px;
        font-size: 0.9rem;
        font-weight: 500;
        margin: 0.25rem;
        border: 1px solid var(--blue-200);
        transition: all 0.3s ease;
    }
    
    .pill:hover {
        background: var(--blue-100);
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(30, 136, 229, 0.15);
    }
    
    /* Feature Cards */
    .feature-card {
        display: flex;
        align-items: center;
        margin-bottom: 1.5rem;
    }
    
    .feature-icon {
        width: 50px;
        height: 50px;
        border-radius: 14px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 1rem;
        font-size: 1.5rem;
    }
    
    .feature-content {
        flex: 1;
    }
    
    .feature-title {
        font-weight: 600;
        color: var(--primary-dark);
        margin-bottom: 0.25rem;
    }
    
    .feature-desc {
        font-size: 0.9rem;
        color: var(--secondary-dark);
    }
    
    /* Text Styling */
    .login-text {
        color: var(--secondary-dark);
        margin-bottom: 2rem;
        font-size: 1rem;
        line-height: 1.5;
    }
</style>
""", unsafe_allow_html=True)

# ==============================
# 2. SESSION STATE INIT
# ==============================
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_name' not in st.session_state:
    st.session_state['user_name'] = ""
if 'subscribe_flag' not in st.session_state:
    st.session_state['subscribe_flag'] = 0
if 'current_page' not in st.session_state:
    st.session_state['current_page'] = "dashboard"
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []
# เพิ่มค่านี้ด้วย
if 'show_create_account' not in st.session_state:
    st.session_state['show_create_account'] = False  # เพิ่มบรรทัดนี้

# ==============================
# 3. UTILITY FUNCTIONS
# ==============================
def show_feature_cards():
    """แสดงฟีเจอร์ต่าง ๆ ในรูปแบบ card"""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon" style="background: var(--gradient-primary); color: white;">
                📊
            </div>
            <div class="feature-content">
                <div class="feature-title">วิเคราะห์แบบเรียลไทม์</div>
                <div class="feature-desc">ข้อมูลน้ำมันล่าสุดทุกวัน</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon" style="background: var(--gradient-secondary); color: white;">
                🤖
            </div>
            <div class="feature-content">
                <div class="feature-title">AI Assistant</div>
                <div class="feature-desc">ตอบคำถามเกี่ยวกับตลาดน้ำมัน</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon" style="background: var(--gradient-accent); color: white;">
                📈
            </div>
            <div class="feature-content">
                <div class="feature-title">พยากรณ์แนวโน้ม</div>
                <div class="feature-desc">คาดการณ์ราคาล่วงหน้า 30 วัน</div>
            </div>
        </div>
        """, unsafe_allow_html=True)


def premium_card(title, content, icon=None, color="primary"):
    """Premium card component"""
    colors = {
        "primary": "linear-gradient(135deg, #1e88e5 0%, #1976d2 100%)",
        "secondary": "linear-gradient(135deg, #00acc1 0%, #00838f 100%)",
        "accent": "linear-gradient(135deg, #29b6f6 0%, #0288d1 100%)"
    }
    
    # แก้ไข: ใช้ f-string ที่ถูกต้องและแยก HTML ออก
    icon_html = ""
    if icon:
        icon_html = f'<span style="font-size: 2.2rem; margin-right: 1rem; background: {colors[color]}; -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{icon}</span>'
    
    st.markdown(f"""
    <div class="premium-card fade-in">
        <div style="display: flex; align-items: center; margin-bottom: 1.5rem;">
            {icon_html}
            <h3 style="margin: 0; color: var(--primary-dark); font-weight: 600; font-size: 1.5rem;">
                {title}
            </h3>
        </div>
        {content}
    </div>
    """, unsafe_allow_html=True)

def metric_card(value, label, icon=None, trend=None, trend_value=None):
    """Metric card component"""
    trend_html = ""
    if trend:
        trend_color = "#00c853" if trend == "up" else "#ff5252" if trend == "down" else "#29b6f6"
        trend_icon = "📈" if trend == "up" else "📉" if trend == "down" else "➡️"
        trend_text = f'{trend_value if trend_value else trend}'
        trend_html = f'<div style="color: {trend_color}; font-size: 0.9rem; margin-top: 0.75rem; font-weight: 600;">{trend_icon} {trend_text}</div>'
    
    icon_html = f'<div style="font-size: 2rem; margin-bottom: 1rem; color: var(--primary);">{icon if icon else ""}</div>' if icon else ""
    
    st.markdown(f"""
    <div class="metric-card fade-in">
        {icon_html}
        <div class="metric-value">{value}</div>
        <div class="metric-label">{label}</div>
        {trend_html}
    </div>
    """, unsafe_allow_html=True)

def glass_card(content):
    """Glassmorphism card"""
    st.markdown(f"""
    <div class="glass-card fade-in">
        {content}
    </div>
    """, unsafe_allow_html=True)

# ==============================
# 4. AUTH FUNCTIONS
# ==============================
def logoff():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.cache_data.clear()
    st.cache_resource.clear()
    st.session_state['logged_in'] = False
    st.session_state['user_name'] = ""
    st.session_state['subscribe_flag'] = 0
    st.session_state['current_page'] = "dashboard"
    st.session_state['chat_history'] = []
    st.rerun()

def go_to_package():
    st.session_state['current_page'] = "package"
    st.rerun()

def go_to_home():
    st.session_state['current_page'] = "dashboard"
    st.rerun()

def register_pro():
    username = st.session_state['user_name']
    try:
        sf_cfg = st.secrets["connections"]["snowflake"]
        conn = snowflake.connector.connect(
            user=sf_cfg["user"],
            password=sf_cfg["password"],
            account=sf_cfg["account"],
            warehouse=sf_cfg["warehouse"],
            database=sf_cfg["database"],
            schema=sf_cfg["schema"]
        )
        cursor = conn.cursor()
        update_query = f"UPDATE users SET subscribe_flag = 1 WHERE username = '{username}'"
        cursor.execute(update_query)
        conn.commit()
        st.session_state['subscribe_flag'] = 1
        st.session_state['current_page'] = "dashboard"
        cursor.close()
        conn.close()
        st.success("✨ อัปเกรดเป็น PRO สำเร็จ!")
    except Exception as e:
        st.error(f"❌ เกิดข้อผิดพลาด: {str(e)}")
    st.rerun()

def login_user(user_name, subscribe_flag=0):
    st.session_state['logged_in'] = True
    st.session_state['user_name'] = user_name
    st.session_state['subscribe_flag'] = subscribe_flag
    st.session_state['current_page'] = "dashboard"
    st.rerun()

# ==============================
# 5. PREMIUM PAGES
# ==============================

def show_premium_login():
    """Premium login page"""
    col1, col2 = st.columns([1, 1.2])
    
    with col1:
        st.markdown("""
        <div style="padding: 4rem 2rem;">
            <div class="float-animation" style="font-size: 4rem; margin-bottom: 1rem; text-align: center;">⛽</div>
            <h1 style="text-align: center; margin-bottom: 1.5rem;">OILSOPHAENG</h1>
            <p style="text-align: center; color: var(--primary-dark); font-size: 1.2rem; line-height: 1.6; margin-bottom: 3rem;">
                <strong>Oil Analytics Platform</strong><br>
                ระบบวิเคราะห์ข้อมูลน้ำมันอัจฉริยะ
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # ใช้ฟังก์ชันที่สร้างไว้
        show_feature_cards()
    
    with col2:
        # สร้าง tab ภายใน column ที่สอง
        tab_login, tab_register = st.tabs(["🔐 เข้าสู่ระบบ", "📝 สร้างบัญชีใหม่"])
        
        with tab_login:
            show_login_form()
        
        with tab_register:
            show_register_form()


def show_login_form():
    """แสดงฟอร์มเข้าสู่ระบบ"""
    st.markdown("""
    
    <div class="premium-card fade-in">
        <div style="display: flex; align-items: center; margin-bottom: 1.5rem;">
            <span style="font-size: 2.2rem; margin-right: 1rem; background: linear-gradient(135deg, #29b6f6 0%, #0288d1 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">🔐</span>
            <h3 style="margin: 0; color: var(--primary-dark); font-weight: 600; font-size: 1.5rem;">
                เข้าสู่ระบบ
            </h3>
        </div>
        <div style="margin-top: 1rem;">
            <p class="login-text">เข้าสู่ระบบเพื่อใช้งานระบบวิเคราะห์ข้อมูลน้ำมัน</p>
        </div>
    """, unsafe_allow_html=True)
    
 
    with st.form("login_form", clear_on_submit=False):
        username = st.text_input(
            "ชื่อผู้ใช้",
            placeholder="กรอกชื่อผู้ใช้",
            key="login_username"
        )
        
        password = st.text_input(
            "รหัสผ่าน", 
            placeholder="กรอกรหัสผ่าน",
            type="password",
            key="login_password"
        )
        
        submit = st.form_submit_button(
            "🚀 เข้าสู่ระบบ",
            use_container_width=True,
            
        )
        
        if submit:
            if not username or not password:
                st.error("โปรดกรอกชื่อผู้ใช้และรหัสผ่าน")
            else:
                username_safe = username.replace("'", "''")
                query = f"""
                    SELECT 
                        USER_ID,
                        USERNAME, 
                        PASSWORD, 
                        EMAIL, 
                        FULL_NAME, 
                        COMPANY, 
                        PHONE,
                        ADDRESS,
                        SUBSCRIPTION_PLAN,
                        SUBSCRIPTION_STATUS,
                        IS_ACTIVE
                    FROM users
                    WHERE USERNAME = '{username_safe}'
                    LIMIT 1
                """
                
                try:
                    # ใช้ Snowflake connector โดยตรง
                    sf = st.secrets["connections"]["snowflake"]
                    
                    # เชื่อมต่อกับ Snowflake
                    snowflake_conn = snowflake.connector.connect(
                        account=sf["account"],
                        user=sf["user"],
                        password=sf["password"],
                        role=sf["role"],
                        warehouse=sf["warehouse"],
                        database=sf["database"],
                        schema=sf["schema"]
                    )
                    
                    cursor = snowflake_conn.cursor()
                    
                    try:
                        # Execute SELECT query
                        cursor.execute(query)
                        result = cursor.fetchone()
                        
                        if not result:
                            st.error("ไม่พบผู้ใช้งานนี้")
                        else:
                            # ดึงข้อมูลจาก result
                            user_id = result[0]
                            db_user = result[1]
                            db_pass = result[2]
                            email = result[3]
                            full_name = result[4]
                            company = result[5]
                            phone = result[6]
                            address = result[7]
                            subscription_plan = result[8]
                            subscription_status = result[9]
                            is_active = result[10]
                            
                            # ตรวจสอบสถานะผู้ใช้
                            if not is_active:
                                st.error("❌ บัญชีนี้ถูกระงับการใช้งาน")
                                return
                            
                            if password == db_pass:
                                with st.spinner("กำลังเข้าสู่ระบบ..."):
                                    time.sleep(1)
                                    
                                    # ตั้งค่า session state
                                    st.session_state['logged_in'] = True
                                    st.session_state['user_id'] = user_id
                                    st.session_state['user_name'] = username
                                    st.session_state['user_email'] = email
                                    st.session_state['user_fullname'] = full_name
                                    st.session_state['user_company'] = company if company else ""
                                    st.session_state['user_phone'] = phone if phone else ""
                                    st.session_state['user_address'] = address if address else ""
                                    st.session_state['subscription_plan'] = subscription_plan
                                    st.session_state['subscription_status'] = subscription_status
                                    st.session_state['current_page'] = "dashboard"
                                    
                                    # ตั้งค่า subscribe_flag ตาม subscription_plan
                                    plan_mapping = {'FREE': 0, 'PRO': 1, 'ENTERPRISE': 2}
                                    st.session_state['subscribe_flag'] = plan_mapping.get(subscription_plan, 0)
                                    
                                    st.success(f"✅ เข้าสู่ระบบสำเร็จ! ยินดีต้อนรับ {full_name}")
                                    
                                    # อัปเดตเวลาเข้าสู่ระบบล่าสุด
                                    update_query = f"""
                                    UPDATE users 
                                    SET UPDATED_AT = CURRENT_TIMESTAMP()
                                    WHERE USER_ID = '{user_id}'
                                    """
                                    
                                    # Execute UPDATE query
                                    cursor.execute(update_query)
                                    snowflake_conn.commit()
                                    
                                    time.sleep(1)
                                    st.rerun()
                            else:
                                st.error("รหัสผ่านไม่ถูกต้อง")
                    
                    finally:
                        cursor.close()
                        snowflake_conn.close()
                        
                except Exception as e:
                    st.error(f"เกิดข้อผิดพลาด: {e}")
                    import traceback
                    st.code(traceback.format_exc())
    
    st.markdown("</div>", unsafe_allow_html=True)

def show_register_form():
    """แสดงฟอร์มสร้างบัญชี"""
    st.markdown("""
    <div class="premium-card fade-in">
        <div style="display: flex; align-items: center; margin-bottom: 1.5rem;">
            <span style="font-size: 2.2rem; margin-right: 1rem; background: linear-gradient(135deg, #00acc1 0%, #00838f 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">📝</span>
            <h3 style="margin: 0; color: var(--primary-dark); font-weight: 600; font-size: 1.5rem;">
                สร้างบัญชีใหม่
            </h3>
        </div>
        <div style="margin-top: 1rem;">
            <p class="login-text">กรอกข้อมูลเพื่อสร้างบัญชีผู้ใช้ใหม่</p>
        </div>
    """, unsafe_allow_html=True)
    
    with st.form("register_form", clear_on_submit=True):
        # ข้อมูลส่วนตัว
        col1, col2 = st.columns(2)
        with col1:
            first_name = st.text_input("ชื่อ *", placeholder="กรอกชื่อจริง")
        with col2:
            last_name = st.text_input("นามสกุล *", placeholder="กรอกนามสกุล")
        
        st.markdown("---")
        
        # ข้อมูลติดต่อ
        col3, col4 = st.columns(2)
        with col3:
            email = st.text_input("อีเมล *", placeholder="example@email.com")
        with col4:
            phone = st.text_input("เบอร์โทรศัพท์ *", placeholder="089-123-4567")
        
        st.markdown("---")
        
        # ข้อมูลที่อยู่
        address = st.text_area("ที่อยู่", placeholder="กรอกที่อยู่ของคุณ", height=100,
                             help="บ้านเลขที่, หมู่บ้าน, ถนน, ตำบล, อำเภอ, จังหวัด, รหัสไปรษณีย์")
        
        st.markdown("---")
        
        # ข้อมูลบริษัท
        company = st.text_input("บริษัท/องค์กร", placeholder="กรอกชื่อบริษัทของคุณ (ถ้ามี)")
        
        st.markdown("---")
        
        # ข้อมูลเข้าสู่ระบบ
        username = st.text_input("ชื่อผู้ใช้ *", placeholder="กรอกชื่อผู้ใช้",
                               help="ชื่อผู้ใช้ควรมีความยาว 4-20 ตัวอักษร, ใช้ได้เฉพาะ a-z, 0-9, _")
        
        col5, col6 = st.columns(2)
        with col5:
            password = st.text_input("รหัสผ่าน *", type="password", 
                                   help="รหัสผ่านควรมีความยาวอย่างน้อย 8 ตัวอักษร")
        with col6:
            confirm_password = st.text_input("ยืนยันรหัสผ่าน *", type="password")
        
        # เงื่อนไข
        agree_terms = st.checkbox("✅ ฉันยอมรับข้อกำหนดและเงื่อนไขการให้บริการ")
        
        # ปุ่ม
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            submit = st.form_submit_button("✨ สร้างบัญชี", use_container_width=True)
        with col_btn2:
            cancel_btn = st.form_submit_button("← ยกเลิก", use_container_width=True)
            if cancel_btn:
                st.info("การสร้างบัญชีถูกยกเลิก")
        
        if submit:
            # ตรวจสอบข้อมูล
            errors = []
            
            # ตรวจสอบข้อมูลที่จำเป็น
            required_fields = {
                "ชื่อ": first_name,
                "นามสกุล": last_name,
                "อีเมล": email,
                "เบอร์โทรศัพท์": phone,
                "ชื่อผู้ใช้": username,
                "รหัสผ่าน": password
            }
            
            for field_name, field_value in required_fields.items():
                if not field_value or field_value.strip() == "":
                    errors.append(f"กรุณากรอก{field_name}")
            
            # ตรวจสอบ username format
            username_pattern = r'^[a-zA-Z0-9_]{4,20}$'
            if username and not re.match(username_pattern, username):
                errors.append("ชื่อผู้ใช้ควรมีความยาว 4-20 ตัวอักษร, ใช้ได้เฉพาะ a-z, 0-9, _")
            
            # ตรวจสอบรหัสผ่าน
            if password != confirm_password:
                errors.append("รหัสผ่านไม่ตรงกัน")
            
            if len(password) < 8:
                errors.append("รหัสผ่านควรมีความยาวอย่างน้อย 8 ตัวอักษร")
            
            if not agree_terms:
                errors.append("กรุณายอมรับข้อกำหนดและเงื่อนไข")
            
            # ตรวจสอบอีเมล format
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if email and not re.match(email_pattern, email):
                errors.append("รูปแบบอีเมลไม่ถูกต้อง")
            
            # ตรวจสอบเบอร์โทรศัพท์
            phone_pattern = r'^[0-9\-\+\(\)\s]{10,20}$'
            if phone and not re.match(phone_pattern, phone.replace(" ", "")):
                errors.append("รูปแบบเบอร์โทรศัพท์ไม่ถูกต้อง")
            
            if errors:
                for error in errors:
                    st.error(f"❌ {error}")
            else:
                try:
                    # เชื่อมต่อฐานข้อมูล
                    conn = st.connection("snowflake", type="snowflake")
                    
                    # ตรวจสอบว่ามี username ซ้ำหรือไม่
                    check_username_query = f"""
                    SELECT COUNT(*) as count 
                    FROM users 
                    WHERE USERNAME = '{username.replace("'", "''")}'
                    """
                    
                    # ตรวจสอบว่ามี email ซ้ำหรือไม่
                    check_email_query = f"""
                    SELECT COUNT(*) as count 
                    FROM users 
                    WHERE EMAIL = '{email.replace("'", "''")}'
                    """
                    
                    check_username_df = conn.query(check_username_query)
                    check_email_df = conn.query(check_email_query)
                    
                    if check_username_df.iloc[0]['COUNT'] > 0:
                        st.error("❌ ชื่อผู้ใช้นี้มีผู้ใช้งานแล้ว กรุณาใช้ชื่อผู้ใช้อื่น")
                    elif check_email_df.iloc[0]['COUNT'] > 0:
                        st.error("❌ อีเมลนี้มีผู้ใช้งานแล้ว กรุณาใช้อีเมลอื่น")
                    else:
                        # สร้าง ID และ full name
                        user_id = str(uuid.uuid4())
                        full_name = f"{first_name} {last_name}"
                        
                        # เตรียมค่า company
                        if not company or company.strip() == '':
                            company_value = "NULL"
                        else:
                            company_safe = company.replace("'", "''")
                            company_value = f"'{company_safe}'"
                        
                        # เตรียมค่า address
                        if not address or address.strip() == '':
                            address_value = "NULL"
                        else:
                            address_safe = address.replace("'", "''")
                            address_value = f"'{address_safe}'"
                        
                        # สร้าง INSERT query
                        insert_query = f"""
                        INSERT INTO users (
                            USER_ID,
                            USERNAME, 
                            PASSWORD, 
                            EMAIL, 
                            FULL_NAME, 
                            COMPANY, 
                            PHONE,
                            ADDRESS,
                            SUBSCRIPTION_PLAN,
                            SUBSCRIPTION_STATUS,
                            IS_ACTIVE,
                            CREATED_AT,
                            UPDATED_AT
                        ) VALUES (
                            '{user_id}',
                            '{username.replace("'", "''")}',
                            '{password.replace("'", "''")}',
                            '{email.replace("'", "''")}',
                            '{full_name.replace("'", "''")}',
                            {company_value},
                            '{phone.replace("'", "''")}',
                            {address_value},
                            'FREE',
                            'ACTIVE',
                            TRUE,
                            CURRENT_TIMESTAMP(),
                            CURRENT_TIMESTAMP()
                        )
                        """
                        
                        # Debug: แสดง query สำหรับตรวจสอบ
                        st.write("**Debug - Query ที่จะส่งไป:**")
                        st.code(insert_query, language='sql')
                        
                        # Execute query
                        result = conn.query(insert_query)
                        
                        st.success("🎉 สร้างบัญชีสำเร็จ!")
                        st.balloons()
                        
                        # อัตโนมัติเข้าสู่ระบบ
                        st.session_state['logged_in'] = True
                        st.session_state['user_id'] = user_id
                        st.session_state['user_name'] = username
                        st.session_state['user_email'] = email
                        st.session_state['user_fullname'] = full_name
                        st.session_state['user_company'] = company if company else ""
                        st.session_state['user_phone'] = phone
                        st.session_state['user_address'] = address if address else ""
                        st.session_state['subscription_plan'] = "FREE"
                        st.session_state['subscription_status'] = "ACTIVE"
                        st.session_state['current_page'] = "dashboard"
                        
                        # แสดงข้อมูล
                        st.info(f"""
                        **ข้อมูลบัญชีของคุณ:**
                        - ชื่อ: {full_name}
                        - อีเมล: {email}
                        - เบอร์โทร: {phone}
                        - ที่อยู่: {address if address else 'ไม่ระบุ'}
                        - บริษัท: {company if company else 'ไม่ระบุ'}
                        - ชื่อผู้ใช้: {username}
                        - แพ็คเกจ: FREE
                        - สถานะ: ACTIVE
                        
                        กำลังเข้าสู่ระบบอัตโนมัติ...
                        """)
                        
                        time.sleep(3)
                        st.rerun()
                        
                except Exception as e:
                    st.error(f"เกิดข้อผิดพลาดในการสร้างบัญชี: {str(e)}")
                    import traceback
                    st.error("**Traceback สำหรับ debugging:**")
                    st.code(traceback.format_exc())
                    
                    # แสดงข้อมูลสำหรับ debugging
                    st.error("**ข้อมูลที่พยายามบันทึก:**")
                    st.write(f"Username: {username}")
                    st.write(f"Email: {email}")
                    st.write(f"Full Name: {full_name}")
                    st.write(f"Company: {company}")
                    st.write(f"Phone: {phone}")
                    st.write(f"Address: {address}")
                    st.write(f"Company Value: {company_value}")
                    st.write(f"Address Value: {address_value}")
    
    st.markdown("</div>", unsafe_allow_html=True)

def show_user_profile():
    """แสดงโปรไฟล์ผู้ใช้"""
    if not st.session_state.get('logged_in'):
        st.warning("กรุณาเข้าสู่ระบบก่อน")
        return
    
    st.markdown("""
    <div class="premium-card">
        <h2 style="color: var(--primary-dark); margin-bottom: 2rem;">👤 โปรไฟล์ผู้ใช้</h2>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ข้อมูลส่วนตัว")
        st.write(f"**ชื่อ-นามสกุล:** {st.session_state.get('user_fullname', '')}")
        st.write(f"**อีเมล:** {st.session_state.get('user_email', '')}")
        st.write(f"**เบอร์โทร:** {st.session_state.get('user_phone', '')}")
        
        if st.session_state.get('user_address'):
            st.write(f"**ที่อยู่:**")
            st.write(st.session_state.get('user_address'))
    
    with col2:
        st.markdown("### ข้อมูลบัญชี")
        st.write(f"**ชื่อผู้ใช้:** {st.session_state.get('user_name', '')}")
        st.write(f"**บริษัท:** {st.session_state.get('user_company', 'ไม่ระบุ')}")
        
        subscription_plan = st.session_state.get('subscription_plan', 'FREE')
        subscription_status = st.session_state.get('subscription_status', 'ACTIVE')
        
        # สีตามสถานะ subscription
        status_color = "🟢" if subscription_status == "ACTIVE" else "🔴"
        plan_color = "🟡" if subscription_plan == "FREE" else "🟣"
        
        st.write(f"**แพ็คเกจ:** {plan_color} {subscription_plan}")
        st.write(f"**สถานะ:** {status_color} {subscription_status}")
    
    st.markdown("</div>", unsafe_allow_html=True)


# ฟังก์ชันสำหรับตรวจสอบการเข้าสู่ระบบ
def is_logged_in():
    """ตรวจสอบว่าผู้ใช้เข้าสู่ระบบแล้วหรือไม่"""
    return st.session_state.get('logged_in', False)


# ฟังก์ชันสำหรับออกจากระบบ
def logout_user():
    """ออกจากระบบผู้ใช้"""
    st.session_state['logged_in'] = False
    st.session_state['user_name'] = None
    st.session_state['user_id'] = None
    st.session_state['user_email'] = None
    st.session_state['user_fullname'] = None
    st.session_state['user_company'] = None
    st.session_state['user_phone'] = None
    st.session_state['user_address'] = None
    st.session_state['subscription_plan'] = None
    st.session_state['subscription_status'] = None
    st.session_state['current_page'] = "login"
    st.rerun()


# ฟังก์ชันสำหรับอัปเดตโปรไฟล์
def update_user_profile():
    """อัปเดตข้อมูลโปรไฟล์ผู้ใช้"""
    if not st.session_state.get('logged_in'):
        st.warning("กรุณาเข้าสู่ระบบก่อน")
        return
    
    conn = st.connection("snowflake", type="snowflake")
    
    with st.form("update_profile_form"):
        st.markdown("### แก้ไขข้อมูลโปรไฟล์")
        
        # แบ่งชื่อและนามสกุล
        full_name = st.session_state.get('user_fullname', '')
        name_parts = full_name.split(' ', 1)
        first_name = name_parts[0] if len(name_parts) > 0 else ''
        last_name = name_parts[1] if len(name_parts) > 1 else ''
        
        col1, col2 = st.columns(2)
        with col1:
            new_first_name = st.text_input("ชื่อ", value=first_name)
        with col2:
            new_last_name = st.text_input("นามสกุล", value=last_name)
        
        new_email = st.text_input("อีเมล", value=st.session_state.get('user_email', ''))
        new_phone = st.text_input("เบอร์โทรศัพท์", value=st.session_state.get('user_phone', ''))
        new_address = st.text_area("ที่อยู่", value=st.session_state.get('user_address', ''), height=100)
        new_company = st.text_input("บริษัท", value=st.session_state.get('user_company', ''))
        
        submit = st.form_submit_button("💾 บันทึกการเปลี่ยนแปลง")
        
        if submit:
            new_full_name = f"{new_first_name} {new_last_name}"
            user_id = st.session_state.get('user_id')
            
            update_query = f"""
            UPDATE users 
            SET 
                FULL_NAME = '{new_full_name.replace("'", "''")}',
                EMAIL = '{new_email.replace("'", "''")}',
                PHONE = '{new_phone.replace("'", "''")}',
                ADDRESS = {new_address.replace("'", "''")}',
                COMPANY = {new_company.replace("'", "''")}',
                UPDATED_AT = CURRENT_TIMESTAMP()
            WHERE USER_ID = '{user_id}'
            """
            
            try:
                conn.query(update_query)
                
                # อัปเดต session state
                st.session_state['user_fullname'] = new_full_name
                st.session_state['user_email'] = new_email
                st.session_state['user_phone'] = new_phone
                st.session_state['user_address'] = new_address
                st.session_state['user_company'] = new_company
                
                st.success("✅ อัปเดตโปรไฟล์สำเร็จ!")
                time.sleep(1)
                st.rerun()
                
            except Exception as e:
                st.error(f"เกิดข้อผิดพลาดในการอัปเดต: {str(e)}")





def show_register_form():
    """แสดงฟอร์มสร้างบัญชี"""
    st.markdown("""
    <div class="premium-card fade-in">
        <div style="display: flex; align-items: center; margin-bottom: 1.5rem;">
            <span style="font-size: 2.2rem; margin-right: 1rem; background: linear-gradient(135deg, #00acc1 0%, #00838f 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">📝</span>
            <h3 style="margin: 0; color: var(--primary-dark); font-weight: 600; font-size: 1.5rem;">
                สร้างบัญชีใหม่
            </h3>
        </div>
        <div style="margin-top: 1rem;">
            <p class="login-text">กรอกข้อมูลเพื่อสร้างบัญชีผู้ใช้ใหม่</p>
        </div>
    """, unsafe_allow_html=True)
    
    with st.form("register_form", clear_on_submit=True):
        # ข้อมูลส่วนตัว
        col1, col2 = st.columns(2)
        with col1:
            first_name = st.text_input("ชื่อ *", placeholder="กรอกชื่อจริง")
        with col2:
            last_name = st.text_input("นามสกุล *", placeholder="กรอกนามสกุล")
        
        st.markdown("---")
        
        # ข้อมูลติดต่อ
        col3, col4 = st.columns(2)
        with col3:
            email = st.text_input("อีเมล *", placeholder="example@email.com")
        with col4:
            phone = st.text_input("เบอร์โทรศัพท์ *", placeholder="089-123-4567")
        
        st.markdown("---")
        
        # ข้อมูลที่อยู่
        address = st.text_area("ที่อยู่", placeholder="กรอกที่อยู่ของคุณ", height=100,
                             help="บ้านเลขที่, หมู่บ้าน, ถนน, ตำบล, อำเภอ, จังหวัด, รหัสไปรษณีย์")
        
        st.markdown("---")
        
        # ข้อมูลบริษัท
        company = st.text_input("บริษัท/องค์กร", placeholder="กรอกชื่อบริษัทของคุณ (ถ้ามี)")
        
        st.markdown("---")
        
        # ข้อมูลเข้าสู่ระบบ
        username = st.text_input("ชื่อผู้ใช้ *", placeholder="กรอกชื่อผู้ใช้",
                               help="ชื่อผู้ใช้ควรมีความยาว 4-20 ตัวอักษร, ใช้ได้เฉพาะ a-z, 0-9, _")
        
        col5, col6 = st.columns(2)
        with col5:
            password = st.text_input("รหัสผ่าน *", type="password", 
                                   help="รหัสผ่านควรมีความยาวอย่างน้อย 8 ตัวอักษร")
        with col6:
            confirm_password = st.text_input("ยืนยันรหัสผ่าน *", type="password")
        
        # เงื่อนไข
        agree_terms = st.checkbox("✅ ฉันยอมรับข้อกำหนดและเงื่อนไขการให้บริการ")
        
        # ปุ่ม
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            submit_btn = st.form_submit_button("✨ สร้างบัญชี", use_container_width=True)
        with col_btn2:
            cancel_btn = st.form_submit_button("← ยกเลิก", use_container_width=True)
    
    # ตรวจสอบเมื่อกด submit
    if submit_btn:
        # Validate inputs
        errors = []
        
        # ตรวจสอบข้อมูลที่จำเป็น
        required_fields = {
            "ชื่อ": first_name,
            "นามสกุล": last_name,
            "อีเมล": email,
            "เบอร์โทรศัพท์": phone,
            "ชื่อผู้ใช้": username,
            "รหัสผ่าน": password
        }
        
        for field_name, field_value in required_fields.items():
            if not field_value or field_value.strip() == "":
                errors.append(f"กรุณากรอก{field_name}")
        
        if errors:
            for error in errors:
                st.error(f"❌ {error}")
        elif password != confirm_password:
            st.error("รหัสผ่านไม่ตรงกัน")
        elif not agree_terms:
            st.error("กรุณายอมรับข้อกำหนดและเงื่อนไข")
        else:
            # ตรวจสอบเพิ่มเติม
            # ตรวจสอบ username format
            username_pattern = r'^[a-zA-Z0-9_]{4,20}$'
            if username and not re.match(username_pattern, username):
                st.error("ชื่อผู้ใช้ควรมีความยาว 4-20 ตัวอักษร, ใช้ได้เฉพาะ a-z, 0-9, _")
            # ตรวจสอบรหัสผ่าน
            elif len(password) < 8:
                st.error("รหัสผ่านควรมีความยาวอย่างน้อย 8 ตัวอักษร")
            # ตรวจสอบอีเมล format
            elif not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
                st.error("รูปแบบอีเมลไม่ถูกต้อง")
            # ตรวจสอบเบอร์โทรศัพท์
            elif not re.match(r'^[0-9\-\+\(\)\s]{10,20}$', phone.replace(" ", "")):
                st.error("รูปแบบเบอร์โทรศัพท์ไม่ถูกต้อง")
            else:
                try:
                    # ใช้ secrets สำหรับการเชื่อมต่อ
                    sf = st.secrets["connections"]["snowflake"]
                    
                    # เชื่อมต่อกับ Snowflake โดยตรง
                    snowflake_conn = snowflake.connector.connect(
                        account=sf["account"],
                        user=sf["user"],
                        password=sf["password"],
                        role=sf["role"],
                        warehouse=sf["warehouse"],
                        database=sf["database"],
                        schema=sf["schema"]
                    )
                    
                    cursor = snowflake_conn.cursor()
                    
                    try:
                        # Check if username exists
                        check_query = f"""
                        SELECT COUNT(*) as count 
                        FROM users 
                        WHERE username = '{username.replace("'", "''")}'
                        """
                        cursor.execute(check_query)
                        check_result = cursor.fetchone()
                        
                        if check_result[0] > 0:
                            st.error("❌ ชื่อผู้ใช้นี้มีอยู่แล้ว")
                        else:
                            # Check if email exists
                            check_email_query = f"""
                            SELECT COUNT(*) as count 
                            FROM users 
                            WHERE email = '{email.replace("'", "''")}'
                            """
                            cursor.execute(check_email_query)
                            email_result = cursor.fetchone()
                            
                            if email_result[0] > 0:
                                st.error("❌ อีเมลนี้มีผู้ใช้งานแล้ว")
                            else:
                                # สร้าง USER_ID และ FULL_NAME
                                user_id = str(uuid.uuid4())
                                full_name = f"{first_name} {last_name}"
                                
                                # สร้าง INSERT query
                                insert_query = f"""
                                INSERT INTO users (
                                    USER_ID,
                                    USERNAME, 
                                    PASSWORD, 
                                    EMAIL, 
                                    FULL_NAME, 
                                    COMPANY, 
                                    PHONE,
                                    ADDRESS,
                                    SUBSCRIPTION_PLAN,
                                    SUBSCRIPTION_STATUS,
                                    IS_ACTIVE,
                                    CREATED_AT,
                                    UPDATED_AT
                                ) VALUES (
                                    '{user_id}',
                                    '{username.replace("'", "''")}',
                                    '{password.replace("'", "''")}',
                                    '{email.replace("'", "''")}',
                                    '{full_name.replace("'", "''")}',
                                    '{company.replace("'", "''")}',
                                    '{phone.replace("'", "''")}',
                                    '{address.replace("'", "''")}',
                                    'FREE',
                                    'ACTIVE',
                                    TRUE,
                                    CURRENT_TIMESTAMP(),
                                    CURRENT_TIMESTAMP()
                                )
                                """
                                
                                # Debug: แสดง query
                                with st.expander("แสดง SQL Query"):
                                    st.code(insert_query, language='sql')
                                
                                # Execute the INSERT
                                with st.spinner("กำลังสร้างบัญชี..."):
                                    time.sleep(0.5)
                                    cursor.execute(insert_query)
                                    snowflake_conn.commit()
                                    
                                    st.success("🎉 สร้างบัญชีสำเร็จ!")
                                    st.balloons()
                                    
                                    # Auto login after successful registration
                                    st.session_state['logged_in'] = True
                                    st.session_state['user_id'] = user_id
                                    st.session_state['user_name'] = username
                                    st.session_state['user_email'] = email
                                    st.session_state['user_fullname'] = full_name
                                    st.session_state['user_company'] = company if company else ""
                                    st.session_state['user_phone'] = phone
                                    st.session_state['user_address'] = address if address else ""
                                    st.session_state['subscription_plan'] = "FREE"
                                    st.session_state['subscription_status'] = "ACTIVE"
                                    st.session_state['current_page'] = "dashboard"
                                    
                                    # แสดงข้อมูล
                                    st.info(f"""
                                    **ข้อมูลบัญชีของคุณ:**
                                    - ชื่อ: {full_name}
                                    - อีเมล: {email}
                                    - เบอร์โทร: {phone}
                                    - ที่อยู่: {address if address else 'ไม่ระบุ'}
                                    - บริษัท: {company if company else 'ไม่ระบุ'}
                                    - ชื่อผู้ใช้: {username}
                                    - แพ็คเกจ: FREE
                                    - สถานะ: ACTIVE
                                    
                                    กำลังเข้าสู่ระบบอัตโนมัติ...
                                    """)
                                    
                                    time.sleep(3)
                                    st.rerun()
                    
                    finally:
                        cursor.close()
                        snowflake_conn.close()
                
                except Exception as e:
                    st.error(f"เกิดข้อผิดพลาดในการสร้างบัญชี: {str(e)}")
                    import traceback
                    st.error("**รายละเอียดข้อผิดพลาด:**")
                    st.code(traceback.format_exc())
                    
                    # แสดงข้อมูลทดสอบ
                    st.info("""
                    **สำหรับการทดสอบ:**
                    - ลองใช้ username: testuser
                    - รหัสผ่าน: 12345678
                    - อีเมล: test@example.com
                    """)
    
    # ตรวจสอบเมื่อกดยกเลิก
    if cancel_btn:
        st.info("การสร้างบัญชีถูกยกเลิก")
        time.sleep(1)
        st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)

def show_premium_dashboard():
        # ---------------------------
    # Page config - Premium Theme
    # ---------------------------


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
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    '''

    st.components.v1.html(html_content, height=100, scrolling=False)

    col1, col2, col3 = st.columns([1, 2, 1])

   
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

# ฟังก์ชันแสดงหน้าโปรไฟล์สำหรับ Free User
def show_free_profile():
    """แสดงโปรไฟล์สำหรับผู้ใช้ฟรี"""
    st.title("👤 โปรไฟล์ผู้ใช้")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("""
        <div style="text-align: center;">
            <div style="font-size: 4rem; background: linear-gradient(135deg, #1e88e5 0%, #1976d2 100%); 
                    -webkit-background-clip: text; -webkit-text-fill-color: transparent; 
                    width: 100px; height: 100px; margin: 0 auto;">
                👤
            </div>
            <h3>{}</h3>
            <div style="background: #ffd700; color: #333; padding: 0.25rem 1rem; 
                    border-radius: 15px; display: inline-block; font-weight: bold;">
                🆓 FREE ACCOUNT
            </div>
        </div>
        """.format(st.session_state.get('user_fullname', '')), unsafe_allow_html=True)
    
    with col2:
        st.markdown("### ข้อมูลบัญชี")
        
        info_col1, info_col2 = st.columns(2)
        
        with info_col1:
            st.text_input("ชื่อผู้ใช้", value=st.session_state.get('user_name', ''), disabled=True)
            st.text_input("อีเมล", value=st.session_state.get('user_email', ''), disabled=True)
        
        with info_col2:
            st.text_input("บริษัท", value=st.session_state.get('user_company', '') or "ไม่ระบุ", disabled=True)
            st.text_input("เบอร์โทร", value=st.session_state.get('user_phone', '') or "ไม่ระบุ", disabled=True)
        
        st.text_area("ที่อยู่", value=st.session_state.get('user_address', '') or "ไม่ระบุ", disabled=True, height=100)
    
    st.markdown("---")
    
    # Account stats
    st.markdown("### 📊 สถิติการใช้งาน")
    
    col_s1, col_s2, col_s3 = st.columns(3)
    
    with col_s1:
        st.metric("วันที่สมัคร", "15/11/2023", "30 วัน")
    
    with col_s2:
        st.metric("ใช้งานล่าสุด", "วันนี้", "")
    
    with col_s3:
        st.metric("รายงานที่สร้าง", "2 ฉบับ", "เหลืออีก 2 ฉบับ/เดือน")
    
    # Upgrade reminder
    st.markdown("---")
    st.warning("""
    **อัปเกรดเป็น PRO เพื่อปลดล็อก:**
    - สร้างรายงานไม่จำกัด
    - วิเคราะห์ข้อมูลย้อนหลัง 1 ปี
    - พยากรณ์ราคา 30 วัน
    - เครื่องมือวิเคราะห์ขั้นสูง
    """)
    
    if st.button("🚀 อัปเกรดเป็น PRO เดี๋ยวนี้", use_container_width=True):
        st.session_state['current_page'] = "upgrade"
        st.rerun()

# ============================================
# SNOWFLAKE CONNECTION
# ============================================
def get_snowflake_connection():
    """Create and return Snowflake connection"""
    try:
        sf = st.secrets["connections"]["snowflake"]
        
        conn = snowflake.connector.connect(
            account=sf["account"],
            user=sf["user"],
            password=sf["password"],
            role=sf.get("role", "ACCOUNTADMIN"),
            warehouse=sf["warehouse"],
            database=sf["database"],
            schema=sf["schema"]
        )
        return conn
    except Exception as e:
        st.error(f"❌ ไม่สามารถเชื่อมต่อกับ Snowflake: {str(e)}")
        return None

# ============================================
# DATABASE INITIALIZATION
# ============================================
def initialize_database():
    """Initialize all required tables in Snowflake"""
    conn = get_snowflake_connection()
    if not conn:
        st.error("❌ ไม่สามารถเชื่อมต่อกับฐานข้อมูล")
        return False
    
    try:
        return True
        
    except Exception as e:
        st.error(f"❌ เกิดข้อผิดพลาดในการสร้างตาราง: {str(e)}")
        try:
            conn.close()
        except:
            pass
        return False

# ============================================
# USER MANAGEMENT - FIXED SQL SYNTAX
# ============================================

def get_current_user_id():
    """Get current user ID from session state"""
    # หากมีการ login แล้ว ควรดึง user_id จาก session
    if 'logged_in' in st.session_state and st.session_state['logged_in']:
        # ตรวจสอบว่ามี user_id ใน session หรือไม่
        if 'user_id' in st.session_state and st.session_state['user_id']:
            return st.session_state['user_id']
    
    # ถ้าไม่มี ให้สร้างจาก session หรือใช้ guest
    session_id = st.session_state.get('session_id', str(uuid.uuid4()))
    user_id = f"USER_{hashlib.md5(session_id.encode()).hexdigest()[:15]}"
    st.session_state['user_id'] = user_id
    
    # กำหนดข้อมูลเริ่มต้นสำหรับ guest
    if 'user_email' not in st.session_state:
        st.session_state['user_email'] = 'guest@oilprice.com'
    if 'user_name' not in st.session_state:
        st.session_state['user_name'] = 'Guest User'
    if 'user_company' not in st.session_state:
        st.session_state['user_company'] = 'Individual'
    
    return user_id
def get_current_user_email():
    """Get current user email"""
    return st.session_state.get('user_email', 'guest@oilprice.com')

def get_current_user_name():
    """Get current user name"""
    return st.session_state.get('user_name', 'Guest User')

def check_user_exists(user_id):
    """Check if user exists in database"""
    conn = get_snowflake_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        # ใช้ string formatting แทน parameter binding
        query = f"SELECT COUNT(*) FROM USERS WHERE USER_ID = '{user_id}'"
        cursor.execute(query)
        count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        
        return count > 0
    except Exception as e:
        st.error(f"❌ ข้อผิดพลาดในการตรวจสอบผู้ใช้: {str(e)}")
        try:
            conn.close()
        except:
            pass
        return False

def create_or_update_user(user_id, plan_type, payment_duration):
    """Create or update user in database"""
    conn = get_snowflake_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # Calculate subscription dates
        start_date = datetime.now().date()
        if payment_duration == 'monthly':
            end_date = start_date + timedelta(days=30)
        else:  # yearly
            end_date = start_date + timedelta(days=365)
        
        # Check if user exists
        user_exists = check_user_exists(user_id)
        
        if user_exists:
            # Get old plan for history
            query = f"SELECT SUBSCRIPTION_PLAN FROM USERS WHERE USER_ID = '{user_id}'"
            cursor.execute(query)
            result = cursor.fetchone()
            old_plan = result[0] if result else 'FREE'
            
            # Update existing user - ใช้ string formatting
            update_query = f"""
            UPDATE USERS 
            SET SUBSCRIPTION_PLAN = '{plan_type}',
                SUBSCRIPTION_STATUS = 'ACTIVE',
                SUBSCRIPTION_START_DATE = '{start_date}',
                SUBSCRIPTION_END_DATE = '{end_date}',
                UPDATED_AT = CURRENT_TIMESTAMP()
            WHERE USER_ID = '{user_id}'
            """
            cursor.execute(update_query)
            
            # Log history if plan changed
            if old_plan != plan_type:
                history_id = f"HIST_{random.randint(10000, 99999)}"
                insert_history = f"""
                INSERT INTO SUBSCRIPTION_HISTORY (HISTORY_ID, USER_ID, OLD_PLAN, NEW_PLAN, REASON)
                VALUES ('{history_id}', '{user_id}', '{old_plan}', '{plan_type}', 'UPGRADE')
                """
                cursor.execute(insert_history)
            
        else:
            # Insert new user - ใช้ string formatting
            email = get_current_user_email()
            name = get_current_user_name()
            
            insert_query = f"""
            INSERT INTO USERS (
                USER_ID, EMAIL, FULL_NAME, SUBSCRIPTION_PLAN,
                SUBSCRIPTION_STATUS, SUBSCRIPTION_START_DATE, SUBSCRIPTION_END_DATE
            ) VALUES ('{user_id}', '{email}', '{name}', '{plan_type}', 'ACTIVE', '{start_date}', '{end_date}')
            """
            cursor.execute(insert_query)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        # Update session state
        plan_mapping = {'FREE': 0, 'PRO': 1, 'ENTERPRISE': 2}
        st.session_state['subscribe_flag'] = plan_mapping.get(plan_type, 0)
        
        return True
        
    except Exception as e:
        st.error(f"❌ เกิดข้อผิดพลาดในการบันทึกผู้ใช้: {str(e)}")
        try:
            conn.close()
        except:
            pass
        return False

def get_user_subscription(user_id):
    """Get user's current subscription"""
    conn = get_snowflake_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor()
        # ตรวจสอบจากตาราง USERS
        query = f"""
        SELECT SUBSCRIPTION_PLAN, SUBSCRIPTION_STATUS, 
               SUBSCRIPTION_START_DATE, SUBSCRIPTION_END_DATE
        FROM USERS 
        WHERE USER_ID = '{user_id}'
        """
        cursor.execute(query)
        
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if result:
            return {
                'plan': result[0] or 'FREE',
                'status': result[1] or 'INACTIVE',
                'start_date': result[2],
                'end_date': result[3]
            }
        return None
        
    except Exception as e:
        # ถ้าไม่พบตารางหรือ error ให้ return default
        st.error(f"❌ เกิดข้อผิดพลาดในการดึงข้อมูลสมาชิก: {str(e)}")
        try:
            conn.close()
        except:
            pass
        return None
# ============================================
# PAYMENT MANAGEMENT - FIXED SQL SYNTAX
# ============================================
def save_payment_to_db(payment_data):
    """Save payment transaction to database"""
    conn = get_snowflake_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # ใช้ string formatting สำหรับการ insert
        insert_query = f"""
        INSERT INTO PAYMENTS (
            PAYMENT_ID, USER_ID, ORDER_ID, PLAN_TYPE, DURATION,
            PAYMENT_METHOD, AMOUNT, TAX, TOTAL_AMOUNT, PAYMENT_STATUS,
            TRANSACTION_ID, PAYMENT_DATE, SUBSCRIPTION_START_DATE, SUBSCRIPTION_END_DATE
        ) VALUES (
            '{payment_data['payment_id']}',
            '{payment_data['user_id']}',
            '{payment_data['order_id']}',
            '{payment_data['plan_type']}',
            '{payment_data['duration']}',
            '{payment_data['payment_method']}',
            {float(payment_data['amount'])},
            {float(payment_data['tax'])},
            {float(payment_data['total_amount'])},
            '{payment_data['status']}',
            '{payment_data['transaction_id']}',
            '{payment_data['payment_date']}',
            '{payment_data['subscription_start']}',
            '{payment_data['subscription_end']}'
        )
        """
        
        cursor.execute(insert_query)
        conn.commit()
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        st.error(f"❌ เกิดข้อผิดพลาดในการบันทึกการชำระเงิน: {str(e)}")
        try:
            conn.close()
        except:
            pass
        return False

# ============================================
# COUPON & TICKET MANAGEMENT - FIXED SQL SYNTAX
# ============================================
def generate_coupon_code():
    """Generate unique coupon code"""
    characters = string.ascii_uppercase + string.digits
    coupon_code = 'OIL' + ''.join(random.choice(characters) for _ in range(3)) + '-' + ''.join(random.choice(characters) for _ in range(4))
    return coupon_code

def create_welcome_coupon(user_id, discount_percent=15):
    """Create welcome coupon and ticket for new PRO user"""
    conn = get_snowflake_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor()
        
        # Generate coupon
        coupon_code = generate_coupon_code()
        coupon_id = f"CPN_{random.randint(10000, 99999)}"
        
        # Set validity
        valid_from = datetime.now().date()
        valid_to = valid_from + timedelta(days=30)
        
        # Create coupon - ใช้ string formatting
        coupon_query = f"""
        INSERT INTO COUPONS (
            COUPON_ID, USER_ID, COUPON_CODE, COUPON_TYPE,
            DISCOUNT_PERCENT, MINIMUM_PURCHASE, VALID_FROM, VALID_TO
        ) VALUES (
            '{coupon_id}',
            '{user_id}',
            '{coupon_code}',
            'WELCOME_PRO',
            {float(15.00)},  -- 15% discount
            {float(500.00)},  -- Minimum purchase 500฿
            '{valid_from}',
            '{valid_to}'
        )
        """
        cursor.execute(coupon_query)
        
        # Create ticket
        ticket_id = f"TKT_{random.randint(10000, 99999)}"
        expires_at = datetime.now().date() + timedelta(days=365)
        
        ticket_query = f"""
        INSERT INTO TICKETS (
            TICKET_ID, USER_ID, COUPON_ID, TICKET_TYPE,
            DESCRIPTION, EXPIRES_AT
        ) VALUES (
            '{ticket_id}',
            '{user_id}',
            '{coupon_id}',
            'PRO_WELCOME_TICKET',
            'Welcome to PRO membership - 15%% discount coupon',
            '{expires_at}'
        )
        """
        cursor.execute(ticket_query)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return coupon_code
        
    except Exception as e:
        st.error(f"❌ เกิดข้อผิดพลาดในการสร้างคูปอง: {str(e)}")
        try:
            conn.close()
        except:
            pass
        return None

def get_user_coupons(user_id):
    """Get user's active coupons"""
    conn = get_snowflake_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor()
        # ใช้ string formatting
        query = f"""
        SELECT COUPON_CODE, DISCOUNT_PERCENT, VALID_TO, CREATED_AT
        FROM COUPONS 
        WHERE USER_ID = '{user_id}' 
        AND STATUS = 'ACTIVE'
        AND VALID_TO >= CURRENT_DATE()
        ORDER BY CREATED_AT DESC
        """
        cursor.execute(query)
        
        coupons = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return coupons
        
    except Exception as e:
        # ไม่แสดง error ถ้าไม่มีคูปอง
        try:
            conn.close()
        except:
            pass
        return []

# ============================================
# MAIN PACKAGE PAGE
# ============================================
def show_package_page():
    """Main package subscription page"""
    
    # Initialize session state
    if 'payment_processing' not in st.session_state:
        st.session_state.payment_processing = False
    if 'selected_plan' not in st.session_state:
        st.session_state.selected_plan = None
    if 'payment_step' not in st.session_state:
        st.session_state.payment_step = 'select_plan'
    # ไม่ต้องกำหนด subscribe_flag = 0 ตรงนี้ เพราะจะถูกกำหนดจาก database
    
    # Initialize database tables
    try:
        initialize_database()
    except:
        pass  # Continue even if table creation fails
    
    # Check user subscription from database
    user_id = get_current_user_id()
    subscription = get_user_subscription(user_id)
    
    if subscription:
        plan_mapping = {'FREE': 0, 'PRO': 1, 'ENTERPRISE': 2}
        # อัปเดตค่า subscribe_flag จาก database ทุกครั้ง
        st.session_state.subscribe_flag = plan_mapping.get(subscription['plan'], 0)
    
    # Show payment page if in payment mode
    if st.session_state.payment_processing:
        return show_payment_page()
    
    # Main UI
    st.title("⛽ Oil Price Analysis Plans")
    st.markdown("เลือกแผนที่เหมาะสมกับความต้องการของคุณ")
    
    # User info section
    if subscription and subscription.get('plan'):
        col1, col2, col3 = st.columns(3)
        with col1:
            plan_icon = "🆓" if subscription['plan'] == 'FREE' else "⚡" if subscription['plan'] == 'PRO' else "🏢"
            st.info(f"{plan_icon} **แพ็คเกจปัจจุบัน:** {subscription['plan']}")
        
        with col2:
            if subscription.get('end_date'):
                try:
                    days_left = (subscription['end_date'] - datetime.now().date()).days
                    if days_left > 0:
                        st.info(f"📅 **เหลืออายุ:** {days_left} วัน")
                    else:
                        st.warning("⚠️ **สมาชิกหมดอายุแล้ว**")
                except:
                    st.info("📅 **สถานะ:** ใช้งานได้")
        
        with col3:
            if st.button("🔄 โหลดข้อมูลใหม่", key="refresh_data"):
                st.rerun()
    
    # Pricing cards
    col1, col2, col3 = st.columns(3)

    # Features data
    features_data = [
        ("ข้อมูลราคาน้ำมัน", "1 เดือน", "3 ปี", "3 ปี"),
        ("คูปองส่วนลด", "ไม่ได้รับ", "15% คูปองต้อนรับ", "20% คูปองต้อนรับ"),
        ("เปรียบเทียบชนิดน้ำมัน", "❌", "✅", "✅"),
        ("เปรียบเทียบแบรนด์", "❌", "✅", "✅"),
        ("Agentic AI", "❌", "✅", "✅"),
        ("ข้อมูลผู้ใช้แบ็กเอนด์", "❌", "❌", "✅"),
        ("แผนที่สถานี", "✅", "✅", "✅")
    ]

    # FREE Plan
    with col1:
        with st.container():
            st.markdown("""
            <div style='border: 2px solid #6B7280; border-radius: 15px; padding: 20px; margin: 10px;'>
                <div style='text-align: center;'>
                    <div style='font-size: 40px; margin-bottom: 10px;'>🆓</div>
                    <h3 style='color: #6B7280; margin-bottom: 5px;'>FREE</h3>
                    <h2 style='color: #6B7280; margin: 10px 0;'>฿0</h2>
                    <p style='color: #6B7280;'>เริ่มต้นใช้งาน</p>
                </div>
            """, unsafe_allow_html=True)
            
            # Features
            for feature in features_data:
                st.markdown(f"""
                <div style='display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #f0f0f0;'>
                    <span style='font-size: 14px;'>{feature[0]}</span>
                    <span style='color: #6B7280; font-size: 14px;'>{feature[1]}</span>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Action button
            if st.session_state.subscribe_flag == 0:
                st.button("แพ็คเกจปัจจุบัน", disabled=True, use_container_width=True, key="free_current")
            else:
                if st.button("เปลี่ยนเป็น FREE", use_container_width=True, key="switch_to_free"):
                    if create_or_update_user(user_id, 'FREE', 'monthly'):
                        st.success("✅ เปลี่ยนเป็นแพ็คเกจ FREE สำเร็จ!")
                        st.rerun()

    # PRO Plan (Recommended)
    with col2:
        with st.container():
            st.markdown("""
            <div style='position: relative; border: 3px solid #10a37f; border-radius: 15px; padding: 20px; margin: 10px;'>
                <div style='position: absolute; top: -12px; left: 50%; transform: translateX(-50%); 
                            background: #10a37f; color: white; padding: 4px 20px; border-radius: 15px;
                            font-weight: bold; font-size: 14px;'>
                    ⭐ คุ้มค่า
                </div>
                <div style='text-align: center;'>
                    <div style='font-size: 40px; margin-bottom: 10px;'>⚡</div>
                    <h3 style='color: #10a37f; margin-bottom: 5px;'>PRO</h3>
                    <h2 style='color: #10a37f; margin: 10px 0;'>฿200</h2>
                    <p style='color: #10a37f;'>ต่อเดือน</p>
                </div>
            """, unsafe_allow_html=True)
            
            # Features
            for feature in features_data:
                st.markdown(f"""
                <div style='display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #f0f0f0;'>
                    <span style='font-size: 14px;'>{feature[0]}</span>
                    <span style='color: #10a37f; font-size: 14px;'>{feature[2]}</span>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Action button
            if st.session_state.subscribe_flag == 1:
                st.button("แพ็คเกจปัจจุบัน", disabled=True, use_container_width=True, key="pro_current")
            else:
                if st.button("✨ อัพเกรดเป็น PRO", use_container_width=True, key="upgrade_to_pro"):
                    st.session_state.payment_processing = True
                    st.session_state.selected_plan = "PRO"
                    st.session_state.payment_step = 'select_duration'
                    st.rerun()

    # ENTERPRISE Plan
    with col3:
        with st.container():
            st.markdown("""
            <div style='border: 2px solid #6C63FF; border-radius: 15px; padding: 20px; margin: 10px;'>
                <div style='text-align: center;'>
                    <div style='font-size: 40px; margin-bottom: 10px;'>🏢</div>
                    <h3 style='color: #6C63FF; margin-bottom: 5px;'>ENTERPRISE</h3>
                    <h2 style='color: #6C63FF; margin: 10px 0;'>฿500</h2>
                    <p style='color: #6C63FF;'>ต่อเดือน</p>
                </div>
            """, unsafe_allow_html=True)
            
            # Features
            for feature in features_data:
                st.markdown(f"""
                <div style='display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #f0f0f0;'>
                    <span style='font-size: 14px;'>{feature[0]}</span>
                    <span style='color: #6C63FF; font-size: 14px;'>{feature[3]}</span>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Action button
            if st.session_state.subscribe_flag == 2:
                st.button("แพ็คเกจปัจจุบัน", disabled=True, use_container_width=True, key="enterprise_current")
            else:
                if st.button("✨ อัพเกรดเป็น Enterprise", use_container_width=True, key="upgrade_to_enterprise"):
                    st.session_state.payment_processing = True
                    st.session_state.selected_plan = "ENTERPRISE"  # เปลี่ยนจาก Enterprise เป็น ENTERPRISE ให้สอดคล้องกับ database
                    st.session_state.payment_step = 'select_duration'
                    st.rerun()

    # Show user's coupons
    st.markdown("---")
    coupons = get_user_coupons(user_id)
    if coupons:
        st.markdown("### 🎫 คูปองส่วนลดของคุณ")
        cols = st.columns(min(3, len(coupons)))
        for idx, coupon in enumerate(coupons[:3]):  # Show max 3 coupons
            with cols[idx % len(cols)]:
                valid_to = coupon[2].strftime('%d/%m/%Y') if coupon[2] else "-"
                st.markdown(f"""
                <div style='border: 1px solid #10a37f; border-radius: 10px; padding: 15px; margin: 5px;'>
                    <div style='font-size: 16px; font-weight: bold; color: #10a37f;'>{coupon[0]}</div>
                    <div style='font-size: 20px; font-weight: bold; color: #10a37f; margin: 5px 0;'>{coupon[1]}% OFF</div>
                    <div style='font-size: 12px; color: #666;'>ใช้ได้ถึง: {valid_to}</div>
                </div>
                """, unsafe_allow_html=True)
    else:
        # ถ้ายังไม่มีคูปอง ให้แสดงข้อความแนะนำ
        if st.session_state.subscribe_flag == 1:
            st.info("💡 อัพเกรดเป็น PRO เพื่อรับคูปองส่วนลด 15%!")

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p>✅ รับประกันคืนเงินภายใน 7 วัน | ✅ ชำระเงินปลอดภัย | ✅ สนับสนุน 24/7</p>
        <p>📧 ติดต่อ: support@oilsophaeng.com | 📞 02-XXX-XXXX</p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("← กลับไปหน้าหลัก", use_container_width=True, key="back_to_home"):
        st.session_state.page = 'home'  # เปลี่ยนตาม context ของ app
# ============================================
# PAYMENT PROCESSING PAGES
# ============================================
def show_payment_page():
    # Initialize payment state
    if 'payment_duration' not in st.session_state:
        st.session_state.payment_duration = 'monthly'
    if 'payment_method' not in st.session_state:
        st.session_state.payment_method = None

    # Get selected plan
    selected_plan = st.session_state.selected_plan

    # Calculate prices based on plan
    if selected_plan == "PRO":
        if st.session_state.payment_duration == 'monthly':
            base_price = 200
            duration_text = "รายเดือน"
            duration_days = 30
            yearly_price = 2200  # ประหยัด 200 บาท
        else:
            base_price = 2200
            duration_text = "รายปี"
            duration_days = 365
    elif selected_plan == "ENTERPRISE":
        if st.session_state.payment_duration == 'monthly':
            base_price = 500
            duration_text = "รายเดือน"
            duration_days = 30
            yearly_price = 5500  # ประหยัด 500 บาท
        else:
            base_price = 5500
            duration_text = "รายปี"
            duration_days = 365
    else:
        # Default to FREE (should not happen here)
        base_price = 0
        duration_text = "รายเดือน"
        duration_days = 30

    tax = base_price * 0.07
    total_price = base_price + tax

    # Show appropriate step
    if st.session_state.payment_step == 'select_duration':
        show_duration_selection(selected_plan, base_price, duration_text, yearly_price if 'yearly_price' in locals() else None)
    elif st.session_state.payment_step == 'payment_method':
        show_payment_method(selected_plan, base_price, tax, total_price, duration_text, duration_days)
    elif st.session_state.payment_step == 'payment_processing':
        process_payment(selected_plan, base_price, tax, total_price, duration_text, duration_days)
    elif st.session_state.payment_step == 'payment_complete':
        show_payment_complete()

def show_payment_complete():
    """Show payment completion page"""
    
    payment_data = st.session_state.get('payment_data', {})
    coupon_code = st.session_state.get('last_coupon', '')
    plan_name = payment_data.get('plan_type', 'PRO')
    
    plan_display_name = "PRO" if plan_name == "PRO" else "Enterprise"
    plan_color = "#10a37f" if plan_name == "PRO" else "#6C63FF"
    plan_icon = "⚡" if plan_name == "PRO" else "🏢"
    
    st.markdown(f"""
    <div style='text-align: center; padding: 40px 20px;'>
        <div style='font-size: 60px; color: {plan_color}; margin-bottom: 20px;'>{plan_icon}</div>
        <h1 style='color: {plan_color};'>ชำระเงินสำเร็จ!</h1>
        <p style='font-size: 18px; color: #666; margin-bottom: 30px;'>
            คุณได้อัพเกรดเป็นแพ็คเกจ {plan_display_name} สำเร็จแล้ว
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Show coupon if available
    if coupon_code:
        coupon_discount = 20 if plan_name == "ENTERPRISE" else 15
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, {plan_color}, {'#0d8c6c' if plan_name == 'PRO' else '#5a52d4'}); 
                   color: white; padding: 20px; border-radius: 10px; margin: 20px 0;'>
            <div style='text-align: center;'>
                <div style='font-size: 20px; font-weight: bold; margin-bottom: 10px;'>🎁 ของขวัญต้อนรับสมาชิก {plan_display_name}!</div>
                <div style='font-size: 28px; font-weight: bold; margin: 15px 0;'>{coupon_code}</div>
                <div>คูปองส่วนลด {coupon_discount}% สำหรับการซื้อครั้งถัดไป</div>
                <div style='font-size: 14px; margin-top: 10px;'>
                    ใช้ได้ถึง: {(datetime.now() + timedelta(days=30)).strftime('%d/%m/%Y')}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Order details
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div style='background: #f8f9fa; padding: 20px; border-radius: 10px;'>
            <h4>📄 ข้อมูลการสั่งซื้อ</h4>
            <p><strong>หมายเลขใบสั่งซื้อ:</strong> {payment_data.get('order_id', 'N/A')}</p>
            <p><strong>หมายเลขธุรกรรม:</strong> {payment_data.get('transaction_id', 'N/A')}</p>
            <p><strong>วันที่ชำระ:</strong> {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
            <p><strong>อายุสมาชิกถึง:</strong> {payment_data.get('subscription_end', 'N/A')}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        duration_text = "รายเดือน" if payment_data.get('duration') == 'monthly' else "รายปี"
        st.markdown(f"""
        <div style='background: #f8f9fa; padding: 20px; border-radius: 10px;'>
            <h4>💰 ข้อมูลการชำระเงิน</h4>
            <p><strong>แพ็คเกจ:</strong> {plan_display_name}</p>
            <p><strong>ระยะเวลา:</strong> {duration_text}</p>
            <p><strong>ยอดรวม:</strong> ฿{payment_data.get('total_amount', 0):,.2f}</p>
            <p><strong>สถานะ:</strong> <span style='color: {plan_color}; font-weight: bold;'>ชำระเงินแล้ว</span></p>
        </div>
        """, unsafe_allow_html=True)
    
    # Action buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🏠 กลับไปหน้าหลัก", use_container_width=True, key="back_to_home_final"):
            st.session_state.payment_processing = False
            st.session_state.payment_step = 'select_plan'
            st.session_state.page = 'home'  # หรือหน้าหลักของคุณ
            st.rerun()
    
    with col2:
        if st.button(f"{plan_icon} เริ่มใช้งาน {plan_display_name}", use_container_width=True, key="start_pro"):
            st.session_state.payment_processing = False
            st.session_state.payment_step = 'select_plan'
            st.success(f"🎉 ยินดีต้อนรับสู่แพ็คเกจ {plan_display_name}!")
            st.rerun()
    
    with col3:
        # Generate receipt
        receipt = f"""
        ⛽ Oil Price Analysis - ใบเสร็จรับเงิน
        ==================================
        หมายเลขใบสั่งซื้อ: {payment_data.get('order_id', 'N/A')}
        หมายเลขธุรกรรม: {payment_data.get('transaction_id', 'N/A')}
        วันที่: {datetime.now().strftime('%d/%m/%Y %H:%M')}
        
        รายละเอียด:
        - แพ็คเกจ: {plan_display_name}
        - ระยะเวลา: {duration_text}
        - ราคา: ฿{payment_data.get('amount', 0):,.2f}
        - ภาษี 7%: ฿{payment_data.get('tax', 0):,.2f}
        - รวมทั้งสิ้น: ฿{payment_data.get('total_amount', 0):,.2f}
        
        ข้อมูลสมาชิก:
        - อายุสมาชิกถึง: {payment_data.get('subscription_end', 'N/A')}
        {'- คูปองส่วนลด: ' + coupon_code if coupon_code else ''}
        
        ขอบคุณที่ใช้บริการ!
        """
        
        st.download_button(
            label="📥 ดาวน์โหลดใบเสร็จ",
            data=receipt,
            file_name=f"receipt_{payment_data.get('order_id', 'N/A')}.txt",
            mime="text/plain",
            use_container_width=True,
            key="download_receipt"
        )

def show_duration_selection():
    """Show duration selection - รับข้อมูลจาก session_state"""
    
    selected_plan = st.session_state.selected_plan
    payment_duration = st.session_state.payment_duration
    
    # ข้อมูลแผน
    plan_info = {
        "PRO": {
            "display_name": "PRO",
            "color": "#10a37f",
            "icon": "⚡",
            "monthly_price": 200,
            "yearly_price": 2200,
            "yearly_saving": "ประหยัด 200฿",
            "normal_yearly": "2,400฿"
        },
        "ENTERPRISE": {
            "display_name": "Enterprise",
            "color": "#6C63FF",
            "icon": "🏢",
            "monthly_price": 500,
            "yearly_price": 5500,
            "yearly_saving": "ประหยัด 500฿",
            "normal_yearly": "6,000฿"
        }
    }
    
    info = plan_info.get(selected_plan, plan_info["PRO"])
    
    # กำหนด duration_text ตามการเลือก
    duration_text = "รายเดือน" if payment_duration == 'monthly' else "รายปี"
    
    st.markdown(f"""
    <div style='max-width: 600px; margin: 0 auto; padding: 20px;'>
        <h2 style='color: {info["color"]};'>📅 เลือกระยะเวลาสมัครสมาชิก {info["display_name"]}</h2>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div style='border: 2px solid {info["color"]}; border-radius: 10px; padding: 20px; text-align: center;'>
            <div style='font-size: 30px;'>📅</div>
            <h3>รายเดือน</h3>
            <h2 style='color: {info["color"]};'>฿{info["monthly_price"]:,}</h2>
            <p>ยืดหยุ่นสูงสุด</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("เลือกรายเดือน", key="monthly_btn", use_container_width=True):
            st.session_state.payment_duration = 'monthly'
            st.session_state.payment_step = 'payment_method'
            st.rerun()
    
    with col2:
        st.markdown(f"""
        <div style='border: 2px solid {info["color"]}; border-radius: 10px; padding: 20px; text-align: center;'>
            <div style='font-size: 30px;'>📆</div>
            <h3>รายปี</h3>
            <h2 style='color: {info["color"]};'>฿{info["yearly_price"]:,}</h2>
            <p style='color: #FFD700; font-weight: bold;'>✨ {info["yearly_saving"]} ✨</p>
            <p>จากราคาปกติ {info["normal_yearly"]}</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("เลือกรายปี", key="yearly_btn", use_container_width=True):
            st.session_state.payment_duration = 'yearly'
            st.session_state.payment_step = 'payment_method'
            st.rerun()
    
    # Back button
    if st.button("← ย้อนกลับ", use_container_width=True, key="back_from_duration"):
        st.session_state.payment_processing = False
        st.rerun()

def show_payment_method():
    """Show payment method selection"""
    
    selected_plan = st.session_state.selected_plan
    payment_duration = st.session_state.payment_duration
    
    # ข้อมูลแผน
    plan_info = {
        "PRO": {
            "display_name": "PRO",
            "color": "#10a37f",
            "monthly": 200,
            "yearly": 2200
        },
        "ENTERPRISE": {
            "display_name": "Enterprise",
            "color": "#6C63FF",
            "monthly": 500,
            "yearly": 5500
        }
    }
    
    info = plan_info.get(selected_plan, plan_info["PRO"])
    
    # คำนวณราคา
    if payment_duration == 'monthly':
        base_price = info["monthly"]
        duration_days = 30
        duration_thai = "รายเดือน"
    else:
        base_price = info["yearly"]
        duration_days = 365
        duration_thai = "รายปี"
    
    tax = base_price * 0.07
    total_price = base_price + tax
    
    st.markdown(f"""
    <div style='background: #f8f9fa; padding: 20px; border-radius: 10px; margin: 20px 0;'>
        <h4>📋 สรุปรายการสั่งซื้อ</h4>
        <div style='display: flex; justify-content: space-between; margin: 10px 0;'>
            <span>แพ็คเกจ {info["display_name"]} ({duration_thai})</span>
            <span>฿{base_price:,.2f}</span>
        </div>
        <div style='display: flex; justify-content: space-between; margin: 10px 0;'>
            <span>ภาษี 7%</span>
            <span>฿{tax:,.2f}</span>
        </div>
        <hr>
        <div style='display: flex; justify-content: space-between; font-size: 18px; font-weight: bold;'>
            <span>รวมทั้งหมด</span>
            <span style='color: {info["color"]};'>฿{total_price:,.2f}</span>
        </div>
        <p style='font-size: 12px; color: #666;'>การต่ออายุอัตโนมัติในอีก {duration_days} วัน</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Payment methods
    st.markdown("### 💰 วิธีการชำระเงิน")
    
    payment_options = ["พร้อมเพย์ (QR Code)", "บัตรเครดิต", "โอนผ่านธนาคาร"]
    payment_method = st.radio("เลือกวิธีชำระเงิน", payment_options, key="payment_method_radio", label_visibility="collapsed")
    
    # Terms checkbox
    agree = st.checkbox("✅ ฉันยอมรับข้อกำหนดและเงื่อนไขการให้บริการ", key="terms_checkbox")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("← ย้อนกลับ", use_container_width=True, key="back_to_duration"):
            st.session_state.payment_step = 'select_duration'
            st.rerun()
    
    with col2:
        if st.button("ดำเนินการชำระเงิน", use_container_width=True, key="proceed_payment", disabled=not agree):
            st.session_state.payment_method = payment_method
            st.session_state.payment_step = 'payment_processing'
            st.rerun()



def process_payment():
    """Process payment and save to database"""
    
    selected_plan = st.session_state.selected_plan
    payment_duration = st.session_state.payment_duration
    user_id = get_current_user_id()
    
    # ข้อมูลแผน
    plan_info = {
        "PRO": {
            "display_name": "PRO",
            "color": "#10a37f",
            "monthly": 200,
            "yearly": 2200,
            "coupon_discount": 15
        },
        "ENTERPRISE": {
            "display_name": "Enterprise",
            "color": "#6C63FF",
            "monthly": 500,
            "yearly": 5500,
            "coupon_discount": 20
        }
    }
    
    info = plan_info.get(selected_plan, plan_info["PRO"])
    
    # คำนวณราคา
    if payment_duration == 'monthly':
        base_price = info["monthly"]
        duration_days = 30
        duration_text = "รายเดือน"
    else:
        base_price = info["yearly"]
        duration_days = 365
        duration_text = "รายปี"
    
    tax = base_price * 0.07
    total_price = base_price + tax
    
    # Generate IDs
    payment_id = f"PAY_{random.randint(100000, 999999)}"
    order_id = f"ORD_{random.randint(100000, 999999)}"
    transaction_id = f"TXN_{random.randint(1000000, 9999999)}"
    
    # Calculate dates
    start_date = datetime.now().date()
    end_date = start_date + timedelta(days=duration_days)
    
    # Prepare payment data
    payment_data = {
        'payment_id': payment_id,
        'user_id': user_id,
        'order_id': order_id,
        'plan_type': selected_plan,
        'duration': payment_duration,
        'payment_method': st.session_state.payment_method,
        'amount': float(base_price),
        'tax': float(tax),
        'total_amount': float(total_price),
        'status': 'COMPLETED',
        'transaction_id': transaction_id,
        'payment_date': datetime.now(),
        'subscription_start': start_date,
        'subscription_end': end_date
    }
    
    # QR Code display for PromptPay
    if "พร้อมเพย์" in str(st.session_state.payment_method):
        st.markdown(f"""
        <div style='text-align: center; padding: 30px;'>
            <h3 style='color: {info["color"]};'>📱 สแกน QR Code เพื่อชำระเงิน</h3>
            <div style='font-size: 36px; font-weight: bold; color: {info["color"]}; margin: 20px 0;'>
                ฿{total_price:,.2f}
            </div>
            <div style='background: #f0f0f0; padding: 30px; border-radius: 10px; display: inline-block; margin: 20px 0;'>
                <div style='font-size: 60px;'>📱</div>
                <div style='font-size: 12px; color: #666;'>QR Code PromptPay</div>
            </div>
            <p style='color: #666;'>ระบบจะตรวจสอบการชำระเงินอัตโนมัติภายใน 5-10 นาที</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Simulate payment confirmation
        if st.button("✅ ฉันชำระเงินแล้ว", use_container_width=True, key="confirm_payment"):
            # Save payment to database
            if save_payment_to_db(payment_data):
                # Update user subscription
                if create_or_update_user(user_id, selected_plan, payment_duration):
                    # Generate welcome coupon based on plan
                    coupon_code = create_welcome_coupon(user_id, info["coupon_discount"])
                    
                    # Store coupon in session for display
                    st.session_state.last_coupon = coupon_code
                    st.session_state.payment_data = payment_data
                    
                    st.session_state.payment_step = 'payment_complete'
                    st.rerun()
                else:
                    st.error("❌ เกิดข้อผิดพลาดในการอัพเดตสมาชิก")
            else:
                st.error("❌ เกิดข้อผิดพลาดในการบันทึกการชำระเงิน")
    else:
        # For other payment methods, simulate immediate payment
        if st.button("✅ ยืนยันการชำระเงิน", use_container_width=True, key="confirm_payment_alt"):
            if save_payment_to_db(payment_data):
                if create_or_update_user(user_id, selected_plan, payment_duration):
                    coupon_code = create_welcome_coupon(user_id, info["coupon_discount"])
                    st.session_state.last_coupon = coupon_code
                    st.session_state.payment_data = payment_data
                    st.session_state.payment_step = 'payment_complete'
                    st.rerun()
                else:
                    st.error("❌ เกิดข้อผิดพลาดในการอัพเดตสมาชิก")
            else:
                st.error("❌ เกิดข้อผิดพลาดในการบันทึกการชำระเงิน")
    
    # Back button
    if st.button("← ย้อนกลับ", use_container_width=True, key="back_from_payment"):
        st.session_state.payment_step = 'payment_method'
        st.rerun()

def show_payment_page():
    """Handle payment processing"""
    
    # Initialize payment state
    if 'payment_duration' not in st.session_state:
        st.session_state.payment_duration = 'monthly'
    if 'payment_method' not in st.session_state:
        st.session_state.payment_method = None
    
    # Show appropriate step
    if st.session_state.payment_step == 'select_duration':
        show_duration_selection()
    elif st.session_state.payment_step == 'payment_method':
        show_payment_method()
    elif st.session_state.payment_step == 'payment_processing':
        process_payment()
    elif st.session_state.payment_step == 'payment_complete':
        show_payment_complete()

# ============================================
# STREAMLIT APP
# ============================================
def main():
    """Main Streamlit app"""
    st.set_page_config(
        page_title="Oil Price Analysis - สมัครสมาชิก",
        page_icon="⛽",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Add custom CSS
    st.markdown("""
    <style>
    .stButton>button {
        border-radius: 8px;
        padding: 10px 24px;
    }
    .stAlert {
        border-radius: 10px;
    }
    div[data-testid="stExpander"] div[role="button"] p {
        font-size: 1.2rem;
        font-weight: 600;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Run the package page
    show_package_page()

# ==============================
# 6. SIDEBAR
# ==============================
def premium_sidebar():
    """Premium sidebar"""
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 2rem 1rem;">
            <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">⛽</div>
            <h2 style="color: var(--primary-dark); margin: 0; font-weight: 700;">OILSOPHAENG</h2>
            <p style="color: var(--secondary-dark); margin: 0; font-size: 0.9rem;">Oil Analytics Platform</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # User info
        plan_label = (
            "⭐ PRO Member" if st.session_state['subscribe_flag'] == 1
            else "⭐ ENTERPRISE Member" if st.session_state['subscribe_flag'] == 2
            else "🔵 Free Plan"
        )

        # ใส่ค่า plan_label ลงใน HTML
        st.markdown(f"""
        <div style="background: rgba(255, 255, 255, 0.7); backdrop-filter: blur(10px); 
                    border-radius: 20px; padding: 1.5rem; margin-bottom: 1.5rem;
                    border: 1px solid rgba(255, 255, 255, 0.2);">
            <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                <div style="width: 50px; height: 50px; background: var(--gradient-primary); 
                            border-radius: 50%; display: flex; align-items: center; justify-content: center; 
                            margin-right: 1rem; color: white; font-size: 1.2rem;">
                    👤
                </div>
                <div>
                    <div style="font-weight: 600; color: var(--primary-dark);">{st.session_state['user_name']}</div>
                    <div style="font-size: 0.85rem; color: var(--secondary-dark);">
                        {plan_label}
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Navigation
        st.markdown("### 🧭 Navigation")
        
        # กำหนดเมนูทั้งหมด
        menu_items = [
            ("🏠", "Home", "dashboard"),
            ("📊", "Oil Calculation Distance", "fulecal"),
            ("📈", "Oil Prediction", "analytics"),
            ("🤖", "AI Assistant", "ai"),
            ("🚕", "Oil Distance", "distance"),
            ("🎮", "Oil Cost Simulate", "simmulate"),
            ("🔖", "Report", "reports"),
            ("💼", "Package", "package"),
            ("⚙️", "Setting", "settings")
        ]
        
        # ตรวจสอบสิทธิ์การเข้าถึงตาม plan
        for icon, label, page in menu_items:
            if st.session_state['subscribe_flag'] == 0:  
                if page in ["ai", "analytics", "distance", "simmulate"]:
                    continue
            elif st.session_state['subscribe_flag'] == 1:  
                if page == "simmulate":
                    continue
            
            # สร้างปุ่มสำหรับเมนูที่อนุญาต
            if st.button(
                f"{icon} {label}",
                key=f"nav_{page}",
                use_container_width=True,
                type="primary" if st.session_state['current_page'] == page else "secondary"
            ):
                st.session_state['current_page'] = page
                st.rerun()
        
        st.markdown("---")
        
        # Quick Actions
        st.markdown("### ⚡ Quick Actions")
        
        if st.session_state['subscribe_flag'] == 0:
            if st.button("✨ Upgrade to PRO", use_container_width=True):
                go_to_package()
        elif st.session_state['subscribe_flag'] == 1:
            if st.button("✨ Upgrade to ENTERPRISE", use_container_width=True):
                go_to_package()
        
        if st.button("🔄 Refresh Information", use_container_width=True):
            st.info("กำลังอัปเดตข้อมูลล่าสุด...")
            time.sleep(1)
            st.rerun()
        
        if st.button("📥 Download Data", use_container_width=True):
            st.success("กำลังส่งออกข้อมูล...")
        
        st.markdown("---")
        
        # Logout button
        if st.button("🚪 Logoff", use_container_width=True, type="secondary"):
            logoff()
        
        # Footer
        st.markdown("""
        <div style="text-align: center; padding: 1rem; color: var(--secondary-dark); font-size: 0.85rem;">
            <div style="margin-bottom: 0.5rem;">© 2025 OILSOPHAENG</div>
            <div>Version 2.0.1</div>
        </div>
        """, unsafe_allow_html=True)


def show_fule_cal():
# calc_trip_cost.py


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



def show_oil_price_daily():
    st.markdown("""
    <style>
    /* ตัวอักษรใน Fuel Types Selectbox */
    div[data-testid="stSelectbox"] div[data-baseweb="select"] span {
        color: #000000 !important;
        font-weight: 500 !important;
    }

    /* ตัวอักษรใน Companies Multiselect */
    div[data-testid="stMultiSelect"] div[data-baseweb="select"] span {
        color: #000000 !important;
        font-weight: 500 !important;
    }

    /* ตัวอักษรใน Latest Data Date input */
    div[data-testid="stDateInput"] input {
        color: #000000 !important;
        font-weight: 500 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    # -------------------------------------------------
    # Page config
    # -------------------------------------------------
    st.set_page_config(page_title="Oil Price Forecast (Prophet)", page_icon="⛽", layout="wide")
    st.title("⛽ Oil Price Forecast")
    st.caption("แหล่งข้อมูล: PROJECT_5001.OIL_PRICE.OIL_TRANSACTION")

    # -------------------------------------------------
    # Snowflake helpers
    # -------------------------------------------------
    sf = st.secrets["connections"]["snowflake"]

    def get_connection():
        return snowflake.connector.connect(
            account=sf["account"], user=sf["user"], password=sf["password"],
            role=sf["role"], warehouse=sf["warehouse"],
            database=sf["database"], schema=sf["schema"]
        )

    @st.cache_data(ttl=1800, show_spinner=False)
    def run_query(sql: str) -> pd.DataFrame:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(sql)
        df = pd.DataFrame(cur.fetchall(), columns=[d[0] for d in cur.description])
        cur.close(); conn.close()
        return df

    @st.cache_data(ttl=1800, show_spinner=False)
    def load_options():
        # ดึง TYPE_NAME และ TYPE_ID เรียงตาม TYPE_ID
        sql = """
        SELECT 
            OTY.TYPE_NAME
        FROM OIL_TRANSACTION OT
        JOIN OIL_TYPE OTY ON OT.TYPE_ID = OTY.TYPE_NO
        GROUP BY OT.TYPE_ID, OTY.TYPE_NAME
        ORDER BY OT.TYPE_ID
        """

        types = run_query(sql)["TYPE_NAME"].tolist()

        # ดึงรายชื่อบริษัท
        # ดึงรายชื่อบริษัท
        sql_comp = """
            SELECT DISTINCT COM.COMPANY_ID, COM.COMPANY_NAME
            FROM OIL_TRANSACTION OT
            JOIN COMPANY COM ON OT.COMPANY_ID = COM.COMPANY_ID
            ORDER BY COM.COMPANY_ID
        """
        companies = run_query(sql_comp)["COMPANY_NAME"].tolist()

        # ดึงวันที่ min-max
        dmm = run_query("SELECT MIN(DATE_TRANSACTION) AS DMIN, MAX(DATE_TRANSACTION) AS DMAX FROM OIL_TRANSACTION")
        dmin = pd.to_datetime(dmm.iloc[0]["DMIN"]).date()
        dmax = pd.to_datetime(dmm.iloc[0]["DMAX"]).date()

        return types, companies, dmin, dmax

    types, companies, dmin, dmax = load_options()


    # -------------------------------------------------
    # Sidebar controls
    # -------------------------------------------------
    with st.sidebar:
        st.header("Filters")
        sel_type = st.selectbox("ชนิดน้ำมัน (TYPE_ID)", options=types)
        sel_companies = st.multiselect("บริษัท (COMPANY_ID)", options=companies, default=companies)
        date_range = st.date_input("ช่วงวันที่", value=(dmin, dmax), min_value=dmin, max_value=dmax)

        st.divider()
        st.header("Prophet settings")
        interval_width = st.slider("Uncertainty interval (เช่น 0.9 = 90%)", 0.5, 0.98, 0.9, 0.01)
        seasonality_mode = st.selectbox("Seasonality mode", ["additive", "multiplicative"], index=0)
        add_weekly = st.checkbox("ใช้ seasonality รายสัปดาห์", value=True)
        add_yearly = st.checkbox("ใช้ seasonality รายปี", value=True)
        add_daily = st.checkbox("ใช้ seasonality รายวัน", value=False)
        changepoint_prior_scale = st.number_input("ความยืดหยุ่น trend (changepoint_prior_scale)", value=0.05, min_value=0.001, step=0.01, format="%.3f")
        seasonality_prior_scale = st.number_input("seasonality_prior_scale", value=10.0, min_value=1.0, step=1.0)
        n_changepoints = st.slider("จำนวน changepoints", 5, 50, 25)

        st.divider()
        forecast_days = st.slider("พยากรณ์ล่วงหน้า (วัน)", 7, 120, 30)

        st.divider()
        do_backtest = st.checkbox("ทำ Backtest (Prophet cross_validation)", value=False)
        init_pct = st.slider("Initial train % (สำหรับ backtest)", 50, 90, 80)
        horizon_days = st.slider("Horizon สำหรับ backtest (วัน)", 7, 60, 30)
        period_days = st.slider("ระยะเลื่อนระหว่าง cutoff (วัน)", 7, 60, 15)

    # -------------------------------------------------
    # Load data
    # -------------------------------------------------
    start_date, end_date = date_range

    if sel_companies:
        companies_str = ",".join(f"'{c}'" for c in sel_companies)  # ใส่ single quotes
        comp_clause = f"COM.COMPANY_NAME IN ({companies_str})"
    else:
        comp_clause = "1=1"

    sql = f"""
    SELECT 
        OT.DATE_TRANSACTION,
        OT.TYPE_ID,
        OTY.TYPE_NAME,
        OT.COMPANY_ID,
        OT.PRICE
    FROM OIL_TRANSACTION OT
    JOIN OIL_TYPE OTY ON OT.TYPE_ID = OTY.TYPE_NO
    JOIN COMPANY COM ON OT.COMPANY_ID = COM.COMPANY_ID
    WHERE OTY.TYPE_NAME = '{sel_type}'
    AND {comp_clause}
    AND OT.DATE_TRANSACTION BETWEEN '{start_date}' AND '{end_date}'
    ORDER BY OT.DATE_TRANSACTION ASC
    """
    raw = run_query(sql)

    # Clean
    raw["DATE_TRANSACTION"] = pd.to_datetime(raw["DATE_TRANSACTION"], errors="coerce")
    raw["PRICE"] = pd.to_numeric(raw["PRICE"], errors="coerce")
    raw = raw.dropna(subset=["DATE_TRANSACTION", "PRICE"]).sort_values("DATE_TRANSACTION")

    if raw.empty:
        st.error("⚠️ ไม่มีข้อมูลหลังการกรอง — ลองปรับช่วงวันที่/บริษัท")
        st.stop()

    with st.expander("ตัวอย่างข้อมูล (Top 10)"):
        st.write(raw.head(10))

    # -------------------------------------------------
    # Aggregate (ถ้าเลือกหลายบริษัท → เฉลี่ยรายวัน)
    # -------------------------------------------------
    df = (
        raw.groupby("DATE_TRANSACTION", as_index=False)
        .agg(PRICE=("PRICE", "mean"))
        .rename(columns={"DATE_TRANSACTION": "ds", "PRICE": "y"})
    )

    # Prophet ต้องการ ds (datetime) และ y (float)
    df["ds"] = pd.to_datetime(df["ds"], errors="coerce")
    df["y"]  = pd.to_numeric(df["y"], errors="coerce")
    df = df.dropna(subset=["ds", "y"]).sort_values("ds")

    if len(df) < 30:
        st.warning("ข้อมูลน้อยกว่า 30 จุด — Prophet อาจทำนายไม่เสถียร")
    if df["y"].max() > 1e6:
        st.warning("สเกลราคาดูผิดปกติ (หลักล้าน) — ตรวจความถูกต้องของ PRICE หน่วยบาท/ลิตร")

    # -------------------------------------------------
    # Train Prophet
    # -------------------------------------------------
    m = Prophet(
        interval_width=interval_width,
        seasonality_mode=seasonality_mode,
        changepoint_prior_scale=changepoint_prior_scale,
        seasonality_prior_scale=seasonality_prior_scale,
        n_changepoints=n_changepoints
    )

    if add_weekly: m.add_seasonality(name="weekly", period=7, fourier_order=3)
    if add_yearly: m.add_seasonality(name="yearly", period=365.25, fourier_order=10)
    if add_daily:  m.add_seasonality(name="daily", period=1, fourier_order=8)

    with st.spinner("กำลังเทรน Prophet..."):
        m.fit(df)

    # -------------------------------------------------
    # Forecast future
    # -------------------------------------------------
    future = m.make_future_dataframe(periods=forecast_days, freq="D", include_history=True)
    forecast = m.predict(future)

    # -------------------------------------------------
    # Plotly: Forecast + uncertainty interval
    # -------------------------------------------------
    st.subheader(f"🔮 Forecast {forecast_days} วัน (รวมแถบความไม่แน่นอน)")
    fig_forecast = plot_plotly(m, forecast)
    fig_forecast.update_layout(height=480, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    st.plotly_chart(fig_forecast, use_container_width=True)

    st.subheader("Component plots (trend/seasonality)")
    fig_comp = plot_components_plotly(m, forecast)
    fig_comp.update_layout(height=600)
    st.plotly_chart(fig_comp, use_container_width=True)

    # ตารางผลพยากรณ์
    with st.expander("ตารางผลพยากรณ์ (yhat, yhat_lower, yhat_upper)"):
        st.dataframe(
            forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]].tail(forecast_days),
            use_container_width=True
        )
        st.download_button(
            "⬇️ ดาวน์โหลด Forecast (CSV)",
            forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]].to_csv(index=False).encode("utf-8"),
            file_name=f"prophet_forecast_type{sel_type}.csv",
            mime="text/csv"
        )

    # -------------------------------------------------
    # Backtest (optional) ด้วย Prophet cross_validation
    # -------------------------------------------------
    if do_backtest:
        st.subheader("📏 Backtest (Prophet cross_validation)")
        # ตั้งค่า initial/period/horizon ตามสัดส่วนที่เลือก
        total_days = (df["ds"].max() - df["ds"].min()).days
        initial_days = max(int(total_days * init_pct / 100), horizon_days * 2)  # กันไม่ให้สั้นเกินไป

        try:
            with st.spinner("กำลังรัน cross_validation... (อาจใช้เวลาขึ้นกับขนาดข้อมูล)"):
                df_cv = cross_validation(
                    m,
                    initial=f"{initial_days} days",
                    period=f"{period_days} days",
                    horizon=f"{horizon_days} days",
                    parallel="processes"  # เร็วขึ้นหน่อย
                )
                df_perf = performance_metrics(df_cv)
            # แสดงผล
            c1, c2, c3 = st.columns(3)
            c1.metric("RMSE", f"{df_perf['rmse'].iloc[-1]:,.3f}")
            c2.metric("MAE",  f"{df_perf['mae'].iloc[-1]:,.3f}")
            c3.metric("MAPE", f"{df_perf['mape'].iloc[-1]*100:,.2f}%")

            with st.expander("ดูตาราง performance metrics ทั้งหมด"):
                st.dataframe(df_perf, use_container_width=True)
                st.download_button(
                    "⬇️ ดาวน์โหลดผล Backtest (CSV)",
                    df_perf.to_csv(index=False).encode("utf-8"),
                    file_name=f"prophet_backtest_type{sel_type}.csv",
                    mime="text/csv"
                )

            # กราฟพยากรณ์กับจริงในแต่ละ cutoff
            st.subheader("Actual vs Predicted (ตาม cutoff ใน backtest)")
            fig_cv = go.Figure()
            fig_cv.add_trace(go.Scatter(x=df_cv['ds'], y=df_cv['y'], name='Actual', mode='lines', line=dict(color='#1f77b4')))
            fig_cv.add_trace(go.Scatter(x=df_cv['ds'], y=df_cv['yhat'], name='Predicted', mode='lines', line=dict(color='#d62728')))
            fig_cv.update_layout(height=420, xaxis_title="วันที่", yaxis_title="ราคา (บาท/ลิตร)", legend=dict(orientation="h"))
            st.plotly_chart(fig_cv, use_container_width=True)

        except Exception as e:
            st.warning(f"Backtest ล้มเหลว: {e}\nลองลด horizon หรือเพิ่ม initial ให้ยาวขึ้น แล้วรันใหม่ครับ")

# ==============================
# AI ASSISTANT FUNCTIONS
# ==============================
def show_ai_assistant():
    st.title("🤖 AI Assistant - Oil Analytics")

    # Status badge
    if 'subscribe_flag' in st.session_state and st.session_state['subscribe_flag'] >= 1:
        st.success("✅ AI Assistant พร้อมใช้งาน")
    else:
        st.error("⛔ คุณต้องอัปเกรดเป็น PRO เพื่อใช้งานฟีเจอร์นี้")
        return

    # CSS สำหรับ styling
    st.markdown("""
    <style>
    .user-box {
        background-color: #f0f2f6;
        color: black;
        padding: 12px 16px;
        border-radius: 10px;
        margin: 8px 0;
        border-left: 4px solid #2196F3;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        max-width: 80%;
        margin-left: auto;
    }
    .bot-box {
        background-color: white;
        color: black;
        padding: 12px 16px;
        border-radius: 10px;
        margin: 8px 0;
        border-left: 4px solid #4CAF50;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        max-width: 80%;
    }
    .source-box {
        background-color: #e8f5e9;
        color: #2e7d32;
        padding: 8px 12px;
        border-radius: 6px;
        margin: 4px 0;
        font-size: 12px;
        border-left: 3px solid #4CAF50;
    }
    .quick-question {
        padding: 8px 12px;
        margin: 4px;
        border-radius: 8px;
        border: 1px solid #ddd;
        cursor: pointer;
        transition: all 0.2s;
    }
    .quick-question:hover {
        background-color: #f5f5f5;
        transform: translateY(-2px);
    }
    </style>
    """, unsafe_allow_html=True)

    # Initialize chat history
    if "ai_chat_history" not in st.session_state:
        st.session_state.ai_chat_history = []

    # แสดงประวัติการสนทนา
    st.markdown("### 💬 สนทนากับ AI Assistant")

    # Container สำหรับแชท
    chat_container = st.container()

    with chat_container:
        for msg in st.session_state.ai_chat_history:
            if msg["role"] == "user":
                st.markdown(
                    f'<div class="user-box">👤 คุณ:<br>{msg["content"]}</div>',
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f'<div class="bot-box">🤖 AI Assistant:<br>{msg["content"]}</div>',
                    unsafe_allow_html=True
                )
                
                # แสดง Source (ถ้ามี)
                if msg.get("sources"):
                    with st.expander("📚 แหล่งข้อมูลอ้างอิง"):
                        for s in msg["sources"]:
                            st.markdown(
                                f'<div class="source-box">📄 {s}</div>',
                                unsafe_allow_html=True
                            )

    # Quick questions
    st.markdown("### 💡 คำถามที่พบบ่อย")

    col1, col2 = st.columns(2)

    quick_questions = [
        ("ราคาน้ำมันล่าสุดเป็นอย่างไรบ้าง?", "📈"),
        ("บริษัทน้ำมันไหนถูกที่สุด?", "🏆"),
        ("ราคาเฉลี่ยของน้ำมันเบนซิน?", "💰"),
        ("แนวโน้มราคาน้ำมันเดือนหน้า?", "📊"),
        ("ควรเติมน้ำมันเวลาไหนดีที่สุด?", "⏰"),
        ("น้ำมันดีเซลราคาเท่าไหร่?", "⛽"),
    ]

    for i, (question, icon) in enumerate(quick_questions):
        col = col1 if i % 2 == 0 else col2
        with col:
            if st.button(f"{icon} {question}", key=f"quick_{i}", use_container_width=True):
                process_ai_query(question)
                st.rerun()

    # ช่องพิมพ์ข้อความ
    st.markdown("---")
    col_input, col_send = st.columns([4, 1])

    with col_input:
        user_input = st.text_input(
            "พิมพ์คำถามของคุณ...",
            key="ai_chat_input",
            label_visibility="collapsed",
            placeholder="ถามอะไรเกี่ยวกับข้อมูลน้ำมัน..."
        )

    with col_send:
        send_button = st.button("🚀 ส่ง", use_container_width=True)

    # เมื่อกดส่ง
    if send_button and user_input:
        process_ai_query(user_input)
        st.rerun()

def process_ai_query(query):

    # เก็บข้อความผู้ใช้
    st.session_state.ai_chat_history.append({"role": "user", "content": query})
    client = boto3.client("bedrock-runtime", region_name="ap-southeast-1")

# MODEL ARN (คงของคุณ)
    MODEL_ARN = "arn:aws:bedrock:ap-southeast-1:905418199182:inference-profile/apac.amazon.nova-lite-v1:0"

# YOUR LAMBDA API URL
    LAMBDA_URL = "https://ur66rgdmrb.execute-api.us-east-1.amazonaws.com/prod"

    # เรียก Lambda API
    try:
        with st.spinner("🤖 AI กำลังคิดคำตอบ..."):
            payload = {"prompt": query}
            
            response = requests.post(
                LAMBDA_URL,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            # Parse response
            if response.status_code == 200:
                data = response.json()
                body = json.loads(data["body"])
                
                answer = body.get("answer", "ขออภัย ไม่สามารถให้คำตอบได้ในขณะนี้")
                sources = body.get("sources", [])
                
                # เก็บคำตอบ
                st.session_state.ai_chat_history.append({
                    "role": "assistant",
                    "content": answer,
                    "sources": sources
                })
            else:
                st.session_state.ai_chat_history.append({
                    "role": "assistant",
                    "content": "ขออภัย ระบบขัดข้องชั่วคราว กรุณาลองใหม่ในภายหลัง"
                })
                
    except requests.exceptions.Timeout:
        st.session_state.ai_chat_history.append({
            "role": "assistant",
            "content": "ขออภัย การเชื่อมต่อใช้เวลานานเกินไป กรุณาลองใหม่อีกครั้ง"
        })
    except Exception as e:
        st.session_state.ai_chat_history.append({
            "role": "assistant",
            "content": f"เกิดข้อผิดพลาด: {str(e)}"
        })


def _ai_analyze_price_query():
    """วิเคราะห์คำถามเกี่ยวกับราคา"""
    try:
        # ดึงข้อมูลจาก database
        conn = st.connection("snowflake", type="snowflake")
        query = """
        SELECT 
            DATE_TRANSACTION,
            COMPANY_NAME,
            TYPE_NAME,
            PRICE
        FROM OIL_TRANSACTION OT
        JOIN COMPANY COM ON OT.COMPANY_ID = COM.COMPANY_ID
        JOIN OIL_TYPE OTY ON OT.TYPE_ID = OTY.TYPE_NO
        ORDER BY DATE_TRANSACTION DESC
        LIMIT 20
        """
        
        df = conn.query(query)
        
        if df.empty:
            return "ไม่พบข้อมูลราคาในระบบ"
        
        # คำนวณสถิติ
        avg_price = df['PRICE'].mean()
        min_price = df['PRICE'].min()
        max_price = df['PRICE'].max()
        
        # แสดงตารางข้อมูลล่าสุด
        st.dataframe(df.head(5), use_container_width=True)
        
        return f"""
        **📊 สรุปข้อมูลราคาล่าสุด:**
        
        • 📈 ราคาเฉลี่ย: **฿{avg_price:.2f}** ต่อลิตร
        • 📉 ราคาต่ำสุด: **฿{min_price:.2f}** ต่อลิตร
        • 📈 ราคาสูงสุด: **฿{max_price:.2f}** ต่อลิตร
        
        **💡 ข้อมูลล่าสุดแสดงด้านบน**
        """
        
    except Exception as e:
        return f"เกิดข้อผิดพลาดในการดึงข้อมูล: {str(e)}"

def _ai_analyze_company_query():
    """วิเคราะห์คำถามเกี่ยวกับบริษัท"""
    try:
        conn = st.connection("snowflake", type="snowflake")
        query = """
        SELECT 
            COMPANY_NAME,
            AVG(PRICE) as AVG_PRICE,
            MIN(PRICE) as MIN_PRICE,
            MAX(PRICE) as MAX_PRICE,
            COUNT(*) as TRANSACTION_COUNT
        FROM OIL_TRANSACTION OT
        JOIN COMPANY COM ON OT.COMPANY_ID = COM.COMPANY_ID
        GROUP BY COMPANY_NAME
        ORDER BY AVG_PRICE
        """
        
        df = conn.query(query)
        
        if df.empty:
            return "ไม่พบข้อมูลบริษัทในระบบ"
        
        # หาบริษัทที่ราคาถูกที่สุดและแพงที่สุด
        cheapest = df.loc[df['AVG_PRICE'].idxmin()]
        expensive = df.loc[df['AVG_PRICE'].idxmax()]
        
        # แสดงตาราง
        st.dataframe(df, use_container_width=True)
        
        return f"""
        **🏢 การเปรียบเทียบบริษัทน้ำมัน:**
        
        **🏆 บริษัทที่ราคาถูกที่สุด:**
        • {cheapest['COMPANY_NAME']}: ฿{cheapest['AVG_PRICE']:.2f} ต่อลิตร
        
        **📈 บริษัทที่ราคาแพงที่สุด:**
        • {expensive['COMPANY_NAME']}: ฿{expensive['AVG_PRICE']:.2f} ต่อลิตร
        
        **📊 ข้อมูลทั้งหมดแสดงในตารางด้านบน**
        """
        
    except Exception as e:
        return f"เกิดข้อผิดพลาดในการดึงข้อมูล: {str(e)}"

def _ai_analyze_trend_query():
    """วิเคราะห์แนวโน้มราคา"""
    try:
        conn = st.connection("snowflake", type="snowflake")
        query = """
        SELECT 
            DATE(DATE_TRANSACTION) as TRANSACTION_DATE,
            AVG(PRICE) as AVG_PRICE
        FROM OIL_TRANSACTION
        WHERE DATE_TRANSACTION >= DATEADD(day, -7, CURRENT_DATE())
        GROUP BY DATE(DATE_TRANSACTION)
        ORDER BY TRANSACTION_DATE
        """
        
        df = conn.query(query)
        
        if df.empty:
            return "ไม่พบข้อมูลสำหรับวิเคราะห์แนวโน้ม"
        
        # คำนวณการเปลี่ยนแปลง
        if len(df) >= 2:
            last_price = df['AVG_PRICE'].iloc[-1]
            prev_price = df['AVG_PRICE'].iloc[-2]
            change = last_price - prev_price
            change_percent = (change / prev_price) * 100
            
            if change > 0:
                trend = f"📈 เพิ่มขึ้น **฿{change:.2f}** ({change_percent:.1f}%)"
            elif change < 0:
                trend = f"📉 ลดลง **฿{abs(change):.2f}** ({abs(change_percent):.1f}%)"
            else:
                trend = "➡️ คงที่"
        else:
            trend = "➡️ ข้อมูลไม่เพียงพอ"
            last_price = df['AVG_PRICE'].iloc[0] if len(df) > 0 else 0
        
        # แสดงข้อมูล
        st.dataframe(df, use_container_width=True)
        
        return f"""
        **📈 แนวโน้มราคาน้ำมัน 7 วันล่าสุด:**
        
        • {trend}
        • 💰 ราคาล่าสุด: **฿{last_price:.2f}** ต่อลิตร
        • 📅 จำนวนวันที่มีข้อมูล: **{len(df)}** วัน
        
        **📊 ข้อมูลรายวันแสดงในตารางด้านบน**
        """
        
    except Exception as e:
        return f"เกิดข้อผิดพลาดในการวิเคราะห์: {str(e)}"

def _ai_generate_summary():
    """สร้างสรุปข้อมูล"""
    try:
        conn = st.connection("snowflake", type="snowflake")
        
        # ดึงข้อมูลสรุป
        query1 = "SELECT COUNT(*) as TOTAL_TRANSACTIONS FROM OIL_TRANSACTION"
        query2 = "SELECT COUNT(DISTINCT COMPANY_ID) as TOTAL_COMPANIES FROM OIL_TRANSACTION"
        query3 = "SELECT AVG(PRICE) as AVG_PRICE FROM OIL_TRANSACTION"
        
        total_trans = conn.query(query1).iloc[0]['TOTAL_TRANSACTIONS']
        total_companies = conn.query(query2).iloc[0]['TOTAL_COMPANIES']
        avg_price = conn.query(query3).iloc[0]['AVG_PRICE']
        
        return f"""
        **📋 รายงานสรุปข้อมูลน้ำมัน:**
        
        **📊 สถิติโดยรวม:**
        • 💰 ราคาเฉลี่ย: **฿{avg_price:.2f}** ต่อลิตร
        • 🔢 จำนวนธุรกรรมทั้งหมด: **{total_trans}** รายการ
        • 🏢 จำนวนบริษัททั้งหมด: **{total_companies}** บริษัท
        
        **💡 ข้อเสนอแนะ:**
        • ติดตามราคาในแอปพลิเคชันเพื่อรับข้อมูลล่าสุด
        • เปรียบเทียบราคาก่อนตัดสินใจซื้อ
        • วางแผนการซื้อล่วงหน้าในช่วงราคาต่ำ
        """
        
    except Exception as e:
        return f"เกิดข้อผิดพลาดในการสร้างรายงาน: {str(e)}"

# ==============================
# QUICK ACTION FUNCTIONS
# ==============================

def _ai_analyze_price_trend():
    """วิเคราะห์แนวโน้มราคา"""
    return _ai_analyze_trend_query()

def _ai_analyze_cheapest_company():
    """วิเคราะห์บริษัทที่ราคาถูกที่สุด"""
    return _ai_analyze_company_query()

def _ai_compare_companies():
    """เปรียบเทียบบริษัท"""
    return _ai_analyze_company_query()

def _ai_analyze_price_data(start_date, end_date):
    """วิเคราะห์ข้อมูลราคา"""
    try:
        conn = st.connection("snowflake", type="snowflake")
        query = f"""
        SELECT 
            DATE_TRANSACTION,
            COMPANY_NAME,
            TYPE_NAME,
            PRICE
        FROM OIL_TRANSACTION OT
        JOIN COMPANY COM ON OT.COMPANY_ID = COM.COMPANY_ID
        JOIN OIL_TYPE OTY ON OT.TYPE_ID = OTY.TYPE_NO
        WHERE DATE_TRANSACTION BETWEEN '{start_date}' AND '{end_date}'
        ORDER BY DATE_TRANSACTION
        """
        
        df = conn.query(query)
        
        if df.empty:
            st.warning("ไม่พบข้อมูลในช่วงเวลาที่เลือก")
            return
        
        # แสดงข้อมูล
        st.dataframe(df, use_container_width=True)
        
        # สรุปสถิติ
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("ราคาเฉลี่ย", f"฿{df['PRICE'].mean():.2f}")
        with col2:
            st.metric("ราคาสูงสุด", f"฿{df['PRICE'].max():.2f}")
        with col3:
            st.metric("ราคาต่ำสุด", f"฿{df['PRICE'].min():.2f}")
            
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาด: {str(e)}")

def _ai_analyze_company_data(start_date, end_date):
    """วิเคราะห์ข้อมูลบริษัท"""
    try:
        conn = st.connection("snowflake", type="snowflake")
        query = f"""
        SELECT 
            COMPANY_NAME,
            AVG(PRICE) as AVG_PRICE,
            MIN(PRICE) as MIN_PRICE,
            MAX(PRICE) as MAX_PRICE,
            COUNT(*) as TRANSACTION_COUNT
        FROM OIL_TRANSACTION OT
        JOIN COMPANY COM ON OT.COMPANY_ID = COM.COMPANY_ID
        WHERE DATE_TRANSACTION BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY COMPANY_NAME
        ORDER BY AVG_PRICE
        """
        
        df = conn.query(query)
        
        if df.empty:
            st.warning("ไม่พบข้อมูลในช่วงเวลาที่เลือก")
            return
        
        # แสดงข้อมูล
        st.dataframe(df, use_container_width=True)
        
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาด: {str(e)}")

def _ai_show_latest_data():
    """แสดงข้อมูลล่าสุด"""
    try:
        conn = st.connection("snowflake", type="snowflake")
        query = """
        SELECT 
            DATE_TRANSACTION,
            COMPANY_NAME,
            TYPE_NAME,
            PRICE
        FROM OIL_TRANSACTION OT
        JOIN COMPANY COM ON OT.COMPANY_ID = COM.COMPANY_ID
        JOIN OIL_TYPE OTY ON OT.TYPE_ID = OTY.TYPE_NO
        ORDER BY DATE_TRANSACTION DESC
        LIMIT 50
        """
        
        df = conn.query(query)
        
        if df.empty:
            st.warning("ไม่พบข้อมูลล่าสุด")
            return
        
        # แสดงข้อมูล
        st.dataframe(df, use_container_width=True)
        
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาด: {str(e)}")

def _ai_generate_report(report_type):
    """สร้างรายงาน"""
    try:
        conn = st.connection("snowflake", type="snowflake")
        
        if report_type == "รายงานรายวัน":
            query = """
            SELECT 
                DATE(DATE_TRANSACTION) as DATE,
                COUNT(*) as TRANSACTIONS,
                AVG(PRICE) as AVG_PRICE,
                MIN(PRICE) as MIN_PRICE,
                MAX(PRICE) as MAX_PRICE
            FROM OIL_TRANSACTION
            WHERE DATE_TRANSACTION >= DATEADD(day, -1, CURRENT_DATE())
            GROUP BY DATE(DATE_TRANSACTION)
            """
        elif report_type == "รายงานรายสัปดาห์":
            query = """
            SELECT 
                DATE_TRUNC('week', DATE_TRANSACTION) as WEEK,
                COUNT(*) as TRANSACTIONS,
                AVG(PRICE) as AVG_PRICE,
                MIN(PRICE) as MIN_PRICE,
                MAX(PRICE) as MAX_PRICE
            FROM OIL_TRANSACTION
            WHERE DATE_TRANSACTION >= DATEADD(week, -1, CURRENT_DATE())
            GROUP BY DATE_TRUNC('week', DATE_TRANSACTION)
            """
        else:  # รายเดือน
            query = """
            SELECT 
                DATE_TRUNC('month', DATE_TRANSACTION) as MONTH,
                COUNT(*) as TRANSACTIONS,
                AVG(PRICE) as AVG_PRICE,
                MIN(PRICE) as MIN_PRICE,
                MAX(PRICE) as MAX_PRICE
            FROM OIL_TRANSACTION
            WHERE DATE_TRANSACTION >= DATEADD(month, -1, CURRENT_DATE())
            GROUP BY DATE_TRUNC('month', DATE_TRANSACTION)
            """
        
        df = conn.query(query)
        
        if df.empty:
            st.warning(f"ไม่พบข้อมูลสำหรับ{report_type}")
            return
        
        # แสดงรายงาน
        st.markdown(f"### 📋 {report_type}")
        st.dataframe(df, use_container_width=True)
        
        # สรุป
        col1, col2 = st.columns(2)
        with col1:
            st.metric("จำนวนธุรกรรม", f"{df['TRANSACTIONS'].sum():,}")
        with col2:
            st.metric("ราคาเฉลี่ย", f"฿{df['AVG_PRICE'].mean():.2f}")
            
        st.success(f"✅ สร้าง{report_type}เรียบร้อยแล้ว")
        
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการสร้างรายงาน: {str(e)}")

def show_oil_cost_simulate():
        # ---------------------------
    # Page config + Premium Theme
    # ---------------------------
    st.set_page_config(
        page_title="Oil Cost Simulation | Premium",
        page_icon="⛽",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # ---------- Global CSS ให้ match กับ dashboard เพื่อน ----------
    st.markdown(
        """
    <style>
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

        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }

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

        /* การ์ดหลัก */
        .premium-card {
            background: var(--card-bg);
            border-radius: 16px;
            padding: 1.5rem;
            border: 1px solid #e2e8f0;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1),
                        0 2px 4px -1px rgba(0, 0, 0, 0.06);
            transition: all 0.3s ease;
            height: 100%;
        }

        .premium-card:hover {
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1),
                        0 4px 6px -2px rgba(0, 0, 0, 0.05);
            transform: translateY(-2px);
        }

        .section-title {
            font-size: 1.1rem;
            font-weight: 600;
            color: var(--primary);
            margin-bottom: 0.75rem;
            display: flex;
            align-items: center;
            gap: 0.4rem;
        }

        .section-title span.icon {
            font-size: 1.3rem;
        }

        /* กล่องผลลัพธ์ด้านล่างให้ดูกลมกลืน */
        .result-box {
            border-radius: 0.8rem;
            padding: 1.0rem 1.2rem;
            background: linear-gradient(135deg, var(--light-bg), #ffffff);
            border: 1px solid #e2e8f0;
            margin-top: 0.5rem;
        }

        .result-main-number {
            font-size: 1.4rem;
            font-weight: 700;
            color: var(--primary);
        }

        /* กล่องราคาล่าสุด */
        .latest-price-box {
            background: linear-gradient(135deg, #f0f9ff, #e0f2fe);
            border: 1px solid #bae6fd;
            border-radius: 10px;
            padding: 1rem;
            margin-bottom: 1rem;
        }

        /* footer เว้นระยะท้ายหน้า */
        .footer-space {
            height: 1.5rem;
        }
    </style>
    """,
        unsafe_allow_html=True,
    )

    # ---------------------------
    # Premium Header
    # ---------------------------
    header_col1, header_col2, header_col3 = st.columns([1, 2, 1])
    with header_col2:
        st.markdown(
            """
            <div style="text-align: center; margin-bottom: 2rem;">
                <h1 style="font-size: 2.4rem; margin-bottom: 0.5rem;">
                    ⛽ Oil Cost Simulation
                </h1>
                <p style="color: var(--text-secondary); font-size: 1.0rem; margin-top: 0;">
                    คำนวณต้นทุนรวมจากราคาน้ำมัน และเปรียบเทียบกับราคาจริงล่าสุด
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # =========================
    # ดึงข้อมูลราคาน้ำมัน (แบบ long)
    # =========================
    @st.cache_data
    def load_data():
        return get_oilprice_long()

    df = load_data()

    # หาวันล่าสุดของข้อมูลทั้งหมด
    latest_date_all = df["Date"].max()
    latest_df = df[df["Date"] == latest_date_all]

    # =========================
    # 1) เตรียม default ต่าง ๆ
    # =========================

    # รายชื่อ Brand
    brand_list = sorted(latest_df["Brand"].unique())

    # default brand
    default_brand = "PTT"
    if default_brand not in brand_list:
        default_brand = brand_list[0]

    # รายชื่อชนิดน้ำมันทั้งหมด (จากวันล่าสุด)
    fuel_type_list = sorted(latest_df["FULE_TYPE"].unique())

    # default fuel type
    default_fuel_type = "แก๊สโซฮอล ออกเทน 91 (Gasohol 91-E10)"
    if default_fuel_type not in fuel_type_list:
        default_fuel_type = fuel_type_list[0]

    # =========================
    # ฟังก์ชันหาราคาล่าสุด
    # =========================
    def get_latest_price(brand, fuel_type, df_latest):
        """หาราคาล่าสุดสำหรับ brand และ fuel_type ที่เลือก"""
        mask = (
            (df_latest["Brand"] == brand)
            & (df_latest["FULE_TYPE"] == fuel_type)
        )
        
        if mask.any():
            return float(df_latest.loc[mask, "Price"].iloc[0])
        else:
            # ถ้าไม่มีข้อมูลให้ใช้ราคาล่าสุดจากแบรนด์นี้
            brand_latest = df_latest[df_latest["Brand"] == brand]
            if not brand_latest.empty:
                return float(brand_latest["Price"].iloc[0])
            else:
                return 0.0

    # =========================
    # INPUT SECTION (ใส่ใน premium-card)
    # =========================
    st.markdown('<div', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-title"><span class="icon">🧮</span>กรอกข้อมูลเพื่อคำนวณ</div>',
        unsafe_allow_html=True,
    )

    # แถวที่ 1 : Brand + Fuel Type
    col3, col4 = st.columns(2)

    with col3:
        brand_selected = st.selectbox(
            "เลือกแบรนด์น้ำมัน",
            brand_list,
            index=brand_list.index(default_brand),
            key="brand_select"
        )

    brand_df = df[df["Brand"] == brand_selected]
    fuel_types_for_brand = sorted(brand_df["FULE_TYPE"].unique())

    with col4:
        fuel_selected = st.selectbox(
            "เลือกชนิดเชื้อเพลิง",
            fuel_types_for_brand,
            index=fuel_types_for_brand.index(default_fuel_type)
            if default_fuel_type in fuel_types_for_brand
            else 0,
            key="fuel_select"
        )

    # =========================
    # หาราคาล่าสุดและตั้งค่า current_price
    # =========================
    latest_price = get_latest_price(brand_selected, fuel_selected, latest_df)

    # ตั้งค่า session_state สำหรับราคา
    current_session_key = f"current_price_{brand_selected}_{fuel_selected}"
    if current_session_key not in st.session_state:
        st.session_state[current_session_key] = latest_price

    # แถวที่ 2 : ราคาตั้งต้น + ราคาที่คาดหวัง
    col1, col2 = st.columns(2)

    with col1:
        # ดึงค่าจาก session_state สำหรับ brand/fuel ปัจจุบัน
        current_price_value = st.session_state[current_session_key]
        
        # ถ้าราคาไม่ตรงกับราคาล่าสุด ให้อัปเดตเป็นราคาล่าสุดทันที
        if abs(current_price_value - latest_price) > 0.001:
            st.session_state[current_session_key] = latest_price
            current_price_value = latest_price
        
        current_price = st.number_input(
            "ราคาเชื้อเพลิงตั้งต้น (บาท/ลิตร)",
            value=float(current_price_value),
            min_value=0.0,
            step=0.05,
            key=f"current_price_input_{brand_selected}_{fuel_selected}",
            help=f"ราคาล่าสุด: {latest_price:.2f} บาท"
        )
        
        # ตรวจสอบว่าผู้ใช้เปลี่ยนราคาเอง
        if abs(float(current_price) - float(current_price_value)) > 0.001:
            st.session_state[current_session_key] = float(current_price)

    with col2:
        future_session_key = f"future_price_{brand_selected}_{fuel_selected}"
        if future_session_key not in st.session_state:
            st.session_state[future_session_key] = latest_price - 0.5
        
        future_price = st.number_input(
            "ราคาเชื้อเพลิงที่คาดหวัง (บาท/ลิตร)",
            value=float(st.session_state[future_session_key]),
            min_value=0.0,
            step=0.05,
            key=f"future_price_input_{brand_selected}_{fuel_selected}",
            help="ถ้าไม่ต้องการเปรียบเทียบ ให้ใส่ 0 ไว้ได้"
        )
        st.session_state[future_session_key] = float(future_price)

    # แถวที่ 3 : ปริมาณน้ำมัน
    col5, col6 = st.columns(2)
    with col5:
        amount_liter = st.number_input(
            "กรอกปริมาณน้ำมัน (ลิตร)",
            min_value=0.1,
            value=st.session_state.get("amount_liter", 50000.0),
            step=10.0,
            key="amount_input"
        )
        st.session_state["amount_liter"] = amount_liter

    # กล่องแสดงราคาล่าสุด (ไว้บนสุดของส่วนผลลัพธ์)
    st.markdown(
        f"""
        <div class="latest-price-box">
            <div style="font-size: 0.85rem; color: #0369a1; margin-bottom: 0.3rem;">
                <strong>💰 ราคาล่าสุดของ {brand_selected} - {fuel_selected}:</strong>
            </div>
            <div style="font-size: 1.2rem; font-weight: 700; color: #1e40af; text-align: center;">
                {latest_price:.2f} บาท/ลิตร
            </div>
            <div style="font-size: 0.8rem; color: #64748b; text-align: center; margin-top: 0.3rem;">
                ราคาจริงล่าสุด ณ วันที่ {latest_date_all.strftime('%d/%m/%Y')}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("</div>", unsafe_allow_html=True)  # ปิด premium-card input

    st.markdown("<div class='footer-space'></div>", unsafe_allow_html=True)

    # ======================================================
    # 📈 กราฟเปรียบเทียบราคาน้ำมัน (อยู่ใน premium-card)
    # ======================================================
    st.markdown('<div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-title"><span class="icon">📈</span>กราฟเปรียบเทียบราคาน้ำมัน</div>',
        unsafe_allow_html=True,
    )

    # เตรียมข้อมูลสำหรับกราฟ: เลือกเฉพาะ brand + fuel_type ที่สนใจ
    df_plot = (
        df[(df["Brand"] == brand_selected) & (df["FULE_TYPE"] == fuel_selected)]
        .sort_values("Date")
        .copy()
    )

    df_plot["current_price"] = float(current_price)
    df_plot["future_price"] = float(future_price)

    latest_date = df_plot["Date"].max()
    latest_row = df_plot[df_plot["Date"] == latest_date].iloc[0]
    latest_actual = float(latest_row["Price"])

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df_plot["Date"],
            y=df_plot["Price"],
            mode="lines",
            name="ราคาจริง",
            line=dict(color="green", width=2),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=df_plot["Date"],
            y=df_plot["current_price"],
            mode="lines",
            name="ราคาเชื้อเพลิงตั้งต้น",
            line=dict(color="orangered", width=3, dash="solid"),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=df_plot["Date"],
            y=df_plot["future_price"],
            mode="lines",
            name="ราคาเชื้อเพลิงที่คาดหวัง",
            line=dict(color="blue", width=3, dash="solid"),
            fill="tonexty",
            fillcolor="rgba(0,0,0,0.08)",
        )
    )

    fig.add_annotation(
        x=latest_date,
        y=latest_actual,
        text=f"ราคาจริง {latest_actual:.2f}",
        showarrow=True,
        arrowhead=2,
        ax=40,
        ay=-30,
        font=dict(color="green", size=12),
        bgcolor="rgba(255,255,255,0.9)",
    )

    fig.add_annotation(
        x=latest_date,
        y=float(current_price),
        text=f"ตั้งต้น {float(current_price):.2f}",
        showarrow=True,
        arrowhead=2,
        ax=40,
        ay=10,
        font=dict(color="orangered", size=12),
        bgcolor="rgba(255,255,255,0.9)",
    )

    fig.add_annotation(
        x=latest_date,
        y=float(future_price),
        text=f"คาดหวัง {float(future_price):.2f}",
        showarrow=True,
        arrowhead=2,
        ax=40,
        ay=40,
        font=dict(color="blue", size=12),
        bgcolor="rgba(255,255,255,0.9)",
    )

    fig.update_layout(
        title=f"ราคาน้ำมันของ {brand_selected} – {fuel_selected}",
        xaxis_title="วันที่",
        yaxis_title="ราคาน้ำมัน (บาทต่อลิตร)",
        template="plotly_white",
        hovermode="x unified",
    )

    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)  # ปิด premium-card chart

    st.markdown("<div class='footer-space'></div>", unsafe_allow_html=True)

    # ======================================================
    # ฟังก์ชันแสดงกล่องกำไร/ขาดทุน (ใช้พื้นฐานเดิม + wrap ใน result-box)
    # ======================================================
    def render_diff_box(title: str, diff_value: float):
        if diff_value > 0:
            status = "กำไร"
            color = "#d9480f"
        elif diff_value < 0:
            status = "ขาดทุน"
            color = "#1971c2"
        else:
            status = "คุ้มค่าเท่าเดิม"
            color = "#495057"

        number_html = f"""
            <div class='result-main-number' style='color:{color}; margin-bottom:4px;'>
                {diff_value:,.2f} บาท
            </div>
        """

        desc_html = f"""
            <div style='font-size:0.85rem; color:{color}; line-height:1.4;'>
                ({status} คำนวณจาก {title} − ค่าใช้จ่ายจากราคาจริง)
            </div>
        """

        st.markdown(
            f"""
            <div class="result-box">
                {number_html}
                {desc_html}
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ======================================================
    # 📊 ผลลัพธ์การคำนวณ (อยู่ใน premium-card)
    # ======================================================
    st.markdown('<div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-title"><span class="icon">📊</span>ผลลัพธ์การคำนวณ</div>',
        unsafe_allow_html=True,
    )

    # หาราคาจริงล่าสุดของ brand + fuel ที่เลือก
    mask_real = (
        (latest_df["Brand"] == brand_selected)
        & (latest_df["FULE_TYPE"] == fuel_selected)
    )
    if mask_real.any():
        latest_real_price = float(latest_df.loc[mask_real, "Price"].iloc[0])
    else:
        latest_real_price = float(df_plot["Price"].iloc[-1])

    current_cost = float(current_price) * float(amount_liter)
    real_cost = float(latest_real_price) * float(amount_liter)
    future_cost = float(future_price) * float(amount_liter)

    col_a, col_b, col_c = st.columns(3)

    with col_a:
        st.markdown("**ค่าใช้จ่ายจากราคาเชื้อเพลิงตั้งต้น**")
        st.markdown(
            f"<div class='result-main-number'>{current_cost:,.2f} บาท</div>",
            unsafe_allow_html=True,
        )
        st.caption(f"ราคา: {float(current_price):.2f} บาท/ลิตร")

    with col_b:
        st.markdown("**ค่าใช้จ่ายจากราคาจริง (วันล่าสุด)**")
        st.markdown(
            f"<div class='result-main-number'>{real_cost:,.2f} บาท</div>",
            unsafe_allow_html=True,
        )
        st.caption(f"ราคา: {latest_real_price:.2f} บาท/ลิตร")

    with col_c:
        st.markdown("**ค่าใช้จ่ายจากราคาที่คาดหวัง**")
        st.markdown(
            f"<div class='result-main-number'>{future_cost:,.2f} บาท</div>",
            unsafe_allow_html=True,
        )
        st.caption(f"ราคา: {float(future_price):.2f} บาท/ลิตร")

    st.markdown("")

    diff_current_vs_real = current_cost - real_cost
    diff_future_vs_real = future_cost - real_cost

    col_d, col_e = st.columns(2)

    with col_d:
        render_diff_box("ค่าใช้จ่ายจากราคาเชื้อเพลิงตั้งต้น", diff_current_vs_real)

    with col_e:
        render_diff_box("ค่าใช้จ่ายจากราคาที่คาดหวัง", diff_future_vs_real)

    st.markdown("</div>", unsafe_allow_html=True)  # ปิด premium-card results

    # แสดงข้อมูลสรุป
    st.markdown(
        f"""
        <div class="premium-card" style="margin-top: 1rem;">
            <div class="section-title"><span class="icon">ℹ️</span>ข้อมูลสรุป</div>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem;">
                <div>
                    <div style="font-size: 0.85rem; color: var(--text-secondary);">แบรนด์</div>
                    <div style="font-weight: 600;">{brand_selected}</div>
                </div>
                <div>
                    <div style="font-size: 0.85rem; color: var(--text-secondary);">ชนิดเชื้อเพลิง</div>
                    <div style="font-weight: 600;">{fuel_selected}</div>
                </div>
                <div>
                    <div style="font-size: 0.85rem; color: var(--text-secondary);">ราคาจริงล่าสุด</div>
                    <div style="font-weight: 600; color: #16a34a;">{latest_real_price:.2f} บาท/ลิตร</div>
                </div>
                <div>
                    <div style="font-size: 0.85rem; color: var(--text-secondary);">ปริมาณ</div>
                    <div style="font-weight: 600;">{amount_liter:,.2f} ลิตร</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def show_oil_distance_addon ():
    # ---------------------------
# Page config + Premium Theme
# ---------------------------
    st.set_page_config(
        page_title="Oil Distance & Cost Calculator | Premium",
        page_icon="🚗",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # ---------- Global CSS ให้ match กับหน้า 01 / dashboard ----------
    st.markdown(
        """
    <style>
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

        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }

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

        /* การ์ดหลัก */
        .premium-card {
            background: var(--card-bg);
            border-radius: 16px;
            padding: 1.5rem;
            border: 1px solid #e2e8f0;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1),
                        0 2px 4px -1px rgba(0, 0, 0, 0.06);
            transition: all 0.3s ease;
            height: 100%;
        }

        .premium-card:hover {
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1),
                        0 4px 6px -2px rgba(0, 0, 0, 0.05);
            transform: translateY(-2px);
        }

        .section-title {
            font-size: 1.1rem;
            font-weight: 600;
            color: var(--primary);
            margin-bottom: 0.75rem;
            display: flex;
            align-items: center;
            gap: 0.4rem;
        }

        .section-title span.icon {
            font-size: 1.3rem;
        }

        .result-main-number {
            font-size: 1.4rem;
            font-weight: 700;
            color: var(--primary);
        }

        .footer-space {
            height: 1.5rem;
        }
    </style>
    """,
        unsafe_allow_html=True,
    )

    # ---------------------------
    # Premium Header
    # ---------------------------
    h1c1, h1c2, h1c3 = st.columns([1, 2, 1])
    with h1c2:
        st.markdown(
            """
            <div style="text-align: center; margin-bottom: 2rem;">
                <h1 style="font-size: 2.4rem; margin-bottom: 0.5rem;">
                    🚗 Oil Distance & Cost Calculator
                </h1>
                <p style="color: var(--text-secondary); font-size: 1.0rem; margin-top: 0;">
                    คำนวณต้นทุนการวิ่งรถจากราคาน้ำมัน และอัตราการสิ้นเปลืองเชื้อเพลิง
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # --- ดึงข้อมูลเพื่อเอาราคาล่าสุดมาเป็น fallback default ---
    df = get_oilprice_long()
    latest_date_all = df["Date"].max()
    latest_df = df[df["Date"] == latest_date_all]

    # default brand / fuel type เหมือนหน้าแรก (ใช้แค่ตอนหา base_price เผื่อไม่มีค่าใน session)
    brand_list = sorted(latest_df["Brand"].unique())
    default_brand = "PTT"
    if default_brand not in brand_list:
        default_brand = brand_list[0]

    fuel_type_list = sorted(latest_df["FULE_TYPE"].unique())
    default_fuel_type = "แก๊สโซฮอล ออกเทน 91 (Gasohol 91-E10)"
    if default_fuel_type not in fuel_type_list:
        default_fuel_type = fuel_type_list[0]

    mask_default = (
        (latest_df["Brand"] == default_brand)
        & (latest_df["FULE_TYPE"] == default_fuel_type)
    )
    if mask_default.any():
        base_price = float(latest_df.loc[mask_default, "Price"].iloc[0])
    else:
        base_price = float(latest_df["Price"].iloc[0])

    # ---------------- ใช้ค่าจากหน้า 01 ถ้ามีใน session_state ----------------
    session_current = st.session_state.get("current_price")
    session_future = st.session_state.get("future_price")

    default_current_price = float(session_current) if session_current is not None else base_price
    default_future_price = (
        float(session_future)
        if session_future is not None
        else float(base_price - 0.5)
    )

    # ======================================================
    # การ์ดที่ 1: ตั้งค่าราคาเชื้อเพลิงและระยะทาง
    # ======================================================
    st.markdown('<div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-title"><span class="icon">⛽</span>ตั้งค่าราคาเชื้อเพลิงและระยะทาง</div>',
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns(2)

    with c1:
        current_price = st.number_input(
            "ราคาเชื้อเพลิงตั้งต้น (บาท/ลิตร)",
            value=default_current_price,
            min_value=0.0,
            step=0.05,
        )

    with c2:
        future_price = st.number_input(
            "ราคาเชื้อเพลิงที่คาดหวัง (บาท/ลิตร)",
            value=default_future_price,
            min_value=0.0,
            step=0.05,
            help="ถ้าไม่ต้องการเปรียบเทียบ ให้ใส่ 0 ไว้ได้",
        )

    st.markdown("</div>", unsafe_allow_html=True)  # ปิดการ์ดที่ 1

    st.markdown("<div class='footer-space'></div>", unsafe_allow_html=True)

    # ======================================================
    # การ์ดที่ 2: ป้อนข้อมูลการวิ่งรถ + ผลคำนวณ
    # ======================================================
    st.markdown('<div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-title"><span class="icon">📍</span>ป้อนข้อมูลการวิ่งรถ</div>',
        unsafe_allow_html=True,
    )

    # ---------- แถวที่ 1 : Input เป็น Grid ----------
    r1c1, r1c2 = st.columns(2)

    with r1c1:
        fuel_eff_extra = st.number_input(
            "อัตราการสิ้นเปลืองเชื้อเพลิง (กิโลเมตรต่อลิตร)",
            min_value=0.1,
            value=6.0,
            step=0.1,
            key="fuel_eff_extra",
        )

    with r1c2:
        trip_distance = st.number_input(
            "ระยะทางต่อเที่ยว (กิโลเมตร)",
            min_value=1.0,
            value=250.0,
            step=10.0,
            key="trip_distance",
        )

    show_future = future_price > 0.0

    # ---------- คำนวณตัวเลขพื้นฐาน ----------
    if fuel_eff_extra > 0:
        liters_per_trip = trip_distance / fuel_eff_extra

        cost_per_km_current = current_price / fuel_eff_extra
        cost_per_km_future = future_price / fuel_eff_extra if show_future else None

        trip_cost_current = liters_per_trip * current_price
        trip_cost_future = liters_per_trip * future_price if show_future else None

        dist_100 = 100.0
        liters_for_100 = dist_100 / fuel_eff_extra
        cost_100_current = liters_for_100 * current_price
        cost_100_future = liters_for_100 * future_price if show_future else None
    else:
        liters_per_trip = 0.0
        cost_per_km_current = None
        cost_per_km_future = None
        trip_cost_current = None
        trip_cost_future = None
        dist_100 = 100.0
        cost_100_current = None
        cost_100_future = None

    # ---------- แถวที่ 2 : สรุปแบบ Metric ----------

    st.markdown("### 📌 สรุปต้นทุนแบบย่อ")

    m1, m2 = st.columns(2)

    with m1:
        st.metric(
            "ค่าใช้จ่ายต่อกม. (ตั้งต้น)",
            f"{(cost_per_km_current or 0):,.2f} บาท/กม.",
        )

    with m2:
        if show_future and cost_per_km_future is not None:
            st.metric(
                "ค่าใช้จ่ายต่อกม. (ที่คาดหวัง)",
                f"{cost_per_km_future:,.2f} บาท/กม.",
            )
        else:
            st.metric("ค่าใช้จ่ายต่อกม. (ที่คาดหวัง)", "ยังไม่ได้กรอก")

    # ---------- แถวที่ 3 : ค่าใช้จ่ายต่อเที่ยว ----------
    st.markdown("### 🚛 ค่าใช้จ่ายต่อหนึ่งเที่ยวส่งของ")

    r4c1, r4c2 = st.columns(2)

    with r4c1:
        st.markdown("**เที่ยวละ (ราคาเชื้อเพลิงตั้งต้น)**")
        if trip_cost_current is not None and fuel_eff_extra > 0:
            st.write(
                f"- ระยะ {trip_distance:,.0f} กม.\n"
                f"- ใช้น้ำมัน ~ {liters_per_trip:,.2f} ลิตร\n"
                f"- ค่าใช้จ่ายต่อเที่ยว ≈ **{trip_cost_current:,.2f} บาท**"
            )
        else:
            st.write("⚠️ กรอกอัตราการสิ้นเปลืองและระยะทางต่อเที่ยวให้ครบ")

    with r4c2:
        st.markdown("**เที่ยวละ (ราคาที่คาดหวัง)**")
        if show_future and trip_cost_future is not None and fuel_eff_extra > 0:
            st.write(
                f"- ระยะ {trip_distance:,.0f} กม.\n"
                f"- ใช้น้ำมัน ~ {liters_per_trip:,.2f} ลิตร\n"
                f"- ค่าใช้จ่ายต่อเที่ยว ≈ **{trip_cost_future:,.2f} บาท**"
            )
        else:
            st.write("⚠️ ยังไม่ได้กรอกราคาที่คาดหวัง (> 0)")

    # ---------- แถวที่ 4 : วิ่ง 100 กม. ----------
    st.markdown("### 🧮 วิ่ง 100 กม. ต้องจ่ายเท่าไหร่?")

    r3c1, r3c2 = st.columns(2)

    with r3c1:
        st.markdown("**ราคาเชื้อเพลิงตั้งต้น**")
        if cost_100_current is not None:
            st.write(f"วิ่ง 100 กม. → จ่ายประมาณ **{cost_100_current:,.2f} บาท**")
        else:
            st.write("⚠️ กรอกอัตราการสิ้นเปลืองให้ถูกต้องก่อน")

    with r3c2:
        st.markdown("**ราคาที่คาดหวัง**")
        if show_future and cost_100_future is not None:
            st.write(f"วิ่ง 100 กม. → จ่ายประมาณ **{cost_100_future:,.2f} บาท**")
        else:
            st.write("⚠️ ยังไม่ได้กรอกราคาที่คาดหวัง (> 0)")

    st.markdown("</div>", unsafe_allow_html=True) 


# ==============================
# 7. MAIN APP LOGIC
# ==============================
def main():
    if not st.session_state['logged_in']:
        # Guest view
        show_premium_login()
    else:
        # User view
        premium_sidebar()
        
        # จัดการหน้าเนื้อหาตาม current_page
        if st.session_state['current_page'] == "dashboard":
            st.title("📊 Oil Price Dashboard")
            show_premium_dashboard()
        elif st.session_state['current_page'] == "package":
            show_package_page()
        elif st.session_state['current_page'] == "ai":
            # ✅ แก้ไข: อนุญาตทั้ง PRO และ ENTERPRISE
            if st.session_state['subscribe_flag'] == 1 or st.session_state['subscribe_flag'] == 2:
                show_ai_assistant()
            else:
                st.error("⛔ คุณต้องอัปเกรดเป็น PRO ขึ้นไปเพื่อใช้งานฟีเจอร์นี้")
                if st.button("✨ อัปเกรดเป็น PRO"):
                    go_to_package()
        elif st.session_state['current_page'] == "analytics":
            # ✅ แก้ไข: อนุญาตทั้ง PRO และ ENTERPRISE
            if st.session_state['subscribe_flag'] == 1 or st.session_state['subscribe_flag'] == 2:
                show_oil_price_daily()
            else:
                st.error("⛔ คุณต้องอัปเกรดเป็น PRO ขึ้นไปเพื่อใช้งานฟีเจอร์นี้")
                if st.button("✨ อัปเกรดเป็น PRO"):
                    go_to_package()
        elif st.session_state['current_page'] == "simmulate":
            # ✅ อนุญาตเฉพาะ ENTERPRISE
            if st.session_state['subscribe_flag'] == 2:
                show_oil_cost_simulate()
            else:
                if st.session_state['subscribe_flag'] == 1:  # PRO user
                    st.error("⛔ คุณต้องอัปเกรดเป็น ENTERPRISE เพื่อใช้งานฟีเจอร์นี้")
                    if st.button("✨ อัปเกรดเป็น ENTERPRISE"):
                        go_to_package()
                else:  # FREE user
                    st.error("⛔ คุณต้องอัปเกรดเป็น ENTERPRISE เพื่อใช้งานฟีเจอร์นี้")
                    if st.button("✨ อัปเกรดเป็น ENTERPRISE"):
                        go_to_package()
        elif st.session_state['current_page'] == "distance":
            # ✅ แก้ไข: อนุญาตทั้ง PRO และ ENTERPRISE
            if st.session_state['subscribe_flag'] == 1 or st.session_state['subscribe_flag'] == 2:
                show_oil_distance_addon()
            else:
                st.error("⛔ คุณต้องอัปเกรดเป็น PRO ขึ้นไปเพื่อใช้งานฟีเจอร์นี้")
                if st.button("✨ อัปเกรดเป็น PRO"):
                    go_to_package()
        elif st.session_state['current_page'] == "fulecal":
            st.title("⛽ Fuel Trip Calculator")
            show_fule_cal()        
        elif st.session_state['current_page'] == "settings":
            st.title("⚙️ การตั้งค่า")
            st.info("หน้านี้กำลังพัฒนา...")
        elif st.session_state['current_page'] == "reports":
            st.title("📈 รายงาน")
            st.info("หน้านี้กำลังพัฒนา...")
        else:
            show_premium_dashboard()

if __name__ == "__main__":
    main()