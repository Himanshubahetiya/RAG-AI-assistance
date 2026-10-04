from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel, Field
from pathlib import Path
import shutil
from retrieval import get_answer
from video_to_mp3 import convert_to_mp3
from mp3_to_json import transcribe_audio
from chunking import create_chunks
from create_embeddings import create_embeddings

app = FastAPI()

class QuestionRequest(BaseModel):
    question: str = Field(min_length=1)

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "data" / "videos"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@app.get("/")
def home():
    return {"message": "RAG API is running"}


@app.post("/upload-video")
def upload_video(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(400, "Filename is missing")

    if Path(file.filename).suffix.lower() not in [".mp4", ".mov", ".mkv", ".avi"]:
        raise HTTPException(400, "Invalid video format")

    path = UPLOAD_DIR / Path(file.filename).name

    try:
        with path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Video processing pipeline
        audio_path = convert_to_mp3(str(path))
        json_path = transcribe_audio(audio_path)
        chunks_path = create_chunks(json_path)
        total_embeddings = create_embeddings(chunks_path)

        return {
            "message": "Video uploaded and processed successfully",
            "filename": path.name,
            "total_embeddings": total_embeddings
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        file.file.close()


@app.post("/ask")
def ask_question(request: QuestionRequest):
    try:
        return get_answer(request.question.strip())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))