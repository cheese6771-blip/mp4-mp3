import streamlit as st
import yt_dlp
import tempfile
import os
import re
from pathlib import Path

st.set_page_config(page_title="YouTube Downloader", page_icon="🎬")
st.title("🎬 YouTube Downloader (No Cookie Mode)")

def clean_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "", name)


BASE_OPTS = {
    "quiet": True,
    "noplaylist": True,

    # 👉 봇 탐지 줄이기용 최소 설정
    "http_headers": {
        "User-Agent": "Mozilla/5.0",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.youtube.com/"
    },

    # 👉 모바일 클라이언트로 위장 (핵심)
    "extractor_args": {
        "youtube": {
            "player_client": ["android", "ios"]
        }
    },

    "force_ipv4": True,
    "socket_timeout": 20,
}


url = st.text_input("유튜브 링크")

info = None

if url:
    try:
        with yt_dlp.YoutubeDL(BASE_OPTS) as ydl:
            info = ydl.extract_info(url, download=False)

        st.success("영상 정보 로드 성공")
        st.image(info.get("thumbnail"))
        st.write(info.get("title"))

    except Exception as e:
        st.error("영상 로드 실패")
        st.code(str(e))


if info:

    filename = st.text_input("파일명", clean_filename(info["title"]))
    mode = st.radio("형식", ["MP4", "MP3"], horizontal=True)

    if st.button("다운로드"):

        temp_dir = tempfile.mkdtemp()
        output = os.path.join(temp_dir, f"{filename}.%(ext)s")

        try:

            if mode == "MP4":
                fmt = "best[ext=mp4]/best"
                ydl_opts = {
                    **BASE_OPTS,
                    "format": fmt,
                    "outtmpl": output,
                    "merge_output_format": "mp4",
                }

            else:
                fmt = "bestaudio[ext=m4a]/bestaudio"
                ydl_opts = {
                    **BASE_OPTS,
                    "format": fmt,
                    "outtmpl": output,
                    "postprocessors": [{
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "192"
                    }]
                }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            files = list(Path(temp_dir).glob("*"))

            if files:
                with open(files[0], "rb") as f:
                    st.download_button("다운로드", f, file_name=os.path.basename(files[0]))

        except Exception as e:
            st.error("실패")
            st.code(str(e))
