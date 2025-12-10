import streamlit as st
import time
from streamlit_extras.stylable_container import stylable_container

# Page config
st.set_page_config(
    page_title="ระบบเข้าสู่ระบบ",
    page_icon="🔐",
    layout="centered"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
    }
    .login-container {
        background: white;
        border-radius: 20px;
        padding: 3rem;
        box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        margin: 2rem auto;
        max-width: 450px;
    }
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        height: 3rem;
        font-weight: 600;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border: none;
    }
    .stTextInput>div>div>input, .stTextInput>div>div>input:focus {
        border-radius: 12px;
        border: 2px solid #e0e0e0;
        padding: 0.75rem;
    }
    .success-message {
        background: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 12px;
        border: 1px solid #c3e6cb;
    }
    .company-logo {
        text-align: center;
        margin-bottom: 2rem;
    }
    .welcome-text {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Header Section
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="company-logo">', unsafe_allow_html=True)
        st.markdown("# 🚗 **FuelTrack**")
        st.markdown("### ระบบติดตามราคาน้ำมัน")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Login Container
    with stylable_container(
        key="login_container",
        css_styles="""
            {
                background: white;
                border-radius: 20px;
                padding: 3rem;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                margin: 1rem auto;
                max-width: 450px;
            }
        """
    ):
        # ถ้าล็อกอินแล้ว
        if st.session_state.get('logged_in'):
            st.markdown(f"""
            <div class="success-message">
                <h3>👋 ยินดีต้อนรับ!</h3>
                <p><strong>ชื่อผู้ใช้:</strong> {st.session_state['user_name']}</p>
                <p><strong>สถานะสมาชิก:</strong> {'✅ Premium' if st.session_state.get('subscribe_flag') else '🔵 Standard'}</p>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("🚪 ออกจากระบบ", use_container_width=True):
                    for key in ['logged_in', 'user_name', 'subscribe_flag']:
                        if key in st.session_state:
                            del st.session_state[key]
                    st.rerun()
            
            # แสดงเมนูหลักหลังจากล็อกอิน
            st.markdown("---")
            st.markdown("### 📊 เมนูหลัก")
            menu_col1, menu_col2 = st.columns(2)
            with menu_col1:
                if st.button("📈 ดูราคาน้ำมัน", use_container_width=True):
                    st.switch_page("pages/dashboard.py")
                if st.button("🔔 การแจ้งเตือน", use_container_width=True):
                    st.switch_page("pages/notifications.py")
            with menu_col2:
                if st.button("👤 โปรไฟล์", use_container_width=True):
                    st.switch_page("pages/profile.py")
                if st.button("⚙️ การตั้งค่า", use_container_width=True):
                    st.switch_page("pages/settings.py")
        
        else:
            # ฟอร์มล็อกอิน
            st.markdown('<div class="welcome-text">', unsafe_allow_html=True)
            st.markdown("## 🔑 เข้าสู่ระบบ")
            st.markdown("กรุณากรอกข้อมูลเพื่อเข้าสู่ระบบ")
            st.markdown('</div>', unsafe_allow_html=True)
            
            with st.form("login_form", clear_on_submit=False):
                username = st.text_input(
                    "👤 **ชื่อผู้ใช้**",
                    placeholder="กรอกชื่อผู้ใช้ของคุณ"
                )
                
                password = st.text_input(
                    "🔒 **รหัสผ่าน**", 
                    type="password",
                    placeholder="กรอกรหัสผ่าน"
                )
                
                col1, col2 = st.columns([1, 1])
                with col1:
                    remember_me = st.checkbox("จำการล็อกอิน")
                with col2:
                    st.markdown("[ลืมรหัสผ่าน?](#)", unsafe_allow_html=True)
                
                submit = st.form_submit_button(
                    "🚀 เข้าสู่ระบบ",
                    use_container_width=True
                )
                
                if submit:
                    if not username or not password:
                        st.error("❌ กรุณากรอกชื่อผู้ใช้และรหัสผ่าน")
                    else:
                        # เชื่อมต่อ Snowflake
                        conn = st.connection("snowflake", type="snowflake")
                        
                        # Query ข้อมูลผู้ใช้ (ป้องกัน SQL Injection)
                        query = """
                            SELECT username, password, subscribe_flag
                            FROM users
                            WHERE username = %s
                            LIMIT 1
                        """
                        df = conn.query(query, params=(username,))
                        
                        if df.empty:
                            st.error("❌ ไม่พบผู้ใช้งานนี้")
                        else:
                            # หา column subscribe_flag แบบ case-insensitive
                            col_subscribe = [c for c in df.columns if c.lower() == "subscribe_flag"][0]
                            subscribe_flag = int(df.iloc[0][col_subscribe])
                            
                            db_user = df.iloc[0]["USERNAME"]
                            db_pass = df.iloc[0]["PASSWORD"]
                            
                            if password == db_pass:
                                # บันทึก session
                                st.session_state['logged_in'] = True
                                st.session_state['user_name'] = db_user
                                st.session_state['subscribe_flag'] = subscribe_flag
                                if remember_me:
                                    st.session_state['remember_me'] = True
                                
                                # Loading animation
                                with st.spinner("กำลังเข้าสู่ระบบ..."):
                                    time.sleep(1)
                                
                                st.success("✅ เข้าสู่ระบบสำเร็จ!")
                                time.sleep(0.5)
                                st.rerun()
                            else:
                                st.error("❌ รหัสผ่านไม่ถูกต้อง")
            
            # Footer
            st.markdown("---")
            st.markdown(
                "<div style='text-align: center; color: #666;'>"
                "ยังไม่มีบัญชี? <a href='#' style='color: #667eea;'>สมัครสมาชิก</a>"
                "</div>",
                unsafe_allow_html=True
            )

if __name__ == "__main__":
    main()