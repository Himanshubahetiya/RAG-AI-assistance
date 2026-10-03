import os
import json
import faiss
from pathlib import Path
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
model = SentenceTransformer("all-MiniLM-L6-v2")

INDEX_PATH = Path("data/faiss/index.faiss")
METADATA_PATH = Path("data/faiss/metadata.json")


def get_answer(query: str):
    if not INDEX_PATH.exists() or not METADATA_PATH.exists():
        return {"answer": "No video context is available."}

    # Load the latest FAISS index and metadata
    index = faiss.read_index(str(INDEX_PATH))

    with open(METADATA_PATH, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    if index.ntotal == 0 or not chunks:
        return {"answer": "No video context is available."}

    query_embedding = model.encode(
        [query],
        normalize_embeddings=True
    ).astype("float32")

    top_k = min(3, index.ntotal)
    scores, indices = index.search(query_embedding, top_k)

    context = []

    for score, idx in zip(scores[0], indices[0]):
        if idx == -1 or idx >= len(chunks):
            continue

        chunk = chunks[idx]
        metadata = chunk["metadata"]

        context.append({
            "title": metadata["title"],
            "start": metadata["start"],
            "end": metadata["end"],
            "text": chunk["page_content"]
        })

    prompt = f"""
You are an AI assistant for a video-based course.

Answer the user's question using only the provided video context.

Instructions:
- Give a clear, concise and human-friendly answer.
- Do not make up information.
- Mention the relevant video title and timestamps in your answer.
- If the answer is not available, say:
  "This topic was not found in the provided videos."

Video context:
{json.dumps(context, ensure_ascii=False, indent=2)}

User question:
{query}
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=prompt
    )

    return {
        "answer": response.text or "No answer generated."
    }
