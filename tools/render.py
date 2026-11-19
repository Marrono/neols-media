"""카드뉴스 렌더러: 뉴스 JSON -> 1080x1350 PNG 카드 묶음.

사용법: python3 render.py news.json out_dir
"""
import html
import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

W, H = 1080, 1350
ACCENT = "#2F5BFF"

BASE_CSS = f"""
* {{ margin:0; padding:0; box-sizing:border-box; }}
html, body {{ width:{W}px; height:{H}px; }}
body {{
  font-family: 'Pretendard', 'Noto Sans CJK KR', 'Noto Sans KR', sans-serif;
  background:#F7F6F2; color:#111; position:relative; overflow:hidden;
  letter-spacing:-0.02em; word-break:keep-all;
}}
.top {{ position:absolute; top:72px; left:88px; right:88px;
  display:flex; justify-content:space-between; align-items:center;
  font-size:26px; font-weight:700; color:#111; }}
.top .brand {{ font-size:34px; font-weight:900; letter-spacing:-0.01em; }} .top .brand i {{ font-style:normal; color:{ACCENT}; }}
.top .date {{ color:#8A8A85; font-weight:500; }}
.rule {{ position:absolute; top:128px; left:88px; right:88px; height:2px; background:#111; }}
.foot {{ position:absolute; bottom:64px; left:88px; right:88px;
  display:flex; justify-content:space-between; font-size:22px; color:#8A8A85; }}
.dot {{ display:inline-block; width:14px; height:14px; border-radius:50%;
  background:{ACCENT}; margin-right:14px; vertical-align:middle; }}
"""


def esc(s):
    return html.escape(s).replace("\n", "<br>")


def page(body, extra_css=""):
    return f"<!DOCTYPE html><html><head><meta charset='utf-8'><style>{BASE_CSS}{extra_css}</style></head><body>{body}</body></html>"


def header(d):
    return (f"<div class='top'><span class='brand'>Ne<i>ol</i>s</span>"
            f"<span class='date'>{d['date']} ({d['weekday']})</span></div><div class='rule'></div>")


def cover(d):
    n = len(d["items"])
    rows = "".join(
        f"<li><span class='n'>{i+1:02d}</span><span class='c'>{esc(it['category'])}</span>"
        f"<span class='t'>{esc(it['title'].replace(chr(10), ' '))}</span></li>"
        for i, it in enumerate(d["items"]))
    css = f"""
    .big {{ position:absolute; top:220px; left:88px; font-size:40px; font-weight:500; color:#8A8A85; }}
    .title {{ position:absolute; top:285px; left:80px; font-size:150px; font-weight:900; line-height:1.05; }}
    .title em {{ font-style:normal; color:{ACCENT}; }} .title .pt {{ color:{ACCENT}; }}
    .slogan {{ position:absolute; top:478px; left:88px; font-size:34px; font-weight:700; color:#111; }}
    .sub {{ position:absolute; top:540px; font-size:32px !important; color:#8A8A85 !important; left:88px; font-size:38px; font-weight:500; color:#333; }}
    ul {{ position:absolute; top:670px; left:88px; right:88px; list-style:none; border-top:1px solid #CFCDC6; }}
    li {{ display:flex; align-items:baseline; padding:30px 0; border-bottom:1px solid #CFCDC6; font-size:32px; }}
    .n {{ width:80px; font-weight:800; color:{ACCENT}; }}
    .c {{ width:130px; color:#8A8A85; font-weight:600; font-size:28px; }}
    .t {{ flex:1; font-weight:700; }}
    """
    body = (header(d)
            + f"<div class='big'>{d['date'][5:].replace('.', '월 ')}일 {d['weekday']}요일</div>"
            + f"<div class='title'>Ne<em>ol</em>s<span class='pt'>.</span></div>"
            + f"<div class='slogan'>{esc(d['slogan'])}</div>"
            + f"<div class='sub'>{esc(d['cover_sub'])}</div>"
            + f"<ul>{rows}</ul>"
            + f"<div class='foot'><span>{d['handle']}</span><span>넘겨서 보기 →</span></div>")
    return page(body, css)


def cover_single(d):
    """소재 1개짜리 카드뉴스 표지: 헤드라인 + THEN 예고."""
    it = d["items"][0]
    m, day = d["date"][5:].split(".")
    css = f"""
    .lab {{ position:absolute; top:220px; left:88px; font-size:34px; font-weight:500; color:#8A8A85; }}
    .cat {{ position:absolute; top:212px; right:88px; font-size:26px; font-weight:700; border:2px solid #111; border-radius:40px; padding:6px 26px; }}
    .title {{ position:absolute; top:330px; left:84px; right:88px; font-size:104px; font-weight:900; line-height:1.18; }}
    .teaser {{ position:absolute; left:88px; right:88px; bottom:150px; background:#111; color:#fff; border-radius:10px; padding:40px 46px; }}
    .teaser .t1 {{ font-size:26px; font-weight:800; letter-spacing:.14em; color:#9DB1FF; }}
    .teaser .t2 {{ margin-top:12px; font-size:60px; font-weight:900; }}
    .teaser .t3 {{ margin-top:10px; font-size:30px; color:#CFCFCA; }}
    """
    ph = it.get("photo")
    if ph:
        import base64, mimetypes
        mt = mimetypes.guess_type(ph["path"])[0] or "image/jpeg"
        b64 = base64.b64encode(open(ph["path"], "rb").read()).decode()
        css += f"""
        .ph {{ position:absolute; top:130px; left:0; right:0; height:560px; background:url(data:{mt};base64,{b64}) center/cover; }}
        .lab {{ top:730px !important; }} .cat {{ top:722px !important; }}
        .title {{ top:790px !important; font-size:72px !important; }}
        .teaser {{ padding:26px 40px !important; }} .teaser .t2 {{ font-size:44px !important; margin-top:6px !important; }} .teaser .t3 {{ font-size:26px !important; }}
        """
        foot_left = f"사진 · {esc(ph['credit'])}"
    else:
        foot_left = d['handle']
    body = (header(d)
            + ("<div class='ph'></div>" if ph else "")
            + f"<div class='lab'>{int(m)}월 {int(day)}일의 뉴스</div><div class='cat'>{esc(it['category'])}</div>"
            + f"<div class='title'>{esc(it['title'])}</div>"
            + f"<div class='teaser'><div class='t1'>THEN</div><div class='t2'>{esc(it['then_label'])}</div>"
            + "<div class='t3'>이 뉴스의 어제로 넘겨 보세요 →</div></div>"
            + f"<div class='foot'><span>{foot_left}</span><span>넘겨서 보기 →</span></div>")
    return page(body, css)


def _bars(v):
    data = v["data"]; mx = max(x[1] for x in data) or 1
    hl = v.get("highlight", len(data) - 1)
    rows = ""
    for k, (lab, val) in enumerate(data):
        w = max(4, val / mx * 100)
        on = k == hl
        rows += (f"<div class='br'><div class='bl'>{esc(str(lab))}</div><div class='bt'>"
                 f"<div class='bf' style='width:{w:.1f}%;background:{ACCENT if on else '#CFCDC6'}'></div></div>"
                 f"<div class='bv' style='color:{ACCENT if on else '#111'}'>{esc(v.get('fmt', '{}').format(val))}</div></div>")
    return f"<div class='bars'>{rows}</div>"


def _timeline(v):
    pts = "".join(f"<div class='tp{' on' if k == len(v['data']) - 1 else ''}'><div class='ty'>{esc(y)}</div>"
                  f"<div class='td'></div><div class='tt'>{esc(t)}</div></div>" for k, (y, t) in enumerate(v["data"]))
    return f"<div class='tl'>{pts}</div>"


def visual_card(d, it):
    """직접 만든 그래픽 페이지: bars / timeline / big. 하단에 자료 출처."""
    v = it["visual"]
    css = f"""
    .vk {{ position:absolute; top:200px; left:88px; font-size:26px; font-weight:800; letter-spacing:.14em; color:{ACCENT}; }}
    .vt {{ position:absolute; top:250px; left:86px; right:88px; font-size:58px; font-weight:900; line-height:1.25; }}
    .vbody {{ position:absolute; top:470px; left:88px; right:88px; bottom:190px; display:flex; flex-direction:column; justify-content:center; }}
    .bars .br {{ display:flex; align-items:center; gap:24px; padding:22px 0; }}
    .bars .bl {{ width:200px; font-size:30px; color:#555; font-weight:500; }}
    .bars .bt {{ flex:1; height:56px; background:#ECEBE6; border-radius:8px; overflow:hidden; }}
    .bars .bf {{ height:100%; border-radius:8px; }}
    .bars .bv {{ width:170px; text-align:right; font-size:36px; font-weight:900; }}
    .tl {{ position:relative; display:flex; flex-direction:column; gap:46px; padding-left:60px; }}
    .tl::before {{ content:''; position:absolute; left:17px; top:20px; bottom:20px; width:4px; background:#CFCDC6; }}
    .tp {{ position:relative; }}
    .tp .td {{ position:absolute; left:-58px; top:12px; width:34px; height:34px; border-radius:50%; background:#F7F6F2; border:5px solid #111; }}
    .tp.on .td {{ background:{ACCENT}; border-color:{ACCENT}; }}
    .tp .ty {{ font-size:46px; font-weight:900; }} .tp.on .ty {{ color:{ACCENT}; }}
    .tp .tt {{ font-size:32px; color:#444; margin-top:6px; line-height:1.4; }}
    .big {{ text-align:center; }} .big .n {{ font-size:220px; font-weight:900; color:{ACCENT}; line-height:1; letter-spacing:-0.04em; }}
    .big .l {{ font-size:40px; font-weight:700; margin-top:30px; }} .big .s {{ font-size:30px; color:#8A8A85; margin-top:16px; }}
    """
    if v["type"] == "bars":
        inner = _bars(v)
    elif v["type"] == "timeline":
        inner = _timeline(v)
    else:
        inner = (f"<div class='big'><div class='n'>{esc(v['value'])}</div><div class='l'>{esc(v['label'])}</div>"
                 + (f"<div class='s'>{esc(v['sub'])}</div>" if v.get('sub') else "") + "</div>")
    body = (header(d) + f"<div class='vk'>BY THE NUMBERS</div><div class='vt'>{esc(v['title'])}</div>"
            + f"<div class='vbody'>{inner}</div>"
            + f"<div class='foot'><span>자료 · {esc(v.get('source', it['source']))} · 그래픽 Neols</span><span>{d['handle']}</span></div>")
    return page(body, css)


def item_card(d, i, it):
    n = len(d["items"])
    pts = "".join(f"<li><span class='dot'></span>{esc(p)}</li>" for p in it["points"])
    css = f"""
    .num {{ position:absolute; top:200px; left:88px; font-size:30px; font-weight:800; color:{ACCENT}; }}
    .num span {{ color:#B5B3AC; font-weight:600; }}
    .cat {{ position:absolute; top:196px; right:88px; font-size:26px; font-weight:700;
      border:2px solid #111; border-radius:40px; padding:6px 26px; }}
    .flow {{ position:absolute; top:280px; left:86px; right:88px; }} .title {{ font-size:84px; font-weight:900; line-height:1.22; }}
    ul {{ margin-top:34px; list-style:none; }}
    li {{ font-size:34px; font-weight:500; line-height:1.45; padding:16px 0; color:#222;
      display:flex; align-items:flex-start; }}
    li .dot {{ margin-top:20px; flex:none; }}
    .then {{ position:absolute; left:88px; right:88px; bottom:140px; background:#111; color:#fff;
      padding:36px 44px; border-radius:8px; }}
    .then .lab {{ font-size:40px; font-weight:900; margin-bottom:14px; }}
    .then .lab span {{ font-size:22px; font-weight:800; letter-spacing:0.14em; color:#9DB1FF;
      border:1.5px solid #9DB1FF; border-radius:30px; padding:4px 16px; margin-right:18px; vertical-align:middle; }}
    .then .old {{ font-size:30px; line-height:1.55; color:#E8E8E4; }}
    .then .now {{ margin-top:18px; padding-top:18px; border-top:1px solid #3A3A3A; font-size:29px; line-height:1.5; color:#fff; }}
    .then .now b {{ color:#9DB1FF; }}
    .why {{ position:absolute; left:88px; right:88px; bottom:150px; background:#fff;
      border-left:8px solid {ACCENT}; padding:34px 40px; border-radius:6px; }}
    .why b {{ display:block; font-size:26px; color:{ACCENT}; margin-bottom:12px; letter-spacing:0.02em; }}
    .why p {{ font-size:31px; line-height:1.55; color:#222; }}
    """
    body = (header(d)
            + (f"<div class='num'>{i+1:02d} <span>/ {n:02d}</span></div>" if n > 1 else f"<div class='num'>NOW</div>")
            + f"<div class='cat'>{esc(it['category'])}</div>"
            + f"<div class='flow'><div class='title'>{esc(it['title'])}</div>"
            + f"<ul>{pts}</ul></div>"
            + f"<div class='then'><div class='lab'><span>THEN</span>{esc(it['then_label'])}</div>"
              f"<p class='old'>{esc(it['then'])}</p><p class='now'><b>NOW →</b> {esc(it['link'])}</p></div>"
            + f"<div class='foot'><span>출처 · {esc(it['source'])}</span><span>{d['handle']}</span></div>")
    return page(body, css)


LOGO_SVG = """<svg width="%d" height="%d" viewBox="0 0 1080 1080" xmlns="http://www.w3.org/2000/svg">
<circle cx="540" cy="540" r="540" fill="#111"/>
<polyline points="350,760 350,320 730,760 730,320" fill="none" stroke="#F7F6F2" stroke-width="44" stroke-linejoin="round" stroke-linecap="round"/>
<circle cx="350" cy="760" r="54" fill="#111" stroke="#F7F6F2" stroke-width="20"/>
<circle cx="730" cy="320" r="62" fill="#2F5BFF"/></svg>"""


def outro(d):
    """계정 홍보 페이지 — 모든 카드뉴스의 마지막 장."""
    css = f"""
    .promo {{ position:absolute; top:190px; left:88px; right:88px; bottom:150px;
      display:flex; flex-direction:column; align-items:center; text-align:center; }}
    .eq {{ margin-top:34px; font-size:30px; font-weight:700; color:#8A8A85; letter-spacing:0.02em; }}
    .eq b {{ color:{ACCENT}; }}
    .name {{ margin-top:6px; font-size:120px; font-weight:900; line-height:1.05; }}
    .name i {{ font-style:normal; color:{ACCENT}; }}
    .slo {{ margin-top:18px; font-size:36px; font-weight:700; }}
    .feat {{ margin-top:48px; width:100%; border-top:1px solid #CFCDC6; }}
    .feat div {{ display:flex; justify-content:space-between; padding:22px 6px; border-bottom:1px solid #CFCDC6;
      font-size:30px; }}
    .feat span {{ color:#8A8A85; font-weight:500; }} .feat b {{ font-weight:700; }}
    .cta {{ margin-top:auto; background:#111; color:#fff; border-radius:80px; padding:26px 56px;
      font-size:36px; font-weight:800; }}
    .cta i {{ font-style:normal; color:#9DB1FF; }}
    """
    body = (header(d)
            + "<div class='promo'>" + (LOGO_SVG % (190, 190))
            + "<div class='eq'>News + <b>old</b> =</div>"
            + "<div class='name'>Ne<i>ol</i>s</div>"
            + f"<div class='slo'>{esc(d.get('slogan', '잊혀진 뉴스와 오늘의 뉴스를 잇다'))}</div>"
            + "<div class='feat'><div><span>매일 아침</span><b>꼭 알아야 할 국내 뉴스</b></div>"
            + "<div><span>THEN → NOW</span><b>그 뉴스의 어제까지</b></div>"
            + "<div><span>저장해 두면</span><b>뉴스의 흐름이 보여요</b></div></div>"
            + f"<div class='cta'>{esc(d['handle'])} <i>팔로우하기</i></div></div>"
            + "<div class='foot'><span>오늘의 뉴스에도 어제가 있어요</span><span>내일 또 만나요</span></div>")
    return page(body, css)


def render(data, out_dir):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    single = len(data["items"]) == 1
    first = cover_single(data) if single else cover(data)
    vis = [visual_card(data, data["items"][0])] if single and data["items"][0].get("visual") else []
    pages = [first] + vis + [item_card(data, i, it) for i, it in enumerate(data["items"])] + [outro(data)]
    paths = []
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
        pg = browser.new_page(viewport={"width": W, "height": H})
        for k, h in enumerate(pages, 1):
            pg.set_content(h)
            pg.wait_for_timeout(150)
            path = out / f"card_{k:02d}.png"
            pg.screenshot(path=str(path))
            paths.append(path)
        browser.close()
    return paths


if __name__ == "__main__":
    d = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    for p in render(d, sys.argv[2]):
        print(p)
