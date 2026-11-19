"""네이버 뉴스 '언론사별 많이 본 뉴스' 랭킹 수집.

사용법: python3 naver_rank.py [--json]
- news.naver.com 이 네트워크 허용 목록에 있어야 동작해요.
- 같은 사건을 여러 언론사가 상위에 올렸는지 보는 게 '급상승' 판단의 핵심이라,
  제목 목록과 함께 자주 나온 단어(2글자 이상) 상위 목록도 출력해요.
"""
import collections
import html
import json
import re
import sys
import urllib.request

URL = "https://news.naver.com/main/ranking/popularDay.naver"
UA = {"User-Agent": "Mozilla/5.0 (NeolsCardBot/1.0; +https://www.instagram.com/neols.news/)"}
STOP = set("단독 속보 종합 영상 포토 오늘 이번 관련 정부 대통령 사진 기자 뉴스 위해 대한 이유 결국 지금 이제 우리".split())


def fetch():
    with urllib.request.urlopen(urllib.request.Request(URL, headers=UA), timeout=30) as r:
        raw = r.read()
    for enc in ("utf-8", "euc-kr"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            pass
    return raw.decode("utf-8", "ignore")


def parse(page):
    items = []
    # 언론사 블록별로 나누고, 블록 안의 제목 링크를 순서대로 모음
    for block in re.split(r'class="rankingnews_box"', page)[1:]:
        press = re.search(r'class="rankingnews_name"[^>]*>(.*?)<', block, re.S)
        press = html.unescape(press.group(1)).strip() if press else "?"
        for rank, m in enumerate(re.finditer(r'<a[^>]+href="([^"]+)"[^>]*class="list_title[^"]*"[^>]*>(.*?)</a>', block, re.S), 1):
            title = html.unescape(re.sub(r"<[^>]+>", "", m.group(2))).strip()
            if title:
                items.append({"press": press, "rank": rank, "title": title, "url": m.group(1)})
    return items


def keywords(items, top=25):
    c = collections.Counter()
    for it in items:
        words = set(w for w in re.findall(r"[가-힣A-Za-z0-9]{2,}", it["title"]) if w not in STOP)
        c.update(words)
    return c.most_common(top)


if __name__ == "__main__":
    items = parse(fetch())
    if "--json" in sys.argv:
        print(json.dumps({"items": items, "keywords": keywords(items)}, ensure_ascii=False))
    else:
        print("자주 나온 단어:", ", ".join(f"{w}({n})" for w, n in keywords(items)))
        for it in items:
            if it["rank"] <= 3:
                print(f"[{it['press']} {it['rank']}] {it['title']}")
