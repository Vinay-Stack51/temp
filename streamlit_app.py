"""
Streamlit launcher for AI Chess Game.
Starts the Flask server and embeds it in a Streamlit iframe.
"""

import streamlit as st
import subprocess
import time
import threading
import requests
import os
import sys

# ── Page config ──────────────────────────────────────────────
st.set_page_config(
    page_title="AI Chess Game",
    page_icon="♟️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Custom CSS ────────────────────────────────────────────────
st.markdown("""
<style>
    .stApp { background: #0d0f14; }
    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding: 0 !important; max-width: 100% !important; }
    iframe { border: none; display: block; }
</style>
""", unsafe_allow_html=True)

FLASK_PORT = 5001
FLASK_URL = f"http://localhost:{FLASK_PORT}"


def is_flask_running():
    try:
        r = requests.get(FLASK_URL, timeout=2)
        return r.status_code == 200
    except:
        return False


import os

def start_flask():
    # Don't start Flask on Streamlit Cloud
    if os.getenv("STREAMLIT_SERVER_PORT"):
        return

    import subprocess
    import sys

    script_dir = os.path.dirname(os.path.abspath(__file__))
    app_path = os.path.join(script_dir, "app.py")

    env = os.environ.copy()
    env["FLASK_ENV"] = "production"

    subprocess.Popen(
        [sys.executable, app_path],
        env={**env, "FLASK_RUN_PORT": str(FLASK_PORT)},
    )
# ── Start Flask if not running ────────────────────────────────
if "flask_started" not in st.session_state:
    st.session_state.flask_started = False

if not st.session_state.flask_started:
    if not is_flask_running():
        start_flask()
        # Wait for Flask to boot
        for _ in range(20):
            if is_flask_running():
                break
            time.sleep(0.5)
    st.session_state.flask_started = True

# ── Embed the game ────────────────────────────────────────────
if is_flask_running():
    st.components.v1.iframe(FLASK_URL, height=860, scrolling=False)
else:
    st.error("⚠️ Could not start the chess server. Please run `python app.py` manually and visit http://localhost:5000")
    st.code("python app.py", language="bash")
