import streamlit as st
import time

st.title("🔑 เข้าสู่ระบบ")

# --- 1. เชื่อม Snowflake ผ่าน Streamlit Connection ---
conn = st.connection("snowflake", type="snowflake")

# --- 2. ถ้าล็อกอินแล้ว ---
if st.session_state.get('logged_in'):
    st.success(f"คุณล็อกอินอยู่แล้ว: {st.session_state['user_name']}")
else:
    with st.form("login_form"):
        username = st.text_input("ชื่อผู้ใช้")
        password = st.text_input("รหัสผ่าน", type="password")
        submit = st.form_submit_button("เข้าสู่ระบบ")

        if submit:
            username_safe = username.replace("'", "''")
            query = f"""
                SELECT username, password, subscribe_flag
                FROM users
                WHERE username = '{username_safe}'
                LIMIT 1
            """
            df = conn.query(query)

            if df.empty:
                st.error("ไม่พบผู้ใช้งานนี้")
            else:
                # หา column subscribe_flag แบบ case-insensitive
                col_subscribe = [c for c in df.columns if c.lower() == "subscribe_flag"][0]
                subscribe_flag = int(df.iloc[0][col_subscribe])

                db_user = df.iloc[0]["USERNAME"]
                db_pass = df.iloc[0]["PASSWORD"]

                if password == db_pass:
                    st.session_state['logged_in'] = True
                    st.session_state['user_name'] = db_user
                    st.session_state['subscribe_flag'] = subscribe_flag  # โหลดจาก DB

                    st.success("เข้าสู่ระบบสำเร็จ!")
                    time.sleep(0.3)
                    st.rerun()
                else:
                    st.error("รหัสผ่านไม่ถูกต้อง")
