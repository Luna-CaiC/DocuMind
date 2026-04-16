import re

with open('app.py', 'r') as f:
    app_code = f.read()

# Find the start of js_code = """
start_idx = app_code.find('js_code = """')
if start_idx == -1:
    print("Cannot find js_code = ")
    exit(1)

# Find the end of components.html
end_idx = app_code.find('components.html(js_code, height=0, width=0)', start_idx)
if end_idx == -1:
    print("Cannot find components.html")
    exit(1)

# Include the components.html line in the replacement so we can safely overwrite up to the end
end_idx += len('components.html(js_code, height=0, width=0)')

perfect_js = '''js_code = """
<script>
setInterval(() => {
    const parent = window.parent.document;
    if (!parent) return;

    // 1. Theme Detection
    const themeStr = localStorage.getItem('stActiveTheme');
    const isLight = themeStr ? themeStr.includes('light') : window.matchMedia('(prefers-color-scheme: light)').matches;

    // 2. Inject specific mode overrides
    let styleTag = parent.getElementById('documind-light-theme');
    if (isLight) {
        if (!styleTag) {
            styleTag = parent.createElement('style');
            styleTag.id = 'documind-light-theme';
            styleTag.innerHTML = `
                /* Main Background & Sidebar */
                html body .stApp, html body [data-testid="stAppViewContainer"], 
                html body [data-testid="stHeader"], html body [data-testid="stSidebar"],
                html body [data-testid="stSidebar"] > div {
                    background-color: #ffffff !important;
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
                    background-color: #fdfdfd !important;
                    border: 1.5px dashed rgba(0,0,0,0.2) !important;
                }
                html body [data-testid="stFileUploader"] *, html body [data-testid="stUploadedFile"] * {
                    color: #000000 !important;
                }

                /* Alerts (Success/Info boxes) */
                html body div[data-testid="stAlert"], html body [data-testid="stAlert"][data-type="success"],
                html body [data-testid="stAlert"][data-type="info"], html body [data-testid="stAlert"][data-type="warning"],
                html body [data-testid="stAlert"][data-type="error"], html body .stAlert {
                    background: #ffffff !important;
                    background-color: #ffffff !important;
                    color: #000000 !important;
                    border: 1px solid rgba(0,0,0,0.15) !important;
                }
                html body [data-testid="stAlert"] *, html body .stAlert * {
                    color: #000000 !important;
                }

                /* Chat Input Box */
                html body [data-testid="stChatInputContainer"] {
                    background-color: #fafafa !important; /* light grey fill */
                    border: 1.5px solid rgba(16,163,127,0.35) !important; /* pale green border */
                }
                html body [data-testid="stChatInputContainer"]:focus-within {
                    border: 1.5px solid rgba(16,163,127,0.8) !important;
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

                /* All General Main Texts (Including Main DocuMind Title) */
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
                
                /* Bottom spacing */
                html body [data-testid="stBottom"], html body [data-testid="stBottom"] > div {
                    background-color: #ffffff !important;
                }

                /* Sidebar inactive history items */
                html body [class*="st-emotion-cache"] .history-item, html body .history-item {
                    border: 1px solid rgba(0,0,0,0.1) !important;
                    background: #ffffff !important;
                    color: #000000 !important;
                }
                html body .history-item.active-session {
                    background: rgba(16,163,127,0.15) !important;
                    border: 1px solid #10a37f !important;
                }
            `;
            parent.head.appendChild(styleTag);
        }
    } else {
        if (styleTag) styleTag.remove();
    }

    // 3. Layout and Bubble Styling per Message
    const msgs = parent.querySelectorAll('[data-testid="stChatMessage"]');
    
    // Explicit inline override for the main DocuMind Title just to absolutely guarantee
    parent.querySelectorAll('h1').forEach(node => {
        if (node.innerText.trim() === 'DocuMind') {
            if (isLight) {
                node.style.setProperty('color', '#000000', 'important');
            } else {
                if (node.style.color === 'rgb(0, 0, 0)') {
                    node.style.removeProperty('color');
                }
            }
        }
    });

    msgs.forEach(msg => {
        const container = msg.querySelector('[data-testid="stMarkdownContainer"]');
        if (!container) return;

        // Check ZWSP marker
        const txt = container.innerText.trim();
        const isUser = txt.startsWith('\\u200B') || txt.startsWith('\u200B');

        if (isUser) {
            msg.style.flexDirection = 'row-reverse';
            container.style.padding = '12px 18px';
            container.style.borderRadius = '18px';
            container.style.display = 'inline-block';
            container.style.maxWidth = 'fit-content';
            container.style.textAlign = 'right';

            if (isLight) {
                container.style.setProperty('background-color', '#d1f0d1', 'important');
                container.style.setProperty('color', '#000000', 'important');
                container.classList.add('documind-user-bubble');
            } else {
                container.style.setProperty('background-color', '#204030', 'important');
                container.style.setProperty('color', '#ececec', 'important');
                container.classList.remove('documind-user-bubble');
            }

            // Force the bubble to the right side next to avatar
            let p = container.parentElement;
            while(p && p !== msg) {
                p.style.display = 'flex';
                p.style.flexDirection = 'column';
                p.style.alignItems = 'flex-end';
                p.style.width = '100%';
                p = p.parentElement;
            }
            
            // Fix code blocks inside user message if any
            container.querySelectorAll('pre, code').forEach(el => {
                el.style.setProperty('text-align', 'left', 'important');
            });
        } else {
            // Restore AI message left-alignment and colors inside the flow
            container.style.textAlign = 'left';
            container.style.background = 'transparent';
            
            if (isLight) {
                container.style.setProperty('color', '#000000', 'important');
                container.querySelectorAll('p, li, span, strong, b').forEach(el => {
                    el.style.setProperty('color', '#000000', 'important');
                });
            } else {
                if (container.style.getPropertyValue('color') === 'rgb(0, 0, 0)') {
                    container.style.removeProperty('color');
                }
                container.querySelectorAll('p, li, span, strong, b').forEach(el => {
                    el.style.removeProperty('color');
                });
            }
        }

        // 4. Inject Copy Button
        if (!msg.querySelector('.custom-msg-copy-btn')) {
            const btn = parent.createElement('button');
            btn.innerHTML = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg> Copy`;
            btn.className = 'custom-msg-copy-btn';
            
            Object.assign(btn.style, {
                background: 'transparent', border: 'none', color: '#888',
                cursor: 'pointer', fontSize: '0.75rem', display: 'flex',
                alignItems: 'center', gap: '4px', marginTop: '6px',
                padding: '4px', transition: 'color 0.2s', width: 'fit-content'
            });

            btn.onclick = () => {
                 let text = '';
                 msg.querySelectorAll('[data-testid="stMarkdownContainer"]').forEach(c => {
                     const clone = c.cloneNode(true);
                     const cb = clone.querySelector('.custom-copy-wrap');
                     if(cb) cb.remove();
                     text += clone.innerText + '\\n\\n';
                 });
                 text = text.trim().replace(/^\\u200B/, '').replace(/^\u200B/, '');
                 
                 const el = parent.createElement('textarea');
                 el.value = text;
                 parent.body.appendChild(el);
                 el.select();
                 parent.execCommand('copy');
                 parent.body.removeChild(el);

                 btn.innerHTML = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#10a37f" stroke-width="2"><polyline points="20 6 9 17 4 12"></polyline></svg> <span style="color:#10a37f">Copied</span>`;
                 setTimeout(() => {
                     btn.innerHTML = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg> Copy`;
                 }, 2000);
            };

            const btnWrapper = parent.createElement('div');
            btnWrapper.className = 'custom-copy-wrap';
            btnWrapper.style.display = 'flex';
            btnWrapper.style.justifyContent = isUser ? 'flex-end' : 'flex-start';
            btnWrapper.style.width = '100%';
            btnWrapper.style.paddingTop = '8px';
            
            btnWrapper.appendChild(btn);
            
            if (isUser) {
                container.appendChild(btnWrapper);
            } else {
                if (msg.children.length > 1) {
                    msg.children[1].appendChild(btnWrapper);
                } else {
                    msg.appendChild(btnWrapper);
                }
            }
        }
    });
}, 100);
</script>
"""
components.html(js_code, height=0, width=0)'''

with open('app.py', 'w') as f:
    f.write(app_code[:start_idx] + perfect_js + app_code[end_idx:])

print("Successfully replaced Javascript block using python write.")
