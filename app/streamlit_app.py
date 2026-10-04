
import streamlit as st
import requests
from pathlib import Path

# ---------------- CONFIG ----------------
API_URL = "http://127.0.0.1:8000"

# streamlit_app.py is inside the app folder
BASE_DIR = Path(__file__).resolve().parent
VIDEO_DIR = BASE_DIR / "data" / "videos"
VIDEO_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = [".mp4", ".mov", ".mkv", ".avi"]

st.set_page_config(
    page_title="RAG Video Assistant",
    page_icon="🎥",
    layout="wide"
)

# ---------------- GET SAVED VIDEOS ----------------
def get_videos():
    return sorted(
        [
            file.name
            for file in VIDEO_DIR.iterdir()
            if file.is_file()
            and file.suffix.lower() in ALLOWED_EXTENSIONS
        ],
        key=str.lower
    )

# ---------------- SESSION STATE ----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# Scan the folder every time the app runs
videos = get_videos()

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.title("🎥 RAG Video Assistant")
    st.caption("Upload videos and ask questions about their content.")

    st.divider()

    # ---------------- UPLOAD VIDEO ----------------
    st.subheader("📤 Upload Video")

    uploaded_file = st.file_uploader(
        "Choose a video",
        type=["mp4", "mov", "mkv", "avi"]
    )

    if uploaded_file is not None:
        if st.button("Upload & Process", use_container_width=True):
            try:
                with st.spinner("Uploading and processing video..."):
                    response = requests.post(
                        f"{API_URL}/upload-video",
                        files={
                            "file": (
                                uploaded_file.name,
                                uploaded_file.getvalue(),
                                uploaded_file.type
                            )
                        },
                        timeout=3600
                    )

                if response.status_code == 200:
                    st.success("Video uploaded and processed successfully!")
                    st.rerun()
                else:
                    try:
                        error_detail = response.json().get(
                            "detail", response.text
                        )
                    except ValueError:
                        error_detail = response.text

                    st.error(f"Upload failed: {error_detail}")

            except requests.exceptions.ConnectionError:
                st.error("Backend server is not running.")
            except requests.exceptions.Timeout:
                st.error("Processing timed out. Please check the backend.")
            except Exception as e:
                st.error(f"Error: {e}")

    st.divider()

    # ---------------- PROCESSED VIDEOS ----------------
    st.subheader("📁 Processed Videos")

    if videos:
        for index, video in enumerate(videos, start=1):
            st.markdown(f"**{index}. 🎬 {video}**")
    else:
        st.caption("No videos found in the videos folder.")

    st.divider()

    # ---------------- CLEAR CHAT ----------------
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ---------------- MAIN DASHBOARD ----------------
st.title("🎥 RAG Video Assistant")
st.write("Ask questions based on your uploaded videos.")

# ---------------- METRICS ----------------
col1, col2 = st.columns(2)

with col1:
    st.metric("Videos Processed", len(videos))

with col2:
    questions_asked = sum(
        1
        for message in st.session_state.messages
        if message["role"] == "user"
    )
    st.metric("Questions Asked", questions_asked)

st.divider()

# ---------------- CHAT HISTORY ----------------
st.subheader("💬 Chat")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        if message["role"] == "assistant" and message.get("sources"):
            with st.expander("📌 Sources"):
                for source in message["sources"]:
                    video_number = source.get("video_number", "")
                    video_id = source.get("video_id", "")
                    start = source.get("start", 0)
                    end = source.get("end", 0)
                    source_text = source.get("text", "")

                    video_label = (
                        f"Video {video_number}"
                        if video_number
                        else video_id or "Video"
                    )

                    st.markdown(
                        f"**{video_label}** ({start}s - {end}s)"
                    )

                    if source_text:
                        st.caption(source_text)

# ---------------- ASK QUESTION ----------------
question = st.chat_input("Ask a question about your videos...")

if question:
    if not videos:
        st.warning("Please upload and process a video first.")
    else:
        st.session_state.messages.append({
            "role": "user",
            "content": question
        })

        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            try:
                with st.spinner("Finding the answer..."):
                    response = requests.post(
                        f"{API_URL}/ask",
                        json={"question": question},
                        timeout=300
                    )

                if response.status_code == 200:
                    result = response.json()

                    answer = result.get(
                        "answer",
                        "No answer was returned by the backend."
                    )
                    sources = result.get("sources", [])

                    st.markdown(answer)

                    if sources:
                        with st.expander("📌 Sources"):
                            for source in sources:
                                video_number = source.get("video_number", "")
                                video_id = source.get("video_id", "")
                                start = source.get("start", 0)
                                end = source.get("end", 0)
                                source_text = source.get("text", "")

                                video_label = (
                                    f"Video {video_number}"
                                    if video_number
                                    else video_id or "Video"
                                )

                                st.markdown(
                                    f"**{video_label}** ({start}s - {end}s)"
                                )

                                if source_text:
                                    st.caption(source_text)

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "sources": sources
                    })

                else:
                    try:
                        error_detail = response.json().get(
                            "detail", response.text
                        )
                    except ValueError:
                        error_detail = response.text

                    error_message = f"Request failed: {error_detail}"
                    st.error(error_message)

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_message,
                        "sources": []
                    })

            except requests.exceptions.ConnectionError:
                error_message = "Backend server is not running."
                st.error(error_message)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_message,
                    "sources": []
                })

            except requests.exceptions.Timeout:
                error_message = "The request timed out. Please try again."
                st.error(error_message)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_message,
                    "sources": []
                })

            except Exception as e:
                error_message = f"Error: {e}"
                st.error(error_message)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_message,
                    "sources": []
                })

        st.rerun()
