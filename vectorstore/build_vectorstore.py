import os
import argparse
from typing import List, Tuple, Dict
from PyPDF2 import PdfReader
from vectorstore.vector_store import VectorStore

PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))

def read_pdf(path: str) -> List[Tuple[int, str]]:
    pages = []
    try:
        reader = PdfReader(path)
        for i, page in enumerate(reader.pages):
            try:
                text = page.extract_text() or ""
                pages.append((i + 1, text))
            except Exception:
                pages.append((i + 1, ""))
    except Exception as e:
        print(f"Failed to read PDF {path}: {e}")
    return pages

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    text = (text or "").strip()
    if not text:
        return []
    chunks = []
    start = 0
    n = len(text)
    while start < n:
        end = min(start + chunk_size, n)
        chunk = text[start:end]
        chunks.append(chunk)
        if end == n:
            break
        start = max(0, end - overlap)
    return chunks

def collect_texts_from_pdfs(pdf_dir: str, chunk_size: int, overlap: int) -> Tuple[List[str], List[Dict]]:
    texts, metas = [], []
    pdf_files = [f for f in os.listdir(pdf_dir) if f.lower().endswith(".pdf")]
    for fname in pdf_files:
        fpath = os.path.join(pdf_dir, fname)
        pages = read_pdf(fpath)
        for page_num, page_text in pages:
            for chunk_idx, chunk in enumerate(chunk_text(page_text, chunk_size, overlap)):
                texts.append(chunk)
                metas.append({"source": f"{fname}#page{page_num}#chunk{chunk_idx+1}"})
    return texts, metas

def main():
    parser = argparse.ArgumentParser(description="Build vector store from PDFs using Ollama embeddings.")
    parser.add_argument("--pdf-dir", default=os.path.join(PROJECT_ROOT, "pdfs"), help="Folder containing PDFs")
    parser.add_argument("--out", default=os.path.join(PROJECT_ROOT, "vectorstore", "vector_store.json"), help="Output vector store path")
    parser.add_argument("--chunk-size", type=int, default=1000, help="Characters per chunk")
    parser.add_argument("--overlap", type=int, default=200, help="Characters overlap between chunks")
    args = parser.parse_args()

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    os.makedirs(args.pdf_dir, exist_ok=True)

    if not os.listdir(args.pdf_dir):
        print(f"No PDFs found in {args.pdf_dir}. Place your PDFs there and re-run.")
        return

    print(f"Building vector store from PDFs in: {args.pdf_dir}")
    texts, metas = collect_texts_from_pdfs(args.pdf_dir, args.chunk_size, args.overlap)
    print(f"Total chunks to embed: {len(texts)}")

    store = VectorStore(store_path=args.out)  # reads OLLAMA_URL and OLLAMA_EMBED_MODEL from env if set
    # Embedding and saving
    store.add_texts(texts, metas)
    print(f"Vector store saved to: {args.out}")
    print("Done.")

if __name__ == "__main__":
    main()
