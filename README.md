# DocuMind — AI-Powered Document Assistant 🤖

**DocuMind** is a professional RAG (Retrieval-Augmented Generation) application that allows you to chat with your documents. Whether it's a standard PDF, a complex Word file, or even an image-based document, DocuMind uses high-performance LLMs and Vision models to provide accurate, citation-backed answers.

---

## 🌟 Key Features

### 📄 Multi-Format Support
- **Text PDFs**: High-speed parsing for standard text-based documents.
- **Image-Based PDFs**: Automatically runs Gemini Vision OCR for scanned files or slides.
- **Word Documents (.docx)**: Comprehensive extraction including tables and text boxes.
- **Standalone Images**: Upload JPG, PNG, or WEBP files to chat with visual data, charts, or diagrams.

### 🌓 Professional UI & Themes
- **Modern Interface**: A clean, GPT-style layout designed for productivity.
- **Adaptive Themes**: Fully supports **Light**, **Dark**, and **System** modes natively. The UI adjusts every element (sidebar, inputs, and avatars) to match your preference perfectly.
- **Responsive Design**: Works across different screen sizes with a sidebar-integrated document management system.

### 🧠 Advanced RAG Engine
- **Fast Responses**: Powered by **Groq (Llama 3.3)** for near-instant inference.
- **Vision OCR**: Powered by **Google Gemini 2.0 Flash** for high-quality visual context.
- **Local Embeddings**: Uses HuggingFace `all-MiniLM-L6-v2` locally to ensure data efficiency and stability.
- **Citation Tracking**: Every response is grounded in your source documents, with filenames labeled at the chunk level.

### 💾 Persistent Sessions
- **Session History**: Automatically saves your chat sessions and metadata locally.
- **Session Resumption**: Resume any past conversation; DocuMind retains the context and message history.

---

## 🛠️ Technical Stack

- **Frontend**: [Streamlit](https://streamlit.io/)
- **Orchestration**: [LangChain](https://www.langchain.com/)
- **Inference**: [Groq](https://groq.com/) & [Google Gemini](https://ai.google.dev/)
- **Vector Database**: [ChromaDB](https://www.trychroma.com/)
- **Embeddings**: Sentence-Transformers (Local)
- **Document Parsing**: PyMuPDF (fitz), python-docx, Pillow

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

## 📸 Interface Showcase

| Dark Mode | Light Mode |
| :---: | :---: |
| ![Dark Mode](file:///Users/lucky/.gemini/antigravity/brain/e64e1258-349d-4774-9e54-ccd4bc0ce432/media__1776384326755.png) | ![Light Mode](file:///Users/lucky/.gemini/antigravity/brain/e64e1258-349d-4774-9e54-ccd4bc0ce432/media__1776384334105.png) |

---

## 📁 Project Structure
- `app.py`: Main entry point and UI logic.
- `src/ingest.py`: Document processing, OCR, and vectorization pipeline.
- `src/history.py`: Local session and chat history management.
- `data/`: Local storage for vector indexes, session files, and history JSON.
- `.streamlit/config.toml`: Custom theme colors and app configuration.

---

## 📜 License
This project is licensed under the MIT License.
