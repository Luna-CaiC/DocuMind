import re

with open('app.py', 'r') as f:
    code = f.read()

js_start = code.find('# ── Global JS UI Engine (Layout & Theme)')
if js_start == -1:
    js_start = code.find('# ── Global JS UI Engine')

js_end = code.find('components.html', js_start)

NEW_JS = '''# ── Global JS UI Engine (Layout & Theme) ──────────────────────────────
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
    // CHAT MESSAGE LAYOUT (ChatGPT Style)
    // ──────────────────────────────────────────
    const msgs = parent.querySelectorAll('[data-testid="stChatMessage"]');
    
    msgs.forEach(msg => {
        // Find if this is a user message
        const mdContainer = msg.querySelector('[data-testid="stMarkdownContainer"]');
        if (!mdContainer) return;
        
        const txt = mdContainer.innerText.trim();
        const isUser = txt.startsWith('\\u200B') || txt.startsWith('\\u200b') || txt.charCodeAt(0) === 8203;

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
                    textToCopy += clone.innerText + '\\n\\n';
                });
                textToCopy = textToCopy.trim().replace(/^\\u200B/, '').replace(/^\\u200b/, '');
                
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
            btnWrapper.appendChild(btn);
            
            // Append the copy button wrapper to the message body
            msgBody.appendChild(btnWrapper);
        }

        if (isUser) {
            // -- USER MESSAGE: Align RIGHT --
            msg.style.setProperty('flex-direction', 'row-reverse', 'important');
            msgBody.style.setProperty('display', 'flex', 'important');
            msgBody.style.setProperty('flex-direction', 'column', 'important');
            msgBody.style.setProperty('align-items', 'flex-end', 'important');
            msgBody.style.setProperty('width', '100%', 'important');
            
            // The copy button should be on the right side
            const copyWrap = msg.querySelector('.custom-copy-wrap');
            if (copyWrap) copyWrap.style.setProperty('justify-content', 'flex-end', 'important');

            // Style the text bubble
            const allMd = msg.querySelectorAll('[data-testid="stMarkdownContainer"]');
            allMd.forEach(md => {
                md.style.setProperty('padding', '12px 18px', 'important');
                md.style.setProperty('border-radius', '18px', 'important');
                md.style.setProperty('display', 'inline-block', 'important');
                md.style.setProperty('text-align', 'left', 'important');
                
                if (isLight) {
                    md.style.setProperty('background-color', '#d1f0d1', 'important');
                    md.style.setProperty('color', '#000000', 'important');
                    md.querySelectorAll('*').forEach(e => e.style.setProperty('color', '#000000', 'important'));
                } else {
                    md.style.setProperty('background-color', '#204030', 'important');
                    md.style.setProperty('color', '#ffffff', 'important');
                    md.querySelectorAll('*').forEach(e => e.style.setProperty('color', '#ffffff', 'important'));
                }
            });
        } else {
            // -- AI MESSAGE: Align LEFT --
            msg.style.setProperty('flex-direction', 'row', 'important');
            msgBody.style.setProperty('align-items', 'flex-start', 'important');
            
            // The copy button should be on the left side
            const copyWrap = msg.querySelector('.custom-copy-wrap');
            if (copyWrap) copyWrap.style.setProperty('justify-content', 'flex-start', 'important');
            
            // Remove user specific bubbling
            const allMd = msg.querySelectorAll('[data-testid="stMarkdownContainer"]');
            allMd.forEach(md => {
                md.style.removeProperty('padding');
                md.style.removeProperty('border-radius');
                md.style.removeProperty('display');
                md.style.removeProperty('background-color');
                if (isLight) {
                    md.style.setProperty('color', '#000000', 'important');
                    md.querySelectorAll('p, li, span').forEach(e => e.style.setProperty('color', '#000000', 'important'));
                } else {
                    md.style.removeProperty('color');
                    md.querySelectorAll('p, li, span').forEach(e => e.style.removeProperty('color'));
                }
            });
        }
    });

}, 150);
</script>
"""
'''

if js_start != -1 and js_end != -1:
    new_code = code[:js_start] + NEW_JS + code[js_end:]
    with open('app.py', 'w') as f:
        f.write(new_code)
    print("SUCCESS JS INJECT")
else:
    print("FAIL TO FIND JS BLOCK")
