import os
import yt_dlp

def download_youtube_video(url):
    try:
        output_filename = "video.mp4"
        ydl_opts = {
            'format': 'best[ext=mp4]',
            'outtmpl': output_filename,
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
            'retries': 3,
            'cookiefile': 'data/cookies.txt'
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            title = info_dict.get('title', 'video')

        if not os.path.exists(output_filename):
            print("Video File Was Not Created.")
            return None, None

        with open(output_filename, "rb") as f:
            video_data = f.read()

        os.remove(output_filename)
        return title, video_data
    except Exception as e:
        print("Download error:", str(e))
        return None, None
