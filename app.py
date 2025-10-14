from flask import Flask, render_template, request, jsonify
import yt_dlp
import time

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_link', methods=['POST'])
def get_link():
    url = request.form.get('url')
    if not url:
        return jsonify({'error': 'No URL provided'}), 400

    ydl_opts = {
        'quiet': True,
        'skip_download': True,
    }

    retries = 3
    for attempt in range(1, retries + 1):
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
            return jsonify({'title': info.get('title'), 'id': info.get('id')})
        except yt_dlp.utils.DownloadError as e:
            error_msg = str(e)
            if 'HTTP Error 429' in error_msg:
                if attempt < retries:
                    time.sleep(5)  # wait 5 seconds before retrying
                    continue
                else:
                    return jsonify({'error': 'Too Many Requests (429). Please try again later.'}), 429
            else:
                return jsonify({'error': error_msg}), 500
        except Exception as e:
            return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
