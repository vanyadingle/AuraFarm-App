import urllib.request
import re
import json
import ssl

ssl._create_default_https_context = ssl._create_unverified_context
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Referer': 'https://www.tiktok.com/',
}

video_ids = ['7600035522785856784', '7472787641612782854']

for vid in video_ids:
    url = f"https://www.tiktok.com/@user/video/{vid}"
    print(f"\n--- Checking TikTok {vid} ---")
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            
            # Find __UNIVERSAL_DATA_FOR_REHYDRATION__ or SIGI_STATE
            rehy = re.findall(r'<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__" type="application/json">({.*?})</script>', html)
            if rehy:
                data = json.loads(rehy[0])
                print("Found Universal Data!")
                # Search for capcut or anchor
                data_str = json.dumps(data)
                cap_links = re.findall(r'https://[^\s"\'<>]*(?:capcut|template)[^\s"\'<>]*', data_str)
                print("Capcut links in universal data:", len(cap_links))
                for cl in cap_links[:5]:
                    print(" ->", cl)
                    
                # Search for video playAddr / downloadAddr
                vids = re.findall(r'"playAddr":"(.*?)"', data_str)
                if vids:
                    print("PlayAddr found:", vids[0][:100])
            else:
                print("No universal data, searching raw html...")
                cap_links = re.findall(r'https://[^\s"\'<>]*(?:capcut|template)[^\s"\'<>]*', html)
                print("Capcut links:", cap_links)
    except Exception as e:
        print(f"Error checking {vid}: {e}")
