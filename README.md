# CampusGPT - AI-Powered University Knowledge Assistant

CampusGPT is AI School of India's Project 1 for students/freshers. It demonstrates an end-to-end RAG application using a simple, student-friendly stack.

## Finalized stack
- LLM: Groq `openai/gpt-oss-20b`
- Embeddings: Sentence Transformers `all-MiniLM-L6-v2`
- Vector index: FAISS CPU
- Framework: LangChain
- Loader: PyPDFLoader
- Chunking: RecursiveCharacterTextSplitter (600 chars, 100 overlap)
- Retrieval: semantic Top-K, K=4
- Citations: source/page metadata
- Conversation: Streamlit session state
- UI: Streamlit
- Deployment: GitHub + Streamlit Community Cloud

## Architecture
PDFs -> PyPDFLoader -> Cleaning -> Recursive Chunking -> MiniLM -> FAISS
Question -> MiniLM -> FAISS Top-K -> RAG Prompt -> GPT-OSS-20B via Groq -> Answer + metadata citations

## 1. Prerequisites
Install Python 3.11 (recommended), Git, and create a Groq API key.

## 2. Create virtual environment
### Windows PowerShell
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```
### Windows CMD
```bat
python -m venv .venv
.venv\Scripts\activate.bat
```
### macOS/Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 3. Install dependencies
```bash
pip install -r requirements.txt
```
The first embedding run downloads the MiniLM model from Hugging Face.

## 4. Configure Groq
Copy `.env.example` to `.env` and add your key:
```env
GROQ_API_KEY=gsk_your_key_here
GROQ_MODEL=openai/gpt-oss-20b
```
Never commit `.env`.

## 5. Run CampusGPT
```bash
streamlit run app.py
```
The bundled fictional university PDFs are indexed automatically. Ask: `What is the minimum attendance requirement?`

## 6. Upload your own PDFs
Use **Upload campus PDFs** in the sidebar, then click **Process Documents**. Uploaded documents replace the in-memory knowledge base for that Streamlit session.

## 7. Run basic retrieval evaluation
```bash
python evaluate_retrieval.py
```
This calculates Hit@4 against the included golden dataset. Expand it to 30-50 questions for the classroom exercise.

## 8. Deploy to Streamlit Community Cloud
1. Create a GitHub repository and push this project (do not push `.env`).
2. In Streamlit Community Cloud choose the repository, branch, and `app.py`.
3. In app Settings -> Secrets add:
```toml
GROQ_API_KEY = "gsk_your_key_here"
GROQ_MODEL = "openai/gpt-oss-20b"
```
4. Deploy and test the live URL.

## Teaching extensions (not baseline)
- BM25 keyword retrieval
- Hybrid dense + BM25 retrieval
- Sentence Transformers CrossEncoder reranking
- RAGAS-based generation evaluation
These should be introduced after students understand the baseline RAG pipeline.

## Important note
The included `Silver Oak University` is entirely fictional and exists only as a teaching dataset. Groq API availability/pricing/limits can change; check the provider before classroom use.
