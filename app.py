import os
import time
import google.generativeai as genai
from openai import OpenAI
from dotenv import load_dotenv
import streamlit as st

load_dotenv()



# --- Page configuration ---
st.set_page_config(page_title="Multi-AI Chatbot", page_icon="🤖")
st.title("Multi-AI Chatbot")
st.caption("A multi-model ai chatbot")

# --- API Keys ---
# st.session_state["gemini_api_key"] = st.secrets["GEMINI_API_KEY"]
# st.session_state["openai_api_key"] = st.secrets["OPENAI_API_KEY"]

st.session_state["gemini_api_key"] = os.getenv("GEMINI_API_KEY")
st.session_state["openai_api_key"] = os.getenv("OPENAI_API_KEY")

if not st.session_state["gemini_api_key"]:
    st.error("Error: GEMINI_API_KEY not found in environment.")
    st.stop()
if not st.session_state["openai_api_key"]:
    st.error("Error: OPENAI_API_KEY not found in environment.")
    st.stop()

# Configure APIs
genai.configure(api_key=st.session_state["gemini_api_key"])
client = OpenAI(api_key=st.session_state["openai_api_key"])

# --- Sidebar ---
with st.sidebar:
    st.header("Settings")

    model_choice = st.selectbox("Choose a model:", ("Gemini", "OpenAI"))

    if st.button("Clear chat", use_container_width=True, type="primary"):
        st.session_state["gemini_history"] = []
        st.session_state["openai_history"] = []
        st.rerun()

# --- Initialize histories ---
if "gemini_history" not in st.session_state:
    st.session_state["gemini_history"] = []
if "openai_history" not in st.session_state:
    st.session_state["openai_history"] = []

# Pick the active history
active_history = (
    st.session_state["gemini_history"]
    if model_choice == "Gemini"
    else st.session_state["openai_history"]
)

# --- Render existing history ---
for message in active_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Input & streaming reply ---
if prompt := st.chat_input("Type your message..."):
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # Add user message to active history
    active_history.append({"role": "user", "content": prompt})

    # --- Gemini response ---
    if model_choice == "Gemini":
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown("Thinking...")

            try:
                model = genai.GenerativeModel("gemini-1.5-flash")
                chat = model.start_chat(
                    history=[{"role": m["role"], "parts": [m["content"]]} for m in active_history]
                )

                full_response = ""
                for chunk in chat.send_message(prompt, stream=True):
                    if chunk.text:
                        full_response += chunk.text
                        message_placeholder.markdown(full_response)

                # Save assistant response
                active_history.append({"role": "assistant", "content": full_response})

            except genai.types.generation_types.BlockedPromptException as e:
                st.exception(e)
            except Exception as e:
                st.exception(e)

    # --- OpenAI response ---
    elif model_choice == "OpenAI":
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown("Thinking...")

            try:
                stream = client.chat.completions.create(
                    model="gpt-5-nano",
                    messages=active_history,
                    stream=True,
                )

                full_response = ""
                for chunk in stream:
                    content = chunk.choices[0].delta.content or ""
                    if content:
                        full_response += content
                        message_placeholder.markdown(full_response)

                # Save assistant response
                active_history.append({"role": "assistant", "content": full_response})

            except Exception as e:
                st.exception(e)
