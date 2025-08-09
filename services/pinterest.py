import requests
from bs4 import BeautifulSoup

def extract_pinterest_image_url(pinterest_url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(pinterest_url, headers=headers)
        if res.status_code != 200:
            print(f"Failed to get Pinterest page, status: {res.status_code}")
            return None
        soup = BeautifulSoup(res.text, "html.parser")
        for tag in soup.find_all("meta"):
            if tag.get("property") == "og:image":
                return tag.get("content")
        print("og:image meta tag not found")
        return None
    except Exception as e:
        print("Pinterest image extraction error:", e)
        return None


def download_pinterest_image(url):
    image_url = extract_pinterest_image_url(url)
    if not image_url:
        return None, None
    image_data = requests.get(image_url).content
    return "pinterest_image.jpg", image_data
