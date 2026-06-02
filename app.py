import streamlit as st
import yt_dlp
import tempfile
import os
import re
from pathlib import Path

st.set_page_config(
    page_title="YouTube Downloader",
    page_icon="🎬",
    layout="centered"
)

st.markdown("""
<style>
.stApp {
    background-color: #7ca982;
}

h1, h2, h3, p, label {
    color: white;
}

.stButton > button,
.stDownloadButton > button {
    background-color: #f7f3d7;
    color: #2d4739;
    border-radius: 10px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

st.title("🎬 YouTube Downloader")


# -------------------------
# 파일명 정리
# -------------------------
def clean_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "", name)


# -------------------------
# yt-dlp 안정 설정
# -------------------------
BASE_OPTS = {
    "quiet": True,
    "noplaylist": True,

    "http_headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.youtube.com/",
    },

    "extractor_args": {
        "youtube": {
            "player_client": ["android", "web", "ios"],
        }
    },

    "retries": 10,
    "fragment_retries": 10,
    "extractor_retries": 5,
    "force_ipv4": True,
    "socket_timeout": 20,
    "concurrent_fragment_downloads": 1,
}


# -------------------------
# URL 입력
# -------------------------
url = st.text_input("유튜브 링크")

info = None

if url:
    try:
        with yt_dlp.YoutubeDL(BASE_OPTS) as ydl:
            info = ydl.extract_info(url, download=False)

        st.success("영상 정보 로드 성공")

        title = info.get("title", "")
        uploader = info.get("uploader", "")
        thumbnail = info.get("thumbnail")

        if thumbnail:
            st.image(thumbnail, use_container_width=True)

        st.write(f"**제목:** {title}")
        st.write(f"**채널:** {uploader}")

    except Exception as e:
        st.error("영상 정보를 가져오지 못했습니다")
        st.code(str(e))


# -------------------------
# 다운로드 UI
# -------------------------
if info:

    filename = st.text_input(
        "파일명",
        value=clean_filename(info.get("title", "video"))
    )

    file_type = st.radio(
        "형식 선택",
        ["MP4", "MP3"],
        horizontal=True
    )

    quality = st.selectbox(
        "화질 선택 (MP4 전용)",
        ["best", "1080p", "720p", "480p", "360p", "240p", "144p"]
    )

    if st.button("다운로드 시작"):

        temp_dir = tempfile.mkdtemp()
        output = os.path.join(temp_dir, f"{filename}.%(ext)s")

        progress = st.progress(0)
        status = st.empty()

        def hook(d):
            if d["status"] == "downloading":
                if "total_bytes" in d and d["total_bytes"]:
                    pct = d["downloaded_bytes"] / d["total_bytes"]
                    progress.progress(min(pct, 1.0))
                    status.info(f"{pct*100:.1f}% 다운로드 중")

            if d["status"] == "finished":
                progress.progress(1.0)
                status.success("다운로드 완료")

        try:

            # ---------------- MP4 ----------------
            if file_type == "MP4":

                if quality == "best":
                    fmt = "bestvideo+bestaudio/best"
                else:
                    height = quality.replace("p", "")
                    fmt = f"bestvideo[height<={height}]+bestaudio/best"

                ydl_opts = {
                    **BASE_OPTS,
                    "format": fmt,
                    "outtmpl": output,
                    "merge_output_format": "mp4",
                    "progress_hooks": [hook],
                }
                ext = "mp4"

            # ---------------- MP3 ----------------
            else:
                ydl_opts = {
                    **BASE_OPTS,
                    "format": "bestaudio/best",
                    "outtmpl": output,
                    "progress_hooks": [hook],
                    "postprocessors": [{
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "192"
                    }]
                }
                ext = "mp3"

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            files = list(Path(temp_dir).glob(f"*.{ext}"))

            if files:
                with open(files[0], "rb") as f:
                    st.download_button(
                        label=f"{ext.upper()} 다운로드",
                        data=f,
                        file_name=f"{filename}.{ext}",
                        mime="video/mp4" if ext == "mp4" else "audio/mpeg"
                    )

        except Exception as e:
            st.error("다운로드 실패")
            st.code(str(e))
