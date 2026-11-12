import csv, io, json, os, urllib.request

URL = "https://raw.githubusercontent.com/WimPalaLab/thai-lottery-data/main/data/thai_lottery.csv"
OUT = os.path.join(os.path.dirname(__file__), "..", "data", "draws.json")
FROM_DATE = "2015-09-01"

def numbers(cell):
    return [n.strip() for n in (cell or "").split("|") if n.strip().isdigit()]

def parse(text):
    draws = []
    for row in csv.DictReader(io.StringIO(text)):
        if row["draw_date"] < FROM_DATE:
            continue
        front, back = numbers(row.get("front3")), numbers(row.get("back3"))
        if front and back:
            draws.append({"date": row["draw_date"], "front3": front, "back3": back})
    return sorted(draws, key=lambda d: d["date"])

def main():
    req = urllib.request.Request(URL, headers={"User-Agent": "lottery-stats/1.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        text = r.read().decode("utf-8-sig")
    draws = parse(text)
    if not draws:
        raise SystemExit("ไม่พบข้อมูล: รูปแบบไฟล์ต้นทางอาจเปลี่ยน")
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(draws, f, ensure_ascii=False, separators=(",", ":"))
    print(f"บันทึก {len(draws)} งวด ({draws[0]['date']} ถึง {draws[-1]['date']})")

if __name__ == "__main__":
    main()
