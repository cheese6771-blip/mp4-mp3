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
}
</style>

""", unsafe_allow_html=True)

st.title("🎬 YouTube Downloader")

def clean_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "", name)

st.write("앱 로딩 성공")
url = st.text_input(
    "유튜브 링크",
    placeholder="https://www.youtube.com/watch?v=..."
)

if url:

    try:

        with yt_dlp.YoutubeDL({
            "quiet": True,
            "noplaylist": True
        }) as ydl:

            info = ydl.extract_info(
                url,
                download=False
            )

        st.success("영상 정보 불러오기 성공")

        st.write("제목:", info.get("title"))

        thumbnail = info.get("thumbnail")

        if thumbnail:
            st.image(
                thumbnail,
                use_container_width=True
            )

    except Exception as e:

        st.error(str(e))
import re

def clean_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "", name)

filename = st.text_input(
    "저장 파일명",
    value=clean_filename(
        info.get("title", "video")
    )
)
file_type = st.radio(
    "형식 선택",
    ["MP4", "MP3"],
    horizontal=True
)
if st.button("다운로드 시작"):
    st.info("다운로드 기능 테스트 단계")
