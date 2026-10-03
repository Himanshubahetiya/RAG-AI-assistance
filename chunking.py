import json
from pathlib import Path
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

CHUNK_DIR = Path("data/chunks")
CHUNK_DIR.mkdir(parents=True, exist_ok=True)

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100,
    length_function=len
)

def create_chunks(json_path: str):
    json_path = Path(json_path)

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    documents = []

    for segment in data["chunks"]:
        document = Document(
            page_content=segment["text"].strip(),
            metadata={
                "title": segment["title"],
                "start": segment["start"],
                "end": segment["end"],
                "source": json_path.stem
            }
        )
        documents.append(document)

    chunks = text_splitter.split_documents(documents)

    for i, chunk in enumerate(chunks):
        chunk.metadata["chunk_id"] = i

    output_path = CHUNK_DIR / f"{json_path.stem}.json"

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(
            [
                {
                    "page_content": chunk.page_content,
                    "metadata": chunk.metadata
                }
                for chunk in chunks
            ],
            f,
            ensure_ascii=False,
            indent=2
        )

    print(f"Chunks saved to: {output_path}")
    print(f"Total segments: {len(documents)}")
    print(f"Total chunks: {len(chunks)}")

    return str(output_path)
