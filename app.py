"""
Simple AI Chatbot using Streamlit + Hugging Face Inference API
Beginner-friendly, fully commented.
"""

import streamlit as st
from huggingface_hub import InferenceClient

# ---------- PAGE SETUP ----------
st.set_page_config(page_title="Islamic Q&A Bot", page_icon="🕌")
st.title("🕌 Islamic Q&A Assistant")
st.caption("Basic info on Quran, Hadith, and general Islamic knowledge")
st.info(
    "⚠️ This bot gives general, basic information only. It is **not** a substitute "
    "for a qualified scholar (Alim/Mufti). For fatwas, rulings, or detailed fiqh "
    "questions, please consult a trusted scholar.",
    icon="ℹ️",
)

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

# ---------- MULTIPLE CHATS SETUP ----------
# Instead of one conversation, we now store MANY conversations in a dictionary.
# Each chat has a unique ID, a title, and its own list of messages.
import uuid

DEFAULT_SYSTEM_MSG = {
    "role": "system",
    "content": (
        "You are an Islamic Q&A assistant that ONLY answers questions about "
        "basic Islamic knowledge: the 5 pillars of Islam, general beliefs (Aqeedah), "
        "well-known stories of the Prophets, basic guidance on Salah/Fasting/Zakat/Hajj, "
        "and widely-agreed-upon general Islamic etiquette (Akhlaq).\n\n"
        "STRICT RULES:\n"
        "1. If asked about something outside Islamic topics (e.g. coding, sports, "
        "general trivia), politely say: 'I can only help with basic Islamic Q&A. "
        "Please ask me something related to that.'\n"
        "2. NEVER issue a fatwa or personal religious ruling on disputed/complex fiqh "
        "matters (e.g. inheritance division, divorce specifics, sectarian differences). "
        "Instead say this needs a qualified scholar (Alim/Mufti) and general guidance only.\n"
        "3. When citing a Hadith or Quran verse, be cautious: mention the general "
        "reference (e.g. 'Surah Al-Baqarah' or 'reported in Sahih Bukhari') only if "
        "reasonably confident, and always remind the user to verify exact wording "
        "and authenticity from a trusted source or scholar.\n"
        "4. Avoid taking sides on sectarian (Sunni/Shia) or scholarly disputes — "
        "present that scholars may differ, without declaring one view correct.\n"
        "5. Keep answers simple, respectful, and factual — never argumentative."
    ),
}

if "all_chats" not in st.session_state:
    first_chat_id = str(uuid.uuid4())
    st.session_state.all_chats = {
        first_chat_id: {"title": "New Chat", "messages": [DEFAULT_SYSTEM_MSG]}
    }
    st.session_state.current_chat_id = first_chat_id

# ---------- SIDEBAR: Chat history list ----------
with st.sidebar:
    st.header("💬 Chats")

    if st.button("➕ New Chat", use_container_width=True):
        new_id = str(uuid.uuid4())
        st.session_state.all_chats[new_id] = {
            "title": "New Chat", "messages": [DEFAULT_SYSTEM_MSG]
        }
        st.session_state.current_chat_id = new_id
        st.rerun()

    st.divider()

    # List every saved chat as a clickable button
    for chat_id, chat_data in st.session_state.all_chats.items():
        is_active = chat_id == st.session_state.current_chat_id
        label = ("🟢 " if is_active else "") + chat_data["title"]
        if st.button(label, key=chat_id, use_container_width=True):
            st.session_state.current_chat_id = chat_id
            st.rerun()

    st.divider()
    if st.button("🗑️ Delete Current Chat", use_container_width=True):
        del st.session_state.all_chats[st.session_state.current_chat_id]
        if not st.session_state.all_chats:
            new_id = str(uuid.uuid4())
            st.session_state.all_chats[new_id] = {
                "title": "New Chat", "messages": [DEFAULT_SYSTEM_MSG]
            }
            st.session_state.current_chat_id = new_id
        else:
            st.session_state.current_chat_id = list(st.session_state.all_chats.keys())[0]
        st.rerun()

# Shortcut: point "messages" at the currently active chat's message list
current_chat = st.session_state.all_chats[st.session_state.current_chat_id]

# Show previous messages on screen
for msg in current_chat["messages"]:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

# ---------- USER INPUT ----------
user_input = st.chat_input("Type your message here...")

if user_input:
    # If this is the first message in the chat, use it as the chat's title
    if current_chat["title"] == "New Chat":
        current_chat["title"] = user_input[:30]

    # 1. Show user's message
    current_chat["messages"].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    # 2. Get AI response (with error handling)
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=current_chat["messages"],
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
    current_chat["messages"].append({"role": "assistant", "content": ai_reply})
    st.rerun()
