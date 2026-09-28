import urllib.request
import re
import json
import ssl

ssl._create_default_https_context = ssl._create_unverified_context
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
}

url = 'https://www.capcut.com/template-detail/new-skull-top-vs-phonk/7452270956178935093'
req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req, timeout=10) as resp:
    html = resp.read().decode('utf-8', errors='ignore')

# Search for any JSON or URLs
print("Searching for URLs inside HTML...")
urls = re.findall(r'https://[^"\'\\<>\s]+', html)
print("Found URLs:", len(urls))

video_urls = [u for u in urls if any(ext in u.lower() for ext in ['.mp4', '.m3u8', '.webm', 'tiktokcdn', 'byteoversea', 'ibyteimg', 'capcut'])]
print("Filtered media/cdn URLs:", len(video_urls))
for u in video_urls[:20]:
    print(" ->", u[:100])
