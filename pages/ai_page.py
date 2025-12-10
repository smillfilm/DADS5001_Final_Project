import streamlit as st
from google import genai
from google.genai import types 


st.set_page_config(page_title="🤖 My Gemini Chatbot", layout="wide")
st.title("🤖 My Gemini Chatbot")

@st.cache_resource
def get_gemini_client():
    """สร้างและคืนค่า client ของ Gemini API"""
    try:
        return genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
    except KeyError:
        st.error("ไม่พบ **GEMINI_API_KEY** ใน `st.secrets` กรุณาตรวจสอบการตั้งค่า")
        st.stop()

client = get_gemini_client()

if "messages" not in st.session_state:
    system_instruction = "คุณคือ AI Chatbot ที่เป็นมิตร ให้ข้อมูลที่เป็นประโยชน์และตอบคำถามอย่างกระชับและสุภาพ"
    st.session_state["messages"] = [
        {"role": "system", "content": system_instruction}
    ]

def prepare_gemini_messages(messages):
    gemini_messages = []
    
    for msg in messages:
        if msg["role"] == "system":
            continue
            
        role = 'model' if msg["role"] == 'assistant' else msg["role"]
        gemini_messages.append(
            types.Content(
                role=role, 
                parts=[types.Part.from_text(text=msg["content"])] 
            )
        )
    return gemini_messages

for msg in st.session_state["messages"][1:]:
    st.chat_message(msg["role"]).write(msg["content"])


user_input = st.chat_input("พิมพ์ข้อความที่นี่...")

if user_input:
    st.session_state["messages"].append({"role": "user", "content": user_input})
    st.chat_message("user").write(user_input)

    system_instruction = st.session_state["messages"][0]["content"]
    gemini_messages = prepare_gemini_messages(st.session_state["messages"])
    
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        try:
            response_stream = client.models.generate_content_stream(
                model="gemini-2.5-flash",
                contents=gemini_messages,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction
                )
            )
            
            for chunk in response_stream:
                if chunk.text:
                    full_response += chunk.text
                    message_placeholder.markdown(full_response + "▌") 
            
            message_placeholder.markdown(full_response)
            ai_reply = full_response
            
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาดในการเรียกใช้ Gemini API: {e}")
            ai_reply = f"Error: {e}"

    st.session_state["messages"].append({"role": "assistant", "content": ai_reply})