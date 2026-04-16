import re

with open('app.py', 'r') as f:
    content = f.read()

# Locate the JS script block inside app.py
start_idx = content.find('const isLight = ')
end_idx = content.find('</script>', start_idx)

# We want to replace the msgs.forEach loop exactly with the working one.
# First, let's just replace the whole msgs.forEach block inside the JS.
js_start = content.find('msgs.forEach(msg => {', start_idx)
js_end = content.find('}, 100);', js_start)

if js_start == -1 or js_end == -1:
    js_end = content.find('}, 500);', js_start)

# The correct working code block:
correct_js = """msgs.forEach(msg => {
        const container = msg.querySelector('[data-testid="stMarkdownContainer"]');
        if (!container) return;

        // Check ZWSP marker
        const txt = container.innerText.trim();
        const isUser = txt.startsWith('\\u200B') || txt.startsWith('​');

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
                el.style.textAlign = 'left';
            });
        } else {
            // Restore AI message left-alignment and colors inside the flow
            container.style.textAlign = 'left';
            container.style.background = 'transparent';
            if (isLight) {
                container.style.setProperty('color', '#000000', 'important');
            } else {
                container.style.removeProperty('color');
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
                 text = text.trim().replace(/^\\\\u200B/, '').replace(/^​/, '');
                 
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
"""

if js_start != -1 and js_end != -1:
    new_content = content[:js_start] + correct_js + content[js_end:]
    with open('app.py', 'w') as f:
        f.write(new_content)
    print("Fixed JS logic")
else:
    print("Could not find blocks")
