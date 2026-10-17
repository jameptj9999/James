import requests, re

H = {"User-Agent": "Mozilla/5.0"}
URLS = [
    "https://www.apple.com/th/shop/buy-iphone/iphone-18-pro",
    "https://www.apple.com/th/shop/buy-iphone",
]

parts = set()
for u in URLS:
    try:
        html = requests.get(u, headers=H, timeout=20).text
        found = set(re.findall(r"\b[A-Z0-9]{5,6}TH/A\b", html))
        print(u, "-> found", len(found))
        parts |= found
    except Exception as e:
        print(u, "error:", repr(e))

print("ALL PARTS:", sorted(parts))

for p in sorted(parts):
    try:
        r = requests.get(
            "https://www.apple.com/th/shop/fulfillment-messages",
            params={"pl": "true", "mts.0": "regular", "parts.0": p,
                    "location": "Bangkok"},
            headers=H, timeout=20)
        stores = r.json()["body"]["content"]["pickupMessage"]["stores"]
        for s in stores:
            if "central" in s["storeName"].lower():
                a = s["partsAvailability"][p]
                print(p, "|", a.get("storePickupProductTitle"), "|", a["pickupDisplay"])
    except Exception as e:
        print(p, "error:", repr(e))
