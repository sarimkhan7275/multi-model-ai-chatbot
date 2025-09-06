import os
import time
import random
import google.generativeai as genai
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

st.set_page_config(page_title="Gemini AI Chatbot", page_icon="🤖")
st.title("Gemini AI Chatbot")
st.caption("A chatbot powered by Gemini AI")

# --- API key ---
st.session_state["gemini_api_key"] = os.getenv("GEMINI_API_KEY")

if not st.session_state["gemini_api_key"]:
    st.error("Error: GEMINI_API_KEY not found in environment.")
    st.stop()

genai.configure(api_key=st.session_state["gemini_api_key"])

# --- History ---
if "history" not in st.session_state:
    st.session_state["history"] = []

model = genai.GenerativeModel("gemini-2.5-flash")
chat = model.start_chat(history=st.session_state["history"])

# --- Sidebar ---
with st.sidebar:
    if st.button("Clear chat", use_container_width=True, type="primary"):
        st.session_state["history"] = []
        st.rerun()

# --- Render existing history ---
for message in chat.history:
    role = "assistant" if message.role == "model" else message.role
    with st.chat_message(role):
        # message.parts can be multiple parts; show first text part if present
        text = message.parts[0].text if message.parts and hasattr(message.parts[0], "text") else ""
        st.markdown(text)

# --- Input & streaming reply ---
if prompt := st.chat_input("Type your message..."):
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("Thinking...")

    try:
        full_response = ""
        for chunk in chat.send_message(prompt, stream=True):
            # chunk.text is the new text delta; append and refresh the placeholder
            if hasattr(chunk, "text") and chunk.text:
                full_response += chunk.text
                message_placeholder.markdown(full_response)
                # (optional) tiny jitter to feel "streamy"
                time.sleep(random.uniform(0.01, 0.03))

        # persist updated history
        st.session_state["history"] = chat.history

    except genai.types.generation_types.BlockedPromptException as e:
        st.exception(e)
    except Exception as e:
        st.exception(e)
