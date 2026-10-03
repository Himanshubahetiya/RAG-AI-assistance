import subprocess
from pathlib import Path

AUDIO_DIR = Path("data/audios")
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

def convert_to_mp3(video_path: str) -> str:
    video_path = Path(video_path)
    output_path = AUDIO_DIR / f"{video_path.stem}.mp3"

    subprocess.run([
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-vn",
        str(output_path)
    ], check=True, capture_output=True)

    return str(output_path)