ydl_opts = {

```
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
        "192"
    }
],

"quiet": True,

"noplaylist": True
```

}
