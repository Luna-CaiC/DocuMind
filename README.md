# DocuMind: Your AI-Powered Document Assistant 🤖

**DocuMind** is a smart, high-speed Retrieval-Augmented Generation (RAG) system. Simply put, you upload your documents (PDFs, Word files, or even images), and you can chat with them. It reads the files, understands the context, and answers your questions by grounding itself *strictly* in your uploaded content—no hallucinations.

---

## ✨ Core Advantages & How It Works

DocuMind isn't just a basic wrapper around an AI model. It's built to handle messy, real-world data efficiently and accurately. Here is what makes the engine tick:

### 1. It Can "Read" Almost Anything (Smart Document Parsing)
Real-world documents are messy. DocuMind routes your files intelligently:
*   **Standard Text**: If you upload a normal Word doc (`.docx`) or text PDF, it extracts the text blazingly fast using tools like `PyMuPDF` and `python-docx`. (It even dives into underlying XML to rescue text trapped in weird Word shapes).
*   **Scans & Images (Fallback to Vision AI)**: If it detects a PDF page is mostly images (or if you just upload a screenshot), it automatically switches gears. It sends the image to **Google Gemini 2.0 Flash Vision**, instructing the visual AI to "look" at the image and extract the text or summarize the charts into usable data. 

### 2. High Accuracy & Zero Hallucinations (Strict Chunking)
Before sending huge documents to the AI, the system chops them into smaller, digestible pieces ("chunks"). 
*   **The Technical Trick**: DocuMind mathematically stamps the *original filename* directly into every single chunk (e.g., `[Source Document: report.pdf]`). Because of this, when the AI searches its database to answer your question, it knows exactly which file the information came from, completely preventing it from mixing up facts across different uploads.

### 3. Lightning Fast & Cost-Effective (Hybrid Architecture)
DocuMind splits the heavy lifting to give you instant answers without breaking the bank:
*   **Local Embeddings**: Turning your text into searchable vectors is done completely *locally* on your machine using HuggingFace's `all-MiniLM-L6-v2`. This means zero API costs just to build your searchable database, plus better privacy.
*   **Groq LPU Processing**: When you actually ask a question, the reading and answering is handled by **Groq running Llama-3.3**. Groq uses specialized hardware instead of traditional GPUs, which allows it to type out highly intelligent answers almost instantaneously.

### 4. Pick Up Where You Left Off (Persistent Sessions)
Closing the browser doesn't ruin your work. DocuMind manages separate local `ChromaDB` vector databases for every chat session. It saves your history so you can drop off and resume a complex research session days later without ever waiting for files to re-process.

*(Bonus: It features a professional, native-feeling UI built in Streamlit that seamlessly adapts to your system's Light or Dark mode.)*

---

## 🛠️ Technical Stack at a Glance

- **UI & Framework**: Streamlit (with adaptive custom theming)
- **RAG Orchestration**: LangChain
- **The "Brain" (LLM)**: Groq (Llama-3.3) for extreme speed, Google Gemini for Vision/OCR
- **The "Memory" (Vector DB)**: ChromaDB
- **Text-to-Vector Math**: Sentence-Transformers (Local embedding)
- **File Extractors**: PyMuPDF, python-docx, Pillow

---

## 🚀 Getting Started

### 1. Prerequisites
Ensure you have **Python 3.10+** installed.

### 2. Installation
Clone the repository and install the dependencies:
```bash
git clone https://github.com/Luna-CaiC/DocuMind.git
cd DocuMind
pip install -r requirements.txt
```

### 3. Environment Configuration
Create a `.env` file in the root directory and add your API keys:
```env
GROQ_API_KEY=your_groq_api_key
GOOGLE_API_KEY=your_google_api_key
GEMINI_MODEL=gemini-2.0-flash
GROQ_MODEL=llama-3.3-70b-versatile
```

### 4. Running the App
Start the Streamlit server:
```bash
streamlit run app.py
```

---

## 📜 License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
