"""위키미디어 공용에서 재사용 가능한 사진 찾기·내려받기.

사용법: python3 wiki_photo.py "<검색어>" <저장경로.jpg> [후보수]
- CC0 · 퍼블릭 도메인 · CC BY 만 허용 (CC BY-SA, NC, ND 제외)
- 결과를 JSON으로 출력: {path, credit, title, page, license}
"""
import json
import re
import sys
import urllib.parse
import urllib.request

API = "https://commons.wikimedia.org/w/api.php"
UA = {"User-Agent": "NeolsCardBot/1.0 (https://www.instagram.com/neols.news/; neols card news) python-urllib"}
OK = re.compile(r"^(cc0|public domain|pd|cc by \d|cc-by-\d|cc by$)", re.I)
BAD = re.compile(r"sa|nc|nd", re.I)


def get(params):
    import time; time.sleep(2)  # 위키미디어 API에 부담 주지 않도록
    url = API + "?" + urllib.parse.urlencode({**params, "format": "json"})
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
        return json.load(r)


def clean(html):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", html or "")).strip()


def find(query, limit=15):
    if query.startswith("Category:"):  # 분류(카테고리) 안의 파일에서 고르기 — 검색보다 정확
        gen = {"generator": "categorymembers", "gcmtitle": query, "gcmtype": "file", "gcmlimit": limit}
    else:
        gen = {"generator": "search", "gsrsearch": f"{query} filetype:bitmap", "gsrnamespace": 6, "gsrlimit": limit}
    res = get({"action": "query", **gen, "prop": "imageinfo",
               "iiprop": "url|extmetadata|size|mime", "iiurlwidth": 1280})
    pages = sorted(res.get("query", {}).get("pages", {}).values(), key=lambda p: p.get("index", 99))
    for p in pages:
        ii = (p.get("imageinfo") or [{}])[0]
        if ii.get("mime") not in ("image/jpeg", "image/png") or ii.get("width", 0) < 1000:
            continue
        md = ii.get("extmetadata", {})
        lic = clean(md.get("LicenseShortName", {}).get("value"))
        if not lic or not OK.match(lic) or (lic.lower().startswith("cc") and BAD.search(lic.lower().replace("cc", "", 1))):
            continue
        artist = clean(md.get("Artist", {}).get("value")) or "Unknown"
        yield {"title": p["title"], "page": ii.get("descriptionurl"), "license": lic,
               "artist": artist[:60], "thumb": (ii.get("thumburl") or ii.get("url") or "").split("?")[0]}


LIB = "/home/claude/neols-media/photos"


def thumb_url(title, width=1280):
    """API 없이 표준 썸네일 주소 만들기 (위키미디어 API가 막혔을 때)."""
    import hashlib
    n = title.replace("File:", "").replace(" ", "_")
    h = hashlib.md5(n.encode()).hexdigest()
    q = urllib.parse.quote(n)
    return f"https://thumb.wikimedia.org/wikipedia/commons/thumb/{h[0]}/{h[:2]}/{q}/{width}px-{q}"


def save_to_library(c, out, tags):
    """받은 사진을 저장소의 사진 보관함에 출처와 함께 남겨 재사용."""
    import os, shutil
    os.makedirs(LIB, exist_ok=True)
    idx_path = os.path.join(LIB, "index.json")
    idx = json.load(open(idx_path, encoding="utf-8")) if os.path.exists(idx_path) else []
    if any(x["title"] == c["title"] for x in idx):
        return
    fname = re.sub(r"[^A-Za-z0-9가-힣._-]+", "_", c["title"].replace("File:", ""))[:80]
    if not fname.lower().endswith(".jpg"):
        fname += ".jpg"
    shutil.copy(out, os.path.join(LIB, fname))
    idx.append({"file": fname, "title": c["title"], "credit": c["credit"], "license": c["license"],
                "page": c.get("page"), "tags": tags})
    json.dump(idx, open(idx_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def main():
    # 보관함 검색: python3 wiki_photo.py --lib "<키워드>"
    if sys.argv[1] == "--lib":
        import os
        idx_path = os.path.join(LIB, "index.json")
        idx = json.load(open(idx_path, encoding="utf-8")) if os.path.exists(idx_path) else []
        kw = sys.argv[2].lower()
        for x in idx:
            if kw in (" ".join(x["tags"]) + " " + x["title"]).lower():
                print(json.dumps({**x, "path": os.path.join(LIB, x["file"])}, ensure_ascii=False))
        return
    # API 없이 바로 받기: python3 wiki_photo.py --direct "<File:제목>" <저장.jpg> "<작가>" "<라이선스>" "<태그,태그>"
    if sys.argv[1] == "--direct":
        import io
        from PIL import Image
        title, out, artist, lic = sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5]
        tags = sys.argv[6].split(",") if len(sys.argv) > 6 else []
        with urllib.request.urlopen(urllib.request.Request(thumb_url(title), headers=UA), timeout=60) as r:
            im = Image.open(io.BytesIO(r.read())).convert("RGB")
        im.save(out, "JPEG", quality=90)
        credit = f"{artist} / Wikimedia Commons / {lic}" + (" · 잘라서 사용" if lic.upper().startswith("CC BY") else "")
        c = {"title": title, "license": lic, "artist": artist, "credit": credit, "path": out,
             "page": "https://commons.wikimedia.org/wiki/" + title.replace(" ", "_")}
        save_to_library(c, out, tags)
        print(json.dumps(c, ensure_ascii=False))
        return
    # 후보 보기: python3 wiki_photo.py --list "<검색어>"   → 제목·라이선스 목록 (사람이/Claude가 제목을 보고 고름)
    # 내려받기: python3 wiki_photo.py "<검색어>" <저장경로> [--pick "<File:제목>"]
    if sys.argv[1] == "--list":
        for c in find(sys.argv[2], 25):
            print(f"{c['title']} | {c['license']} | {c['artist']}")
        return
    q, out = sys.argv[1], sys.argv[2]
    pick = sys.argv[4] if len(sys.argv) > 4 and sys.argv[3] == "--pick" else None
    for c in find(q, 25):
        if pick and c["title"] != pick:
            continue
        req = urllib.request.Request(c["thumb"], headers=UA)
        with urllib.request.urlopen(req, timeout=120) as r:
            data = r.read()
        # 위키미디어 권장 표준 썸네일(1280px, thumb.wikimedia.org)을 받아 JPEG 저장
        import io
        from PIL import Image
        im = Image.open(io.BytesIO(data)).convert("RGB")
        im.thumbnail((1600, 1600))
        im.save(out, "JPEG", quality=90)
        c["path"] = out
        c["credit"] = f"{c['artist']} / Wikimedia Commons / {c['license']}" + (" · 잘라서 사용" if c["license"].upper().startswith("CC BY") else "")
        save_to_library(c, out, [q])
        print(json.dumps(c, ensure_ascii=False))
        return
    print(json.dumps({"error": "no reusable photo found"}, ensure_ascii=False))
    sys.exit(1)


if __name__ == "__main__":
    main()
