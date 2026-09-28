import urllib.request
import re
import os
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
}

templates = [
    {
        "id": "template_1",
        "name": "New Skull Top vs Phonk",
        "url": "https://www.capcut.com/template-detail/new-skull-top-vs-phonk/7452270956178935093"
    },
    {
        "id": "template_2",
        "name": "Phonk Trend Trending Viral Export",
        "url": "https://www.capcut.com/template-detail/phonk-trend-trending-viral-export/7443974836612762935"
    },
    {
        "id": "template_3",
        "name": "Phonk Edit Skull Freezeframe",
        "url": "https://www.capcut.com/template-detail/phonk-edit-skull-freezeframe-foryou/7445955698594303285"
    },
    {
        "id": "template_4",
        "name": "Skull Funksigilo Trend",
        "url": "https://www.capcut.com/template-detail/skull-funksigilo-trend-capcuthq-fyp/7525200265075526973"
    }
]

out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "capcut_videos")
os.makedirs(out_dir, exist_ok=True)

for tmpl in templates:
    print(f"\n[CapCut] Processing: {tmpl['name']}...")
    try:
        req = urllib.request.Request(tmpl["url"], headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
        
        # Search for capcutvod.com or mp4 URLs
        vod_urls = re.findall(r'https://[^"\'\\<>\s]+capcutvod\.com[^"\'\\<>\s]+', html)
        if not vod_urls:
            vod_urls = re.findall(r'https://[^"\'\\<>\s]+\.mp4[^"\'\\<>\s]*', html)
            
        if vod_urls:
            video_url = vod_urls[0].replace('\\u002F', '/').replace('&amp;', '&')
            print(f"Found Video URL: {video_url[:100]}...")
            out_file = os.path.join(out_dir, f"{tmpl['id']}.mp4")
            
            # Download video
            dl_req = urllib.request.Request(video_url, headers=headers)
            with urllib.request.urlopen(dl_req, timeout=30) as v_resp, open(out_file, 'wb') as f_out:
                f_out.write(v_resp.read())
            print(f"Successfully downloaded {out_file} ({os.path.getsize(out_file)} bytes)")
        else:
            print("No VOD URL found in page HTML.")
    except Exception as e:
        print(f"Error downloading {tmpl['name']}: {e}")
