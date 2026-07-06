"""
Simple AI Chatbot using Streamlit + Hugging Face Inference API
Beginner-friendly, fully commented.
"""

import streamlit as st
from huggingface_hub import InferenceClient

# ---------- PAGE SETUP ----------
st.set_page_config(page_title="My AI Chatbot", page_icon="🤖")
st.title("🤖 My AI Chatbot")
st.caption("Built with Streamlit + Hugging Face API")

# ---------- API KEY ----------
# We read the key from Streamlit "secrets" so it's never visible in the code.
# (See README.md for how to set this up)
try:
    HF_TOKEN = st.secrets["HF_TOKEN"]
except Exception:
    HF_TOKEN = st.text_input("Enter your Hugging Face API Token:", type="password")

if not HF_TOKEN:
    st.warning("Please add your Hugging Face token to continue.")
    st.stop()

# ---------- MODEL SETUP ----------
# You can swap this for any other chat model available on Hugging Face
# (browse models + providers at https://huggingface.co/models?inference_provider=all)
MODEL_NAME = "openai/gpt-oss-120b:cerebras"

client = InferenceClient(token=HF_TOKEN)

# ---------- CONVERSATION HISTORY ----------
# st.session_state keeps data alive between messages (like a memory for the app)
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are a helpful, friendly assistant."}
    ]

# Show previous messages on screen
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

# ---------- USER INPUT ----------
user_input = st.chat_input("Type your message here...")

if user_input:
    # 1. Show user's message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    # 2. Get AI response (with error handling)
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=st.session_state.messages,
                    max_tokens=300,
                )
                ai_reply = response.choices[0].message.content

            except Exception as e:
                # Handle API errors / rate limits gracefully
                ai_reply = (
                    "⚠️ Sorry, something went wrong talking to the AI. "
                    f"(Error: {str(e)[:150]})"
                )

        st.write(ai_reply)

    # 3. Save AI reply to history
    st.session_state.messages.append({"role": "assistant", "content": ai_reply})

# ---------- SIDEBAR: Clear chat button ----------
with st.sidebar:
    st.header("Options")
    if st.button("🗑️ Clear Conversation"):
        st.session_state.messages = [
            {"role": "system", "content": "You are a helpful, friendly assistant."}
        ]
        st.rerun()
