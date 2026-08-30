import os

from dotenv import load_dotenv

load_dotenv()

# Local .env is loaded at import. Streamlit Cloud secrets are read lazily
# so we never call st.secrets before st.set_page_config.
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


def resolve_gemini_api_key() -> str:
    key = os.getenv("GEMINI_API_KEY") or GEMINI_API_KEY or ""
    if key:
        return key
    try:
        import streamlit as st

        return str(st.secrets.get("GEMINI_API_KEY", "") or "")
    except Exception:
        return ""

# gemini-2.5-flash is retired for new API keys (404). Current Flash-tier:
MODEL_NAME = "gemini-3.6-flash"
FALLBACK_MODEL_NAME = "gemini-3.5-flash-lite"
