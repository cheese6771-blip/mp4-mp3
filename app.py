import streamlit as st
import yt_dlp
import tempfile
import os
import re
from pathlib import Path

st.set_page_config(page_title="YouTube Downloader", page_icon="🎬")

st.title("🎬 YouTube Downloader")

def clean_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "", name)


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


url = st.text_input("유튜브 링크")

info = None

if url:
    try:
        with yt_dlp.YoutubeDL(BASE_OPTS) as ydl:
            info = ydl.extract_info(url, download=False)

        st.success("영상 정보 로드 성공")
        st.image(info.get("thumbnail"), use_container_width=True)
        st.write(info.get("title"))

    except Exception as e:
        st.error(e)


if info:

    filename = st.text_input("파일명", clean_filename(info["title"]))
    file_type = st.radio("형식", ["MP4", "MP3"], horizontal=True)

    if st.button("다운로드"):

        temp_dir = tempfile.mkdtemp()
        output = os.path.join(temp_dir, f"{filename}.%(ext)s")

        progress = st.progress(0)
        status = st.empty()

        def hook(d):
            if d["status"] == "downloading":
                if d.get("total_bytes"):
                    pct = d["downloaded_bytes"] / d["total_bytes"]
                    progress.progress(min(pct, 1.0))
                    status.info(f"{pct*100:.1f}%")

        try:

            # ---------------- MP4 ----------------
            if file_type == "MP4":

                ydl_opts = {
                    **BASE_OPTS,
                    "format": "best[ext=mp4]/best",
                    "outtmpl": output,
                    "merge_output_format": "mp4",
                    "progress_hooks": [hook],
                }

                ext = "mp4"

            # ---------------- MP3 (핵심 안정 버전) ----------------
            else:

                ydl_opts = {
                    **BASE_OPTS,

                    # 👉 핵심: 가장 안정적인 audio만 요청
                    "format": "bestaudio[ext=m4a]/bestaudio",

                    "outtmpl": output,
                    "progress_hooks": [hook],

                    # 👉 ffmpeg 변환 최소화
                    "postprocessors": [{
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "192"
                    }],

                    # 👉 playlist 차단 (추가 요청 방지)
                    "noplaylist": True,
                }

                ext = "mp3"


            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            files = list(Path(temp_dir).glob(f"*.{ext}"))

            if files:
                with open(files[0], "rb") as f:
                    st.download_button(
                        f"{ext.upper()} 다운로드",
                        f,
                        file_name=f"{filename}.{ext}"
                    )

        except Exception as e:
            st.error("다운로드 실패")
            st.code(str(e))
