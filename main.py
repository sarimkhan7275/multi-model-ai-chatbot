import os
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from the .env file.
load_dotenv()
api_key = os.getenv("API_KEY")

# Check if the API key was successfully loaded.
if not api_key:
    st.error("Error: API_KEY not found.")
    st.stop()

# Configure the Gemini API with your API key.
genai.configure(api_key=api_key)

# Set up the Streamlit page title and a welcome message.
st.title("Gemini Chatbot")
st.markdown("Feel free to ask me anything!")

# Initialize the generative model.
# Using a single model instance for the entire app run.
if "model" not in st.session_state:
    st.session_state.model = genai.GenerativeModel('gemini-2.5-flash')

# Initialize chat history in Streamlit's session state.
# This ensures history persists across reruns.
if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialize chat session in Streamlit's session state.
if "chat" not in st.session_state:
    st.session_state.chat = st.session_state.model.start_chat(history=[])

# Display previous chat messages from history.
# This loop re-renders the entire conversation every time the app reruns.
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle new user input.
# The `st.chat_input` widget displays a text input box at the bottom.
if prompt := st.chat_input("What is up?"):
    # Add user message to chat history.
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display the user message.
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        # Get the Gemini model's response based on the conversation history.
        with st.chat_message("assistant"):
            # The `send_message` method takes care of appending new turns to the history
            # object, so we pass the new user prompt as a single item here.
            response = st.session_state.chat.send_message(prompt)
            st.markdown(response.text)

            # Add assistant response to chat history.
            st.session_state.messages.append({"role": "assistant", "content": response.text})

    except Exception as e:
        st.error(f"An error occurred: {e}")

