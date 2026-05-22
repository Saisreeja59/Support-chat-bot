# import os
# import requests
# import streamlit as st
# from langdetect import detect
# from dotenv import load_dotenv

# load_dotenv()
# BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8075")

# st.set_page_config(page_title="AutoRouteAI Swarm Chat", layout="centered")
# st.title("Civil Engineering Assistant – Swarm AI")

# # Initialize session state
# if "history" not in st.session_state:
#     st.session_state.history = []

# if "last_input" not in st.session_state:
#     st.session_state.last_input = ""

# # Chat input
# user_input = st.chat_input("Ask me anything (any language)...")

# def call_backend(msg: str, lang: str) -> str:
#     try:
#         response = requests.post(
#             f"{BACKEND_URL}/chat",
#             json={"query": msg, "lang": lang},
#             timeout=60,
#             verify=True
#         )
#         result = response.json()
#         return result.get("response", result.get("error", "Unknown error"))
#     except Exception as exc:
#         return f"Backend unreachable: {exc}"

# # Process input only if new
# if user_input and user_input != st.session_state.last_input:
#     st.session_state.last_input = user_input

#     # Detect language
#     try:
#         user_lang = detect(user_input)
#     except:
#         user_lang = "en"

#     # Append user message
#     st.session_state.history.append(("user", user_input))

#     # Get assistant reply
#     reply = call_backend(user_input, user_lang)
#     st.session_state.history.append(("assistant", reply))

# # Display chat history
# for role, msg in st.session_state.history:
#     st.chat_message(role).write(msg)













import os
import json
import requests
import streamlit as st
from langdetect import detect
from dotenv import load_dotenv
import re

load_dotenv()
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8075")
CACHE_FILE  = "cache.json"

# ── Page config ─────────────────────────────────────────────────────
st.set_page_config(page_title="AI Support Assistant", layout="centered")

# ══════════════════════════════════════════════════════════════════════
# CACHE HELPERS
# ══════════════════════════════════════════════════════════════════════
def load_disk_cache() -> dict:
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_disk_cache(cache: dict) -> None:
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def normalize_question(text: str) -> str:
    text = text.lower().strip()

    text = re.sub(
        r"[^\w\s]",
        "",
        text
    )

    return text

# ── Predefined FAQ answers (English — translated on-the-fly if needed)
FAQ_CACHE: dict[str, str] = {
    "i forgot my password": (
        "🔑 **Password Reset**\n\n"
        "1. Go to the login page and click **'Forgot Password'**.\n"
        "2. Enter your registered email address.\n"
        "3. Check your inbox for a reset link (also check spam).\n"
        "4. Click the link and set a new password.\n\n"
        "If you don't receive the email within 5 minutes, contact support."
    ),
    "how do i get a refund?": (
        "💳 **Refund Process**\n\n"
        "1. Log in to your account and go to **Billing → Order History**.\n"
        "2. Select the charge you want refunded and click **'Request Refund'**.\n"
        "3. Refunds are processed within **5–7 business days**.\n\n"
        "For charges older than 30 days, please contact our billing team directly."
    ),
    "my internet connection is not working": (
        "🔧 **Internet Troubleshooting**\n\n"
        "1. Restart your router — unplug it for 30 seconds, then plug back in.\n"
        "2. Check if other devices on the same network are affected.\n"
        "3. Run a speed test at **fast.com**.\n"
        "4. If the issue persists, check our status page for outages.\n\n"
        "Still down? Chat with technical support and have your account number ready."
    ),
    "how can i update my email?": (
        "👤 **Update Email Address**\n\n"
        "1. Log in and go to **Account Settings → Profile**.\n"
        "2. Click **'Edit'** next to your current email.\n"
        "3. Enter your new email and click **'Save'**.\n"
        "4. A verification link will be sent to the new address — click it to confirm.\n\n"
        "Your old email remains active until verification is complete."
    ),
    "i was charged twice for my subscription": (
        "💳 **Duplicate Charge**\n\n"
        "We're sorry about that! Here's what to do:\n\n"
        "1. Go to **Billing → Transaction History** and screenshot both charges.\n"
        "2. Click **'Dispute Charge'** on the duplicate entry.\n"
        "3. Our billing team will review and refund the duplicate within **3 business days**.\n\n"
        "You can also email billing@support.com with your transaction IDs."
    ),
}

# _FAQ_KEYS = {k.lower().strip(): v for k, v in FAQ_CACHE.items()}
_FAQ_KEYS = {
    normalize_question(k): v
    for k, v in FAQ_CACHE.items()
}

# ── Session-state initialisation ────────────────────────────────────
if "history"          not in st.session_state:
    st.session_state.history = []
if "last_input"       not in st.session_state:
    st.session_state.last_input = ""
if "answer_cache"     not in st.session_state:
    st.session_state.answer_cache = load_disk_cache()
if "recent_questions" not in st.session_state:
    st.session_state.recent_questions = []
if "injected_input"   not in st.session_state:
    st.session_state.injected_input = None


# ══════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## ⚙️ Options")
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.history          = []
        st.session_state.last_input       = ""
        st.session_state.recent_questions = []
        st.session_state.injected_input   = None
        st.rerun()

    st.divider()

    st.markdown("### 📌 Frequently Asked Questions")
    for label in FAQ_CACHE:
        if st.button(label, key=f"faq_{label}", use_container_width=True):
            st.session_state.injected_input = label
            st.rerun()

    st.divider()

    st.markdown("### 🕒 Recent Questions")
    if st.session_state.recent_questions:
        for q, _ in st.session_state.recent_questions:
            short_label = q if len(q) <= 40 else q[:37] + "…"
            if st.button(short_label, key=f"recent_{q}", use_container_width=True):
                st.session_state.injected_input = q
                st.rerun()
    else:
        st.caption("No recent questions yet.")


# ══════════════════════════════════════════════════════════════════════
# MAIN AREA — Header
# ══════════════════════════════════════════════════════════════════════
st.title("🤖 AI Support Assistant")
st.caption("Billing • Technical Support • Account Management • General Queries")
st.divider()

if not st.session_state.history:
    st.markdown(
        """
        👋 **Welcome to AI Support Assistant**

        How can I help you today? I can assist with:

        - 💳 Billing and payments
        - 🔧 Technical issues
        - 👤 Account management
        - 💬 General support questions
        """
    )


# ══════════════════════════════════════════════════════════════════════
# BACKEND HELPERS
# ══════════════════════════════════════════════════════════════════════
def call_backend(msg: str, lang: str) -> str:
    """
    Send question to FastAPI /chat endpoint.
    FastAPI handles translation and agent routing.
    """
    try:
        response = requests.post(
            f"{BACKEND_URL}/chat",
            json={
                "query": msg,
                "lang": lang
            },
            timeout=60
        )

        result = response.json()

        return result.get(
            "response",
            result.get("error", "Unknown error")
        )

    except Exception as exc:
        return f"Backend unreachable: {exc}"


def translate_text(text: str, to_lang: str) -> str:
    """
    Translate FAQ/cache answers using FastAPI /translate endpoint.
    """

    if to_lang == "en":
        return text

    try:
        response = requests.post(
            f"{BACKEND_URL}/translate",
            json={
                "text": text,
                "to_lang": to_lang
            },
            timeout=30
        )

        result = response.json()

        if "error" in result:
            return text

        return result.get("translated", text)

    except Exception:
        return text

# ══════════════════════════════════════════════════════════════════════
# UNIFIED QUESTION HANDLER
# ══════════════════════════════════════════════════════════════════════
def handle_question(question: str) -> None:

    question_key = normalize_question(question)

    # Prevent duplicate consecutive questions
    if (
        st.session_state.history
        and len(st.session_state.history) >= 2
        and st.session_state.history[-2][0] == "user"
        and normalize_question(
            st.session_state.history[-2][1]
        ) == question_key
    ):
        return

    # --------------------------------------------------
    # 1. FAQ CACHE
    # --------------------------------------------------
    if question_key in _FAQ_KEYS:

        # FAQ answers remain in English always
        reply = _FAQ_KEYS[question_key]

    # --------------------------------------------------
    # 2. NORMAL CACHE
    # --------------------------------------------------
    elif question_key in st.session_state.answer_cache:

        # Return exactly what was cached
        # No re-translation
        reply = st.session_state.answer_cache[
            question_key
        ]

    # --------------------------------------------------
    # 3. NEW QUESTION
    # --------------------------------------------------
    else:

        try:
            user_lang = detect(question)
        except Exception:
            user_lang = "en"

        with st.spinner("Thinking..."):
            reply = call_backend(
                question,
                user_lang
            )

        # Save exact returned answer
        st.session_state.answer_cache[
            question_key
        ] = reply

        save_disk_cache(
            st.session_state.answer_cache
        )

    # --------------------------------------------------
    # Update history
    # --------------------------------------------------
    st.session_state.history.append(
        ("user", question)
    )

    st.session_state.history.append(
        ("assistant", reply)
    )

    # --------------------------------------------------
    # Update recent questions
    # --------------------------------------------------
    st.session_state.recent_questions = [
        (q, a)
        for q, a in st.session_state.recent_questions
        if q != question
    ]

    st.session_state.recent_questions.insert(
        0,
        (question, reply)
    )

    st.session_state.recent_questions = (
        st.session_state.recent_questions[:5]
    )

    st.session_state.last_input = question

# ══════════════════════════════════════════════════════════════════════
# INPUT ROUTING
# ══════════════════════════════════════════════════════════════════════
if st.session_state.injected_input:
    q = st.session_state.injected_input
    st.session_state.injected_input = None
    if q != st.session_state.last_input:
        handle_question(q)
        st.rerun()

user_input = st.chat_input("Ask me anything (any language)...")
if user_input and user_input != st.session_state.last_input:
    handle_question(user_input)
    st.rerun()

# ══════════════════════════════════════════════════════════════════════
# DISPLAY CHAT HISTORY
# ══════════════════════════════════════════════════════════════════════
for role, msg in st.session_state.history:
    st.chat_message(role).write(msg)