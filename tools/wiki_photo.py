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


def main():
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
        c["credit"] = f"{c['artist']} / Wikimedia Commons / {c['license']}"
        print(json.dumps(c, ensure_ascii=False))
        return
    print(json.dumps({"error": "no reusable photo found"}, ensure_ascii=False))
    sys.exit(1)


if __name__ == "__main__":
    main()
