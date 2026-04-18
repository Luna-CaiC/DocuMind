# DocuMind: High-Performance RAG Document Assistant

**DocuMind** is an advanced Retrieval-Augmented Generation (RAG) system engineered to provide low-latency, highly accurate conversational interfaces over multi-modal documents. It parses text, handles complex formats (like Word tables), and seamlessly falls back to Vision AI for image-based PDFs and standalone images, grounding every response strictly in the ingested corpus.

---

## ⚙️ System Architecture & RAG Pipeline

DocuMind's architecture is designed for robust data ingestion and high-speed retrieval:

### 1. Multi-Modal Document Ingestion Setup
The ingestion pipeline (`src/ingest.py`) dynamically routes documents based on format, handling edge cases that standard parsers miss:
*   **Text PDFs**: Processed via `PyMuPDF` for high-fidelity text extraction.
*   **Image-Heavy PDFs & Scans**: The system detects low-character density pages and automatically invokes **Google Gemini 2.0 Flash Vision OCR**. It chunks the document into image batches and processes them via the Vision API to extract text and describe diagrams.
*   **Word Documents (.docx)**: Utilizes `python-docx` to extract structured paragraphs and tables. It implements a raw XML `<w:t>` parsing fallback mechanism to rescue text trapped in unsupported shapes or customized text boxes.
*   **Standalone Images**: Processes formats like PNG and JPEG directly through the Vision LLM to convert visual data into searchable text documents.

### 2. Chunking & Local Vectorization
*   **Text Splitter**: Uses LangChain's `RecursiveCharacterTextSplitter` (chunk size: 1000, overlap: 200) to maintain semantic integrity.
*   **Context Injection**: Explicitly injects the source document filename into *every single chunk* `[Source Document: filename]`. This ensures the LLM always has strict traceability back to the source file, regardless of how deep the chunk was in the original document.
*   **Local Embeddings**: Deploys HuggingFace's `all-MiniLM-L6-v2` embedding model locally. This eliminates embedding API costs and network latency during the vectorization phase.

### 3. Vector Storage & Session Management
*   **Database**: Utilizes **ChromaDB** for fast, local vector storage. 
*   **Persistence**: The `ChatHistoryManager` (`src/history.py`) maintains isolated vector stores and raw file caches for each conversation ID. Users can drop off and resume sessions days later without re-uploading or re-embedding documents.

### 4. High-Speed Inference (LLM)
*   **Generation**: Retrieval chains are powered by **Groq** using the `llama-3.3-70b-versatile` model. By leveraging Groq's LPU inference engine, DocuMind generates comprehensive, context-aware answers almost instantaneously once the context window is populated by ChromaDB.

*Note: The frontend is built with Streamlit, featuring a custom-engineered CSS architecture that provides a seamless, native-feeling Light/Dark/System theme switcher.*

---

## 🛠️ Technical Stack

- **Frontend**: Streamlit
- **Orchestration**: LangChain
- **Inference**: Groq & Google Gemini
- **Vector Database**: ChromaDB
- **Embeddings**: Sentence-Transformers (Local `all-MiniLM-L6-v2`)
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

## 📜 License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
