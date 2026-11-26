import os, tempfile
from pathlib import Path
import streamlit as st
from src.config import DATA_DIR, TOP_K
from src.guardrails import validate_question, validate_pdf
from src.ingestion import load_pdfs, clean_documents, split_documents
from src.vectorstore import build_vectorstore
from src.retrieval import retrieve_documents
from src.rag import answer_question

st.set_page_config(page_title="CampusGPT", page_icon="🎓", layout="wide")

st.markdown("""<style>
.block-container{max-width:1150px;padding-top:1.4rem}.cg-card{background:white;border:1px solid #e8eaf2;border-radius:16px;padding:18px;height:100%}.muted{color:#697386}.source{border-left:3px solid #5B5FEF;padding:8px 12px;background:#f8f8ff;border-radius:8px}.hero{padding:26px 4px 10px}.hero h1{font-size:2.25rem;margin-bottom:.2rem}.hero b{color:#5B5FEF}
</style>""", unsafe_allow_html=True)

def get_api_key():
    try: return st.secrets.get("GROQ_API_KEY", os.getenv("GROQ_API_KEY",""))
    except Exception: return os.getenv("GROQ_API_KEY","")

def process_paths(paths):
    docs=clean_documents(load_pdfs(paths)); chunks=split_documents(docs)
    return build_vectorstore(chunks), len(docs), len(chunks)

if "messages" not in st.session_state: st.session_state.messages=[]
if "vectorstore" not in st.session_state:
    default=list(DATA_DIR.glob("*.pdf"))
    st.session_state.vectorstore, st.session_state.pages, st.session_state.chunks = process_paths(default) if default else (None,0,0)

with st.sidebar:
    st.markdown("## 🎓 CampusGPT")
    st.caption("AI assistant for university information")
    if st.button("＋ New Chat", use_container_width=True): st.session_state.messages=[]; st.rerun()
    st.markdown("### Knowledge Base")
    uploads=st.file_uploader("Upload campus PDFs", type=["pdf"], accept_multiple_files=True)
    if st.button("Process Documents", use_container_width=True, disabled=not uploads):
        paths=[]
        with tempfile.TemporaryDirectory() as td:
            for f in uploads:
                ok,msg=validate_pdf(f)
                if not ok: st.error(msg); continue
                p=Path(td)/f.name; p.write_bytes(f.getvalue()); paths.append(p)
            if paths:
                with st.spinner("Loading → cleaning → chunking → embedding → indexing..."):
                    st.session_state.vectorstore, st.session_state.pages, st.session_state.chunks=process_paths(paths)
                st.success(f"Ready: {st.session_state.pages} pages, {st.session_state.chunks} chunks")
    st.divider()
    st.caption(f"Default knowledge base: {st.session_state.pages} pages · {st.session_state.chunks} chunks")
    st.caption("Project 1 · AI School of India")

if not st.session_state.messages:
    st.markdown('<div class="hero"><h1>👋 Hi! I’m <b>CampusGPT</b></h1><p class="muted">Ask questions and get grounded answers from your campus documents.</p></div>', unsafe_allow_html=True)
    c1,c2,c3,c4=st.columns(4)
    cards=[("📘 Academics","Ask about regulations, exams and curriculum."),("💼 Placements","Explore eligibility, policies and procedures."),("🏫 Campus Info","Find student services and facilities."),("🔎 Sources","Verify answers against source documents.")]
    for col,(h,t) in zip([c1,c2,c3,c4],cards):
        with col: st.markdown(f'<div class="cg-card"><b>{h}</b><p class="muted">{t}</p></div>', unsafe_allow_html=True)
    st.write("")
    st.caption("Try: “What is the minimum attendance requirement?” · “What are the placement eligibility rules?”")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("sources"):
            with st.expander("📚 Sources & retrieved context"):
                seen=set()
                for s in msg["sources"]:
                    key=(s['source'],s['page'])
                    if key in seen: continue
                    seen.add(key)
                    st.markdown(f"**{s['source']} · Page {s['page']}**  · relevance {s['score']:.2f}")
                    st.caption(s['text'][:800] + ("…" if len(s['text'])>800 else ""))

question=st.chat_input("Ask anything about your campus documents...")
if question:
    ok,msg=validate_question(question)
    if not ok: st.warning(msg); st.stop()
    if st.session_state.vectorstore is None: st.error("Please process at least one PDF first."); st.stop()
    api_key=get_api_key()
    if not api_key: st.error("Add GROQ_API_KEY to .env locally or Streamlit Secrets when deployed."); st.stop()
    st.session_state.messages.append({"role":"user","content":question})
    with st.chat_message("user"): st.markdown(question)
    with st.chat_message("assistant"):
        with st.spinner("Searching campus knowledge..."):
            retrieved=retrieve_documents(st.session_state.vectorstore, question, k=TOP_K)
            result=answer_question(question, retrieved, st.session_state.messages[:-1], api_key)
            answer,sources=result if isinstance(result,tuple) else (result,[])
        st.markdown(answer)
        with st.expander("📚 Sources & retrieved context"):
            seen=set()
            for s in sources:
                key=(s['source'],s['page'])
                if key in seen: continue
                seen.add(key)
                st.markdown(f"**{s['source']} · Page {s['page']}** · relevance {s['score']:.2f}")
                st.caption(s['text'][:800] + ("…" if len(s['text'])>800 else ""))
    st.session_state.messages.append({"role":"assistant","content":answer,"sources":sources})
