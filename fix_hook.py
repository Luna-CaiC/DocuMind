import re

with open('app.py', 'r') as f:
    code = f.read()

OLD1 = '''msg_str = ('\\u200B' if message["role"] == "user" else '') + message["content"]
        st.markdown(msg_str)'''

NEW1 = '''if message["role"] == "user":
            st.markdown('<div class="dm-user-hook"></div>', unsafe_allow_html=True)
        st.markdown(message["content"])'''

code = code.replace(OLD1, NEW1)

OLD2 = '''st.markdown('\\u200B' + user_query)'''
NEW2 = '''st.markdown('<div class="dm-user-hook"></div>', unsafe_allow_html=True)
        st.markdown(user_query)'''

code = code.replace(OLD2, NEW2)

# Update JS to search for .dm-user-hook instead of \u200B
JS_OLD = '''const txt = mdContainer.innerText.trim();
        const isUser = txt.startsWith('\\u200B') || txt.startsWith('\\u200b') || txt.charCodeAt(0) === 8203;'''

JS_NEW = '''const hook = msg.querySelector('.dm-user-hook');
        const isUser = !!hook;
        // Hide the hook to prevent spacing issues
        if (hook) hook.style.display = 'none';'''

code = code.replace(JS_OLD, JS_NEW)

with open('app.py', 'w') as f:
    f.write(code)
print("HOOK INJECTED!")
