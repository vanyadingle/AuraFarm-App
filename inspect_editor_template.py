import urllib.request
import re
import json
import ssl

ssl._create_default_https_context = ssl._create_unverified_context
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
}

url = 'https://www.capcut.com/editor-template?&create_id=7391429885513780487&enter_from=main_btn&from_page=towards_page_template_reflux'

req = urllib.request.Request(url, headers=headers)
try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        html = resp.read().decode('utf-8', errors='ignore')
        print(f"HTML length: {len(html)}")
        # Look for draft data, template slots, materials, effects
        m = re.findall(r'https://[^\s"\'<>]+\.(?:mp4|mp3|wav|json)[^\s"\'<>]*', html)
        print("Found links:", len(m))
        for l in m[:10]:
            print(" -", l[:120])
except Exception as e:
    print(f"Error: {e}")
