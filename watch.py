import os, re, requests

H = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1",
    "Accept-Language": "th-TH,th;q=0.9",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://www.apple.com/th/shop/buy-iphone",
}
TOPIC = os.environ["NTFY_TOPIC"]
STORE = "central"
WATCH = ["pro max", "duo"]
EXTRA = []

def notify(msg):
    requests.post(f"https://ntfy.sh/{TOPIC}", data=msg.encode("utf-8"), timeout=20)

parts = set(EXTRA)
for u in ["https://www.apple.com/th/shop/buy-iphone",
          "https://www.apple.com/th/shop/buy-iphone/iphone-18-pro"]:
    try:
        parts |= set(re.findall(r"\b[A-Z0-9]{5,6}TH/A\b",
                                requests.get(u, headers=H, timeout=20).text))
    except Exception as e:
        print("page error", u, e)

failed = 0
for p in sorted(parts):
    try:
        r = requests.get(
            "https://www.apple.com/th/shop/fulfillment-messages",
            params={"pl": "true", "mts.0": "regular", "parts.0": p,
                    "location": "Bangkok"}, headers=H, timeout=20)
        stores = r.json()["body"]["content"]["pickupMessage"]["stores"]
        for s in stores:
            if STORE not in s["storeName"].lower():
                continue
            a = s["partsAvailability"][p]
            title = a.get("storePickupProductTitle") or p
            quote = a.get("pickupSearchQuote", "")
            print(p, "|", title, "|", a["pickupDisplay"], "|", quote)
            if (a["pickupDisplay"] == "available"
                    and any(w in title.lower() for w in WATCH)
                    and ("วันนี้" in quote or "today" in quote.lower())):
                notify(f"{title} รับวันนี้ที่ {s['storeName']} ได้แล้ว!")
    except Exception as e:
        failed += 1
        print(p, "error:", repr(e))

if parts and failed == len(parts):
    notify("บอท Apple เช็กไม่ได้ (Apple อาจบล็อก GitHub)")
