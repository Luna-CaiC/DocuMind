import re

with open("/Users/lucky/Documents/找工/Projects/RAG-Chatbot/app.py", "r") as f:
    lines = f.readlines()

new_lines = []
in_css = False
for line in lines:
    if "st.markdown(" in line and "<style>" in lines[lines.index(line) + 1] if lines.index(line) + 1 < len(lines) else False:
        in_css = True
    elif "</style>" in line:
        in_css = False
        
    if in_css:
        # Repurpose solid dark defaults to CSS variables. 
        # This allows Streamlit's native Light/Dark toggle to dynamically switch backgrounds and text colors!
        line = line.replace("#212121", "var(--background-color)")
        line = line.replace("#171717", "var(--secondary-background-color)")
        line = line.replace("#ececec", "var(--text-color)")
        # Make very light greys / borders dynamic
        line = line.replace("rgba(255,255,255,0.06)", "rgba(128,128,128,0.2)")
        line = line.replace("rgba(255,255,255,0.12)", "rgba(128,128,128,0.2)")
        line = line.replace("rgba(255,255,255,0.08)", "rgba(128,128,128,0.25)")
        line = line.replace("rgba(255,255,255,0.02)", "rgba(128,128,128,0.05)")
        line = line.replace("rgba(255,255,255,0.10)", "rgba(128,128,128,0.15)")
        line = line.replace("rgba(255,255,255,0.07)", "rgba(128,128,128,0.1)")
        line = line.replace("#b0b0b0", "var(--text-color)")
        line = line.replace("#aaaaaa", "var(--text-color)")
        line = line.replace("#888", "var(--text-color)")
        line = line.replace("#d0e8d8", "var(--text-color)")
        line = line.replace("#d0d0d0", "var(--text-color)")
        line = line.replace("#1a1d2e", "var(--secondary-background-color)")
        line = line.replace("#1e2030", "var(--secondary-background-color)")
        
    new_lines.append(line)

with open("/Users/lucky/Documents/找工/Projects/RAG-Chatbot/app.py", "w") as f:
    f.writelines(new_lines)
