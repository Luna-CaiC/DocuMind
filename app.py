"""
DocuMind — Streamlit Application
=====================================
Upload PDFs → ask questions → get citation-backed answers powered by
local HuggingFace embeddings, Groq LLM, and Gemini Vision OCR.
"""

import os
import re
import uuid
import shutil
import base64
import streamlit as st
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import CommaSeparatedListOutputParser
from langchain_community.vectorstores import Chroma

from src.ingest import process_documents
from src.history import ChatHistoryManager

load_dotenv(override=True)
GEMINI_MODEL    = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
GROQ_MODEL      = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
VECTORS_BASE    = os.path.join("data", "session_vectors")

# ── Custom chat avatars (inline SVG data URIs) ────────────────────────
_ASST_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 40">
  <defs>
    <linearGradient id="ag" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#18c99a"/>
      <stop offset="1" stop-color="#0a7a5e"/>
    </linearGradient>
  </defs>
  <circle cx="20" cy="20" r="20" fill="url(#ag)"/>
  <path d="M20 9 L22.8 17.2 L31 20 L22.8 22.8 L20 31 L17.2 22.8 L9 20 L17.2 17.2 Z"
        fill="white" opacity="0.92"/>
</svg>"""

_USER_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 40">
  <circle cx="20" cy="20" r="20" fill="#2a2d36"/>
  <circle cx="20" cy="15" r="7" fill="#6b7a8d"/>
  <path d="M6 36 Q6 27 20 27 Q34 27 34 36" fill="#6b7a8d"/>
</svg>"""

ASST_AVATAR = "data:image/svg+xml;base64," + base64.b64encode(_ASST_SVG.encode()).decode()
USER_AVATAR = "data:image/svg+xml;base64," + base64.b64encode(_USER_SVG.encode()).decode()

# ── Page configuration ───────────────────────────────────────────────
st.set_page_config(
    page_title="DocuMind — AI Document Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ── Global CSS — GPT-style dark minimal UI ───────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ── Base — cover every Streamlit structural element ─────────────── */
html, body, .stApp,
[data-testid="stAppViewContainer"],
[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stBottom"],
[data-testid="stStatusWidget"],
.stAppHeader,
.stAppDeployButton,
header {
    background-color: #212121 !important;
    font-family: 'Inter', -apple-system, sans-serif !important;
}

/* ── Streamlit top header toolbar ────────────────────────────────── */
[data-testid="stHeader"] {
    background: #212121 !important;
    border-bottom: 1px solid rgba(255,255,255,0.06) !important;
}
/* Make the Deploy button text readable */
[data-testid="stHeader"] button,
[data-testid="stHeader"] [data-testid="stToolbarActions"] button {
    color: #b0b0b0 !important;
    background: transparent !important;
    border-color: rgba(255,255,255,0.12) !important;
}

/* ── Bottom chat input container strip ───────────────────────────── */
[data-testid="stBottom"],
[data-testid="stBottom"] > div {
    background: #212121 !important;
    border-top: 1px solid rgba(255,255,255,0.06) !important;
}

/* ── Sidebar shell ───────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background-color: #171717 !important;
    border-right: 1px solid rgba(255,255,255,0.06) !important;
}
[data-testid="stSidebar"] > div:first-child {
    padding: 14px 10px 80px !important;
}

/* All sidebar text white ────────────────────────────────────────── */
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] small,
[data-testid="stSidebar"] div {
    color: #d1d1d1 !important;
}

/* Sidebar section headings */
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #555 !important;
    font-size: 0.68rem !important;
    font-weight: 700 !important;
    letter-spacing: 1.2px !important;
    text-transform: uppercase !important;
    margin: 18px 0 8px 2px !important;
}

/* ── New Chat button ─────────────────────────────────────────────── */
[data-testid="stSidebar"] .stButton:first-of-type button {
    background: #10a37f !important;
    color: #fff !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 0.87rem !important;
    padding: 9px 0 !important;
    transition: background 0.15s, transform 0.15s !important;
    box-shadow: 0 2px 10px rgba(16,163,127,0.25) !important;
}
[data-testid="stSidebar"] .stButton:first-of-type button:hover {
    background: #0d8f6e !important;
    transform: translateY(-1px) !important;
}

/* ── All other sidebar buttons: secondary = dark bg + green glow border */
[data-testid="stSidebar"] .stButton button,
[data-testid="stSidebar"] .stButton button[kind="secondary"] {
    background: rgba(16,163,127,0.04) !important;
    background-color: rgba(16,163,127,0.04) !important;
    border: 1px solid rgba(16,163,127,0.35) !important;
    border-radius: 8px !important;
    color: #c0c0c0 !important;
    font-size: 0.79rem !important;
    text-align: left !important;
    padding: 7px 10px !important;
    line-height: 1.45 !important;
    white-space: pre-wrap !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 0 6px rgba(16,163,127,0.18), inset 0 0 0 1px rgba(16,163,127,0.08) !important;
}
[data-testid="stSidebar"] .stButton button:hover,
[data-testid="stSidebar"] .stButton button[kind="secondary"]:hover {
    background: rgba(16,163,127,0.09) !important;
    background-color: rgba(16,163,127,0.09) !important;
    border-color: rgba(16,163,127,0.60) !important;
    color: #e0e0e0 !important;
    box-shadow: 0 0 10px rgba(16,163,127,0.30), inset 0 0 0 1px rgba(16,163,127,0.15) !important;
}
/* Active / currently selected session — solid green fill */
[data-testid="stSidebar"] .stButton button[kind="primary"] {
    background: #10a37f !important;
    background-color: #10a37f !important;
    border: 1px solid #10a37f !important;
    color: #ffffff !important;
    font-weight: 600 !important;
    box-shadow: 0 2px 12px rgba(16,163,127,0.45) !important;
}
[data-testid="stSidebar"] .stButton button[kind="primary"]:hover {
    background: #0d8f6e !important;
    background-color: #0d8f6e !important;
    border-color: #0d8f6e !important;
    box-shadow: 0 4px 16px rgba(16,163,127,0.55) !important;
}

/* ── File uploader ───────────────────────────────────────────────── */
[data-testid="stFileUploader"] {
    background: rgba(255,255,255,0.02) !important;
    border: 1.5px dashed rgba(255,255,255,0.12) !important;
    border-radius: 10px !important;
}
[data-testid="stFileUploader"]:hover {
    border-color: #10a37f !important;
}
[data-testid="stFileUploader"] label,
[data-testid="stFileUploader"] p,
[data-testid="stFileUploader"] span,
[data-testid="stFileUploader"] small,
[data-testid="stFileUploader"] * {
    color: #c0c0c0 !important;
    font-size: 0.82rem !important;
}

/* ── Main area ───────────────────────────────────────────────────── */
.main .block-container {
    max-width: 780px !important;
    padding: 2rem 2rem 140px !important;
    margin: 0 auto !important;
}

.main h1 {
    color: #ececec !important;
    font-size: 1.45rem !important;
    font-weight: 700 !important;
    letter-spacing: -0.3px !important;
    margin-bottom: 2px !important;
}

/* Force ALL text in main visible */
.main p, .main li, .main span, .main label,
.stMarkdown p, .stMarkdown li, .stMarkdown span,
.stMarkdown strong, .stMarkdown em, .stMarkdown code,
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li,
[data-testid="stMarkdownContainer"] span {
    color: #e0e0e0 !important;
    line-height: 1.65 !important;
}

/* ── Chat messages ───────────────────────────────────────────────── */
[data-testid="stChatMessage"] {
    background: transparent !important;
    padding: 6px 0 !important;
    border: none !important;
    animation: slideFade 0.20s ease-out;
}
@keyframes slideFade {
    from { opacity:0; transform:translateY(6px); }
    to   { opacity:1; transform:translateY(0); }
}
/* Force ALL text inside any chat bubble to bright white */
[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] span,
[data-testid="stChatMessage"] li,
[data-testid="stChatMessage"] div,
[data-testid="stChatMessage"] strong,
[data-testid="stChatMessage"] em,
[data-testid="stChatMessage"] code {
    color: #ececec !important;
}
[data-testid="stChatMessage"] pre,
[data-testid="stChatMessage"] h1,
[data-testid="stChatMessage"] h2,
[data-testid="stChatMessage"] h3,
[data-testid="stChatMessage"] td,
[data-testid="stChatMessage"] th {
    color: #ececec !important;
}

/* ── Chat input bar ──────────────────────────────────────────────── */
[data-testid="stChatInputContainer"] {
    background: #2f2f2f !important;
    border: 1.5px solid rgba(255,255,255,0.10) !important;
    border-radius: 16px !important;
    box-shadow: 0 4px 20px rgba(0,0,0,0.30) !important;
    transition: border-color 0.2s !important;
}
[data-testid="stChatInputContainer"]:focus-within {
    border-color: rgba(16,163,127,0.50) !important;
    box-shadow: 0 0 0 3px rgba(16,163,127,0.10) !important;
}
/* Input text — white, clearly visible */
[data-testid="stChatInputContainer"] textarea {
    background: transparent !important;
    color: #f0f0f0 !important;
    caret-color: #f0f0f0 !important;
    font-size: 0.94rem !important;
    font-family: 'Inter', sans-serif !important;
}
[data-testid="stChatInputContainer"] textarea::placeholder {
    color: #4a4a4a !important;
}

/* ── Alert boxes ─────────────────────────────────────────────────── */
[data-testid="stAlert"] {
    border-radius: 10px !important;
    font-size: 0.86rem !important;
}
[data-testid="stAlert"] p,
[data-testid="stAlert"] span { color: inherit !important; }

/* ── Spinner ─────────────────────────────────────────────────────── */
[data-testid="stSpinner"] p { color: #888 !important; font-size: 0.83rem !important; }

/* ── Dividers ────────────────────────────────────────────────────── */
hr { border-color: rgba(255,255,255,0.07) !important; margin: 8px 0 !important; }

/* ── Welcome card ────────────────────────────────────────────────── */
.welcome-card {
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 12px;
    padding: 32px 24px;
    margin: 36px 0 16px;
    text-align: center;
}
.welcome-card h3  { color: #e0e0e0 !important; font-size: 1rem !important; font-weight: 600; margin-bottom: 6px; }
.welcome-card p   { color: #888 !important; font-size: 0.84rem !important; line-height: 1.6; }
.welcome-card .steps { display:flex; justify-content:center; gap:44px; margin-top:24px; flex-wrap:wrap; }
.welcome-card .step  { display:flex; flex-direction:column; align-items:center; gap:7px; }
.welcome-card .step-icon  { font-size:1.4rem; }
.welcome-card .step-label { color:#555 !important; font-size:0.74rem !important; font-weight:500; }

/* ── Active doc badge ────────────────────────────────────────────── */
.doc-badge {
    display:inline-flex; align-items:center; gap:6px;
    background:rgba(16,163,127,0.10);
    border:1px solid rgba(16,163,127,0.38);
    border-radius:20px; padding:4px 12px;
    font-size:0.78rem; color:#5fd3ba !important; font-weight:500;
    margin-top:6px;
}

/* ── Subtitle ────────────────────────────────────────────────────── */
.subtitle-text { color:#888 !important; font-size:0.85rem !important; margin-bottom:1rem; line-height:1.5; }

/* ── Scrollbar ───────────────────────────────────────────────────── */
::-webkit-scrollbar { width:4px; }
::-webkit-scrollbar-thumb { background:rgba(255,255,255,0.08); border-radius:10px; }
::-webkit-scrollbar-thumb:hover { background:rgba(255,255,255,0.15); }

/* ── Inline code ─────────────────────────────────────────────────── */
[data-testid="stChatMessage"] code,
[data-testid="stMarkdownContainer"] code {
    background: #1e2030 !important;
    color: #7dd3b8 !important;
    border: 1px solid rgba(16,163,127,0.25) !important;
    border-radius: 4px !important;
    padding: 2px 6px !important;
    font-family: 'JetBrains Mono', 'Fira Code', 'Courier New', monospace !important;
    font-size: 0.85em !important;
}

/* ── Code blocks (pre) ───────────────────────────────────────────── */
[data-testid="stChatMessage"] pre,
[data-testid="stMarkdownContainer"] pre {
    background: #1a1d2e !important;
    border: 1px solid rgba(16,163,127,0.20) !important;
    border-left: 3px solid #10a37f !important;
    border-radius: 8px !important;
    padding: 14px 16px !important;
    overflow-x: auto !important;
}
[data-testid="stChatMessage"] pre code,
[data-testid="stMarkdownContainer"] pre code {
    background: transparent !important;
    color: #d0e8d8 !important;
    border: none !important;
    padding: 0 !important;
    font-size: 0.88rem !important;
    line-height: 1.65 !important;
}

/* ── Markdown tables ─────────────────────────────────────────────── */
[data-testid="stChatMessage"] table,
[data-testid="stMarkdownContainer"] table {
    border-collapse: collapse !important;
    width: 100% !important;
    font-size: 0.88rem !important;
}
[data-testid="stChatMessage"] th,
[data-testid="stMarkdownContainer"] th {
    background: rgba(16,163,127,0.15) !important;
    color: #ececec !important;
    border: 1px solid rgba(255,255,255,0.10) !important;
    padding: 8px 12px !important;
}
[data-testid="stChatMessage"] td,
[data-testid="stMarkdownContainer"] td {
    background: rgba(255,255,255,0.02) !important;
    color: #d0d0d0 !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    padding: 7px 12px !important;
}

/* ── Blockquotes ─────────────────────────────────────────────────── */
[data-testid="stChatMessage"] blockquote,
[data-testid="stMarkdownContainer"] blockquote {
    border-left: 3px solid #10a37f !important;
    background: rgba(16,163,127,0.05) !important;
    margin: 8px 0 !important;
    padding: 8px 14px !important;
    color: #aaaaaa !important;
    border-radius: 0 6px 6px 0 !important;
}

/* ── Links ───────────────────────────────────────────────────────── */
[data-testid="stChatMessage"] a,
[data-testid="stMarkdownContainer"] a {
    color: #5fd3ba !important;
    text-decoration: underline !important;
    text-underline-offset: 2px !important;
}
[data-testid="stChatMessage"] a:hover,
[data-testid="stMarkdownContainer"] a:hover {
    color: #10a37f !important;
}

/* ── Code block copy button ──────────────────────────────────────── */
[data-testid="stChatMessage"] pre button,
[data-testid="stMarkdownContainer"] pre button,
[data-testid="stCodeToolbar"] button,
.stCodeBlock button,
button[title="Copy to clipboard"],
button[aria-label="Copy to clipboard"] {
    background: #1e2030 !important;
    background-color: #1e2030 !important;
    color: #7dd3b8 !important;
    border: 1px solid rgba(16,163,127,0.30) !important;
    border-radius: 5px !important;
    opacity: 1 !important;
}
button[title="Copy to clipboard"]:hover,
button[aria-label="Copy to clipboard"]:hover {
    background: rgba(16,163,127,0.20) !important;
    color: #ffffff !important;
}

/* ── Alert / info / warning / error boxes ────────────────────────── */
[data-testid="stAlert"],
[data-testid="stNotification"],
div[data-baseweb="notification"] {
    background: #1a1d2e !important;
    border-radius: 8px !important;
    border-left-width: 3px !important;
}
/* info → blue-teal tint */
[data-testid="stAlert"][data-type="info"],
.stAlert.stInfo {
    border-color: #3b9edd !important;
    color: #b0d4f0 !important;
}
/* success → green tint */
[data-testid="stAlert"][data-type="success"],
.stAlert.stSuccess {
    border-color: #10a37f !important;
    color: #7dd3b8 !important;
}
/* warning → amber tint */
[data-testid="stAlert"][data-type="warning"],
.stAlert.stWarning {
    border-color: #d4a017 !important;
    color: #e8c97a !important;
}
/* error → red tint */
[data-testid="stAlert"][data-type="error"],
.stAlert.stError {
    border-color: #c94040 !important;
    color: #f0a0a0 !important;
}
/* Force all text inside alerts to be visible */
[data-testid="stAlert"] p,
[data-testid="stAlert"] span,
[data-testid="stAlert"] div {
    color: inherit !important;
}

/* ── Spinner ─────────────────────────────────────────────────────── */
[data-testid="stSpinner"],
[data-testid="stSpinner"] p,
[data-testid="stSpinner"] span,
.stSpinner p {
    color: #a0a0a0 !important;
    font-size: 0.88rem !important;
}

/* ── HR horizontal rule in chat ──────────────────────────────────── */
[data-testid="stChatMessage"] hr,
[data-testid="stMarkdownContainer"] hr {
    border: none !important;
    border-top: 1px solid rgba(16,163,127,0.25) !important;
    margin: 14px 0 !important;
}

/* ── User Message Bubble (Right Aligned) ─────────────────────────── */
[data-testid="stChatMessage"]:has(.dm-user-hook) {
    flex-direction: row-reverse !important;
    gap: 8px !important;
    align-items: center !important; /* Forces Avatar and Bubble to be vertically level */
}

/* Strip native margins pushing the avatar out of place when reversed */
[data-testid="stChatMessage"]:has(.dm-user-hook) [data-testid="stChatAvatar"] {
    margin: 0 !important;
}

/* Make the message text container stretch and align items right */
[data-testid="stChatMessage"]:has(.dm-user-hook) > div:last-child {
    display: flex !important;
    flex-direction: column !important;
    align-items: flex-end !important;
    width: 100% !important;
    flex-grow: 1 !important;
}

/* Style the actual text message containers (exclude the hook) */
[data-testid="stChatMessage"]:has(.dm-user-hook) [data-testid="stMarkdownContainer"]:not(:has(.dm-user-hook)) {
    display: inline-block !important; /* shrink wrap */
    width: fit-content !important;
    max-width: 75vw !important;
    padding: 12px 18px !important;
    border-radius: 18px !important;
    background-color: #204030 !important;
    color: #ffffff !important;
    margin-left: auto !important; /* push firmly right */
    margin-right: 0 !important;
}

[data-theme="light"] [data-testid="stChatMessage"]:has(.dm-user-hook) [data-testid="stMarkdownContainer"]:not(:has(.dm-user-hook)) {
    background-color: #d1f0d1 !important;
    color: #000000 !important;
}

/* Force inner text right and remove native P margins */
[data-testid="stChatMessage"]:has(.dm-user-hook) [data-testid="stMarkdownContainer"]:not(:has(.dm-user-hook)) * {
    color: inherit !important;
    text-align: right !important;
    margin-bottom: 0 !important;
    margin-top: 0 !important;
}

/* Hide the invisible hook completely */
[data-testid="stChatMessage"]:has(.dm-user-hook) [data-testid="stMarkdownContainer"]:has(.dm-user-hook) {
    display: none !important;
}


/* ═══════════════════════════════════════════════════════════════════
   LIGHT MODE OVERRIDES — triggered by Streamlit's data-theme="light"
   ═══════════════════════════════════════════════════════════════════ */

/* Base backgrounds */
[data-theme="light"] html,
[data-theme="light"] body,
[data-theme="light"] .stApp,
[data-theme="light"] [data-testid="stAppViewContainer"],
[data-theme="light"] [data-testid="stHeader"],
[data-theme="light"] [data-testid="stToolbar"],
[data-theme="light"] [data-testid="stBottom"],
[data-theme="light"] [data-testid="stBottom"] > div,
[data-theme="light"] header {
    background-color: #ffffff !important;
}

/* Sidebar - very light grey */
[data-theme="light"] [data-testid="stSidebar"],
[data-theme="light"] [data-testid="stSidebar"] > div {
    background-color: #f7f7f8 !important;
    border-right: 1px solid rgba(0,0,0,0.08) !important;
}

/* All sidebar text - black */
[data-theme="light"] [data-testid="stSidebar"] p,
[data-theme="light"] [data-testid="stSidebar"] span,
[data-theme="light"] [data-testid="stSidebar"] label,
[data-theme="light"] [data-testid="stSidebar"] small,
[data-theme="light"] [data-testid="stSidebar"] div {
    color: #1a1a1a !important;
}

[data-theme="light"] [data-testid="stSidebar"] h2,
[data-theme="light"] [data-testid="stSidebar"] h3 {
    color: #444 !important;
}

/* Secondary sidebar buttons (inactive sessions) */
[data-theme="light"] [data-testid="stSidebar"] .stButton button,
[data-theme="light"] [data-testid="stSidebar"] .stButton button[kind="secondary"] {
    background: #ffffff !important;
    background-color: #ffffff !important;
    border: 1px solid rgba(0,0,0,0.12) !important;
    color: #1a1a1a !important;
    box-shadow: none !important;
}
[data-theme="light"] [data-testid="stSidebar"] .stButton button:hover,
[data-theme="light"] [data-testid="stSidebar"] .stButton button[kind="secondary"]:hover {
    background: #f0f0f0 !important;
    background-color: #f0f0f0 !important;
    border-color: rgba(16,163,127,0.50) !important;
    color: #000000 !important;
}

/* File uploader */
[data-theme="light"] [data-testid="stFileUploader"] {
    background: #ffffff !important;
    border: 1.5px dashed rgba(0,0,0,0.15) !important;
}
[data-theme="light"] [data-testid="stFileUploader"] label,
[data-theme="light"] [data-testid="stFileUploader"] p,
[data-theme="light"] [data-testid="stFileUploader"] span,
[data-theme="light"] [data-testid="stFileUploader"] small,
[data-theme="light"] [data-testid="stFileUploader"] * {
    color: #333333 !important;
}

/* Main area text */
[data-theme="light"] .main h1,
[data-theme="light"] h1, [data-theme="light"] h2, [data-theme="light"] h3,
[data-theme="light"] h4, [data-theme="light"] h5, [data-theme="light"] h6 {
    color: #000000 !important;
}

[data-theme="light"] .main p,
[data-theme="light"] .main li,
[data-theme="light"] .main span,
[data-theme="light"] .main label,
[data-theme="light"] .stMarkdown p,
[data-theme="light"] .stMarkdown li,
[data-theme="light"] .stMarkdown span,
[data-theme="light"] .stMarkdown strong,
[data-theme="light"] .stMarkdown em,
[data-theme="light"] [data-testid="stMarkdownContainer"] p,
[data-theme="light"] [data-testid="stMarkdownContainer"] li,
[data-theme="light"] [data-testid="stMarkdownContainer"] span,
[data-theme="light"] [data-testid="stMarkdownContainer"] strong,
[data-theme="light"] [data-testid="stMarkdownContainer"] b,
[data-theme="light"] [data-testid="stMarkdownContainer"] em {
    color: #000000 !important;
}

/* AI chat message text */
[data-theme="light"] [data-testid="stChatMessage"] p,
[data-theme="light"] [data-testid="stChatMessage"] span,
[data-theme="light"] [data-testid="stChatMessage"] li,
[data-theme="light"] [data-testid="stChatMessage"] strong,
[data-theme="light"] [data-testid="stChatMessage"] em,
[data-theme="light"] [data-testid="stChatMessage"] h1,
[data-theme="light"] [data-testid="stChatMessage"] h2,
[data-theme="light"] [data-testid="stChatMessage"] h3,
[data-theme="light"] [data-testid="stChatMessage"] td,
[data-theme="light"] [data-testid="stChatMessage"] th {
    color: #000000 !important;
}

/* Code blocks - green on light */
[data-theme="light"] [data-testid="stChatMessage"] code,
[data-theme="light"] [data-testid="stMarkdownContainer"] code {
    background: #f0f9f0 !important;
    color: #0a694e !important;
    border: 1px solid rgba(16,163,127,0.25) !important;
}
[data-theme="light"] [data-testid="stChatMessage"] pre,
[data-theme="light"] [data-testid="stMarkdownContainer"] pre {
    background: #f5f5f5 !important;
    border: 1px solid rgba(0,0,0,0.08) !important;
    border-left: 3px solid #10a37f !important;
}
[data-theme="light"] [data-testid="stChatMessage"] pre code,
[data-theme="light"] [data-testid="stMarkdownContainer"] pre code {
    background: transparent !important;
    color: #0a694e !important;
    border: none !important;
}

/* Chat input box */
[data-theme="light"] [data-testid="stChatInputContainer"] {
    background: #f4f4f4 !important;
    border: 1.5px solid rgba(16,163,127,0.30) !important;
}
[data-theme="light"] [data-testid="stChatInputContainer"]:focus-within {
    border-color: #10a37f !important;
}
[data-theme="light"] [data-testid="stChatInputContainer"] textarea {
    color: #000000 !important;
    caret-color: #000000 !important;
    -webkit-text-fill-color: #000000 !important;
}
[data-theme="light"] [data-testid="stChatInputContainer"] textarea::placeholder {
    color: #999999 !important;
}
[data-theme="light"] [data-testid="stChatInputContainer"] svg {
    stroke: #333333 !important;
}

/* Top header bar buttons */
[data-theme="light"] [data-testid="stHeader"] {
    background: #ffffff !important;
    border-bottom: 1px solid rgba(0,0,0,0.08) !important;
}
[data-theme="light"] [data-testid="stHeader"] button,
[data-theme="light"] [data-testid="stToolbarActions"] button {
    color: #000000 !important;
    background-color: #ffffff !important;
    border: 1px solid rgba(0,0,0,0.12) !important;
}

/* Welcome card */
[data-theme="light"] .welcome-card {
    background: #fafafa !important;
    border: 1px solid rgba(0,0,0,0.08) !important;
}
[data-theme="light"] .welcome-card h3 { color: #000000 !important; }
[data-theme="light"] .welcome-card p { color: #444444 !important; }
[data-theme="light"] .welcome-card .step-label { color: #555555 !important; }

/* Subtitle */
[data-theme="light"] .subtitle-text { color: #444444 !important; }

/* Scrollbar */
[data-theme="light"] ::-webkit-scrollbar-thumb { background: rgba(0,0,0,0.12); }

/* Alert boxes */
[data-theme="light"] [data-testid="stAlert"],
[data-theme="light"] [data-testid="stNotification"] {
    background: #ffffff !important;
}

/* Tables */
[data-theme="light"] [data-testid="stChatMessage"] th,
[data-theme="light"] [data-testid="stMarkdownContainer"] th {
    background: rgba(16,163,127,0.10) !important;
    color: #000000 !important;
    border: 1px solid rgba(0,0,0,0.10) !important;
}
[data-theme="light"] [data-testid="stChatMessage"] td,
[data-theme="light"] [data-testid="stMarkdownContainer"] td {
    background: #ffffff !important;
    color: #000000 !important;
    border: 1px solid rgba(0,0,0,0.08) !important;
}

</style>
""", unsafe_allow_html=True)



# ── Cache the embedding model (loads once per server session) ─────────
@st.cache_resource(show_spinner="⚙️ Loading AI models — first launch only…")
def get_embeddings():
    from langchain_community.embeddings import HuggingFaceEmbeddings
    return HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)


# ── Persistent history manager ───────────────────────────────────────
history_mgr = ChatHistoryManager()


# ── FileWrapper: mimics Streamlit UploadedFile for on-disk files ─────
class FileWrapper:
    def __init__(self, name: str, content: bytes):
        self.name     = name
        self._content = content
        self.file_id  = f"disk_{name}"

    def read(self) -> bytes:
        return self._content


# ── Friendly error message helper ────────────────────────────────────
def friendly_error(raw_error: str) -> str:
    """Convert raw technical errors into user-friendly messages."""
    e = str(raw_error).lower()
    if "429" in e or "resource_exhausted" in e or "quota" in e:
        return (
            "⏳ **API rate limit reached.** The AI service is temporarily busy. "
            "Please wait 30–60 seconds and try again. "
            "If this happens often, your daily quota may be exhausted — "
            "it resets automatically at midnight (Pacific time)."
        )
    if "api key" in e or "authentication" in e or "invalid_api_key" in e or "401" in e:
        return (
            "🔑 **API key error.** The AI service credentials are invalid or missing. "
            "Please check that your `.env` file contains a valid `GROQ_API_KEY`."
        )
    if "connection" in e or "timeout" in e or "network" in e or "ssl" in e:
        return (
            "🌐 **Network issue.** Could not reach the AI service. "
            "Please check your internet connection and try again."
        )
    if "no such file" in e or "filenotfounderror" in e:
        return (
            "📁 **File not found.** The session data may have been cleared. "
            "Please upload your document(s) again to start a new session."
        )
    if "context_length" in e or "token" in e and "exceed" in e:
        return (
            "📄 **Document too large for a single query.** "
            "Try breaking your question into smaller parts, "
            "or reduce the number of documents in this session."
        )
    if "chroma" in e or "collection" in e or "embedding" in e:
        return (
            "🗄️ **Session data error.** The document index could not be loaded. "
            "Please start a new chat and re-upload your files."
        )
    # Generic fallback — show a readable version, not the full stack trace
    short = str(raw_error)[:200]
    return (
        f"❌ **Something went wrong.** "
        f"Please try again, or start a new chat.\n\n"
        f"<details><summary>Technical details</summary>{short}</details>"
    )


# ── Session state defaults ───────────────────────────────────────────
for key, default in {
    "chat_history":    [],
    "vector_store":    None,
    "session_id":      None,
    "doc_names":       [],
    "viewing_history": False,
    "pending_resume":  None,
    "last_file_ids":   None,
    "resume_no_create": False,
    "uploader_key":    0,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default


# ── Handle pending session resume ─────────────────────────────────────
if st.session_state.pending_resume is not None:
    resume_id = st.session_state.pending_resume
    st.session_state.pending_resume = None

    vector_dir = os.path.join(VECTORS_BASE, resume_id)

    if os.path.exists(vector_dir):
        with st.spinner("🔄 Restoring session…"):
            try:
                embeddings = get_embeddings()
                vs = Chroma(
                    persist_directory=vector_dir,
                    embedding_function=embeddings,
                    collection_name="main",
                )
                st.session_state.vector_store    = vs
                st.session_state.viewing_history = False
                st.session_state.resume_no_create = True
            except Exception as e:
                st.warning(friendly_error(e))
                st.session_state.viewing_history = True
                st.session_state.vector_store    = None
    else:
        st.session_state.viewing_history = True
        st.session_state.vector_store    = None

    st.rerun()


# ── LLM ──────────────────────────────────────────────────────────────
LLM = ChatGroq(
    model=GROQ_MODEL,
    temperature=0.4,
)

SYSTEM_PROMPT = (
    "You are an expert document assistant. "
    "The user has uploaded the following document(s): {doc_names}.\n\n"
    "IMPORTANT CONTEXT NOTE:\n"
    "The context below is a SAMPLE of retrieved chunks from the documents — "
    "it is NOT the complete document. Large documents contain far more content "
    "than what is shown here. Do NOT imply that the examples you see are the "
    "only content in the document.\n\n"
    "INSTRUCTIONS:\n"
    "1. Read the retrieved context thoroughly before answering.\n"
    "2. For SUMMARY or OVERVIEW questions (e.g. 'what does this file contain?', "
    "'what is this document about?'):\n"
    "   - Describe the overall nature and scope of the document.\n"
    "   - Use phrases like 'for example', 'including but not limited to', "
    "'among other topics' — NOT 'it includes: [list]' which implies completeness.\n"
    "   - If the document clearly covers many topics, explicitly say so.\n"
    "   - Give a rich, multi-paragraph answer.\n"
    "3. For SPECIFIC questions, provide a complete and detailed answer ONLY using the provided context.\n"
    "4. If the provided context does NOT contain the answer to a specific question, you MUST "
    "explicitly state: 'I cannot answer this based on the provided documents.' Do NOT guess, "
    "and do NOT use your general knowledge to answer.\n"
    "5. Do NOT use any outside knowledge whatsoever. You are strictly restricted to the documents.\n"
    "6. Cite page numbers and source filenames when available.\n"
    "7. When the user refers to a document by filename, answer about its content.\n\n"
    "Context:\n{context}"
)

PROMPT = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", "{input}"),
])


# ────────────────────────────────────────────────────────────────────
# SIDEBAR
# ────────────────────────────────────────────────────────────────────
with st.sidebar:

    # ── Logo / brand ─────────────────────────────────────────────────
    st.markdown("""
    <div style="display:flex;align-items:center;gap:10px;padding:4px 4px 12px;">
        <span style="font-size:1.4rem;">🤖</span>
        <span style="font-weight:700;font-size:1rem;color:#ececec;letter-spacing:-0.3px;">DocuMind</span>
    </div>
    """, unsafe_allow_html=True)

    # ── New Chat button ───────────────────────────────────────────────
    if st.button("✏️  New Chat", use_container_width=True, type="primary"):
        st.session_state.chat_history     = []
        st.session_state.vector_store     = None
        st.session_state.session_id       = None
        st.session_state.doc_names        = []
        st.session_state.viewing_history  = False
        st.session_state.last_file_ids    = None
        st.session_state.resume_no_create = False
        st.session_state.uploader_key    += 1
        st.rerun()

    st.divider()

    # ── Upload section ───────────────────────────────────────────────
    st.header("Upload Documents")
    uploaded_files = st.file_uploader(
        "Choose one or more files (PDF, Word, or Image)",
        type=["pdf", "docx", "jpg", "jpeg", "png", "webp", "gif"],
        accept_multiple_files=True,
        help="Supported: PDF, Word (.docx), Images (.jpg .jpeg .png .webp .gif) — max 200 MB each",
        key=f"uploader_{st.session_state.uploader_key}",
    )

    if uploaded_files:
        current_ids  = tuple(sorted(f.file_id for f in uploaded_files))
        previous_ids = st.session_state.last_file_ids

        if current_ids != previous_ids:
            if st.session_state.resume_no_create:
                st.session_state.last_file_ids   = current_ids
                st.session_state.resume_no_create = False
            else:
                with st.spinner("📖 Reading and indexing your documents…"):
                    try:
                        file_data = [(f.name, f.read()) for f in uploaded_files]

                        st.session_state.vector_store    = None
                        st.session_state.chat_history    = []
                        st.session_state.viewing_history = False

                        session_id  = uuid.uuid4().hex[:8]
                        persist_dir = os.path.join(VECTORS_BASE, session_id)
                        embeddings  = get_embeddings()
                        wrappers    = [FileWrapper(n, d) for n, d in file_data]

                        vector_store = process_documents(
                            wrappers,
                            persist_directory=persist_dir,
                            embeddings=embeddings,
                        )
                        doc_names = [name for name, _ in file_data]

                        st.session_state.vector_store  = vector_store
                        st.session_state.last_file_ids = current_ids
                        st.session_state.doc_names     = doc_names
                        st.session_state.session_id    = session_id

                        history_mgr.create_session(session_id, doc_names)
                        history_mgr.save_session_files(session_id, file_data)

                        # st.success(f"✅ {len(doc_names)} file(s) ready — ask away!")
                    except Exception as e:
                        st.error(friendly_error(e))

    # Active document badge
    if st.session_state.vector_store is not None:
        names = ", ".join(st.session_state.doc_names)
        st.markdown(f'<div class="doc-badge">📚 {names}</div>', unsafe_allow_html=True)

    st.divider()

    # ── Clear chat button ─────────────────────────────────────────────
    if st.button("🗑️  Clear Chat History", use_container_width=True):
        if st.session_state.session_id:
            history_mgr.delete_session(st.session_state.session_id)

        st.session_state.chat_history     = []
        st.session_state.viewing_history  = False
        st.session_state.vector_store     = None
        st.session_state.session_id       = None
        st.session_state.doc_names        = []
        st.session_state.last_file_ids    = None
        st.session_state.resume_no_create = False
        st.rerun()

    st.divider()

    # ── Past sessions list ────────────────────────────────────────────
    st.header("Past Sessions")
    sessions  = history_mgr.load_sessions()
    active_id = st.session_state.session_id

    if not sessions:
        st.caption("No saved sessions yet.")
    else:
        for s in sessions[:25]:
            docs_label = ", ".join(s["documents"]) or "Unknown"
            ts         = s["timestamp"][:16].replace("T", " ")
            msg_count  = s["message_count"]
            label      = f"📝 {docs_label} ({msg_count} msgs)\n{ts}"
            btn_type   = "primary" if s["id"] == active_id else "secondary"

            if st.button(label, key=f"hist_{s['id']}",
                         use_container_width=True, type=btn_type):
                full_session = history_mgr.get_session(s["id"])
                if full_session:
                    st.session_state.chat_history   = full_session["messages"]
                    st.session_state.doc_names      = full_session["documents"]
                    st.session_state.session_id     = s["id"]
                    st.session_state.pending_resume = s["id"]
                    st.session_state.vector_store   = None
                    st.session_state.viewing_history = False
                    st.rerun()

    # ── Powered-by footer ─────────────────────────────────────────────
    st.markdown("""
    <div style="position:fixed;bottom:16px;left:12px;right:12px;
                text-align:center;font-size:0.72rem;color:#444;">
        Groq · Llama 3.3 · Gemini · ChromaDB
    </div>
    """, unsafe_allow_html=True)


# ────────────────────────────────────────────────────────────────────
# MAIN CHAT INTERFACE
# ────────────────────────────────────────────────────────────────────
st.markdown('<h1>DocuMind</h1>', unsafe_allow_html=True)
st.markdown(
    '<p class="subtitle-text">AI-powered document assistant — '
    'Upload your files in the sidebar, then ask anything. '
    'Answers are grounded strictly in your documents.</p>',
    unsafe_allow_html=True,
)

# Read-only banner
if st.session_state.viewing_history:
    st.info(
        "📜 **Past session loaded (read-only).** "
        "The original document index is not available for this session. "
        "Upload your files again in the sidebar to continue chatting."
    )

# Welcome card — shown only when no messages yet
if not st.session_state.chat_history:
    st.markdown("""
    <div class="welcome-card">
        <h3>Get started in 3 steps</h3>
        <p>Ask questions about your PDFs, Word docs, and images — instantly.</p>
        <div class="steps">
            <div class="step">
                <span class="step-icon">📄</span>
                <span class="step-label">1. Upload a file</span>
            </div>
            <div class="step">
                <span class="step-icon">✨</span>
                <span class="step-label">2. AI indexes it</span>
            </div>
            <div class="step">
                <span class="step-icon">💬</span>
                <span class="step-label">3. Ask anything</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Render chat history
for message in st.session_state.chat_history:
    _avatar = ASST_AVATAR if message["role"] == "assistant" else USER_AVATAR
    with st.chat_message(message["role"], avatar=_avatar):
        if message["role"] == "user":
            st.markdown('<div class="dm-user-hook"></div>', unsafe_allow_html=True)
        st.markdown(message["content"])

# Chat input — always enabled
user_query = st.chat_input("Ask a question about your document(s)…")

if user_query:
    st.session_state.viewing_history = False

    with st.chat_message("user", avatar=USER_AVATAR):
        st.markdown('<div class="dm-user-hook"></div>', unsafe_allow_html=True)
        st.markdown(user_query)
    st.session_state.chat_history.append({"role": "user", "content": user_query})

    with st.chat_message("assistant", avatar=ASST_AVATAR):
        message_placeholder = st.empty()
        if st.session_state.vector_store is None:
            msg = (
                "📂 **No documents loaded yet.**\n\n"
                "Please upload a PDF, Word, or image file in the left sidebar first, "
                "then ask your question."
            )
            message_placeholder.markdown(msg)
            st.session_state.chat_history.append({"role": "assistant", "content": msg})
        else:
            with st.spinner("Thinking…"):
                try:
                    # ── MMR Retriever ─────────────────────────────────
                    num_docs  = len(st.session_state.doc_names)
                    retriever = st.session_state.vector_store.as_retriever(
                        search_type="mmr",
                        search_kwargs={
                            "k":           max(8, num_docs * 6),
                            "fetch_k":     max(30, num_docs * 20),
                            "lambda_mult": 0.65,
                        },
                    )

                    # ── Rule-based query decomposition ────────────────
                    def decompose_query(q: str) -> list[str]:
                        parts = re.split(r'[?？。]|\band\b|\bAND\b', q)
                        parts = [p.strip() for p in parts if len(p.strip()) > 5]
                        return parts if parts else [q]

                    sub_queries = decompose_query(user_query)
                    all_queries = list(dict.fromkeys([user_query] + sub_queries))

                    all_docs = []
                    for q in all_queries:
                        all_docs.extend(retriever.invoke(q))
                    unique_docs = list(
                        {doc.page_content: doc for doc in all_docs}.values()
                    )

                    # ── Chain ─────────────────────────────────────────
                    document_prompt = PromptTemplate.from_template(
                        "Source: {source}\nContent: {page_content}"
                    )
                    document_chain = create_stuff_documents_chain(
                        LLM, PROMPT, document_prompt=document_prompt
                    )
                    doc_names_str = ", ".join(st.session_state.doc_names) or "Unknown"
                    answer = document_chain.invoke({
                        "input":     user_query,
                        "doc_names": doc_names_str,
                        "context":   unique_docs,
                    })

                    st.markdown(answer)
                    st.session_state.chat_history.append(
                        {"role": "assistant", "content": answer}
                    )
                except Exception as e:
                    err_msg = friendly_error(e)
                    st.error(err_msg, icon="⚠️")
                    st.session_state.chat_history.append(
                        {"role": "assistant", "content": err_msg}
                    )

    # Auto-save
    if st.session_state.session_id:
        history_mgr.save_messages(
            st.session_state.session_id,
            st.session_state.chat_history,
        )

# ── Global JS UI Engine (Layout & Theme) ──────────────────────────────
import streamlit.components.v1 as components
js_code = """
<script>
setInterval(() => {
    const parent = window.parent.document;
    if (!parent) return;

    // Detect if Light Mode is active
    let isLight = false;
    try {
        const themeStr = localStorage.getItem('stActiveTheme') || "";
        isLight = themeStr.includes('light') || window.matchMedia('(prefers-color-scheme: light)').matches;
    } catch(e) {}

    // Apply data-theme so global CSS triggers
    if (isLight) {
        parent.documentElement.setAttribute('data-theme', 'light');
    } else {
        parent.documentElement.removeAttribute('data-theme');
    }

    // ──────────────────────────────────────────
    // CHAT MESSAGE LAYOUT (Copy Button Only)
    // ──────────────────────────────────────────
    const msgs = parent.querySelectorAll('[data-testid="stChatMessage"]');
    
    msgs.forEach(msg => {
        // Find if this is a user message
        const mdContainer = msg.querySelector('[data-testid="stMarkdownContainer"]');
        if (!mdContainer) return;
        
        const hook = msg.querySelector('.dm-user-hook');
        const isUser = !!hook;

        // Message body is the 2nd generic div inside stChatMessage
        const msgBody = msg.children.length > 1 ? msg.children[1] : msg;

        // Fix missing copy wrapper
        if (!msg.querySelector('.custom-copy-wrap')) {
            const btn = parent.createElement('button');
            btn.innerHTML = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg> Copy`;
            Object.assign(btn.style, {
                background: 'transparent', border: 'none', color: '#888',
                cursor: 'pointer', fontSize: '0.75rem', display: 'flex',
                alignItems: 'center', gap: '4px', padding: '4px', 
                transition: 'color 0.2s', width: 'fit-content'
            });

            btn.onclick = () => {
                let textToCopy = '';
                msg.querySelectorAll('[data-testid="stMarkdownContainer"]').forEach(c => {
                    const clone = c.cloneNode(true);
                    if (clone.querySelector('.custom-copy-wrap')) {
                        clone.querySelector('.custom-copy-wrap').remove();
                    }
                    if (clone.querySelector('.dm-user-hook')) {
                        clone.querySelector('.dm-user-hook').remove();
                    }
                    textToCopy += clone.innerText + '\n\n';
                });
                textToCopy = textToCopy.trim().replace(/^\u200B/, '').replace(/^\u200b/, '');
                
                const ta = parent.createElement('textarea');
                ta.value = textToCopy;
                parent.body.appendChild(ta);
                ta.select();
                parent.execCommand('copy');
                parent.body.removeChild(ta);

                btn.innerHTML = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#10a37f" stroke-width="2"><polyline points="20 6 9 17 4 12"></polyline></svg> <span style="color:#10a37f">Copied</span>`;
                setTimeout(() => {
                    btn.innerHTML = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg> Copy`;
                }, 2000);
            };

            const btnWrapper = parent.createElement('div');
            btnWrapper.className = 'custom-copy-wrap';
            btnWrapper.style.display = 'flex';
            btnWrapper.style.width = '100%';
            btnWrapper.style.paddingTop = '8px';
            
            // Align copy button based on user/AI
            if (isUser) {
                btnWrapper.style.justifyContent = 'flex-end';
            } else {
                btnWrapper.style.justifyContent = 'flex-start';
            }

            btnWrapper.appendChild(btn);
            
            // Append the copy button wrapper to the message body
            msgBody.appendChild(btnWrapper);
        }
    });

}, 150);
</script>
"""
components.html(js_code, height=0, width=0)


