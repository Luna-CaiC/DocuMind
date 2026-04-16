import streamlit as st
import streamlit.components.v1 as components

st.markdown("Test message.")
components.html("""
<script>
function doCopy() {
    try {
        navigator.clipboard.writeText("Test copy").then(() => {
            document.getElementById('btn').innerText = "Copied!";
        });
    } catch(e) {
        document.getElementById('btn').innerText = "V2 Fallback";
        // Fallback for older browsers
        const el = document.createElement('textarea');
        el.value = "Test copy";
        document.body.appendChild(el);
        el.select();
        document.execCommand('copy');
        document.body.removeChild(el);
    }
}
window.parent.console.log("iframe script loaded");
</script>
<button id="btn" onclick="doCopy()">Copy</button>
""", height=50)
