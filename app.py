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

# -------------------------
# CSS
# -------------------------
st.markdown("""
<style>

.stApp{
    background: linear-gradient(
        135deg,
        #7ca982 0%,
        #a8c686 45%,
        #f7f3d7 100%
    );
}

.title{
    text-align:center;
    font-size:42px;
    font-weight:700;
    color:#2f4f3f;
    margin-bottom:15px;
}

.video-card{
    background:rgba(255,255,255,0.35);
    padding:20px;
    border-radius:20px;
    backdrop-filter: blur(8px);
}

.stButton > button,
.stDownloadButton > button{
    background:#f7f3d7;
    color:#2f4f3f;
    border:none;
    border-radius:12px;
    font-weight:bold;
}

</style>
""", unsafe_allow_html=True)

st.markdown(
    '<div class="title">🎬 YouTube Downloader</div>',
    unsafe_allow_html=True
)

# -------------------------
# 파일명 정리
# -------------------------
def clean_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "", name)

# -------------------------
# 진행률 Hook
# -------------------------
progress_bar = st.empty()
status_text = st.empty()

class ProgressHook:

    def __call__(self, d):

        if d["status"] == "downloading":

            total = d.get("total_bytes")

            if not total:
                total = d.get("total_bytes_estimate")

            downloaded = d.get("downloaded_bytes", 0)

            if total:
                percent = downloaded / total
                progress_bar.progress(min(percent, 1.0))
                status_text.info(
                    f"다운로드 중... {percent*100:.1f}%"
                )

        elif d["status"] == "finished":

            progress_bar.progress(1.0)
            status_text.success("다운로드 완료")

# -------------------------
# URL 입력
# -------------------------
url = st.text_input(
    "유튜브 링크",
    placeholder="https://www.youtube.com/watch?v=..."
)

if url:

    try:

        with yt_dlp.YoutubeDL({
            "quiet": True
        }) as ydl:

            info = ydl.extract_info(
                url,
                download=False
            )

        title = info.get("title")
        thumbnail = info.get("thumbnail")
        duration = info.get("duration")
        uploader = info.get("uploader")

        st.image(
            thumbnail,
            use_container_width=True
        )

        mins = duration // 60
        secs = duration % 60

        st.markdown(
            f"""
            ### {title}

            **채널:** {uploader}

            **길이:** {mins}:{secs:02d}
            """
        )

        filename = st.text_input(
            "파일명 수정",
            value=clean_filename(title)
        )

        file_type = st.radio(
            "형식 선택",
            ["MP4", "MP3"],
            horizontal=True
        )

        if file_type == "MP4":

            quality = st.selectbox(
                "화질 선택",
                [
                    "360p",
                    "720p",
                    "1080p",
                    "최고화질"
                ]
            )

        if st.button("다운로드 준비"):

            temp_dir = tempfile.mkdtemp()

            progress_bar.progress(0)

            # -------------------------
            # MP4
            # -------------------------
            if file_type == "MP4":

                if quality == "360p":
                    fmt = (
                        "bestvideo[height<=360]+bestaudio/"
                        "best[height<=360]"
                    )

                elif quality == "720p":
                    fmt = (
                        "bestvideo[height<=720]+bestaudio/"
                        "best[height<=720]"
                    )

                elif quality == "1080p":
                    fmt = (
                        "bestvideo[height<=1080]+bestaudio/"
                        "best[height<=1080]"
                    )

                else:
                    fmt = "bestvideo+bestaudio/best"

                output = os.path.join(
                    temp_dir,
                    f"{filename}.%(ext)s"
                )

                ydl_opts = {
                    "format": fmt,
                    "outtmpl": output,
                    "merge_output_format": "mp4",
                    "progress_hooks": [
                        ProgressHook()
                    ],
                    "quiet": True,
                }

                with yt_dlp.YoutubeDL(
                    ydl_opts
                ) as ydl:
                    ydl.download([url])

                files = list(
                    Path(temp_dir).glob("*.mp4")
                )

                if files:

                    with open(
                        files[0],
                        "rb"
                    ) as f:

                        st.download_button(
                            "📥 MP4 다운로드",
                            f,
                            file_name=f"{filename}.mp4",
                            mime="video/mp4"
                        )

            # -------------------------
            # MP3
            # -------------------------
            else:

                output = os.path.join(
                    temp_dir,
                    f"{filename}.%(ext)s"
                )

                ydl_opts = {
                    "format": "bestaudio/best",
                    "outtmpl": output,
                    "progress_hooks": [
                        ProgressHook()
                    ],
                    "postprocessors": [
                        {
                            "key":
                            "FFmpegExtractAudio",
                            "preferredcodec":
                            "mp3",
                            "preferredquality":
                            "192",
                        }
                    ],
                    "quiet": True,
                }

                with yt_dlp.YoutubeDL(
                    ydl_opts
                ) as ydl:
                    ydl.download([url])

                files = list(
                    Path(temp_dir).glob("*.mp3")
                )

                if files:

                    with open(
                        files[0],
                        "rb"
                    ) as f:

                        st.download_button(
                            "🎵 MP3 다운로드",
                            f,
                            file_name=f"{filename}.mp3",
                            mime="audio/mpeg"
                        )

    except Exception as e:
        st.error(f"오류 발생: {e}")
