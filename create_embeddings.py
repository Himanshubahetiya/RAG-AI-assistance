import json
from pathlib import Path
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

FAISS_DIR = Path("data/faiss")
FAISS_DIR.mkdir(parents=True, exist_ok=True)

INDEX_PATH = FAISS_DIR / "index.faiss"
METADATA_PATH = FAISS_DIR / "metadata.json"

model = SentenceTransformer("all-MiniLM-L6-v2")

def create_embeddings(chunks_path: str):
    with open(chunks_path, "r", encoding="utf-8") as f:
        new_chunks = json.load(f)

    if not new_chunks:
        return "No chunks found"

    texts = [chunk["page_content"] for chunk in new_chunks]

    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=True
    ).astype("float32")

    if INDEX_PATH.exists() and METADATA_PATH.exists():
        index = faiss.read_index(str(INDEX_PATH))

        with open(METADATA_PATH, "r", encoding="utf-8") as f:
            metadata = json.load(f)

        if index.d != embeddings.shape[1]:
            raise ValueError("Embedding dimension mismatch")
    else:
        index = faiss.IndexFlatIP(embeddings.shape[1])
        metadata = []

    index.add(embeddings)
    metadata.extend(new_chunks)

    faiss.write_index(index, str(INDEX_PATH))

    with open(METADATA_PATH, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    print(f"Total embeddings stored: {index.ntotal}")
    print("FAISS index and metadata saved successfully.")

    return index.ntotal
