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
