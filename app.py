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

st.title("🎬 YouTube Downloader (Cookie Support)")

st.markdown("""
<style>
.stApp { background-color: #7ca982; }
h1, h2, h3, p, label { color: white; }
.stButton > button, .stDownloadButton > button {
    background-color: #f7f3d7;
    color: #2d4739;
    border-radius: 10px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)


# -------------------------
# 파일명 정리
# -------------------------
def clean_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "", name)


# -------------------------
# yt-dlp 기본 안정 설정
# -------------------------
BASE_OPTS = {
    "quiet": True,
    "noplaylist": True,
    "force_ipv4": True,
    "socket_timeout": 20,

    "http_headers": {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://www.youtube.com/"
    }
}


# -------------------------
# 입력
# -------------------------
url = st.text_input("유튜브 링크")

cookie_file = st.file_uploader(
    "쿠키 파일 업로드 (cookies.txt)",
    type=["txt", "cookie"]
)

info = None

if url:
    try:
        with yt_dlp.YoutubeDL(BASE_OPTS) as ydl:
            info = ydl.extract_info(url, download=False)

        st.success("영상 정보 로드 성공")
        st.image(info.get("thumbnail"), use_container_width=True)

        st.write("**제목:**", info.get("title"))
        st.write("**채널:**", info.get("uploader"))

    except Exception as e:
        st.error("정보 로드 실패")
        st.code(str(e))


# -------------------------
# 다운로드 UI
# -------------------------
if info:

    filename = st.text_input(
        "파일명",
        value=clean_filename(info.get("title", "video"))
    )

    file_type = st.radio("형식", ["MP4", "MP3"], horizontal=True)

    quality = st.selectbox(
        "화질",
        ["best", "1080p", "720p", "480p", "360p"]
    )


    if st.button("다운로드 시작"):

        temp_dir = tempfile.mkdtemp()
        output = os.path.join(temp_dir, f"{filename}.%(ext)s")

        progress = st.progress(0)
        status = st.empty()

        def hook(d):
            if d["status"] == "downloading":
                if d.get("total_bytes"):
                    pct = d["downloaded_bytes"] / d["total_bytes"]
                    progress.progress(min(pct, 1.0))
                    status.info(f"{pct*100:.1f}% 다운로드 중")

            if d["status"] == "finished":
                status.success("다운로드 완료")

        try:

            # ---------------- 쿠키 처리 ----------------
            cookie_path = None
            if cookie_file:
                cookie_path = os.path.join(temp_dir, "cookies.txt")
                with open(cookie_path, "wb") as f:
                    f.write(cookie_file.read())

            # ---------------- MP4 ----------------
            if file_type == "MP4":

                if quality == "best":
                    fmt = "bestvideo+bestaudio/best"
                else:
                    h = quality.replace("p", "")
                    fmt = f"bestvideo[height<={h}]+bestaudio/best"

                ydl_opts = {
                    **BASE_OPTS,
                    "format": fmt,
                    "outtmpl": output,
                    "merge_output_format": "mp4",
                    "progress_hooks": [hook],
                }

                if cookie_path:
                    ydl_opts["cookiefile"] = cookie_path

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

                if cookie_path:
                    ydl_opts["cookiefile"] = cookie_path

                ext = "mp3"


            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            files = list(Path(temp_dir).glob(f"*.{ext}"))

            if files:
                with open(files[0], "rb") as f:
                    st.download_button(
                        f"{ext.upper()} 다운로드",
                        f,
                        file_name=f"{filename}.{ext}",
                        mime="video/mp4" if ext == "mp4" else "audio/mpeg"
                    )

        except Exception as e:
            st.error("다운로드 실패")
            st.code(str(e))
