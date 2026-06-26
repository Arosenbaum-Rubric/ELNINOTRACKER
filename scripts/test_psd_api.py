import requests

API_KEY = "6qVcImaFPcgbrx5DVQujyQxLQ0H9kxZpeaeOpznP"
headers = {"API_KEY": API_KEY}

urls = [
    "https://apps.fas.usda.gov/OpenData/api/psd/commodity/0620000/country/all/year/2024",
    "https://apps.fas.usda.gov/OpenData/api/psd/commodity/0620000/country/CI/year/2024",
    "https://apps.fas.usda.gov/OpenData/api/psd/commodity/0620000",
    "https://apps.fas.usda.gov/OpenData/api/psd/cropYears",
    "https://apps.fas.usda.gov/OpenData/api/psd/commodities",
    "https://apps.fas.usda.gov/OpenData/api/psd/countries",
]

for url in urls:
    try:
        r = requests.get(url, headers=headers, timeout=15)
        print(f"  {r.status_code} {url}")
        if r.status_code == 200:
            data = r.json()
            print(f"    -> type={type(data).__name__} len={len(data) if hasattr(data,'__len__') else 'N/A'}")
            if isinstance(data, list) and len(data) > 0:
                print(f"    -> first item keys: {list(data[0].keys()) if isinstance(data[0], dict) else str(data[0])[:100]}")
            elif isinstance(data, dict):
                print(f"    -> keys: {list(data.keys())[:10]}")
        else:
            print(f"    -> body: {r.text[:200]}")
    except Exception as e:
        print(f"  ERROR {url}: {e}")
