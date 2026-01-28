from flask import Flask, request, send_file
import yt_dlp
import os
import uuid
import subprocess

app = Flask(__name__)

@app.route('/')
def home():
        return render_template("index.html")
    <form method="POST" action="/compile" id="frm">
        <textarea name="links" style="width:400px;height:200px;" placeholder="Paste YouTube links, one per line"></textarea><br><br>
        <button type="submit">Compile Audio</button>
    </form>
    """

@app.route('/compile', methods=['POST'])
def compile_audio():
    raw = request.form.get("links", "")
    links = [x.strip() for x in raw.split("\n") if x.strip()]

    if not links:
        return "No links provided!"

    session_id = str(uuid.uuid4())
    folder = f"tmp/{session_id}"
    os.makedirs(folder, exist_ok=True)

    audio_files = []

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'{folder}/%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '128',
        }],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        for link in links:
            info = ydl.extract_info(link, download=True)
            title = info.get('title')
            audio_files.append(f"{folder}/{title}.mp3")

    # Create concat file list for ffmpeg (no gap)
    list_file = f"{folder}/files.txt"
    with open(list_file, "w", encoding="utf-8") as f:
        for file in audio_files:
            f.write(f"file '{os.path.abspath(file)}'\n")

    output = f"{folder}/compiled.mp3"
    subprocess.run(
        ["ffmpeg", "-f", "concat", "-safe", "0", "-i", list_file, "-c", "copy", output],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    return send_file(output, as_attachment=True, download_name="compilation.mp3")
    
if __name__ == "__main__":
    app.run()
