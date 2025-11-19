import streamlit as st
import requests
import json
from datetime import datetime
import time

st.set_page_config(page_title="Lambda Chatbot", page_icon="🤖", layout="wide")
st.title("🤖 Lambda Knowledge Base Chatbot")

# --- Initialize session state ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "show_system_prompt" not in st.session_state:
    st.session_state.show_system_prompt = False

# Lambda API URL & API Key
LAMBDA_URL = "https://ur66rgdmrb.execute-api.us-east-1.amazonaws.com/prod"
API_KEY = "BkNcTMFzCAaw6YY21OoaO9qD0QjbDwwv57hyZzgl"

# --- Sidebar controls ---
if st.sidebar.button("🗑 Clear Chat"):
    st.session_state.chat_history = []

st.sidebar.checkbox("แสดง System Prompt", key="show_system_prompt")

# --- Form สำหรับ input & submit ---
with st.form(key="chat_form"):
    prompt = st.text_input("พิมพ์ข้อความของคุณ:", key="input_text")
    send_button = st.form_submit_button("ส่งข้อความ")

def send_to_lambda_stream(user_prompt):
    """ส่งข้อความไป Lambda และ return answer, sources, system_prompt"""
    payload = {"prompt": user_prompt}
    response = requests.post(
        LAMBDA_URL,
        headers={"x-api-key": API_KEY, "Content-Type": "application/json"},
        json=payload
    )
    if response.status_code == 200:
        res_json = response.json()
        body = json.loads(res_json.get("body", "{}"))
        answer_text = body.get("answer", "")
        sources = body.get("sources", [])
        system_prompt = body.get("system_prompt", "")
        return answer_text, sources, system_prompt
    else:
        return f"เกิดข้อผิดพลาด: {response.status_code}", [], ""

# --- ส่งข้อความ ---
if send_button and prompt.strip() != "":
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # เก็บ user message
    st.session_state.chat_history.append({
        "role": "user",
        "message": prompt,
        "timestamp": timestamp
    })

    # placeholder แสดงสถานะกำลังประมวลผล
    processing_placeholder = st.empty()
    processing_placeholder.info("⏳ กำลังประมวลผลข้อมูล...")

    # placeholder สำหรับ AI streaming
    ai_placeholder = st.empty()
    ai_message = ""

    # ส่งข้อความไป Lambda
    answer_text, sources, system_prompt = send_to_lambda_stream(prompt)

    # ลบข้อความ processing ก่อนเริ่ม streaming
    processing_placeholder.empty()

    # streaming ทีละตัวอักษร
    for char in answer_text:
        ai_message += char
        ai_placeholder.markdown(
            f"<div style='text-align: left; background-color:#F1F0F0; padding:8px; margin:4px; border-radius:8px'><b>AI:</b> {ai_message}</div>",
            unsafe_allow_html=True
        )
        time.sleep(0.01)

    # บันทึก AI message หลัง streaming
    st.session_state.chat_history.append({
        "role": "lambda",
        "message": answer_text,
        "timestamp": timestamp,
        "sources": sources,
        "system_prompt": system_prompt
    })

st.markdown("---")
# --- แสดง chat history ล่าสุดบนสุด ---
st.subheader("💬 ประวัติการสนทนา")
for chat in reversed(st.session_state.chat_history):  # reverse list
    role = chat["role"]
    timestamp = chat.get("timestamp", "")
    message = chat["message"]

    if role == "user":
        st.markdown(
            f"<div style='text-align: right; background-color:#DCF8C6; padding:8px; margin:4px; border-radius:8px'><b>คุณ:</b> {message}<br><small>{timestamp}</small></div>",
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"<div style='text-align: left; background-color:#F1F0F0; padding:8px; margin:4px; border-radius:8px'><b>AI:</b> {message}<br><small>{timestamp}</small></div>",
            unsafe_allow_html=True
        )
        # sources
        if chat.get("sources"):
            st.markdown(f"<div style='margin-left:16px; font-size:90%'>🔗 Sources: {chat['sources']}</div>", unsafe_allow_html=True)
        # system_prompt
        if st.session_state.show_system_prompt and chat.get("system_prompt"):
            st.markdown(f"<div style='margin-left:16px; font-size:90%; color:gray'>⚙️ System Prompt: {chat['system_prompt']}</div>", unsafe_allow_html=True)
# --- Auto-scroll to bottom ---
st.markdown("<script>window.scrollTo(0, document.body.scrollHeight);</script>", unsafe_allow_html=True)
