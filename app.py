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


url = st.text_input(
    "유튜브 링크",
    placeholder="https://www.youtube.com/watch?v=..."
)

info = None

if url:
    try:
        with yt_dlp.YoutubeDL({
            "quiet": True,
            "noplaylist": True
        }) as ydl:
            info = ydl.extract_info(url, download=False)

        st.success("영상 정보 불러오기 성공")

        title = info.get("title", "video")
        thumbnail = info.get("thumbnail")
        uploader = info.get("uploader", "")

        if thumbnail:
            st.image(thumbnail, use_container_width=True)

        st.write(f"제목: {title}")
        st.write(f"채널: {uploader}")

    except Exception as e:
        st.error("영상 정보를 불러오지 못했습니다.")
        st.code(str(e))

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
        st.info(f"{file_type} 다운로드 준비 완료")
        st.write(f"파일명: {filename}")
