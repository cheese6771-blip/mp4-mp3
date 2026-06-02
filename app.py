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


def clean_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "", name)


url = st.text_input("유튜브 링크")

info = None

# -----------------------------
# yt-dlp 공통 옵션 (403 완화 핵심)
# -----------------------------
YDL_COMMON_OPTS = {
    "quiet": True,
    "noplaylist": True,
    "http_headers": {
        "User-Agent": "Mozilla/5.0"
    },
    "extractor_args": {
        "youtube": {
            "player_client": ["android", "web"]
        }
    }
}

# -----------------------------
# 영상 정보 가져오기
# -----------------------------
if url:
    try:
        with yt_dlp.YoutubeDL(YDL_COMMON_OPTS) as ydl:
            info = ydl.extract_info(url, download=False)

        title = info.get("title", "")
        thumbnail = info.get("thumbnail")
        uploader = info.get("uploader", "")

        st.success("영상 정보 로딩 완료")

        if thumbnail:
            st.image(thumbnail, use_container_width=True)

        st.write(f"**제목:** {title}")
        st.write(f"**채널:** {uploader}")

    except Exception as e:
        st.error("영상 정보를 가져오지 못했습니다")
        st.code(str(e))

# -----------------------------
# 다운로드 UI
# -----------------------------
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

    if st.button("다운로드 시작"):

        temp_dir = tempfile.mkdtemp()
        output_path = os.path.join(temp_dir, f"{filename}.%(ext)s")

        progress = st.progress(0)
        status = st.empty()

        # -----------------------------
        # 진행률
        # -----------------------------
        def hook(d):
            if d["status"] == "downloading":
                if "total_bytes" in d:
                    pct = d["downloaded_bytes"] / d["total_bytes"]
                    progress.progress(min(pct, 1.0))
                    status.info(f"{pct*100:.1f}% 다운로드 중")

            if d["status"] == "finished":
                progress.progress(1.0)
                status.success("다운로드 완료")

        # -----------------------------
        # MP4 / MP3 옵션
        # -----------------------------
        if file_type == "MP4":
            ydl_opts = {
                **YDL_COMMON_OPTS,
                "format": "bestvideo+bestaudio/best",
                "outtmpl": output_path,
                "merge_output_format": "mp4",
                "progress_hooks": [hook],
            }
        else:
            ydl_opts = {
                **YDL_COMMON_OPTS,
                "format": "bestaudio/best",
                "outtmpl": output_path,
                "progress_hooks": [hook],
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "192"
                    }
                ]
            }

        # -----------------------------
        # 다운로드 실행
        # -----------------------------
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            ext = "mp4" if file_type == "MP4" else "mp3"

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
            st.error("다운로드 실패 (403 포함 가능)")
            st.code(str(e))
