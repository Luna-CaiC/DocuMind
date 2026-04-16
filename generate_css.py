css_string = """
/* Main Background & Sidebar */
html body .stApp, html body [data-testid="stAppViewContainer"], 
html body [data-testid="stHeader"], html body [data-testid="stBottom"],
html body [data-testid="stBottom"] > div {
    background-color: #ffffff !important;
}

html body [data-testid="stSidebar"], html body [data-testid="stSidebar"] > div {
    background-color: #f7f7f8 !important; /* light grey sidebar */
}

/* Sidebar content */
html body [data-testid="stSidebar"] *,
html body [data-testid="stSidebar"] p, html body [data-testid="stSidebar"] span, html body [data-testid="stSidebar"] h1, 
html body [data-testid="stSidebar"] h2, html body [data-testid="stSidebar"] h3, html body [data-testid="stSidebar"] div {
    color: #000000 !important;
}

/* Welcome Card & Logo Text */
html body .welcome-card {
    background-color: #ffffff !important;
    border: 1px solid rgba(0,0,0,0.1) !important;
}
html body .welcome-card h3, html body .welcome-card h3 span { 
    color: #000000 !important; 
}
html body .welcome-card h3 svg, html body .welcome-card h3 svg path { 
    fill: #000000 !important; 
    stroke: #000000 !important;
}
html body .welcome-card p, html body .welcome-card .step-label { 
    color: #333333 !important; 
}

/* Uploader */
html body [data-testid="stFileUploader"] {
    background-color: #ffffff !important;
    border: 1.5px dashed rgba(0,0,0,0.2) !important;
}
html body [data-testid="stFileUploader"] *, html body [data-testid="stUploadedFile"] * {
    color: #000000 !important;
}

/* Clear Chat / General Buttons */
html body .clear-btn {
    border: 1px solid rgba(0,0,0,0.15) !important;
    background: #f7f7f8 !important;
    color: #000000 !important;
}

/* Chat Input Box */
html body [data-testid="stChatInputContainer"] {
    background-color: #f4f4f4 !important; 
    border: 1.5px solid rgba(0,0,0,0.1) !important;
}
html body [data-testid="stChatInputContainer"]:focus-within {
    border: 1.5px solid #10a37f !important;
}
html body [data-testid="stChatInputContainer"] textarea {
    color: #000000 !important;
    background-color: transparent !important;
    -webkit-text-fill-color: #000000 !important;
}
html body [data-testid="stChatInputContainer"] svg {
    stroke: #000000 !important;
    fill: #000000 !important;
}

/* All General Main Texts */
html body h1, html body h2, html body h3, html body h4, html body h5, html body h6, 
html body .main h1, html body .main h2, html body .main h3, html body [data-testid="stAppViewContainer"] h1,
html body .stMarkdown, html body .stMarkdown p, html body .stMarkdown li, html body .stMarkdown a,
html body .stMarkdown strong, html body .stMarkdown b, html body .stMarkdown em, html body .stMarkdown span,
html body div[data-testid="stMarkdownContainer"] strong, html body div[data-testid="stMarkdownContainer"] b,
html body [data-testid="stChatMessage"] strong, html body [data-testid="stChatMessage"] b, html body [data-testid="stChatMessage"] em, html body [data-testid="stChatMessage"] span,
html body [data-testid="stChatMessage"] p, html body [data-testid="stChatMessage"] div {
    color: #000000 !important;
}
html body *[data-testid="stChatMessage"] code *,
html body *[data-testid="stChatMessage"] code,
html body .stMarkdown code *,
html body .stMarkdown code {
    color: #0a694e !important;
}
html body .subtitle-text {
    color: #333333 !important;
}

/* Top Right buttons */
html body [data-testid="stHeader"] button, html body [data-testid="stToolbarActions"] button {
    color: #000000 !important;
    background-color: #ffffff !important;
    border: 1px solid rgba(0,0,0,0.1) !important;
}
html body [data-testid="stHeader"] button:hover, html body [data-testid="stToolbarActions"] button:hover {
    background-color: #f0f0f0 !important;
}

/* History Items */
html body [class*="st-emotion-cache"] .history-item, html body .history-item {
    border: 1px solid rgba(0,0,0,0.1) !important;
    background: #ffffff !important;
    color: #000000 !important;
}
html body [class*="st-emotion-cache"] .history-item *, html body .history-item * {
    color: #000000 !important;
}

/* ACTIVE History Item */
html body .history-item.active-session {
    background: #10a37f !important;
    border: 1px solid #10a37f !important;
}
html body .history-item.active-session, html body .history-item.active-session * {
    color: #ffffff !important;
}
"""

with open('app.py', 'r') as f:
    app_code = f.read()

import re

# We rebuild the styleTag.innerHTML from app.py
start_idx = app_code.find('styleTag.innerHTML = `')
if start_idx == -1:
    print("Cannot find styleTag.innerHTML")
    exit(1)

end_idx = app_code.find('`;', start_idx)

# Replace it
new_code = app_code[:start_idx + len('styleTag.innerHTML = `')] + css_string + app_code[end_idx:]

with open('app.py', 'w') as f:
    f.write(new_code)
print("Updated CSS inside app.py!")
