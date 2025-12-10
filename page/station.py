import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import json
import re
import uuid
import random
import string
import hashlib
import duckdb  # สำหรับฐานข้อมูล DuckDB
import plotly.graph_objects as go
import plotly.express as px
import altair as alt
import pydeck as pdk
import os
from pathlib import Path

class OilStationMapApp:
    """Class หลักสำหรับแอป Station Map แบบแยกหน้ารันเดี่ยว"""
    
    def __init__(self):
        """Initialize the application"""
        st.set_page_config(
            page_title="OILSOPHANG Station Map | Premium",
            page_icon="🗺️",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Initialize session state
        self._init_session_state()
        
        # Apply custom CSS
        self._apply_custom_css()
    
    def _init_session_state(self):
        """Initialize session state variables"""
        if 'station_data_loaded' not in st.session_state:
            st.session_state.station_data_loaded = False
        if 'station_df' not in st.session_state:
            st.session_state.station_df = None
        if 'selected_province' not in st.session_state:
            st.session_state.selected_province = None
        if 'selected_brands' not in st.session_state:
            st.session_state.selected_brands = []
        if 'selected_districts' not in st.session_state:
            st.session_state.selected_districts = []
    
    def _apply_custom_css(self):
        """Apply custom CSS for premium blue theme"""
        st.markdown("""
        <style>
        /* Main Blue Theme */
        :root {
            --primary-blue: #1A3C6E;
            --secondary-blue: #4D88FF;
            --light-blue: #E6F2FF;
            --soft-blue: #B3D9FF;
            --accent-blue: #0066CC;
        }
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
                    
                    .stSelectbox label, .stSelectbox div {
        color: black !important;
    }
        
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        
        /* Header Styling */
        .premium-header {
            background: linear-gradient(135deg, #E6F2FF 0%, #B3D9FF 100%);
            padding: 1.5rem 2rem;
            border-radius: 20px;
            margin-bottom: 2rem;
            border-left: 8px solid #4D88FF;
            box-shadow: 0 8px 25px rgba(77, 136, 255, 0.15);
        }
        
        /* Card Styling */
        .premium-card {
            background: white;
            border-radius: 15px;
            padding: 1.5rem;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
            border: 1px solid #E6F2FF;
            margin-bottom: 1.5rem;
        }
        
        .filter-card {
            background: #F0F8FF;
            padding: 1.5rem;
            border-radius: 12px;
            margin-bottom: 1rem;
            border-left: 4px solid #4D88FF;
        }
        
        .stat-card {
            background: linear-gradient(135deg, #E6F2FF 0%, #B3D9FF 100%);
            padding: 1.5rem;
            border-radius: 15px;
            text-align: center;
            border: 2px solid #4D88FF;
        }
        
        /* Button Styling */
        .stButton > button {
            background: linear-gradient(135deg, #4D88FF 0%, #1A3C6E 100%);
            color: white;
            border: none;
            border-radius: 10px;
            padding: 10px 24px;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(77, 136, 255, 0.4);
        }
        
        /* Select Box Styling */
        div[data-testid="stSelectbox"] > div > div {
            background-color: white;
            border: 2px solid #E6F2FF;
            border-radius: 10px;
            padding: 8px 12px;
            transition: all 0.3s ease;
        }
        
        div[data-testid="stSelectbox"] > div > div:hover {
            border-color: #4D88FF;
            box-shadow: 0 4px 12px rgba(77, 136, 255, 0.15);
        }
        
        /* Multi-select Styling */
        div[data-testid="stMultiSelect"] > div > div {
            background-color: white;
            border: 2px solid #E6F2FF;
            border-radius: 10px;
            transition: all 0.3s ease;
        }
        
        /* Tabs Styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
            background-color: #F0F8FF;
            padding: 8px;
            border-radius: 12px;
            border: 1px solid #E6F2FF;
        }
        
        .stTabs [data-baseweb="tab"] {
            background-color: white;
            border-radius: 8px;
            padding: 10px 20px;
            border: 1px solid #E6F2FF;
            color: #1A3C6E;
            font-weight: 500;
            transition: all 0.3s ease;
        }
        
        .stTabs [data-baseweb="tab"]:hover {
            background-color: #E6F2FF;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(77, 136, 255, 0.15);
        }
        
        .stTabs [aria-selected="true"] {
            background-color: #4D88FF !important;
            color: white !important;
            border-color: #4D88FF !important;
            box-shadow: 0 4px 15px rgba(77, 136, 255, 0.25);
        }
        
        /* Dataframe Styling */
        .stDataFrame {
            border: 1px solid #E6F2FF;
            border-radius: 12px;
            overflow: hidden;
        }
        
        /* Custom Scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: #F0F8FF;
            border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb {
            background: #4D88FF;
            border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: #1A3C6E;
        }
        </style>
        """, unsafe_allow_html=True)
    
    def _load_station_data(self):
        """โหลดข้อมูลจาก DuckDB"""
        try:
            # ตรวจสอบว่าไฟล์ฐานข้อมูลมีอยู่หรือไม่
            db_path = 'dads5001.duckdb'
            if not os.path.exists(db_path):
                st.error(f"❌ ไม่พบไฟล์ฐานข้อมูล: {db_path}")
                st.info("""
                **วิธีการแก้ไข:**
                1. ตรวจสอบว่าไฟล์ `dads5001.duckdb` อยู่ในโฟลเดอร์เดียวกันกับไฟล์นี้
                2. หรือเปลี่ยน path ไปยังตำแหน่งที่ถูกต้อง
                3. หรือใช้ข้อมูลตัวอย่างที่จัดเตรียมไว้
                """)
                
                # แสดงข้อมูลตัวอย่างถ้าไม่มีไฟล์จริง
                return self._get_sample_data()
            
            # Connect to DuckDB
            conn = duckdb.connect(db_path)
            
            # Query data from pin table
            query = """
            SELECT 
                company,
                latitude,
                longitude,
                province,
                amphur as district,
                tumbon as subdistrict
            FROM pin
            WHERE latitude IS NOT NULL 
                AND longitude IS NOT NULL
            ORDER BY province, company
            """
            
            
            df = conn.execute(query).fetchdf()
            conn.close()

                        # แล้วเปลี่ยนชื่อคอลัมน์ใน pandas
            if 'tumbon' in df.columns:
                df = df.rename(columns={'tumbon': 'subdistrict'})
            elif 'tambon' in df.columns:
                df = df.rename(columns={'tambon': 'subdistrict'})

            
            if df.empty:
                st.warning("⚠️ ไม่พบข้อมูลในตาราง pin")
                return self._get_sample_data()
            
            # Data Cleaning
            df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
            df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
            df['company'] = df['company'].str.strip().str.upper()
            df['province'] = df['province'].str.strip()
            
            # Remove rows with missing coordinates
            df = df.dropna(subset=['latitude', 'longitude'])
            
            return df
            
        except Exception as e:
            st.error(f"❌ เกิดข้อผิดพลาดในการโหลดข้อมูล: {str(e)}")
            return self._get_sample_data()
    
    def _get_sample_data(self):
        """ข้อมูลตัวอย่างถ้าไม่มีไฟล์ฐานข้อมูล"""
        st.warning("กำลังใช้ข้อมูลตัวอย่าง...")
        
        # สร้างข้อมูลตัวอย่าง
        sample_data = {
            'company': ['PTT', 'SHELL', 'BANGCHAK', 'ESSO', 'PTT', 'SHELL', 'CHEVRON', 'PTG'],
            'latitude': [13.736717, 13.756331, 13.723419, 13.745176, 13.712345, 13.765432, 13.732109, 13.754321],
            'longitude': [100.523186, 100.501765, 100.547891, 100.534567, 100.512345, 100.523456, 100.543210, 100.512345],
            'province': ['กรุงเทพมหานคร', 'กรุงเทพมหานคร', 'กรุงเทพมหานคร', 'กรุงเทพมหานคร', 
                        'สมุทรปราการ', 'สมุทรปราการ', 'นนทบุรี', 'นนทบุรี'],
            'district': ['คลองเตย', 'ปทุมวัน', 'บางนา', 'วัฒนา', 'บางพลี', 'พระประแดง', 'เมืองนนทบุรี', 'บางใหญ่'],
            'subdistrict': ['คลองตัน', 'ปทุมวัน', 'บางนา', 'คลองเตย', 'บางพลี', 'พระประแดง', 'สวนใหญ่', 'บางใหญ่']
        }
        
        return pd.DataFrame(sample_data)
    
    def _show_header(self):
        """แสดง Header ของแอป"""
        st.markdown("""
        <div class="premium-header">
            <h1 style="
                color: #1A3C6E;
                margin: 0;
                font-weight: 700;
                font-size: 2.2rem;
                display: flex;
                align-items: center;
                gap: 15px;
            ">
                <span style="font-size: 2.8rem;">🗺️</span>
                ค้นหาปั๊มน้ำมัน
            </h1>
            <p style="
                color: #4D88FF;
                margin-top: 0.5rem;
                font-size: 1.1rem;
                font-weight: 500;
            ">
                ค้นหาตำแหน่งปั๊มน้ำมันใกล้คุณในพื้นที่ที่ต้องการ
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    def _show_loading_section(self):
        """แสดงส่วน loading และโหลดข้อมูล"""
        with st.spinner("⏳ กำลังโหลดข้อมูลปั๊มน้ำมัน..."):
            time.sleep(0.5)
            
            if not st.session_state.station_data_loaded or st.session_state.station_df is None:
                station_df = self._load_station_data()
                st.session_state.station_df = station_df
                st.session_state.station_data_loaded = True
                
                # แสดงข้อความสำเร็จ
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, #E6FFE6 0%, #B3FFB3 100%);
                    padding: 1.5rem;
                    border-radius: 15px;
                    border-left: 6px solid #00B359;
                    margin-bottom: 2rem;
                    display: flex;
                    align-items: center;
                    gap: 15px;
                ">
                    <div style="
                        background: #00B359;
                        width: 50px;
                        height: 50px;
                        border-radius: 50%;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        color: white;
                        font-size: 1.5rem;
                        font-weight: bold;
                    ">
                        ✓
                    </div>
                    <div>
                        <h4 style="color: #006622; margin: 0;">
                            โหลดข้อมูลสำเร็จ!
                        </h4>
                        <p style="color: #006622; margin: 0.25rem 0 0 0;">
                            พบปั๊มน้ำมันทั้งหมด <strong>{len(station_df):,}</strong> สถานี
                        </p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            return st.session_state.station_df
    
    def _show_filter_section(self, station_df):
        """แสดงส่วนตัวกรองข้อมูล"""
        st.markdown("""
        <div class="premium-card">
            <h3 style="
                color: #1A3C6E;
                margin-bottom: 1.5rem;
                display: flex;
                align-items: center;
                gap: 10px;
            ">
                <span style="font-size: 1.8rem;">🔍</span>
                ตัวกรองการค้นหา
            </h3>
        """, unsafe_allow_html=True)
        
        # Filter Grid - 2 Columns
        col1, col2 = st.columns(2)
        
        with col1:
            # Province Filter
            st.markdown("""
            <div class="filter-card" style="color: black;>
                <h4 style="color: #1A3C6E; margin-bottom: 1rem;">
                    🌆 เลือกจังหวัด
                </h4>
            """, unsafe_allow_html=True)
            
            available_provinces = sorted(station_df['province'].dropna().unique())
            selected_province = st.selectbox(
                "เลือกจังหวัดที่ต้องการ",
                options=available_provinces,
                index=available_provinces.index('กรุงเทพมหานคร') if 'กรุงเทพมหานคร' in available_provinces else 0,
                label_visibility="collapsed",
                key="province_select"
            )
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col2:
            # Brand Filter
            st.markdown("""
            <div class="filter-card">
                <h4 style="color: #1A3C6E; margin-bottom: 1rem;">
                    🏭 เลือกแบรนด์
                </h4>
            """, unsafe_allow_html=True)
            
            available_brands = sorted(station_df['company'].dropna().unique())
            brand_order = ['PTT', 'SHELL', 'BCP', 'BANGCHAK', 'ESSO', 'CHEVRON', 'PTG', 'IRPC']
            ordered_brands = [b for b in brand_order if b in available_brands]
            ordered_brands.extend([b for b in available_brands if b not in ordered_brands])
            
            selected_brands = st.multiselect(
                "เลือกแบรนด์ปั๊มน้ำมัน",
                options=ordered_brands,
                default=['PTT', 'SHELL'] if all(b in ordered_brands for b in ['PTT', 'SHELL']) else ordered_brands[:2],
                label_visibility="collapsed",
                key="brand_multiselect"
            )
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        # District Filter
        st.markdown("""
        <div class="filter-card">
            <h4 style="color: #1A3C6E; margin-bottom: 1rem;">
                📍 กรองตามเขต
            </h4>
        """, unsafe_allow_html=True)
        
        province_filtered = station_df[station_df['province'] == selected_province]
        
        if 'district' in province_filtered.columns and not province_filtered.empty:
            available_districts = sorted(province_filtered['district'].dropna().astype(str).unique())
            
            if available_districts:
                selected_districts = st.multiselect(
                    f"เลือกเขตในจังหวัด{selected_province}",
                    options=available_districts,
                    default=available_districts[:3] if len(available_districts) > 3 else available_districts,
                    help="เลือกเขตที่ต้องการค้นหาปั๊มน้ำมัน",
                    label_visibility="collapsed",
                    key="district_multiselect"
                )
            else:
                selected_districts = []
                st.info("ไม่พบข้อมูลเขตสำหรับจังหวัดนี้")
        else:
            selected_districts = []
        
        st.markdown("</div></div>", unsafe_allow_html=True)
        
        return selected_province, selected_brands, selected_districts, province_filtered
    
    def _show_statistics(self, filtered_data):
        """แสดงสถิติการค้นหา"""
        st.markdown("""
        <div style="margin: 2rem 0;">
            <h3 style="
                color: #1A3C6E;
                margin-bottom: 1.5rem;
                display: flex;
                align-items: center;
                gap: 10px;
            ">
                <span style="font-size: 1.8rem;">📊</span>
                สถิติการค้นหา
            </h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Statistics Cards Grid
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="stat-card">
                <div style="
                    font-size: 2.5rem;
                    color: #1A3C6E;
                    font-weight: bold;
                    margin-bottom: 0.5rem;
                ">
                    {len(filtered_data)}
                </div>
                <div style="color: #4D88FF; font-weight: 600;">
                    🚗 จำนวนปั๊ม
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            brand_count = filtered_data['company'].nunique()
            st.markdown(f"""
            <div class="stat-card">
                <div style="
                    font-size: 2.5rem;
                    color: #1A3C6E;
                    font-weight: bold;
                    margin-bottom: 0.5rem;
                ">
                    {brand_count}
                </div>
                <div style="color: #4D88FF; font-weight: 600;">
                    🏭 จำนวนแบรนด์
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            if 'district' in filtered_data.columns:
                district_count = filtered_data['district'].nunique()
                st.markdown(f"""
                <div class="stat-card">
                    <div style="
                        font-size: 2.5rem;
                        color: #1A3C6E;
                        font-weight: bold;
                        margin-bottom: 0.5rem;
                    ">
                        {district_count}
                    </div>
                    <div style="color: #4D88FF; font-weight: 600;">
                        📍 จำนวนเขต
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        with col4:
            center_lat = filtered_data['latitude'].mean()
            center_lon = filtered_data['longitude'].mean()
            st.markdown(f"""
            <div class="stat-card">
                <div style="
                    font-size: 1.8rem;
                    color: #1A3C6E;
                    font-weight: bold;
                    margin-bottom: 0.5rem;
                    line-height: 1.2;
                ">
                    {center_lat:.4f}<br/>{center_lon:.4f}
                </div>
                <div style="color: #4D88FF; font-weight: 600;">
                    📌 ตำแหน่งกลาง
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    def _show_map(self, filtered_data, selected_province, selected_brands):
        """แสดงแผนที่ปั๊มน้ำมัน"""
        st.markdown("""
        <div style="margin: 3rem 0 2rem 0;">
            <h3 style="
                color: #1A3C6E;
                margin-bottom: 1.5rem;
                display: flex;
                align-items: center;
                gap: 10px;
            ">
                <span style="font-size: 1.8rem;">🗺️</span>
                แผนที่ปั๊มน้ำมัน
            </h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Blue-themed color palette
        brand_colors_blue = {
            'PTT': [255, 87, 51, 200],      # Coral Red
            'SHELL': [255, 193, 7, 200],    # Amber Yellow
            'BCP': [76, 175, 80, 200],      # Green
            'BANGCHAK': [33, 150, 243, 200], # Blue
            'ESSO': [244, 67, 54, 200],     # Red
            'CHEVRON': [255, 152, 0, 200],  # Orange
            'PTG': [158, 158, 158, 200],    # Gray
            'IRPC': [156, 39, 176, 200],    # Purple
            'SUSCO': [0, 150, 136, 200],    # Teal
            'PURE': [121, 85, 72, 200]      # Brown
        }
        
        # Create map layers
        layers = []
        for brand in selected_brands if selected_brands else []:
            brand_data = filtered_data[filtered_data['company'] == brand]
            if not brand_data.empty:
                color = brand_colors_blue.get(brand, [0, 188, 212, 200])
                
                layer = pdk.Layer(
                    "ScatterplotLayer",
                    data=brand_data,
                    get_position='[longitude, latitude]',
                    get_color=color,
                    get_radius=150,
                    pickable=True,
                    auto_highlight=True,
                    filled=True,
                    stroked=True,
                    line_width_min_pixels=2,
                    line_color=[255, 255, 255, 150]
                )
                layers.append(layer)
        
        # Create map view
        if layers:
            view_state = pdk.ViewState(
                latitude=filtered_data['latitude'].mean(),
                longitude=filtered_data['longitude'].mean(),
                zoom=11 if 'กรุงเทพมหานคร' in selected_province else 8,
                pitch=45,
                bearing=0
            )
            
            # Custom tooltip
            tooltip = {
                "html": """
                <div style="
                    background: linear-gradient(135deg, #1A3C6E 0%, #4D88FF 100%);
                    color: white;
                    padding: 12px;
                    border-radius: 8px;
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    border: 2px solid #B3D9FF;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
                ">
                    <div style="
                        display: flex;
                        align-items: center;
                        gap: 8px;
                        margin-bottom: 8px;
                        border-bottom: 1px solid rgba(255,255,255,0.3);
                        padding-bottom: 8px;
                    ">
                        <div style="
                            width: 12px;
                            height: 12px;
                            border-radius: 50%;
                            background-color: {color};
                        "></div>
                        <strong style="font-size: 16px;">{company}</strong>
                    </div>
                    <div style="font-size: 13px; line-height: 1.5;">
                        <div>📍 <strong>{province}</strong></div>
                        <div>🏘️ เขต: {district}</div>
                        <div>🏠 แขวง: {subdistrict}</div>
                        <div style="margin-top: 8px; opacity: 0.9;">
                            📌 Lat: {latitude:.4f}<br/>
                            📌 Long: {longitude:.4f}
                        </div>
                    </div>
                </div>
                """,
                "style": {
                    "backgroundColor": "transparent",
                    "border": "none"
                }
            }
            
            # Create deck
            deck = pdk.Deck(
                layers=layers,
                initial_view_state=view_state,
                tooltip=tooltip,
                map_style='light'
            )
            
            st.pydeck_chart(deck)
            
            # Show color legend
            self._show_color_legend(selected_brands, brand_colors_blue)
    
    def _show_color_legend(self, selected_brands, brand_colors_blue):
        """แสดงคำอธิบายสีในแผนที่"""
        st.markdown("""
        <div class="premium-card">
            <h4 style="
                color: #1A3C6E;
                margin-bottom: 1rem;
                display: flex;
                align-items: center;
                gap: 8px;
            ">
                <span>🎨</span>
                คำอธิบายสีในแผนที่
            </h4>
        """, unsafe_allow_html=True)
        
        # Create legend grid
        legend_cols = st.columns(5)
        brands_to_show = selected_brands if selected_brands else []
        
        for idx, brand in enumerate(brands_to_show):
            if brand in brand_colors_blue:
                color = brand_colors_blue[brand]
                col_idx = idx % 5
                with legend_cols[col_idx]:
                    st.markdown(f"""
                    <div style="
                        background: white;
                        padding: 0.8rem;
                        border-radius: 10px;
                        margin-bottom: 0.5rem;
                        border: 1px solid #E6F2FF;
                        display: flex;
                        align-items: center;
                        gap: 10px;
                        transition: all 0.3s ease;
                        cursor: pointer;
                    " onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 4px 12px rgba(0,0,0,0.1)'" 
                    onmouseout="this.style.transform='none'; this.style.boxShadow='none'">
                        <div style="
                            width: 20px;
                            height: 20px;
                            border-radius: 4px;
                            background-color: rgba({color[0]}, {color[1]}, {color[2]}, 0.8);
                            border: 2px solid rgba({color[0]}, {color[1]}, {color[2]}, 1);
                        "></div>
                        <span style="
                            color: #1A3C6E;
                            font-weight: 600;
                            font-size: 14px;
                        ">{brand}</span>
                    </div>
                    """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    def _show_data_table(self, filtered_data):
        """แสดงตารางข้อมูล"""
        st.markdown("""
        <div style="margin: 3rem 0 2rem 0;">
            <h3 style="
                color: #1A3C6E;
                margin-bottom: 1.5rem;
                display: flex;
                align-items: center;
                gap: 10px;
            ">
                <span style="font-size: 1.8rem;">📋</span>
                รายละเอียดปั๊มน้ำมัน
            </h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Prepare display dataframe
        display_df = filtered_data.copy()
        display_df = display_df[[
            'company', 'province', 'district', 'subdistrict', 
            'latitude', 'longitude'
        ]]
        
        display_df['latitude'] = display_df['latitude'].round(6)
        display_df['longitude'] = display_df['longitude'].round(6)
        
        # Rename columns
        display_df = display_df.rename(columns={
            'company': 'แบรนด์',
            'province': 'จังหวัด',
            'district': 'เขต',
            'subdistrict': 'แขวง',
            'latitude': 'ละติจูด',
            'longitude': 'ลองจิจูด'
        })
        
        # Display styled dataframe
        st.dataframe(
            display_df,
            use_container_width=True,
            height=350,
            column_config={
                "แบรนด์": st.column_config.TextColumn("แบรนด์", width="small"),
                "จังหวัด": st.column_config.TextColumn("จังหวัด", width="medium"),
                "เขต": st.column_config.TextColumn("เขต", width="medium"),
                "แขวง": st.column_config.TextColumn("แขวง", width="medium"),
                "ละติจูด": st.column_config.NumberColumn("ละติจูด", format="%.6f"),
                "ลองจิจูด": st.column_config.NumberColumn("ลองจิจูด", format="%.6f")
            }
        )
        
        # Download button
        csv = display_df.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="📥 ดาวน์โหลดข้อมูล CSV",
            data=csv,
            file_name=f"oil_pin_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            help="ดาวน์โหลดข้อมูลปั๊มน้ำมันที่ค้นหาได้",
            key="download_csv",
            use_container_width=True
        )
    
    def _show_statistics_charts(self, filtered_data, selected_province):
        """แสดงกราฟสถิติ"""
        st.markdown("""
        <div style="margin: 3rem 0 2rem 0;">
            <h3 style="
                color: #1A3C6E;
                margin-bottom: 1.5rem;
                display: flex;
                align-items: center;
                gap: 10px;
            ">
                <span style="font-size: 1.8rem;">📈</span>
                สถิติการกระจายตัว
            </h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Create tabs for charts
        tab_chart1, tab_chart2 = st.tabs(["📊 ตามแบรนด์", "📍 ตามเขต"])
        
        with tab_chart1:
            if 'company' in filtered_data.columns:
                brand_counts = filtered_data['company'].value_counts()
                
                fig_brand = go.Figure(data=[
                    go.Bar(
                        x=brand_counts.index,
                        y=brand_counts.values,
                        marker_color=['#4D88FF' if i < 3 else '#B3D9FF' for i in range(len(brand_counts))],
                        marker_line_color='#1A3C6E',
                        marker_line_width=1.5,
                        opacity=0.8,
                        text=brand_counts.values,
                        textposition='auto',
                        hoverinfo='x+y'
                    )
                ])
                
                fig_brand.update_layout(
                    title={
                        'text': f"📊 จำนวนปั๊มตามแบรนด์ ({selected_province})",
                        'font': {'size': 20, 'color': '#1A3C6E'}
                    },
                    xaxis_title="แบรนด์",
                    yaxis_title="จำนวนปั๊ม",
                    plot_bgcolor='#F8FBFF',
                    paper_bgcolor='white',
                    font=dict(color='#1A3C6E'),
                    height=400,
                    showlegend=False
                )
                
                st.plotly_chart(fig_brand, use_container_width=True)
        
        with tab_chart2:
            if 'district' in filtered_data.columns and filtered_data['district'].nunique() > 1:
                district_counts = filtered_data['district'].value_counts()
                
                fig_district = go.Figure(data=[
                    go.Bar(
                        x=district_counts.index,
                        y=district_counts.values,
                        marker_color='#4D88FF',
                        marker_line_color='#1A3C6E',
                        marker_line_width=1.5,
                        opacity=0.8,
                        text=district_counts.values,
                        textposition='auto',
                        hoverinfo='x+y'
                    )
                ])
                
                fig_district.update_layout(
                    title={
                        'text': f"📍 จำนวนปั๊มตามเขต ({selected_province})",
                        'font': {'size': 20, 'color': '#1A3C6E'}
                    },
                    xaxis_title="เขต",
                    yaxis_title="จำนวนปั๊ม",
                    plot_bgcolor='#F8FBFF',
                    paper_bgcolor='white',
                    font=dict(color='#1A3C6E'),
                    height=400,
                    showlegend=False
                )
                
                st.plotly_chart(fig_district, use_container_width=True)
            else:
                st.info("เลือกมากกว่า 1 เขตเพื่อแสดงกราฟ")
    
    def _show_no_results(self):
        """แสดงเมื่อไม่พบข้อมูล"""
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #FFF3E6 0%, #FFE0B3 100%);
            padding: 3rem;
            border-radius: 15px;
            text-align: center;
            border: 2px solid #FF9800;
            margin: 2rem 0;
        ">
            <div style="font-size: 4rem; margin-bottom: 1rem;">🔍</div>
            <h3 style="color: #E65100; margin-bottom: 1rem;">
                ไม่พบปั๊มน้ำมันที่ตรงกับเงื่อนไข
            </h3>
            <p style="color: #666; max-width: 600px; margin: 0 auto;">
                ลองเปลี่ยนเงื่อนไขการค้นหาดังนี้:
            </p>
            <div style="
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 1rem;
                margin-top: 2rem;
            ">
                <div style="
                    background: white;
                    padding: 1rem;
                    border-radius: 10px;
                    border-left: 4px solid #4D88FF;
                ">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">🌆</div>
                    <strong>เลือกจังหวัดอื่น</strong>
                </div>
                <div style="
                    background: white;
                    padding: 1rem;
                    border-radius: 10px;
                    border-left: 4px solid #4D88FF;
                ">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">🏭</div>
                    <strong>เพิ่มแบรนด์ที่เลือก</strong>
                </div>
                <div style="
                    background: white;
                    padding: 1rem;
                    border-radius: 10px;
                    border-left: 4px solid #4D88FF;
                ">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">📍</div>
                    <strong>ลดจำนวนเขตที่เลือก</strong>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def _show_sidebar(self):
        """แสดง sidebar สำหรับเมนูและข้อมูลเพิ่มเติม"""
        with st.sidebar:
            st.markdown("""
            <div style="text-align: center; padding: 1rem 0; margin-bottom: 2rem;">
                <h2 style="color: #1A3C6E;">⛽ Oil Station Map</h2>
                <p style="color: #4D88FF; font-size: 0.9rem;">
                    Premium Edition
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Refresh button
            if st.button("🔄 โหลดข้อมูลใหม่", use_container_width=True):
                st.session_state.station_data_loaded = False
                st.session_state.station_df = None
                st.rerun()
            
            # Information
            st.markdown("### 📚 ข้อมูลเพิ่มเติม")
            st.info("""
            **แหล่งข้อมูล:**
            - ฐานข้อมูล DuckDB: `dads5001.duckdb`
            - ตาราง: `pin`
            - อัปเดตล่าสุด: {}
            """.format(datetime.now().strftime("%d/%m/%Y %H:%M")))
            
            
            # About section
            st.markdown("""
            <div style="text-align: center; padding: 1rem 0; color: #666; font-size: 0.85rem;">
                <p>© 2025 OILSOPHANG</p>
                <p>Version 2.1.0</p>
            </div>
            """, unsafe_allow_html=True)
    
    def run(self):
        """Main method to run the application"""
        # Show sidebar
        self._show_sidebar()
        
        # Show main content
        self._show_header()
        
        # Load data
        station_df = self._show_loading_section()
        
        if station_df is not None and not station_df.empty:
            # Show filters and get selections
            selected_province, selected_brands, selected_districts, province_filtered = self._show_filter_section(station_df)
            
            # Apply filters
            filtered_data = province_filtered.copy()
            if selected_brands:
                filtered_data = filtered_data[filtered_data['company'].isin(selected_brands)]
            if selected_districts:
                filtered_data = filtered_data[filtered_data['district'].astype(str).isin(selected_districts)]
            
            if not filtered_data.empty:
                # Show statistics
                self._show_statistics(filtered_data)
                
                # Show map
                self._show_map(filtered_data, selected_province, selected_brands)
                
                # Show data table
                self._show_data_table(filtered_data)
                
                # Show statistics charts
                self._show_statistics_charts(filtered_data, selected_province)
            else:
                self._show_no_results()
    
    def run_simple(self):
        """รุ่นที่ง่ายสำหรับรันเดี่ยว"""
        # Show header
        self._show_header()
        
        # Load data
        station_df = self._show_loading_section()
        
        if station_df is not None and not station_df.empty:
            # Show filters
            selected_province, selected_brands, selected_districts, province_filtered = self._show_filter_section(station_df)
            
            # Apply filters
            filtered_data = province_filtered.copy()
            if selected_brands:
                filtered_data = filtered_data[filtered_data['company'].isin(selected_brands)]
            if selected_districts:
                filtered_data = filtered_data[filtered_data['district'].astype(str).isin(selected_districts)]
            
            if not filtered_data.empty:
                self._show_statistics(filtered_data)
                self._show_map(filtered_data, selected_province, selected_brands)
                self._show_data_table(filtered_data)
                self._show_statistics_charts(filtered_data, selected_province)
            else:
                self._show_no_results()


# ============================================================================
# MAIN EXECUTION
# ============================================================================
if __name__ == "__main__":
    # Create app instance
    app = OilStationMapApp()
    
    # Run the app
    app.run()
    
    # หรือใช้รุ่นง่าย
    # app.run_simple()