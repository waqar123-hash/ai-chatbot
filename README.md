# My AI Chatbot 🤖

A simple chatbot built with **Streamlit** and the **Hugging Face Inference API**.
It remembers conversation history and handles API errors gracefully.

---

## 1. What you need before starting
- Python installed on your computer ([download here](https://www.python.org/downloads/))
- A free Hugging Face account: https://huggingface.co/join
- A Hugging Face **Access Token**:
  1. Log in to huggingface.co
  2. Click your profile picture → **Settings** → **Access Tokens**
  3. Click **New Token**, choose type "Read", click **Generate**
  4. Copy the token (keep it secret!)

---

## 2. Setup instructions (run on your computer)

### Step 1: Download/unzip this project
Put the folder anywhere on your computer, e.g. `Desktop/chatbot-project`

### Step 2: Open terminal/command prompt in this folder
```bash
cd chatbot-project
```

### Step 3: Install the required packages
```bash
pip install -r requirements.txt
```

### Step 4: Add your API token
Create a folder called `.streamlit` inside the project, and inside it a file called `secrets.toml` with this content:
```toml
HF_TOKEN = "your_token_here"
```
(Replace `your_token_here` with the token you copied earlier)

### Step 5: Run the app
```bash
streamlit run app.py
```
Your browser will open automatically at `http://localhost:8501` 🎉

---

## 3. Deploying online (to get a shareable live link)

1. Push this project to a **GitHub repository** (public or private)
2. Go to https://streamlit.io/cloud and sign in with GitHub
3. Click **New app**, select your repository and `app.py` as the main file
4. Under **Advanced settings**, add your `HF_TOKEN` as a secret (same format as `secrets.toml` above)
5. Click **Deploy** — you'll get a live public link to share ✅

---

## 4. How the chatbot works (short explanation)
- User types a message → it's added to `st.session_state.messages`
- The whole conversation history is sent to the Hugging Face model each time (this gives it "memory")
- The model's reply is shown and also saved to history
- If the API fails (rate limit, network issue, etc.), a friendly error message is shown instead of crashing

---

## 5. Ideas to improve it further
- Try a different model by changing `MODEL_NAME` in `app.py`
- Add a system prompt to give the bot a personality
- Add a "download conversation" button
