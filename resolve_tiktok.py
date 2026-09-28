import urllib.request
import ssl
import re
import json

ssl._create_default_https_context = ssl._create_unverified_context
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
}

links = [
    "https://vt.tiktok.com/ZSbr59B7J/",
    "https://vt.tiktok.com/ZSbrHraAD/"
]

for l in links:
    print(f"\nResolving {l}...")
    try:
        req = urllib.request.Request(l, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            final_url = resp.geturl()
            print(f"Final URL: {final_url}")
            html = resp.read().decode('utf-8', errors='ignore')
            print(f"HTML length: {len(html)}")
            
            # Find capcut template references, anchor links, video IDs
            capcut_refs = re.findall(r'https://[^\s"\'<>]*(?:capcut|template)[^\s"\'<>]*', html)
            print("CapCut references found:", len(capcut_refs))
            for cr in capcut_refs[:5]:
                print(" ->", cr[:120])
                
            # Search for anchor links or schema data
            anchors = re.findall(r'"anchor":{.*?}', html)
            print("Anchors found:", len(anchors))
            for a in anchors[:3]:
                print(" ->", a[:150])
    except Exception as e:
        print(f"Error resolving {l}: {e}")
