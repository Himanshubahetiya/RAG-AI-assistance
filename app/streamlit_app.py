
import streamlit as st
import requests

# ---------------- Configuration ----------------
API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="RAG Video Assistant",
    page_icon="🎥",
    layout="wide"
)

# ---------------- Custom Styling ----------------
st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    .main-title {
        font-size: 32px;
        font-weight: 700;
        color: #60a5fa;
    }
    .subtitle {
        color: #9ca3af;
        font-size: 16px;
    }
    .status {
        background: #172554;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #2563eb;
    }
    div.stButton > button {
        background-color: #2563eb;
        color: white;
        border-radius: 8px;
        border: none;
    }
</style>
""", unsafe_allow_html=True)

# ---------------- Session State ----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "uploaded_videos" not in st.session_state:
    st.session_state.uploaded_videos = []

# ---------------- Sidebar ----------------
with st.sidebar:
    st.title("🎥 RAG Assistant")
    st.caption("AI-powered video question answering")

    st.divider()

    st.subheader("📤 Upload Video")

    uploaded_file = st.file_uploader(
        "Choose a video",
        type=["mp4", "mov", "mkv", "avi"]
    )

    if uploaded_file:
        st.video(uploaded_file)

        if st.button("🚀 Process Video", use_container_width=True):
            try:
                with st.spinner("Processing video... This may take a while."):
                    response = requests.post(
                        f"{API_URL}/upload-video",
                        files={
                            "file": (
                                uploaded_file.name,
                                uploaded_file.getvalue(),
                                uploaded_file.type
                            )
                        },
                        timeout=None
                    )

                if response.ok:
                    result = response.json()

                    st.session_state.uploaded_videos.append({
                        "filename": result.get("filename", uploaded_file.name),
                        "embeddings": result.get("total_embeddings", 0)
                    })

                    st.success("Video processed successfully!")
                    st.json(result)
                else:
                    st.error(f"Upload failed: {response.text}")

            except requests.exceptions.ConnectionError:
                st.error("Cannot connect to FastAPI. Please start the backend.")
            except requests.exceptions.RequestException as e:
                st.error(f"Request error: {e}")

    st.divider()

    st.subheader("📁 Processed Videos")

    if st.session_state.uploaded_videos:
        for video in st.session_state.uploaded_videos:
            st.markdown(f"**🎬 {video['filename']}**")
            st.caption(f"Embeddings: {video['embeddings']}")
    else:
        st.caption("No videos processed yet.")

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ---------------- Main UI ----------------
st.markdown(
    '<div class="main-title">🎬 RAG Video Assistant</div>',
    unsafe_allow_html=True
)
st.markdown(
    '<div class="subtitle">Upload videos, ask questions, and get answers '
    'with relevant timestamps.</div>',
    unsafe_allow_html=True
)

st.divider()

# ---------------- Dashboard ----------------
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Videos Processed", len(st.session_state.uploaded_videos))

with col2:
    total_embeddings = sum(
        v["embeddings"] for v in st.session_state.uploaded_videos
    )
    st.metric("Total Embeddings", total_embeddings)

with col3:
    st.metric("Questions Asked", len(st.session_state.messages) // 2)

st.divider()

# ---------------- Chat History ----------------
st.subheader("💬 Ask Your Videos")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if isinstance(message["content"], str):
            st.markdown(message["content"])
        else:
            st.json(message["content"])

# ---------------- Question Input ----------------
question = st.chat_input("Ask anything about your uploaded videos...")

if question:
    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        try:
            with st.spinner("Searching video context..."):
                response = requests.post(
                    f"{API_URL}/ask",
                    json={"question": question},
                    timeout=180
                )

            if response.ok:
                result = response.json()

                # Display answer
                answer = result.get("answer", result)

                if isinstance(answer, str):
                    st.markdown(answer)
                else:
                    st.json(answer)

                # Display sources and timestamps, if available
                sources = result.get("sources", [])

                if sources:
                    with st.expander("📌 Sources & Timestamps"):
                        for i, source in enumerate(sources, 1):
                            st.markdown(f"**Source {i}**")
                            st.write(
                                f"Video: {source.get('video_number', 'N/A')}"
                            )
                            st.write(
                                f"Timestamp: {source.get('start', 'N/A')}s - "
                                f"{source.get('end', 'N/A')}s"
                            )
                            if source.get("text"):
                                st.write(source["text"])
                            st.divider()

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer if isinstance(answer, str) else result
                })

            else:
                error = f"API Error ({response.status_code}): {response.text}"
                st.error(error)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error
                })

        except requests.exceptions.ConnectionError:
            error = "Cannot connect to FastAPI. Please check the backend."
            st.error(error)
            st.session_state.messages.append({
                "role": "assistant",
                "content": error
            })

        except requests.exceptions.RequestException as e:
            error = f"Request failed: {e}"
            st.error(error)
            st.session_state.messages.append({
                "role": "assistant",
                "content": error
            })