import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ตั้งค่าหน้าเว็บ
st.set_page_config(
    page_title="ศูนย์ข่าวสารและประชาสัมพันธ์",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Premium Blue Theme CSS
st.markdown("""
<style>
    /* Premium Blue Gradient Background */
    .stApp {
        background: linear-gradient(135deg, #f8fcff 0%, #e8f4ff 30%, #d9ecff 100%);
        font-family: 'Sarabun', 'Kanit', 'Prompt', 'Inter', sans-serif;
    }
    
    /* Premium Header with Glass Effect */
    .main-header {
        background: linear-gradient(90deg, 
            rgba(255, 255, 255, 0.95) 0%, 
            rgba(248, 252, 255, 0.98) 100%);
        backdrop-filter: blur(10px);
        color: #1e3a8a;
        padding: 3rem 2.5rem;
        border-radius: 0 0 40px 40px;
        text-align: center;
        margin-bottom: 2.5rem;
        box-shadow: 0 10px 40px rgba(30, 58, 138, 0.08);
        position: relative;
        overflow: hidden;
        border: 1px solid rgba(173, 216, 230, 0.3);
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, 
            #60a5fa 0%, 
            #3b82f6 33%, 
            #2563eb 66%, 
            #1d4ed8 100%);
        border-radius: 2px;
    }
    
    /* Premium News Card */
    .premium-news-card {
        background: linear-gradient(145deg, #ffffff 0%, #f8fcff 100%);
        padding: 2.2rem;
        border-radius: 24px;
        margin-bottom: 1.8rem;
        box-shadow: 
            0 4px 20px rgba(30, 58, 138, 0.06),
            0 1px 4px rgba(30, 58, 138, 0.04),
            inset 0 0 0 1px rgba(255, 255, 255, 0.8);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        border: 1px solid rgba(191, 219, 254, 0.4);
        position: relative;
        overflow: hidden;
    }
    
    .premium-news-card:hover {
        transform: translateY(-6px);
        box-shadow: 
            0 20px 40px rgba(30, 58, 138, 0.12),
            0 8px 16px rgba(30, 58, 138, 0.08),
            inset 0 0 0 1px rgba(255, 255, 255, 0.9);
        border-color: rgba(59, 130, 246, 0.3);
    }
    
    .premium-news-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 4px;
        background: linear-gradient(90deg, #60a5fa 0%, #3b82f6 100%);
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    
    .premium-news-card:hover::before {
        opacity: 1;
    }
    
    /* Breaking News Card */
    .breaking-news-card {
        background: linear-gradient(145deg, #fef2f2 0%, #fee2e2 100%);
        border: 1px solid rgba(248, 113, 113, 0.2);
        box-shadow: 0 4px 20px rgba(239, 68, 68, 0.08);
    }
    
    .breaking-news-card:hover {
        box-shadow: 0 20px 40px rgba(239, 68, 68, 0.12);
    }
    
    .breaking-news-card::before {
        background: linear-gradient(90deg, #ef4444 0%, #dc2626 100%);
    }
    
    /* Premium Badge */
    .premium-badge {
        display: inline-block;
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: white;
        padding: 0.4rem 1.2rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-right: 0.8rem;
        margin-bottom: 0.8rem;
        box-shadow: 0 2px 8px rgba(59, 130, 246, 0.2);
        transition: all 0.3s ease;
    }
    
    .premium-badge:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
    }
    
    .badge-breaking {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
    }
    
    .badge-event {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
    }
    
    .badge-announcement {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
    }
    
    /* Premium Stats Card */
    .premium-stat-card {
        background: linear-gradient(145deg, #ffffff 0%, #f8fcff 100%);
        padding: 1.8rem;
        border-radius: 20px;
        text-align: center;
        box-shadow: 
            0 4px 16px rgba(30, 58, 138, 0.06),
            inset 0 0 0 1px rgba(191, 219, 254, 0.3);
        transition: all 0.3s ease;
        border: 1px solid rgba(191, 219, 254, 0.2);
        position: relative;
        overflow: hidden;
    }
    
    .premium-stat-card:hover {
        transform: translateY(-4px);
        box-shadow: 
            0 12px 28px rgba(30, 58, 138, 0.1),
            inset 0 0 0 1px rgba(191, 219, 254, 0.4);
    }
    
    .premium-stat-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 4px;
        background: linear-gradient(90deg, #60a5fa 0%, #3b82f6 100%);
    }
    
    /* Premium Button */
    .stButton > button {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: white;
        border: none;
        padding: 0.8rem 2rem;
        border-radius: 12px;
        font-weight: 600;
        font-size: 0.95rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.2);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(59, 130, 246, 0.3);
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
    }
    
    /* Premium Sidebar */
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, 
            rgba(255, 255, 255, 0.98) 0%, 
            rgba(248, 252, 255, 0.98) 100%);
        backdrop-filter: blur(10px);
        padding: 1.8rem;
        border-radius: 24px;
        box-shadow: 
            0 4px 20px rgba(30, 58, 138, 0.06),
            inset 0 0 0 1px rgba(191, 219, 254, 0.2);
        border: 1px solid rgba(191, 219, 254, 0.3);
    }
    
    /* Premium Section Divider */
    .premium-divider {
        height: 1px;
        background: linear-gradient(90deg, 
            transparent 0%, 
            rgba(59, 130, 246, 0.2) 50%, 
            transparent 100%);
        margin: 2.5rem 0;
    }
    
    /* Premium Input Fields */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > div,
    .stDateInput > div > div > input {
        background: rgba(255, 255, 255, 0.9);
        border: 1px solid rgba(191, 219, 254, 0.4);
        border-radius: 12px;
        padding: 0.5rem 1rem;
        box-shadow: 0 2px 8px rgba(30, 58, 138, 0.04);
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div > div:focus,
    .stDateInput > div > div > input:focus {
        border-color: #3b82f6;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
    }
    
    /* Premium Expander */
    .streamlit-expanderHeader {
        background: linear-gradient(145deg, #ffffff 0%, #f8fcff 100%) !important;
        border: 1px solid rgba(191, 219, 254, 0.4) !important;
        border-radius: 12px !important;
        margin-bottom: 0.5rem !important;
        transition: all 0.3s ease !important;
    }
    
    .streamlit-expanderHeader:hover {
        border-color: rgba(59, 130, 246, 0.3) !important;
        box-shadow: 0 4px 12px rgba(30, 58, 138, 0.06) !important;
    }
    
    /* Premium Footer */
    .premium-footer {
        background: linear-gradient(90deg, 
            rgba(255, 255, 255, 0.95) 0%, 
            rgba(248, 252, 255, 0.98) 100%);
        backdrop-filter: blur(10px);
        color: #475569;
        padding: 2.5rem;
        border-radius: 24px 24px 0 0;
        margin-top: 3rem;
        text-align: center;
        box-shadow: 
            0 -4px 20px rgba(30, 58, 138, 0.06),
            inset 0 1px 0 0 rgba(191, 219, 254, 0.3);
        border-top: 1px solid rgba(191, 219, 254, 0.3);
    }
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(219, 234, 254, 0.3);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #60a5fa 0%, #3b82f6 100%);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
    }
    
    /* Premium Typography */
    h1, h2, h3, h4 {
        font-weight: 700;
        letter-spacing: -0.025em;
    }
    
    h1 {
        color: #1e3a8a;
        background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    h2 {
        color: #1e40af;
        position: relative;
        display: inline-block;
    }
    
    h2::after {
        content: '';
        position: absolute;
        bottom: -8px;
        left: 0;
        width: 60px;
        height: 3px;
        background: linear-gradient(90deg, #60a5fa 0%, #3b82f6 100%);
        border-radius: 2px;
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .main-header {
            padding: 2rem 1.5rem;
        }
        
        .premium-news-card {
            padding: 1.5rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# ===========================================
# SNOWFLAKE CONNECTION MANAGER
# ===========================================

sf = st.secrets["connections"]["snowflake"]

def get_connection():
    return snowflake.connector.connect(
        account=sf["account"], user=sf["user"], password=sf["password"],
        role=sf["role"], warehouse=sf["warehouse"],
        database=sf["database"], schema=sf["schema"]
    )

class SnowflakeManager:
    """Manager for Snowflake database operations"""
    
    def __init__(self):
        self.conn = get_connection()
        
    def execute_query(self, query, params=None):
        """Execute SQL query and return DataFrame"""
        try:
            cur = self.conn.cursor()
            if params:
                cur.execute(query, params)
            else:
                cur.execute(query)
            
            # Get column names
            columns = [col[0] for col in cur.description]
            
            # Fetch data
            data = cur.fetchall()
            
            # Convert to DataFrame
            df = pd.DataFrame(data, columns=columns)
            
            cur.close()
            return df
            
        except Exception as e:
            st.error(f"❌ เกิดข้อผิดพลาดในการดึงข้อมูล: {str(e)}")
            return pd.DataFrame()
    
    def execute_update(self, query, params=None):
        """Execute update/insert query"""
        try:
            cur = self.conn.cursor()
            if params:
                cur.execute(query, params)
            else:
                cur.execute(query)
            self.conn.commit()
            cur.close()
            return True
        except Exception as e:
            st.error(f"❌ เกิดข้อผิดพลาดในการอัปเดตข้อมูล: {str(e)}")
            return False
    
    def get_latest_news(self, limit=10):
        """Get latest news articles - CORRECTED VERSION"""
        query = """
        SELECT 
            ARTICLE_ID,
            TITLE,
            CONTENT,
            CATEGORY,
            ARTICLE_TYPE,
            PUBLISH_DATE,
            PUBLISH_TIME,
            VIEW_COUNT,
            AUTHOR,
            PRIORITY_LEVEL,
            TAGS
        FROM NEWS_ARTICLES 
        WHERE IS_ACTIVE = TRUE
        ORDER BY 
            PRIORITY_LEVEL ASC,
            PUBLISH_DATE DESC,
            PUBLISH_TIME DESC
        LIMIT ?
        """
        return self.execute_query(query, (limit,))
        
    def get_upcoming_events(self):
        """Get upcoming events"""
        query = """
        SELECT 
            EVENT_ID,
            EVENT_NAME,
            EVENT_DATE,
            START_TIME,
            END_TIME,
            LOCATION,
            EVENT_TYPE,
            ORGANIZER,
            DESCRIPTION
        FROM EVENTS
        WHERE EVENT_DATE >= CURRENT_DATE()
            AND IS_ACTIVE = TRUE
        ORDER BY EVENT_DATE ASC, START_TIME ASC
        LIMIT 10
        """
        return self.execute_query(query)
    
    def get_active_announcements(self):
        """Get active announcements"""
        query = """
        SELECT 
            ANNOUNCEMENT_ID,
            TITLE,
            ANNOUNCEMENT_TYPE,
            START_DATE,
            END_DATE,
            STATUS,
            LOCATION,
            DESCRIPTION
        FROM ANNOUNCEMENTS
        WHERE IS_ACTIVE = TRUE
            AND STATUS = 'ACTIVE'
        ORDER BY IS_PINNED DESC, START_DATE DESC
        LIMIT 10
        """
        return self.execute_query(query)
    
    def get_dashboard_stats(self):
        """Get dashboard statistics - safe version"""
        try:
            query = """
            SELECT 
                COALESCE((SELECT COUNT(*) FROM NEWS_ARTICLES WHERE IS_ACTIVE = TRUE), 0) as TOTAL_ARTICLES,
                COALESCE((SELECT SUM(VIEW_COUNT) FROM NEWS_ARTICLES WHERE IS_ACTIVE = TRUE), 0) as TOTAL_VIEWS,
                COALESCE((SELECT COUNT(*) FROM ANNOUNCEMENTS WHERE IS_ACTIVE = TRUE AND STATUS = 'ACTIVE'), 0) as ACTIVE_ANNOUNCEMENTS,
                COALESCE((SELECT COUNT(*) FROM EVENTS WHERE EVENT_DATE >= CURRENT_DATE() AND IS_ACTIVE = TRUE), 0) as UPCOMING_EVENTS
            """
            return self.execute_query(query)
        except Exception as e:
            st.error(f"❌ Error getting dashboard stats: {str(e)}")
            # Return empty DataFrame with default values
            return pd.DataFrame({
                'TOTAL_ARTICLES': [0],
                'TOTAL_VIEWS': [0],
                'ACTIVE_ANNOUNCEMENTS': [0],
                'UPCOMING_EVENTS': [0]
            })
    
    def get_category_stats(self):
        """Get statistics by category"""
        query = """
        SELECT 
            CATEGORY,
            COUNT(*) as ARTICLE_COUNT,
            SUM(VIEW_COUNT) as TOTAL_VIEWS,
            AVG(VIEW_COUNT) as AVG_VIEWS
        FROM NEWS_ARTICLES 
        WHERE IS_ACTIVE = TRUE
        GROUP BY CATEGORY
        ORDER BY ARTICLE_COUNT DESC
        """
        return self.execute_query(query)

# Initialize Snowflake Manager
db_manager = SnowflakeManager()

# ===========================================
# PREMIUM HEADER
# ===========================================

st.markdown("""
<div class="main-header">
    <div style="position: relative; z-index: 2;">
        <h1 style="margin:0; font-size: 3.5rem; font-weight: 800; letter-spacing: -0.5px;">
            📰 ศูนย์ข่าวสารและประชาสัมพันธ์
        </h1>
        <p style="margin:1rem 0 0 0; font-size: 1.3rem; color: #4b5563; font-weight: 400;">
            แหล่งรวมข้อมูลข่าวสาร การประกาศ และกิจกรรมล่าสุด
        </p>
        <div style="margin-top: 1.5rem; display: flex; justify-content: center; gap: 1rem;">
            <span style="background: rgba(96, 165, 250, 0.1); color: #1e40af; padding: 0.5rem 1.5rem; 
                      border-radius: 20px; font-weight: 500; border: 1px solid rgba(96, 165, 250, 0.3);">
                📰 ข่าวสารล่าสุด
            </span>
            <span style="background: rgba(96, 165, 250, 0.1); color: #1e40af; padding: 0.5rem 1.5rem; 
                      border-radius: 20px; font-weight: 500; border: 1px solid rgba(96, 165, 250, 0.3);">
                📢 ประกาศสำคัญ
            </span>
            <span style="background: rgba(96, 165, 250, 0.1); color: #1e40af; padding: 0.5rem 1.5rem; 
                      border-radius: 20px; font-weight: 500; border: 1px solid rgba(96, 165, 250, 0.3);">
                📅 กิจกรรม
            </span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ===========================================
# PREMIUM SIDEBAR
# ===========================================

with st.sidebar:
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <div style="width: 60px; height: 60px; background: linear-gradient(135deg, #60a5fa 0%, #3b82f6 100%); 
                 border-radius: 16px; display: flex; align-items: center; justify-content: center; 
                 margin: 0 auto 1rem; color: white; font-size: 1.8rem; box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);">
            🔍
        </div>
        <h3 style="color: #1e3a8a; margin: 0;">ค้นหาข่าวสาร</h3>
    </div>
    """, unsafe_allow_html=True)
    
    search_keyword = st.text_input("", placeholder="🔍 ค้นหาตามคำสำคัญ...", 
                                   help="เช่น น้ำมัน, ราคา, OPEC, พลังงาน")
    
    st.markdown("### 📂 หมวดหมู่")
    categories = ["ทั้งหมด", "ข่าวด่วน", "นโยบาย", "เทคโนโลยี", "เศรษฐกิจ", "พลังงาน", "สิ่งแวดล้อม"]
    selected_category = st.selectbox("เลือกหมวดหมู่", categories, label_visibility="collapsed")
    
    st.markdown("### 📅 วันที่เผยแพร่")
    date_range = st.date_input(
        "",
        [datetime.now().date() - timedelta(days=30), datetime.now().date()],
        label_visibility="collapsed"
    )
    
    # ดึงสถิติสำหรับ sidebar
    sidebar_stats = db_manager.get_dashboard_stats()
    if not sidebar_stats.empty and len(sidebar_stats) > 0:
        st.markdown("""
        <div style="margin-top: 2rem; padding-top: 1.5rem; border-top: 1px solid rgba(191, 219, 254, 0.3);">
            <h3 style="color: #1e3a8a; margin-bottom: 1rem;">📊 สถิติข่าวสาร</h3>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            total_articles = int(sidebar_stats.iloc[0].get('TOTAL_ARTICLES', 0))
            st.metric("ข่าวทั้งหมด", f"{total_articles:,}", "")
        with col2:
            total_views = int(sidebar_stats.iloc[0].get('TOTAL_VIEWS', 0))
            st.metric("ยอดเข้าชม", f"{total_views:,}", "")

# ===========================================
# PREMIUM DASHBOARD STATS
# ===========================================

st.markdown("## 📊 ภาพรวมศูนย์ข่าวสาร")

# ดึงสถิติใหม่สำหรับ dashboard
dashboard_stats = db_manager.get_dashboard_stats()

if not dashboard_stats.empty and len(dashboard_stats) > 0:
    stats_row = dashboard_stats.iloc[0]
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="premium-stat-card">
            <div style="font-size: 2.2rem; color: #1e40af; margin-bottom: 0.5rem;">📰</div>
            <div style="font-size: 2.5rem; font-weight: 700; color: #1e3a8a; margin-bottom: 0.3rem;">
                """ + f"{int(stats_row.get('TOTAL_ARTICLES', 0)):,}" + """
            </div>
            <div style="color: #6b7280; font-size: 0.9rem;">ข่าวสารทั้งหมด</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="premium-stat-card">
            <div style="font-size: 2.2rem; color: #1e40af; margin-bottom: 0.5rem;">👁️</div>
            <div style="font-size: 2.5rem; font-weight: 700; color: #1e3a8a; margin-bottom: 0.3rem;">
                """ + f"{int(stats_row.get('TOTAL_VIEWS', 0)):,}" + """
            </div>
            <div style="color: #6b7280; font-size: 0.9rem;">จำนวนผู้ชม</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="premium-stat-card">
            <div style="font-size: 2.2rem; color: #1e40af; margin-bottom: 0.5rem;">📢</div>
            <div style="font-size: 2.5rem; font-weight: 700; color: #1e3a8a; margin-bottom: 0.3rem;">
                """ + f"{int(stats_row.get('ACTIVE_ANNOUNCEMENTS', 0)):,}" + """
            </div>
            <div style="color: #6b7280; font-size: 0.9rem;">ประกาศสำคัญ</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="premium-stat-card">
            <div style="font-size: 2.2rem; color: #1e40af; margin-bottom: 0.5rem;">📅</div>
            <div style="font-size: 2.5rem; font-weight: 700; color: #1e3a8a; margin-bottom: 0.3rem;">
                """ + f"{int(stats_row.get('UPCOMING_EVENTS', 0)):,}" + """
            </div>
            <div style="color: #6b7280; font-size: 0.9rem;">กิจกรรมใกล้ถึง</div>
        </div>
        """, unsafe_allow_html=True)



# ===========================================
# PREMIUM NEWS SECTION
# ===========================================

st.markdown("""
<br><br><hr><br><div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem;">
    <h2>📰 ข่าวสารล่าสุด</h2>
    <div style="color: #6b7280; font-size: 0.9rem;">
        อัปเดตล่าสุด: """ + datetime.now().strftime("%d/%m/%Y %H:%M") + """
    </div>
</div>
""", unsafe_allow_html=True)

# ค้นหาข่าวสาร
if search_keyword:
    news_data = db_manager.get_latest_news(20)
    if search_keyword:
        news_data = news_data[news_data.apply(lambda row: row.astype(str).str.contains(search_keyword, case=False).any(), axis=1)]
else:
    news_data = db_manager.get_latest_news(20)

# แสดงข่าวสาร
if not news_data.empty:
    for idx, news in news_data.iterrows():
        card_class = "premium-news-card"
        badge_class = "premium-badge"
        
        if news.get('ARTICLE_TYPE') == 'BREAKING':
            card_class += " breaking-news-card"
            badge_class += " badge-breaking"
        
        st.markdown(f'<div class="{card_class}">', unsafe_allow_html=True)
        
        # Header with badge
        col1, col2 = st.columns([0.8, 0.2])
        with col1:
            title = news.get('TITLE', 'ไม่มีหัวข้อ')
            st.markdown(f"### {title}")
        with col2:
            view_count = news.get('VIEW_COUNT', 0)
            st.markdown(f"""
            <div style="text-align: right;">
                <div style="font-size: 0.9rem; color: #6b7280; margin-bottom: 0.3rem;">👁️‍🗨️</div>
                <div style="font-size: 1.2rem; font-weight: 700; color: #1e40af;">
                    {view_count:,}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Badges
        category = news.get('CATEGORY', 'ไม่ระบุ')
        author = news.get('AUTHOR', 'ไม่ระบุ')
        
        st.markdown(f'<span class="{badge_class}">{category}</span>', unsafe_allow_html=True)
        st.markdown(f"""
        <div style="margin: 0.5rem 0; color: #6b7280; font-size: 0.9rem;">
            ✍️ โดย {author}
        </div>
        """, unsafe_allow_html=True)
        
        # Content preview
        content = news.get('CONTENT', '')
        if content:
            preview = content[:250] + '...' if len(content) > 250 else content
            st.markdown(f"""
            <div style="color: #4b5563; line-height: 1.7; padding: 1rem 0; margin: 1rem 0;
                        border-left: 3px solid rgba(96, 165, 250, 0.3); padding-left: 1rem;">
                {preview}
            </div>
            """, unsafe_allow_html=True)
        
        # Footer with date and read button
        col_date, col_button = st.columns([0.7, 0.3])
        with col_date:
            publish_date = news.get('PUBLISH_DATE')
            if publish_date:
                if isinstance(publish_date, str):
                    try:
                        publish_date = datetime.strptime(publish_date, '%Y-%m-%d')
                        date_str = publish_date.strftime('%d/%m/%Y')
                    except:
                        date_str = str(publish_date)
                else:
                    date_str = str(publish_date)
                
                st.markdown(f"""
                <div style="display: flex; align-items: center; gap: 0.5rem; color: #6b7280; font-size: 0.9rem;">
                    <span>📅</span>
                    <span>เผยแพร่: {date_str}</span>
                </div>
                """, unsafe_allow_html=True)
        
        with col_button:
            article_id = news.get('ARTICLE_ID')
            if article_id:
                if st.button("📖 อ่านเพิ่มเติม", key=f"read_{article_id}"):
                    st.success(f"กำลังเปิดข่าว: {title}")
        
        st.markdown('</div>', unsafe_allow_html=True)
else:
    st.markdown("""
    <div style="text-align: center; padding: 3rem; color: #6b7280;">
        <div style="font-size: 3rem; margin-bottom: 1rem;">📭</div>
        <h3 style="color: #4b5563;">ยังไม่มีข่าวสารในขณะนี้</h3>
        <p>โปรดตรวจสอบอีกครั้งในภายหลัง</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="premium-divider"></div>', unsafe_allow_html=True)

# ===========================================
# PREMIUM EVENTS SECTION
# ===========================================

st.markdown("""
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem;">
    <h2>📅 กิจกรรมและกำหนดการ</h2>
    <div style="color: #6b7280; font-size: 0.9rem;">
        แสดงกิจกรรมที่กำลังจะมาถึง
    </div>
</div>
""", unsafe_allow_html=True)

events_data = db_manager.get_upcoming_events()
if not events_data.empty:
    for idx, event in events_data.iterrows():
        event_name = event.get('EVENT_NAME', 'ไม่มีชื่อกิจกรรม')
        event_date = event.get('EVENT_DATE', 'ไม่ระบุ')
        
        with st.expander(f"**{event_name}** - 📅 {event_date}", expanded=False):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown("""
                <div style="padding: 1rem; background: rgba(219, 234, 254, 0.1); 
                            border-radius: 12px; margin-bottom: 1rem;">
                """, unsafe_allow_html=True)
                
                # Event details
                details = []
                
                start_time = event.get('START_TIME')
                end_time = event.get('END_TIME')
                if start_time and end_time:
                    details.append(f"**⏰ เวลา:** {start_time} - {end_time}")
                
                location = event.get('LOCATION')
                if location:
                    details.append(f"**📍 สถานที่:** {location}")
                
                organizer = event.get('ORGANIZER')
                if organizer:
                    details.append(f"**👥 จัดโดย:** {organizer}")
                
                event_type = event.get('EVENT_TYPE')
                if event_type:
                    details.append(f"**🎯 ประเภท:** {event_type}")
                
                for detail in details:
                    st.markdown(f"- {detail}")
                
                st.markdown("</div>", unsafe_allow_html=True)
                
                # Description
                description = event.get('DESCRIPTION')
                if description:
                    st.markdown("**📋 รายละเอียด:**")
                    st.markdown(description)
            
            with col2:
                st.markdown("""
                <div style="text-align: center; padding: 1.5rem; 
                            background: linear-gradient(135deg, rgba(96, 165, 250, 0.1) 0%, rgba(59, 130, 246, 0.1) 100%);
                            border-radius: 12px; border: 1px solid rgba(96, 165, 250, 0.2);">
                """, unsafe_allow_html=True)
                
                event_id = event.get('EVENT_ID')
                if event_id:
                    if st.button("📝 ลงทะเบียน", key=f"reg_{event_id}", use_container_width=True):
                        st.info("กำลังเปิดแบบฟอร์มลงทะเบียน...")
                
                st.markdown("""
                <div style="margin-top: 1rem; color: #6b7280; font-size: 0.85rem;">
                    ⚡ ลงทะเบียนล่วงหน้า
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("---")
else:
    st.markdown("""
    <div style="text-align: center; padding: 2rem; color: #6b7280;">
        <div style="font-size: 2rem; margin-bottom: 0.5rem;">📅</div>
        ยังไม่มีกิจกรรมที่กำลังจะมาถึง
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="premium-divider"></div>', unsafe_allow_html=True)

# ===========================================
# PREMIUM ANNOUNCEMENTS SECTION
# ===========================================

st.markdown("""
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem;">
    <h2>📢 ประกาศสำคัญ</h2>
    <div style="color: #6b7280; font-size: 0.9rem;">
        ประกาศล่าสุดจากศูนย์ข่าวสาร
    </div>
</div>
""", unsafe_allow_html=True)

announcements_data = db_manager.get_active_announcements()
if not announcements_data.empty:
    for idx, ann in announcements_data.iterrows():
        title = ann.get('TITLE', 'ไม่มีหัวข้อประกาศ')
        start_date = ann.get('START_DATE', 'ไม่ระบุ')
        ann_type = ann.get('ANNOUNCEMENT_TYPE', 'ทั่วไป')
        
        # Map announcement types to icons
        icon_map = {
            'IMPORTANT': '📌',
            'URGENT': '🚨', 
            'GENERAL': '📢'
        }
        icon = icon_map.get(ann_type, '📋')
        
        with st.expander(f"{icon} **{title}** - 📅 {start_date}", expanded=False):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                # Announcement details
                st.markdown(f"**🎯 ประเภทประกาศ:** {ann_type}")
                
                status = ann.get('STATUS', 'ไม่ระบุ')
                status_color = {
                    'ACTIVE': '#10b981',
                    'EXPIRED': '#ef4444',
                    'CANCELLED': '#6b7280'
                }.get(status, '#6b7280')
                
                st.markdown(f"**🟢 สถานะ:** <span style='color:{status_color};'>{status}</span>", unsafe_allow_html=True)
                
                location = ann.get('LOCATION')
                if location:
                    st.markdown(f"**📍 สถานที่:** {location}")
                
                # Description
                description = ann.get('DESCRIPTION')
                if description:
                    st.markdown("---")
                    st.markdown("**📋 รายละเอียด:**")
                    st.markdown(description)
            
            with col2:
                st.markdown("""
                <div style="text-align: center; padding: 1rem; 
                            background: rgba(245, 158, 11, 0.1);
                            border-radius: 12px; border: 1px solid rgba(245, 158, 11, 0.2);">
                """, unsafe_allow_html=True)
                
                if ann_type == 'IMPORTANT':
                    st.markdown("""
                    <div style="font-size: 1.5rem; color: #f59e0b; margin-bottom: 0.5rem;">
                        ⭐
                    </div>
                    <div style="color: #92400e; font-weight: 600; font-size: 0.9rem;">
                        ประกาศสำคัญ
                    </div>
                    """, unsafe_allow_html=True)
                elif ann_type == 'URGENT':
                    st.markdown("""
                    <div style="font-size: 1.5rem; color: #ef4444; margin-bottom: 0.5rem;">
                        ⚡
                    </div>
                    <div style="color: #991b1b; font-weight: 600; font-size: 0.9rem;">
                        ด่วน!
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div style="font-size: 1.5rem; color: #6b7280; margin-bottom: 0.5rem;">
                        📄
                    </div>
                    <div style="color: #4b5563; font-weight: 600; font-size: 0.9rem;">
                        ประกาศทั่วไป
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("</div>", unsafe_allow_html=True)
else:
    st.markdown("""
    <div style="text-align: center; padding: 2rem; color: #6b7280;">
        <div style="font-size: 2rem; margin-bottom: 0.5rem;">📭</div>
        ยังไม่มีประกาศสำคัญในขณะนี้
    </div>
    """, unsafe_allow_html=True)



# ===========================================
# ADMIN SECTION (Optional)
# ===========================================

if st.sidebar.checkbox("👑 โหมดผู้ดูแลระบบ", key="admin_mode"):
    st.sidebar.markdown("""
    <div style="padding: 1rem; background: rgba(59, 130, 246, 0.1); 
                border-radius: 12px; margin-top: 1rem; border: 1px solid rgba(59, 130, 246, 0.2);">
        <h4 style="color: #1e3a8a; margin-bottom: 0.5rem;">ผู้ดูแลระบบ</h4>
    </div>
    """, unsafe_allow_html=True)
    
    password = st.sidebar.text_input("รหัสผ่าน", type="password", key="admin_password")
    
    if password == st.secrets.get("admin_password", "admin123"):
        st.sidebar.success("✅ เข้าสู่ระบบผู้ดูแลแล้ว")
        
        # Add admin functionality here if needed