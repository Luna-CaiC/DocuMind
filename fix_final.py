with open('app.py', 'r') as f:
    code = f.read()

OLD_JS_START = '# ── Global JS UI Engine (Layout & Theme)'
NEW_JS = '''# ── Global JS UI Engine (Layout & Theme) ──────────────────────────────
import streamlit.components.v1 as components
js_code = """
<script>
setInterval(() => {
    const parent = window.parent.document;
    if (!parent) return;

    const themeStr = localStorage.getItem('stActiveTheme') || "";
    const isLight = themeStr.includes('light') || window.matchMedia('(prefers-color-scheme: light)').matches;

    // Trigger Streamlit's global light theme CSS rules
    if (isLight) {
        parent.documentElement.setAttribute('data-theme', 'light');
    } else {
        parent.documentElement.removeAttribute('data-theme');
    }

    // Process Chat Messages Layout 
    const msgs = parent.querySelectorAll('[data-testid="stChatMessage"]');

    msgs.forEach(msg => {
        const container = msg.querySelector('[data-testid="stMarkdownContainer"]');
        if (!container) return;

        const txt = container.innerText.trim();
        const isUser = txt.startsWith('\\u200B') || txt.startsWith('\\u200b') || txt.charCodeAt(0) === 8203;

        // Message Layout
        if (isUser) {
            msg.style.flexDirection = 'row-reverse';
            
            // Align bubble
            const contentArea = msg.querySelector('[data-testid="stChatMessageContent"]');
            if (contentArea) {
                contentArea.style.alignItems = 'flex-end';
                contentArea.style.width = '100%';
            }
            
            // Render user bubble text
            const textContainers = msg.querySelectorAll('[data-testid="stMarkdownContainer"]');
            const bubble = textContainers[textContainers.length - 1]; // Content is usually last
            
            if (bubble && bubble.classList) {
                if (!bubble.classList.contains('styled-user-bubble')) {
                    bubble.style.padding = '12px 18px';
                    bubble.style.borderRadius = '18px';
                    bubble.style.display = 'inline-block';
                    bubble.style.maxWidth = '75%';
                    bubble.style.textAlign = 'left';
                    bubble.classList.add('styled-user-bubble');
                }
                
                if (isLight) {
                    bubble.style.setProperty('background-color', '#d1f0d1', 'important');
                    bubble.style.setProperty('color', '#000000', 'important');
                    bubble.querySelectorAll('*').forEach(el => el.style.setProperty('color', '#000000', 'important'));
                } else {
                    bubble.style.setProperty('background-color', '#204030', 'important');
                    bubble.style.setProperty('color', '#ffffff', 'important');
                    bubble.querySelectorAll('*').forEach(el => el.style.setProperty('color', '#ffffff', 'important'));
                }
            }
        } else {
            // Restore AI message
            msg.style.flexDirection = 'row';
            const contentArea = msg.querySelector('[data-testid="stChatMessageContent"]');
            if (contentArea) contentArea.style.alignItems = 'flex-start';
        }

        // Copy Button Injection
        if (!msg.querySelector('.custom-msg-copy-btn')) {
            const btn = parent.createElement('button');
            btn.innerHTML = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg> Copy`;
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
                text = text.trim().replace(/^\\u200B/, '').replace(/^\\u200b/, '');
                
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
            // Align right if user message, left if AI message!
            btnWrapper.style.justifyContent = isUser ? 'flex-end' : 'flex-start';
            btnWrapper.style.width = '100%';
            btnWrapper.style.paddingTop = '8px';
            
            btnWrapper.appendChild(btn);
            
            const lastTextContainer = msg.querySelectorAll('[data-testid="stMarkdownContainer"]');
            if (lastTextContainer.length > 0) {
                 lastTextContainer[lastTextContainer.length - 1].appendChild(btnWrapper);
            }
        }
    });

}, 200);
</script>
"""
components.html(js_code, height=0, width=0)
'''

idx_start = code.find(OLD_JS_START)
idx_end = code.find('components.html(js_code, height=0, width=0)', idx_start)

if idx_start != -1 and idx_end != -1:
    end_replace = idx_end + len('components.html(js_code, height=0, width=0)')
    new_code = code[:idx_start] + NEW_JS + code[end_replace:]
    with open('app.py', 'w') as f:
        f.write(new_code)
    print("PATCHED!")
else:
    print("FAIL TO FIND BLOCKS")
