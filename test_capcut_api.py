import urllib.request
import json
import ssl

ssl._create_default_https_context = ssl._create_unverified_context
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Referer': 'https://www.capcut.com/',
    'Origin': 'https://www.capcut.com',
    'pf': '7',
    'app_version': '1.0.0',
    'device_id': '1234567890123456',
}

template_ids = [
    '7452270956178935093',
    '7443974836612762935',
    '7445955698594303285',
    '7525200265075526973'
]

api_urls = [
    lambda tid: f'https://edit-api-sg.capcut.com/lv/v1/template/detail?template_id={tid}',
    lambda tid: f'https://www.capcut.com/api/template/detail?template_id={tid}',
    lambda tid: f'https://api.capcut.com/lv/v1/template/detail?template_id={tid}',
    lambda tid: f'https://edit-api-va.capcut.com/lv/v1/template/detail?template_id={tid}',
]

for tid in template_ids[:1]:
    for fn in api_urls:
        url = fn(tid)
        print(f"Trying {url}...")
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                print("SUCCESS!", data.keys())
                with open("capcut_api_res.json", "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
                break
        except Exception as e:
            print(f"Failed: {e}")
