import os
import streamlit as st
import google.generativeai as genai

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    system_instruction="""
Eres un experto en biosensores electroquímicos,
impedancia EIS y detección de troponina.
"""
)

st.set_page_config(page_title="Gemini App", page_icon="🤖")
st.title("🤖 Gemini + Streamlit")

if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat(history=[])

prompt = st.chat_input("Escribe tu pregunta...")

if prompt:
    st.chat_message("user").write(prompt)
    response = st.session_state.chat.send_message(prompt)
    st.chat_message("assistant").write(response.text)

