import os
import requests
import shutil
import instaloader
import yt_dlp

from bs4 import BeautifulSoup


def download_instagram_post_with_cookies(url):
    if os.path.exists("insta_download"):
        shutil.rmtree("insta_download")

    L = instaloader.Instaloader(
        dirname_pattern="insta_download",
        save_metadata=False,
        download_comments=False
    )

    cookie_file = "instacookies.txt"
    if os.path.exists(cookie_file):
        L.context._session.cookies.load(
            cookie_file,
            ignore_discard=True,
            ignore_expires=True
        )

    shortcode = url.rstrip("/").split("/")[-1].split("?")[0]
    post = instaloader.Post.from_shortcode(L.context, shortcode)
    L.download_post(post, target="post")

    media_folder = "insta_download/post"
    media_files = sorted(os.listdir(media_folder))

    media_bytes = []
    for file in media_files:
        with open(os.path.join(media_folder, file), "rb") as f:
            media_bytes.append((file, f.read()))

    shutil.rmtree("insta_download")
    return media_bytes


def download_youtube_video(url):
    try:
        ydl_opts = {
            "format": "best[ext=mp4]",
            "outtmpl": "video.mp4",
            "noplaylist": True,
            "quiet": True,
            "cookiefile": "cookies.txt"
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(url, download=True)

        with open("video.mp4", "rb") as f:
            data = f.read()

        os.remove("video.mp4")
        return data
    except Exception:
        return None


def extract_pinterest_image_url(url):
    res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(res.text, "html.parser")
    for tag in soup.find_all("meta"):
        if tag.get("property") == "og:image":
            return tag.get("content")
    return None


def download_pinterest_image(url):
    image_url = extract_pinterest_image_url(url)
    if not image_url:
        return None
    return requests.get(image_url).content
