import os
import shutil
import instaloader

def download_instagram_post_with_cookies(url):
    if os.path.exists("insta_download"):
        shutil.rmtree("insta_download")

    L = instaloader.Instaloader(dirname_pattern="insta_download", save_metadata=False, download_comments=False)

    cookie_file = "data/instacookies.txt" 
    if os.path.exists(cookie_file):
        L.context._session.cookies.load(cookie_file, ignore_discard=True, ignore_expires=True)
    else:
        print("Cookie File Was Not Found")

    shortcode = url.rstrip('/').split("/")[-1].split("?")[0]
    post = instaloader.Post.from_shortcode(L.context, shortcode)

    L.download_post(post, target="post")

    media_folder = "insta_download/post"
    media_files = sorted(os.listdir(media_folder))
    media_bytes = []
    for file in media_files:
        filepath = os.path.join(media_folder, file)
        with open(filepath, "rb") as f:
            media_bytes.append((file, f.read()))

    shutil.rmtree("insta_download")
    return media_bytes
