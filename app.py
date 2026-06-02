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
    border: none;
    border-radius: 10px;
    font-weight: bold;
}
</style>

""", unsafe_allow_html=True)

st.title("🎬 YouTube Downloader")

def clean_filename(name):
return re.sub(r'[\\/*?:"<>|]', "", name)

url = st.text_input(
"유튜브 링크 입력",
placeholder="https://www.youtube.com/watch?v=..."
)

if url:

```
try:

    with yt_dlp.YoutubeDL({
        "quiet": True,
        "noplaylist": True
    }) as ydl:

        info = ydl.extract_info(
            url,
            download=False
        )

    title = info.get("title", "video")
    thumbnail = info.get("thumbnail")
    uploader = info.get("uploader", "")

    if thumbnail:
        st.image(
            thumbnail,
            use_container_width=True
        )

    st.write(f"제목: {title}")
    st.write(f"채널: {uploader}")

    filename = st.text_input(
        "파일명",
        value=clean_filename(title)
    )

    file_type = st.radio(
        "다운로드 형식",
        ["MP4", "MP3"],
        horizontal=True
    )

    if st.button("다운로드 준비"):

        temp_dir = tempfile.mkdtemp()

        output_template = os.path.join(
            temp_dir,
            f"{filename}.%(ext)s"
        )

        if file_type == "MP4":

            ydl_opts = {
                "format": "best",
                "outtmpl": output_template,
                "quiet": True,
                "noplaylist": True
            }

            ext = "mp4"

        else:

            ydl_opts = {
                "format": "bestaudio/best",
                "outtmpl": output_template,
                "quiet": True,
                "noplaylist": True,
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "192"
                    }
                ]
            }

            ext = "mp3"

        with st.spinner("다운로드 중..."):

            with yt_dlp.YoutubeDL(
                ydl_opts
            ) as ydl:

                ydl.download([url])

        files = list(
            Path(temp_dir).glob(
                f"*.{ext}"
            )
        )

        if files:

            with open(
                files[0],
                "rb"
            ) as f:

                st.success("다운로드 완료")

                st.download_button(
                    label=f"{ext.upper()} 다운로드",
                    data=f,
                    file_name=f"{filename}.{ext}",
                    mime=(
                        "video/mp4"
                        if ext == "mp4"
                        else "audio/mpeg"
                    )
                )

except Exception as e:

    st.error("오류 발생")

    st.code(str(e))
```
