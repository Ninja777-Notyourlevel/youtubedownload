from flask import Flask, request, render_template, jsonify
import yt_dlp
import logging

app = Flask(__name__)

# Reduce Flask logs clutter
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_link', methods=['POST'])
def get_link():
    url = request.form.get('url')
    if not url:
        return jsonify({"error": "URL is required"}), 400

    try:
        # yt-dlp options
        ydl_opts = {
            'quiet': True,
            'cookiefile': 'youtube.com_cookies.txt',  # Must match Render secret file
            'noplaylist': True,
            'format': 'best',
            'socket_timeout': 15,  # Avoid long hanging requests
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36'
            },
            'ignoreerrors': True,  # Skip if yt-dlp hits 429
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Extract info but do NOT process full formats (faster)
            info = ydl.extract_info(url, download=False, process=False)
            
            if info is None:
                return jsonify({"error": "Failed to fetch video info (maybe 429)"}), 500
            
            title = info.get('title', 'Unknown Title')
            
            # Get best direct URL
            formats = info.get('formats', [])
            download_url = None
            for f in formats:
                if 'url' in f:
                    download_url = f['url']
                    break  # Pick the first available format
            
            if not download_url:
                # fallback: direct URL in info
                download_url = info.get('url', None)

            if not download_url:
                return jsonify({"error": "No downloadable URL found"}), 500

        return jsonify({
            "title": title,
            "download_url": download_url
        })

    except yt_dlp.utils.DownloadError as e:
        return jsonify({"error": "YouTube blocked this request or cookies expired"}), 500
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
