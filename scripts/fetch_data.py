"""ดึงผลสลากกินแบ่งรัฐบาล (เลขหน้า 3 ตัว / เลขท้าย 3 ตัว) เก็บลง data/draws.json
ใช้ API สาธารณะของ rayriffy (https://github.com/rayriffy/thai-lotto-api)
รัน:  python scripts/fetch_data.py            -> ดึงเฉพาะงวดที่ยังไม่มี
      python scripts/fetch_data.py --sample   -> สร้างข้อมูลสุ่มปลอม ไว้ลองหน้าเว็บ
"""
import json, os, random, sys, time, urllib.request
from datetime import date, timedelta

API = "https://lotto.api.rayriffy.com"
OUT = os.path.join(os.path.dirname(__file__), "..", "data", "draws.json")
MAX_PAGES = 12          # ปรับเพิ่มถ้าอยากย้อนไกลกว่านี้
STOP_AFTER_YEAR = 2558  # เลขหน้า/ท้าย 3 ตัวแบบปัจจุบันเริ่มช่วงปลายปี 2558

def get(path):
    req = urllib.request.Request(API + path, headers={"User-Agent": "lottery-stats/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

def iso_from_id(draw_id):          # "16102569" -> "2026-10-16"
    d, m, y = int(draw_id[:2]), int(draw_id[2:4]), int(draw_id[4:]) - 543
    return date(y, m, d).isoformat()

def load():
    if os.path.exists(OUT):
        with open(OUT, encoding="utf-8") as f:
            return json.load(f)
    return []

def save(draws):
    draws.sort(key=lambda d: d["date"])
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(draws, f, ensure_ascii=False, separators=(",", ":"))
    print(f"บันทึก {len(draws)} งวด")

def sample():
    random.seed(1)
    draws, d = [], date(2021, 11, 1)
    while d <= date.today():
        if d.day in (1, 16):
            n = lambda: f"{random.randrange(1000):03d}"
            draws.append({"date": d.isoformat(), "front3": [n(), n()], "back3": [n(), n()]})
        d += timedelta(days=1)
    save(draws)

def main():
    draws = load()
    have = {d["date"] for d in draws}
    for page in range(1, MAX_PAGES + 1):
        items = get(f"/list/{page}")["response"]
        if not items:
            break
        for it in items:
            draw_id = it.get("id") or it["url"].rsplit("/", 1)[-1]
            if int(draw_id[4:]) < STOP_AFTER_YEAR:
                save(draws); return
            iso = iso_from_id(draw_id)
            if iso in have:
                continue
            prizes = {p["id"]: p["number"] for p in get(f"/lotto/{draw_id}")["response"]["prizes"]}
            draws.append({"date": iso,
                          "front3": prizes.get("runningNumberFrontThree", []),
                          "back3": prizes.get("runningNumberBackThree", [])})
            have.add(iso); time.sleep(0.3)
    save(draws)

if __name__ == "__main__":
    sample() if "--sample" in sys.argv else main()
