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

# ---------- ZERO-SHOT / ONE-SHOT / FEW-SHOT EXAMPLE BANK ----------
# These are sample Q&A pairs that show the AI the exact STYLE of answer we want:
# short, simple, respectful, and always ending with a gentle "verify" reminder.
# They are NOT saved into the visible chat history — they're only added
# behind the scenes when we call the API, based on the selected mode.
EXAMPLE_PAIRS = [
    (
        "What are the 5 pillars of Islam?",
        "The 5 pillars are: 1) Shahada (declaration of faith), 2) Salah (5 daily "
        "prayers), 3) Zakat (charity), 4) Sawm (fasting in Ramadan), and 5) Hajj "
        "(pilgrimage to Makkah, if able). (General info — please verify details "
        "with a trusted scholar or source.)"
    ),
    (
        "Who was Prophet Yusuf (AS)?",
        "Prophet Yusuf (AS) was the son of Prophet Ya'qub (AS). His story, told in "
        "Surah Yusuf, covers being betrayed by his brothers, rising to a position "
        "of trust in Egypt, and eventually being reunited with his family. "
        "(General summary — please verify exact details with a trusted source.)"
    ),
    (
        "What breaks the fast in Ramadan?",
        "Generally, eating, drinking, and intimate relations during fasting hours "
        "break the fast. Some rulings vary by situation (illness, travel, etc.). "
        "(General info only — for specific situations, please consult a scholar.)"
    ),
]

# ---------- SIDEBAR: Who is asking? (Role + Level) ----------
with st.sidebar:
    st.header("🙋 Who's Asking?")
    user_role = st.selectbox(
        "I am a...",
        ["Student", "Teacher"],
        help="Student: simple, easy-to-understand answers.\nTeacher: answers include structure/teaching tips.",
    )
    user_level = st.selectbox(
        "Knowledge Level",
        ["Beginner", "Intermediate", "Advanced"],
        help="Beginner: very simple, basic explanation.\nIntermediate: some detail, assumes basic knowledge.\nAdvanced: in-depth, assumes strong prior knowledge.",
    )
    st.caption(f"Answering as: **{user_role} ({user_level})**")
    st.divider()

    st.header("🧪 Prompting Mode")
    prompting_mode = st.radio(
        "Choose how many examples to show the AI before your question:",
        ["Zero-shot", "One-shot", "Few-shot"],
        index=0,
        help=(
            "Zero-shot: no examples given.\n"
            "One-shot: 1 example given.\n"
            "Few-shot: multiple examples given.\n"
            "Examples teach the AI the exact style/format to follow."
        ),
    )
    st.caption(f"Currently using: **{prompting_mode}**")
    st.divider()

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
                # ---- Build the messages we actually SEND to the API ----
                # This is where zero/one/few-shot examples get injected.
                # (They are NOT added to current_chat["messages"], so they
                # never show up in the visible chat UI.)
                system_msg = current_chat["messages"][0]
                real_conversation = current_chat["messages"][1:]  # everything after system msg

                # ---- Adjust behavior based on selected Role + Level ----
                role_instructions = {
                    "Student": "The user is a STUDENT. Keep the tone friendly and easy to follow, like explaining to someone learning.",
                    "Teacher": "The user is a TEACHER. Structure the answer clearly (e.g. short points) and, where useful, add a brief note on how to explain this to others.",
                }
                level_instructions = {
                    "Beginner": "Use very simple words, short sentences, and avoid assuming any prior knowledge.",
                    "Intermediate": "You may assume basic familiarity with the topic; give a moderate level of detail.",
                    "Advanced": "You may go into more depth and detail, assuming strong prior knowledge of the topic.",
                }
                personalization_msg = {
                    "role": "system",
                    "content": role_instructions[user_role] + " " + level_instructions[user_level],
                }

                if prompting_mode == "Zero-shot":
                    example_msgs = []  # no examples at all
                elif prompting_mode == "One-shot":
                    q, a = EXAMPLE_PAIRS[0]
                    example_msgs = [
                        {"role": "user", "content": q},
                        {"role": "assistant", "content": a},
                    ]
                else:  # Few-shot
                    example_msgs = []
                    for q, a in EXAMPLE_PAIRS:
                        example_msgs.append({"role": "user", "content": q})
                        example_msgs.append({"role": "assistant", "content": a})

                messages_to_send = [system_msg, personalization_msg] + example_msgs + real_conversation

                response = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=messages_to_send,
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
