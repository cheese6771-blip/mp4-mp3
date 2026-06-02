import streamlit as st
import yt_dlp
import tempfile
import os
import re
import traceback
from pathlib import Path

st.set_page_config(
page_title="YouTube Downloader",
page_icon="🎬",
layout="centered"
)

st.markdown("""

<style>
.stApp{
    background: linear-gradient(
        135deg,
        #7ca982 0%,
        #b8d89b 50%,
        #f7f3d7 100%
    );
}

.title{
    text-align:center;
    font-size:40px;
    font-weight:700;
    color:#2d4739;
}

.stButton>button,
.stDownloadButton>button{
    background:#f7f3d7;
    color:#2d4739;
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

def clean_filename(text):
return re.sub(r'[\/*?:"<>|]', "", text)

def get_available_resolutions(info):
resolutions = set()

```
for fmt in info.get("formats", []):
    height = fmt.get("height")

    if height:
        resolutions.add(f"{height}p")

return sorted(
    list(resolutions),
    key=lambda x: int(x[:-1])
)
```

def check_downloadable(url):

```
try:

    opts = {
        "quiet": True,
        "noplaylist": True
    }

    with yt_dlp.YoutubeDL(opts) as ydl:

        info = ydl.extract_info(
            url,
            download=False
        )

    return True, info

except Exception as e:
    return False, str(e)
```

progress = st.empty()
status = st.empty()

class ProgressHook:

```
def __call__(self, d):

    if d["status"] == "downloading":

        total = (
            d.get("total_bytes")
            or d.get("total_bytes_estimate")
        )

        downloaded = d.get(
            "downloaded_bytes",
            0
        )

        if total:

            pct = downloaded / total

            progress.progress(
                min(pct, 1.0)
            )

            status.info(
                f"다운로드 중 {pct*100:.1f}%"
            )

    elif d["status"] == "finished":

        progress.progress(1.0)
        status.success("다운로드 완료")
```

url = st.text_input(
"유튜브 링크",
placeholder="https://youtube.com/watch?v=..."
)

if url:

```
with st.spinner("영상 확인 중..."):

    ok, result = check_downloadable(url)

if not ok:

    st.error("영상 정보를 불러올 수 없습니다.")
    st.code(result)
    st.stop()

info = result

title = info.get("title", "")
uploader = info.get("uploader", "")
duration = info.get("duration", 0)
thumbnail = info.get("thumbnail")

if thumbnail:
    st.image(
        thumbnail,
        use_container_width=True
    )

mins = duration // 60
secs = duration % 60

st.markdown(f"""
```

### {title}

**채널:** {uploader}

**길이:** {mins}:{secs:02d}
""")

```
filename = st.text_input(
    "파일명 수정",
    value=clean_filename(title)
)

filetype = st.radio(
    "형식 선택",
    ["MP4", "MP3"],
    horizontal=True
)

quality = None

if filetype == "MP4":

    resolutions = get_available_resolutions(info)

    if resolutions:

        quality = st.selectbox(
            "화질 선택",
            resolutions[::-1]
        )

if st.button("다운로드 시작"):

    try:

        temp_dir = tempfile.mkdtemp()

        output = os.path.join(
            temp_dir,
            f"{filename}.%(ext)s"
        )

        progress.progress(0)

        if filetype == "MP4":

            if quality:

                selected_height = quality.replace(
                    "p",
                    ""
                )

                ydl_opts = {
                    "format":
                    f"best[height<={selected_height}]/best",
                    "outtmpl":
                    output,
                    "progress_hooks":
                    [ProgressHook()],
                    "quiet":
                    True,
                    "noplaylist":
                    True
                }

            else:

                ydl_opts = {
                    "format":
                    "best",
                    "outtmpl":
                    output,
                    "progress_hooks":
                    [ProgressHook()],
                    "quiet":
                    True,
                    "noplaylist":
                    True
                }

        else:

            ydl_opts = {
                "format":
                "bestaudio/best",

                "outtmpl":
                output,

                "progress_hooks":
                [ProgressHook()],

                "postprocessors": [
                    {
                        "key":
                        "FFmpegExtractAudio",

                        "preferredcodec":
                        "mp3",

                        "preferredquality":
                        "192"
                    }
                ],

                "quiet":
                True,

                "noplaylist":
                True
            }

        with yt_dlp.YoutubeDL(
            ydl_opts
        ) as ydl:

            ydl.download([url])

        ext = (
            "mp4"
            if filetype == "MP4"
            else "mp3"
        )

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

                st.download_button(
                    f"📥 {ext.upper()} 다운로드",
                    data=f,
                    file_name=f"{filename}.{ext}",
                    mime=(
                        "video/mp4"
                        if ext == "mp4"
                        else "audio/mpeg"
                    )
                )

    except Exception:

        st.error(
            "다운로드 실패"
        )

        st.code(
            traceback.format_exc()
        )
```
