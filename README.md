# DocuMind: Your AI-Powered Document Assistant 🤖

**DocuMind** is a high-speed, multi-modal Retrieval-Augmented Generation (RAG) system. Simply put, you upload your documents (PDFs, Word files, or even images), and you can chat with them. It reads the files, understands the context, and answers your questions by grounding itself *strictly* in your uploaded content—no hallucinations.

---

## ⚙️ System Architecture & RAG Pipeline

DocuMind isn't just a basic wrapper around an AI API. It's built on a robust, step-by-step RAG architecture designed to handle messy real-world data efficiently and accurately. Here is how the engine works under the hood:

### Step 1: Multi-Modal Ingestion (Smart Document Parsing)
Real-world documents are rarely perfectly formatted. DocuMind intelligently routes your files during upload:
*   **Standard Text**: For a normal Word doc (`.docx`) or text PDF, it extracts the text blazingly fast using tools like `PyMuPDF` and `python-docx`. (It even dives into underlying XML to rescue text trapped in weird Word shapes).
*   **Scans & Images (Vision AI Fallback)**: If the system detects a PDF page is mostly images (or if you upload a raw screenshot), it automatically switches gears. It sends the images to **Google Gemini 2.0 Flash Vision**, instructing the visual AI to "look" at the image and extract the text or summarize charts into usable data. 

### Step 2: Intelligent Chunking & Anti-Hallucination
Before sending huge documents to the AI, we must chop them into smaller, digestible pieces ("chunks") using LangChain's `RecursiveCharacterTextSplitter`.
*   **The Sourcing Trick**: A common problem in RAG is the AI forgetting where a piece of text came from. DocuMind solves this by mathematically stamping the *original filename* directly into every single chunk (e.g., `[Source Document: annual_report.pdf]`). When the AI retrieves this chunk to answer your question, it knows exactly which file the information came from, completely preventing it from mixing up facts across different uploads.

### Step 3: Local Vectorization & Storage (The "Memory")
Turning your text into searchable vectors is done completely *locally* on your machine using HuggingFace's `all-MiniLM-L6-v2` embedding model. 
*   **Cost & Privacy**: This means zero API costs just to build your searchable database, plus your raw document data stays local during the embedding phase.
*   **Persistent Sessions via ChromaDB**: Closing the browser doesn't ruin your work. DocuMind manages separate local `ChromaDB` vector databases for every chat session. It saves your history so you can drop off and resume a complex research session days later without ever waiting for files to re-process.

### Step 4: High-Speed Inference (The "Brain")
When you actually ask a question, DocuMind retrieves the most relevant chunks from ChromaDB and sends them to the LLM.
*   **Groq LPU Processing**: The reading and answering is handled by **Groq running Llama-3.3**. Because Groq uses specialized Linear Processing Units (LPUs) instead of traditional GPUs, it types out highly intelligent answers almost instantaneously. This hybrid approach (local embeddings + highly optimized cloud inference) gives you the best of both speed and cost-efficiency.



---

## 🛠️ Technical Stack at a Glance

- **RAG Orchestration**: [LangChain](https://www.langchain.com/)
- **The "Brain" (LLM)**: [Groq](https://groq.com/) (Llama-3.3) for extreme speed, [Google Gemini](https://ai.google.dev/) for Vision/OCR
- **The "Memory" (Vector DB)**: [ChromaDB](https://www.trychroma.com/)
- **Text-to-Vector Math**: [Sentence-Transformers](https://sbert.net/) (Local embedding via [HuggingFace](https://huggingface.co/))
- **File Extractors**: [PyMuPDF](https://pymupdf.readthedocs.io/), [python-docx](https://python-docx.readthedocs.io/), [Pillow](https://python-pillow.org/)
- **UI & Framework**: [Streamlit](https://streamlit.io/)

---

## 🚀 Getting Started

### 1. Prerequisites
Ensure you have **Python 3.10+** installed.

### 2. Installation
Clone the repository and set up a virtual environment (recommended):
```bash
git clone https://github.com/Luna-CaiC/DocuMind.git
cd DocuMind

# 1. Create and activate a Virtual Environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration
Create a `.env` file in the root directory and add your API keys (replace the placeholders with your actual keys):
```env
GROQ_API_KEY=<PASTE_YOUR_ACTUAL_GROQ_KEY_HERE>
GOOGLE_API_KEY=<PASTE_YOUR_ACTUAL_GOOGLE_KEY_HERE>
GEMINI_MODEL=gemini-2.0-flash
GROQ_MODEL=llama-3.3-70b-versatile
```

### 4. Running the App
Start the Streamlit server (using `python -m` ensures strict environment binding and prevents caching issues):
```bash
python -m streamlit run app.py
```

---

## 📜 License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
