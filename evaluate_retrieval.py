from pathlib import Path
from src.ingestion import load_pdfs, clean_documents, split_documents
from src.vectorstore import build_vectorstore
from src.evaluation import hit_at_k
from src.config import DATA_DIR

docs=clean_documents(load_pdfs(list(DATA_DIR.glob("*.pdf"))))
store=build_vectorstore(split_documents(docs))
results,score=hit_at_k(store, Path("evals/golden_dataset.csv"), k=4)
print(results.to_string(index=False))
print(f"\nHit@4: {score:.2%}")
