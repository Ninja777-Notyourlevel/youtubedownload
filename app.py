from flask import Flask, request, render_template, jsonify
import yt_dlp

app = Flask(__name__)

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
            'cookiefile': 'youtube.com_cookies.txt',  # must match secret file path in Render
            'noplaylist': True,
            'format': 'best',
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36'
            }
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get('title', 'Unknown Title')
            formats = info.get('formats', [])

            # Pick the best format: highest resolution available
            best_format = None
            max_height = 0
            for f in formats:
                # skip formats with no URL
                if 'url' not in f:
                    continue
                height = f.get('height') or 0
                if height > max_height:
                    max_height = height
                    best_format = f

            if not best_format:
                # fallback to first available format
                best_format = formats[0] if formats else {}
            
            download_url = best_format.get('url', None)
            if not download_url:
                return jsonify({"error": "No downloadable format found"}), 500

        return jsonify({
            "title": title,
            "download_url": download_url
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
