import streamlit as st
import yt_dlp
import tempfile
import os
import re
from pathlib import Path

st.set_page_config(
    page_title="다운받쟈",
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
# 유틸
# -------------------------
def clean_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "", name)


# -------------------------
# yt-dlp 공통 설정
# -------------------------
BASE_OPTS = {
    "quiet": True,
    "noplaylist": True,
    curl -i -k -H "X-Remote-IP: 10.10.10.10" https://example.com HTTP/1.1 200 OK This is secret page
    "http_headers": {
        "User-Agent": "Mozilla/5.0"
    },
    "extractor_args": {
        "youtube": {
            "player_client": ["android", "web"]
        }
    }
}


# -------------------------
# 영상 정보 가져오기
# -------------------------
url = st.text_input("유튜브 링크")

info = None

if url:
    try:
        with yt_dlp.YoutubeDL(BASE_OPTS) as ydl:
            info = ydl.extract_info(url, download=False)

        st.success("영상 정보 로드 완료")

        title = info.get("title", "")
        uploader = info.get("uploader", "")
        thumbnail = info.get("thumbnail")

        if thumbnail:
            st.image(thumbnail, use_container_width=True)

        st.write(f"**제목:** {title}")
        st.write(f"**채널:** {uploader}")

    except Exception as e:
        st.error("영상 정보 가져오기 실패")
        st.code(str(e))


# -------------------------
# 다운로드 로직 (fallback)
# -------------------------
def run_download(ydl_opts, url):
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        return ydl.download([url])


def download_with_fallback(url, file_type, filename, temp_dir, progress_hook):

    output = os.path.join(temp_dir, f"{filename}.%(ext)s")

    # =========================
    # 1차: bestvideo+bestaudio
    # =========================
    try:
        if file_type == "MP4":
            opts = {
                **BASE_OPTS,
                "format": "bestvideo+bestaudio/best",
                "outtmpl": output,
                "merge_output_format": "mp4",
                "progress_hooks": [progress_hook],
            }
        else:
            opts = {
                **BASE_OPTS,
                "format": "bestaudio/best",
                "outtmpl": output,
                "progress_hooks": [progress_hook],
                "postprocessors": [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192"
                }]
            }

        run_download(opts, url)
        return True, temp_dir

    except Exception:
        pass

    # =========================
    # 2차: best fallback
    # =========================
    try:
        if file_type == "MP4":
            opts = {
                **BASE_OPTS,
                "format": "best",
                "outtmpl": output,
                "progress_hooks": [progress_hook],
            }
        else:
            opts = {
                **BASE_OPTS,
                "format": "bestaudio",
                "outtmpl": output,
                "progress_hooks": [progress_hook],
            }

        run_download(opts, url)
        return True, temp_dir

    except Exception:
        pass

    # =========================
    # 3차: android 강제 fallback
    # =========================
    try:
        ultra = {
            **BASE_OPTS,
            "extractor_args": {
                "youtube": {
                    "player_client": ["android"]
                }
            },
            "format": "best",
            "outtmpl": output,
            "progress_hooks": [progress_hook],
        }

        run_download(ultra, url)
        return True, temp_dir

    except Exception as e:
        return False, str(e)


# -------------------------
# UI
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

    if st.button("다운로드 시작"):

        progress = st.progress(0)
        status = st.empty()

        def hook(d):
            if d["status"] == "downloading":
                if "total_bytes" in d:
                    pct = d["downloaded_bytes"] / d["total_bytes"]
                    progress.progress(min(pct, 1.0))
                    status.info(f"{pct*100:.1f}% 다운로드 중")

            if d["status"] == "finished":
                progress.progress(1.0)
                status.success("완료")

        temp_dir = tempfile.mkdtemp()

        success, result = download_with_fallback(
            url,
            file_type,
            filename,
            temp_dir,
            hook
        )

        if not success:
            st.error("다운로드 실패 (모든 fallback 실패)")
            st.code(result)
        else:
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
