import streamlit as st
import streamlit.components.v1 as components

st.chat_message("user").markdown("Hello world")

js = """
<script>
setTimeout(() => {
    const parent = window.parent.document;
    const msgs = parent.querySelectorAll('[data-testid="stChatMessage"]');
    msgs.forEach(msg => {
        if (!msg.querySelector('.custom-copy-btn')) {
            const btn = parent.createElement('button');
            btn.innerText = 'Copy';
            btn.className = 'custom-copy-btn';
            btn.onclick = () => {
                 const text = msg.querySelector('[data-testid="stMarkdownContainer"]').innerText;
                 // use fallback because iframe might not have clipboard perm
                 const el = parent.createElement('textarea');
                 el.value = text;
                 parent.body.appendChild(el);
                 el.select();
                 parent.execCommand('copy');
                 parent.body.removeChild(el);
                 btn.innerText = 'Copied!';
            };
            msg.appendChild(btn);
        }
    });
}, 1000);
</script>
"""
components.html(js, height=0, width=0)
