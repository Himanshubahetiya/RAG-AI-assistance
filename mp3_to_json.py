import json
from pathlib import Path
import whisper

model = whisper.load_model("large-v2")

JSON_DIR = Path("data/jsons")
JSON_DIR.mkdir(parents=True, exist_ok=True)


def transcribe_audio(audio_path: str):
    audio_path = Path(audio_path)
    title = audio_path.stem

    result = model.transcribe(
        str(audio_path),
        language="hi",
        task="translate",
        word_timestamps=False
    )

    chunks = [
        {
            "title": title,
            "start": segment["start"],
            "end": segment["end"],
            "text": segment["text"]
        }
        for segment in result["segments"]
    ]

    output = {
        "chunks": chunks,
        "text": result["text"]
    }

    json_path = JSON_DIR / f"{title}.json"

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    return str(json_path)