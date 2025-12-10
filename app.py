import streamlit as st
import time
from pathlib import Path
import base64
# import streamlit.components.v1 as components # ไม่จำเป็นต้องใช้ components.html แล้ว

# ---------------- Page Config ----------------
st.set_page_config(
    page_title="Welcome",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------- Load Image ----------------
def load_image_base64(path):
    # ปรับปรุง: เพิ่มการจัดการ FileNotFoundError เพื่อความเสถียร
    try:
        img_bytes = Path(path).read_bytes()
        encoded = base64.b64encode(img_bytes).decode()
        return encoded
    except FileNotFoundError:
        # อาจจะแสดงข้อความแจ้งเตือนหรือใช้ภาพสำรองแทน
        st.error(f"Error: Image file not found at {path}")
        return "" 

img_base64 = load_image_base64("image/pic.png")

# ---------------- Hide Streamlit UI ----------------
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
header {visibility: hidden;}
footer {visibility: hidden;}
[data-testid="stSidebar"] {display: none;}
body, html, .stApp {overflow: hidden; height: 100%; margin: 0; padding: 0;}
.main .block-container {padding: 0 !important; max-width: 100% !important;}
</style>
""", unsafe_allow_html=True)

# ---------------- Full Screen Styling ----------------
st.markdown("""
<style>
.stApp {
    background-color: black;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: flex-start;
    height: 100vh;
    gap: 20px;
    padding-top: 20px;
    transition: opacity 1s ease;
}

.image-container img {
    max-width: 200vw;
    max-height: 75vh;
    object-fit: contain;
    border-radius: 20px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    margin: 0 auto;
    display: block;
    opacity: 0;
    animation: fadeIn 1.5s forwards;
}

@keyframes fadeIn {
    to {opacity: 1;}
}

.stButton>button {
    background: linear-gradient(135deg, #4e4e4e, #1b1b1b);
    color: white;
    padding: 18px 50px;
    font-size: 24px;
    border-radius: 50px;
    border: none;
    cursor: pointer;
    font-weight: bold;
    min-width: 280px;
    transition: all 0.3s ease;
}
.stButton>button:hover {
    background: linear-gradient(135deg, #8c8c8c, #545454);
    transform: translateY(-3px);
    box-shadow: 0 6px 20px rgba(255,255,255,0.3);
}
</style>
""", unsafe_allow_html=True)

# ---------------- Session State ----------------
# ไม่จำเป็นต้องใช้ st.session_state.redirected แล้ว
# if 'redirected' not in st.session_state:
#     st.session_state.redirected = False

# ---------------- Main Content ----------------
st.markdown(f"""
<div class="image-container">
    <img src="data:image/png;base64,{img_base64}">
</div><br>
""", unsafe_allow_html=True)

# ---------------- Button Under Image ----------------
col1, col2, col3 = st.columns([1,2,1])
with col2:
    if st.button("เข้าสู่ระบบ / เข้าโปรแกรม", use_container_width=True):
        # ✅ แก้ไข: ใช้ st.switch_page() เพื่อเปลี่ยนหน้าทันที
        st.switch_page("pages/home_index.py")

# ---------------- Countdown + Auto Redirect ----------------
# ตรวจสอบว่ายังไม่มีการกดปุ่ม (ซึ่งจะทำให้โค้ดด้านบนทำงานไปแล้ว)
# แต่เพื่อให้การนับถอยหลังทำงาน เราไม่ต้องเช็ค session state อีกแล้ว เพราะ st.switch_page จะออกจากการทำงานทันที
countdown_sec = 5
placeholder = st.empty()

# เริ่มนับถอยหลัง
for i in range(countdown_sec, 0, -1):
    placeholder.markdown(
        f"<div style='text-align:center; color:white; font-size:20px; margin-top:10px;'>⚠️ จะเปลี่ยนหน้าโดยอัตโนมัติใน {i} วินาที...</div>",
        unsafe_allow_html=True
    )
    time.sleep(1)

placeholder.empty() # ล้างข้อความนับถอยหลัง

# ✅ แก้ไข: ใช้ st.switch_page() สำหรับการเปลี่ยนหน้าอัตโนมัติ
st.switch_page("pages/home_index.py")

# ---------------- Redirect using HTML + JS Fade ----------------
# ❌ ลบส่วนนี้ออกไปทั้งหมด เพราะไม่จำเป็นและเป็นสาเหตุของปัญหา
# if st.session_state.redirected:
#     ... components.html(...)