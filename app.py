import os
import time
import google.generativeai as genai
from openai import OpenAI
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

# Page title
st.set_page_config(page_title="Multi-AI Chatbot", page_icon="🤖")


# API
st.session_state["gemini_api_key"] = os.getenv("GEMINI_API_KEY")
st.session_state["openai_api_key"] = os.getenv("OPENAI_API_KEY")

if not st.session_state["gemini_api_key"]:
    st.error("Error: GEMINI_API_KEY not found in environment.")
    st.stop()
if not st.session_state["openai_api_key"]:
    st.error("Error: OPENAI_API_KEY not found in environment.")
    st.stop()

# Configure AI models
genai.configure(api_key=st.session_state["gemini_api_key"])
openai_client = OpenAI(api_key=st.session_state["openai_api_key"])

# Sidebar
with st.sidebar:
    st.header("Settings")

    model_choice = st.selectbox("Choose a model:", ("Gemini", "OpenAI", "Image Generation (DALL-E)"))

    if st.button("Clear chat", use_container_width=True, type="primary"):
        st.session_state["gemini_history"] = []
        st.session_state["openai_history"] = []
        if "image_history" in st.session_state:
            st.session_state["image_history"] = []
        st.rerun()


if "gemini_history" not in st.session_state:
    st.session_state["gemini_history"] = []
if "openai_history" not in st.session_state:
    st.session_state["openai_history"] = []
if "image_history" not in st.session_state:
    st.session_state["image_history"] = []

# Dynamic Titles
if model_choice == "Gemini":
    st.title("Gemini Chatbot")
    st.caption("Chat with Google's Gemini AI model.")
    active_history = st.session_state["gemini_history"]
elif model_choice == "OpenAI":
    st.title("OpenAI Chatbot")
    st.caption("Chat with OpenAI's GPT models.")
    active_history = st.session_state["openai_history"]
elif model_choice == "Image Generation (DALL-E)":
    st.title("Image Generation (DALL-E)")
    st.caption("Generate images using OpenAI's DALL-E model.")
    active_history = [] 



# Render History
if model_choice != "Image Generation (DALL-E)":
    for message in active_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
else: 
    for item in st.session_state["image_history"]:
        with st.chat_message("user"):
            st.markdown(f"**Prompt:** {item['prompt']}")
        with st.chat_message("assistant"):
            st.image(item['url'], caption=item['prompt'], use_column_width=True)
            st.markdown(f"Image URL: {item['url']}")
        st.markdown("---") 



if prompt := st.chat_input("Type your message..."):
    # User message
    with st.chat_message("user"):
        st.markdown(prompt)

    # Gemini Response
    if model_choice == "Gemini":
        # AAppend user meesage to history
        active_history.append({"role": "user", "content": prompt})

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

                # Append assistant response
                active_history.append({"role": "assistant", "content": full_response})

            except genai.types.generation_types.BlockedPromptException as e:
                st.exception(e)
            except Exception as e:
                st.exception(e)

    # OpenAI response
    elif model_choice == "OpenAI":
        # AAppend user meesage to history
        active_history.append({"role": "user", "content": prompt})

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown("Thinking...")

            try:
                stream = openai_client.chat.completions.create(
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

                # Append assistant response
                active_history.append({"role": "assistant", "content": full_response})

            except Exception as e:
                st.exception(e)

    # Image Generation DALLE
    elif model_choice == "Image Generation (DALL-E)":
        with st.chat_message("assistant"):
            st.write("Generating image...")
            try:
                response = openai_client.images.generate(
                    model="dall-e-3",
                    prompt=prompt,
                    size="1024x1024", 
                    quality="standard", 
                    n=1, 
                )

                image_url = response.data[0].url
                
                st.image(image_url, caption=prompt, use_column_width=True)

                # Append to image history
                st.session_state["image_history"].append({"prompt": prompt, "url": image_url})

            except Exception as e:
                st.error(f"Error generating image: {e}")