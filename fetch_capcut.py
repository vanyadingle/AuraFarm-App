import urllib.request
import json
import re
import ssl

ssl._create_default_https_context = ssl._create_unverified_context
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
}

urls = [
    ('Skull Top', 'https://www.capcut.com/template-detail/new-skull-top-vs-phonk/7452270956178935093'),
    ('Viral Phonk', 'https://www.capcut.com/template-detail/phonk-trend-trending-viral-export/7443974836612762935'),
    ('Skull Freeze', 'https://www.capcut.com/template-detail/phonk-edit-skull-freezeframe-foryou/7445955698594303285'),
    ('Funk Sigilo', 'https://www.capcut.com/template-detail/skull-funksigilo-trend-capcuthq-fyp/7525200265075526973')
]

for name, url in urls:
    print(f"\n--- Fetching {name} ---")
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            print(f"HTML length: {len(html)}")
            
            # Search for __NEXT_DATA__ or JSON blocks
            json_matches = re.findall(r'<script id="__NEXT_DATA__" type="application/json">({.*?})</script>', html)
            if json_matches:
                data = json.loads(json_matches[0])
                print("Found __NEXT_DATA__ keys:", list(data.keys()))
                # Save sample json
                with open(f"capcut_{name.replace(' ', '_')}.json", "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            else:
                # Find all video or audio links
                vids = re.findall(r'https://[^\s"\'<>]+\.(?:mp4|mp3|m4a|wav)[^\s"\'<>]*', html)
                print(f"Media links found: {len(vids)}")
                for v in vids[:5]:
                    print(" -", v[:120])
    except Exception as e:
        print(f"Error: {e}")
