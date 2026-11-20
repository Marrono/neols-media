"""Neols '시네마' 템플릿 — 카드뉴스(1080x1350)와 릴스(1080x1920) 공통.

사진을 화면 가득 깔고, 어두운 그라데이션 위에 흰 글씨. THEN은 흑백·필름 질감.
JSON 추가 항목(선택):
  photos: [{path, credit}, ...]  → 0번 표지·NOW, 1번 숫자 장면(없으면 0번 재사용)
  reel: {hook:"1줄\\n2줄", stat:{label, value}, chips:[["down"|"up", "텍스트"]],
         then_head:"한 줄 요약", then_sub:"보충 설명"}
"""
import base64
import html
import mimetypes
import os
import re
import subprocess

ACCENT, LIGHT = "#2F5BFF", "#7D97FF"


def esc(s):
    return html.escape(str(s)).replace("\n", "<br>")


def data_url(p):
    mt = mimetypes.guess_type(p)[0] or "image/jpeg"
    return f"data:{mt};base64," + base64.b64encode(open(p, "rb").read()).decode()


def photos(it):
    ps = list(it.get("photos") or ([it["photo"]] if it.get("photo") else []))
    return [p for p in ps if p and os.path.exists(p["path"])]


def hook(it):
    r = it.get("reel", {})
    return r.get("hook") or it["title"]


def stat(it):
    r = it.get("reel", {})
    if r.get("stat"):
        return r["stat"]
    vs = it.get("visuals") or ([it["visual"]] if it.get("visual") else [])
    for v in vs:
        if v["type"] == "big":
            return {"label": v["label"], "value": v["value"]}
        if v["type"] == "bars":
            hl = v.get("highlight", len(v["data"]) - 1); lab, val = v["data"][hl]
            return {"label": f"{v['title'].replace(chr(10), ' ')} · {lab}", "value": v.get("fmt", "{}").format(val)}
    return None


def then_parts(it):
    r = it.get("reel", {})
    head = r.get("then_head") or it["then"].split(". ")[0].rstrip(".")
    sub = r.get("then_sub") or ""
    return head, sub


def year_of(s):
    m = re.search(r"(1[89]\d\d|20\d\d)", s or "")
    return int(m.group(1)) if m else None


GRAIN = ("<svg class='grain' width='100%' height='100%'><filter id='gn'><feTurbulence id='tb' type='fractalNoise' "
         "baseFrequency='.9' numOctaves='2' seed='3'/></filter><rect width='100%' height='100%' filter='url(#gn)'/></svg>")

COMMON = f"""
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'Noto Sans CJK KR',sans-serif;letter-spacing:-0.03em;word-break:keep-all;position:relative;overflow:hidden;background:#0B0B0C;color:#fff}}
.bg{{position:absolute;inset:0;background-size:cover;background-position:center}}
.shade{{position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,.6) 0%,rgba(0,0,0,.08) 28%,rgba(0,0,0,.3) 55%,rgba(0,0,0,.88) 100%)}}
.grain{{position:absolute;inset:0;mix-blend-mode:overlay;opacity:.5}}
.brand{{font-weight:900}} .brand i{{font-style:normal;color:{LIGHT}}}
.tag{{font-weight:700;border:2px solid #fff;border-radius:40px}}
.hl{{position:relative;display:inline-block;z-index:0}}
.hl:after{{content:'';position:absolute;left:0;bottom:.08em;height:.24em;width:var(--w,100%);background:{ACCENT};z-index:-1}}
.chip{{display:inline-flex;align-items:center;gap:12px;font-weight:900;border-radius:60px;color:#fff}}
.dn{{background:{ACCENT}}} .up{{background:#FF4B3E}}
.cred{{color:rgba(255,255,255,.72);font-weight:500}}
"""


# ═════════════════════════ 카드뉴스 ═════════════════════════
CW, CH = 1080, 1350

CARD_CSS = COMMON + f"""
html,body{{width:{CW}px;height:{CH}px}}
.segs{{position:absolute;top:56px;left:72px;right:72px;display:flex;gap:8px}}
.segs div{{flex:1;height:5px;border-radius:5px;background:rgba(255,255,255,.28)}} .segs div.on{{background:#fff}}
.top{{position:absolute;top:84px;left:72px;right:72px;display:flex;justify-content:space-between;align-items:center}}
.top .brand{{font-size:36px}} .top .tag{{font-size:22px;padding:5px 18px}}
.foot{{position:absolute;left:72px;right:72px;bottom:46px;display:flex;justify-content:space-between;font-size:21px}}
.foot span:last-child{{color:rgba(255,255,255,.85);font-weight:700}}
"""


def _page(css, body):
    return f"<!DOCTYPE html><html><head><meta charset='utf-8'><style>{CARD_CSS}{css}</style></head><body>{body}</body></html>"


def _chrome(d, k, n, tag, left_foot, right_foot=None):
    segs = "".join(f"<div class='{'on' if i <= k else ''}'></div>" for i in range(n))
    return (f"<div class='segs'>{segs}</div><div class='top'><span class='brand'>Ne<i>ol</i>s</span>"
            f"<span class='tag'>{esc(tag)}</span></div>"
            f"<div class='foot cred'><span>{left_foot}</span><span>{esc(right_foot or d['handle'])}</span></div>")


def _bg(ph, style=""):
    return f"<div class='bg' style=\"background-image:url({data_url(ph['path'])});{style}\"></div>" if ph else ""


def _now_tag(d):
    return f"NOW · {d['date'][:7]}"


def c_cover(d, it, ps, k, n):
    h = hook(it).split("\n")
    h_html = esc(h[0]) + ("<br><span class='hl'>" + esc(" ".join(h[1:])) + "</span>" if len(h) > 1 else "")
    ph = ps[0] if ps else None
    css = """
    .cat{position:absolute;left:72px;bottom:410px;font-size:28px;font-weight:700;color:rgba(255,255,255,.85)}
    .hook{position:absolute;left:72px;right:110px;bottom:200px;font-size:96px;font-weight:900;line-height:1.18}
    .nx{position:absolute;left:72px;right:72px;bottom:112px;display:flex;align-items:center;gap:16px;font-size:26px;font-weight:700;color:rgba(255,255,255,.9)}
    .nx b{font-size:22px;letter-spacing:.12em;border:2px solid currentColor;border-radius:30px;padding:3px 14px}
    """ + ("" if ph else ".bg0{position:absolute;inset:0;background:radial-gradient(circle at 70% 25%,#1d2a66 0,#0B0B0C 60%)}")
    body = ((_bg(ph, "transform:scale(1.04)") if ph else "<div class='bg0'></div>") + "<div class='shade'></div>"
            + _chrome(d, k, n, _now_tag(d), f"사진 · {esc(ph['credit'])}" if ph else "", "넘겨서 보기 →")
            + f"<div class='cat'>{esc(it['category'])} · {int(d['date'][5:7])}월 {int(d['date'][8:10])}일의 뉴스</div>"
            + f"<div class='hook'>{h_html}</div>"
            + f"<div class='nx'><b>THEN</b>{esc(it['then_label'])} — 이 뉴스의 어제까지</div>")
    return _page(css, body)


def c_visual(d, it, v, ps, k, n):
    ph = ps[1] if len(ps) > 1 else (ps[0] if ps else None)
    css = f"""
    .dim{{position:absolute;inset:0;background:rgba(8,8,10,.78)}}
    .vk{{position:absolute;top:190px;left:72px;font-size:24px;font-weight:800;letter-spacing:.14em;color:{LIGHT}}}
    .vt{{position:absolute;top:236px;left:72px;right:100px;font-size:58px;font-weight:900;line-height:1.25}}
    .vb{{position:absolute;top:470px;left:72px;right:90px;bottom:150px;display:flex;flex-direction:column;justify-content:center}}
    .br{{display:flex;align-items:center;gap:22px;padding:20px 0}} .bl{{width:200px;font-size:30px;color:#ddd}}
    .bt{{flex:1;height:54px;background:rgba(255,255,255,.14);border-radius:8px;overflow:hidden}} .bf{{height:100%;border-radius:8px}}
    .bv{{width:170px;text-align:right;font-size:36px;font-weight:900}}
    .tl{{position:relative;display:flex;flex-direction:column;gap:42px;padding-left:60px}}
    .tl:before{{content:'';position:absolute;left:17px;top:20px;bottom:20px;width:4px;background:rgba(255,255,255,.25)}}
    .tp{{position:relative}} .td{{position:absolute;left:-58px;top:12px;width:34px;height:34px;border-radius:50%;background:#0B0B0C;border:5px solid #fff}}
    .tp.on .td{{background:{ACCENT};border-color:{ACCENT}}} .ty{{font-size:46px;font-weight:900}} .tp.on .ty{{color:{LIGHT}}}
    .tt{{font-size:31px;color:#d6d6d6;margin-top:6px;line-height:1.4}}
    .big .n{{font-size:230px;font-weight:900;line-height:1;letter-spacing:-0.04em}} .big .l{{font-size:40px;font-weight:700;margin-top:26px}}
    .big .s{{font-size:30px;color:#bbb;margin-top:14px}}
    """
    if v["type"] == "bars":
        mx = max(x[1] for x in v["data"]) or 1; hl = v.get("highlight", len(v["data"]) - 1)
        inner = "".join(
            f"<div class='br'><div class='bl'>{esc(l)}</div><div class='bt'><div class='bf' style='width:{max(4, val / mx * 100):.1f}%;"
            f"background:{ACCENT if j == hl else 'rgba(255,255,255,.45)'}'></div></div>"
            f"<div class='bv' style='color:{LIGHT if j == hl else '#fff'}'>{esc(v.get('fmt', '{}').format(val))}</div></div>"
            for j, (l, val) in enumerate(v["data"]))
    elif v["type"] == "timeline":
        inner = "<div class='tl'>" + "".join(
            f"<div class='tp{' on' if j == len(v['data']) - 1 else ''}'><div class='ty'>{esc(y)}</div><div class='td'></div>"
            f"<div class='tt'>{esc(t)}</div></div>" for j, (y, t) in enumerate(v["data"])) + "</div>"
    else:
        inner = (f"<div class='big'><div class='n'>{esc(v['value'])}</div><div class='l'>{esc(v['label'])}</div>"
                 + (f"<div class='s'>{esc(v['sub'])}</div>" if v.get("sub") else "") + "</div>")
    body = (_bg(ph, "filter:blur(6px);transform:scale(1.08)") + "<div class='dim'></div>"
            + _chrome(d, k, n, _now_tag(d), f"자료 · {esc(v.get('source', it['source']))} · 그래픽 Neols")
            + f"<div class='vk'>BY THE NUMBERS</div><div class='vt'>{esc(v['title'])}</div><div class='vb'>{inner}</div>")
    return _page(css, body)


def c_now(d, it, ps, k, n, with_then):
    ph = ps[0] if ps else None
    st = stat(it); chips = it.get("reel", {}).get("chips", [])
    css = f"""
    .dim{{position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,.72),rgba(0,0,0,.6) 40%,rgba(0,0,0,.9))}}
    .flow{{position:absolute;top:190px;left:72px;right:100px}}
    .k{{font-size:24px;font-weight:800;letter-spacing:.14em;color:{LIGHT}}}
    .t{{margin-top:14px;font-size:76px;font-weight:900;line-height:1.2}}
    .chips{{margin-top:30px;display:flex;flex-wrap:wrap;gap:14px}} .chip{{font-size:32px;padding:10px 24px}}
    ul{{margin-top:30px;list-style:none}} li{{font-size:33px;line-height:1.45;padding:12px 0;display:flex;color:#eee}}
    li:before{{content:'';flex:none;width:14px;height:14px;border-radius:50%;background:{LIGHT};margin:18px 18px 0 0}}
    .then{{position:absolute;left:72px;right:72px;bottom:110px;border:2px solid rgba(255,255,255,.5);border-radius:10px;padding:28px 34px;background:rgba(0,0,0,.35)}}
    .then .lab{{font-size:36px;font-weight:900}} .then .lab b{{font-size:20px;letter-spacing:.14em;border:2px solid #fff;padding:2px 12px;margin-right:14px;vertical-align:middle}}
    .then p{{font-size:28px;line-height:1.5;color:#ddd;margin-top:10px}} .then .nw{{color:#fff}} .then .nw b{{color:{LIGHT}}}
    """
    ch = "".join(f"<span class='chip {'up' if c[0] == 'up' else 'dn'}'>{'▲' if c[0] == 'up' else '▼'} {esc(c[1])}</span>" for c in chips)
    pts = "".join(f"<li>{esc(p)}</li>" for p in it["points"])
    then = ("" if not with_then else
            f"<div class='then'><div class='lab'><b>THEN</b>{esc(it['then_label'])}</div><p>{esc(it['then'])}</p>"
            f"<p class='nw'><b>NOW →</b> {esc(it['link'])}</p></div>")
    body = (_bg(ph, "transform:scale(1.15) translateY(-20px)") + "<div class='dim'></div>"
            + _chrome(d, k, n, _now_tag(d), f"출처 · {esc(it['source'])}")
            + f"<div class='flow'><div class='k'>NOW · {esc(it['category'])}</div><div class='t'>{esc(it['title'])}</div>"
            + (f"<div class='chips'>{ch}</div>" if ch else "") + f"<ul>{pts}</ul></div>{then}")
    return _page(css, body)


def c_then(d, it, ps, k, n):
    ph = ps[0] if ps else None
    y = year_of(it["then_label"]); head, sub = then_parts(it)
    css = f"""
    .dim{{position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,.7),rgba(0,0,0,.45) 35%,rgba(0,0,0,.92))}}
    .st{{position:absolute;top:200px;left:72px;font-size:64px;font-weight:900;letter-spacing:.06em;border:5px solid #fff;padding:2px 24px}}
    .y{{position:absolute;top:320px;left:66px;font-size:200px;font-weight:900;line-height:1;letter-spacing:-0.03em}}
    .lb{{position:absolute;top:530px;left:72px;font-size:30px;font-weight:700;color:#E8E1C8}}
    .h{{position:absolute;top:600px;left:72px;right:100px;font-size:52px;font-weight:900;line-height:1.3}}
    .s{{margin-top:16px;font-size:32px;font-weight:500;color:#ddd;line-height:1.5}}
    ul{{margin-top:22px;list-style:none}} li{{font-size:30px;line-height:1.5;color:#d9d3c0;padding:6px 0;display:flex}}
    li:before{{content:'—';margin-right:14px;color:#E8E1C8}}
    .nw{{position:absolute;left:72px;right:100px;bottom:110px;border-top:1px solid rgba(255,255,255,.35);padding-top:24px;font-size:32px;line-height:1.5;font-weight:700}}
    .nw b{{color:{LIGHT}}}
    """
    pts = "".join(f"<li>{esc(p)}</li>" for p in it.get("then_points", []))
    body = (_bg(ph, "filter:grayscale(1) sepia(.4) contrast(1.15);transform:scale(1.2)") + "<div class='dim'></div>" + GRAIN
            + _chrome(d, k, n, f"THEN · {it['then_label']}", f"출처 · {esc(it.get('then_source', it['source']))}")
            + "<div class='st'>THEN</div>"
            + f"<div class='y'>{y if y else esc(it['then_label'])}</div>"
            + (f"<div class='lb'>{esc(it['then_label'])}</div>" if y else "")
            + f"<div class='h'>{esc(head)}" + (f"<div class='s'>{esc(sub)}</div>" if sub else "")
            + (f"<ul>{pts}</ul>" if pts else "") + "</div>"
            + f"<div class='nw'><b>NOW →</b> {esc(it['link'])}</div>")
    return _page(css, body)


def c_extra(d, it, ex, ps, k, n):
    ph = ps[-1] if ps else None
    css = f"""
    .dim{{position:absolute;inset:0;background:rgba(8,8,10,.86)}}
    .k{{position:absolute;top:190px;left:72px;font-size:24px;font-weight:800;letter-spacing:.14em;color:{LIGHT}}}
    .t{{position:absolute;top:236px;left:72px;right:100px;font-size:62px;font-weight:900;line-height:1.25}}
    ol{{position:absolute;top:500px;left:72px;right:100px;list-style:none;counter-reset:n}}
    ol li{{counter-increment:n;font-size:34px;line-height:1.5;padding:22px 0 22px 78px;position:relative;border-top:1px solid rgba(255,255,255,.2)}}
    ol li:before{{content:counter(n,decimal-leading-zero);position:absolute;left:0;top:22px;font-weight:900;color:{LIGHT}}}
    """
    lis = "".join(f"<li>{esc(x)}</li>" for x in ex["lines"])
    body = (_bg(ph, "filter:blur(10px);transform:scale(1.1)") + "<div class='dim'></div>"
            + _chrome(d, k, n, _now_tag(d), f"출처 · {esc(ex.get('source', it['source']))}")
            + f"<div class='k'>{esc(ex.get('kicker', 'MORE'))}</div><div class='t'>{esc(ex['title'])}</div><ol>{lis}</ol>")
    return _page(css, body)


def c_outro(d, k, n):
    css = f"""
    body{{background:#F7F6F2;color:#111}}
    .segs div{{background:#DDDBD3}} .segs div.on{{background:#111}} .top .tag{{border-color:#111}} .brand i{{color:{ACCENT}}}
    .foot{{color:#8A8A85}} .foot span:last-child{{color:#111}}
    .c{{position:absolute;inset:0;display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center}}
    .eq{{font-size:30px;font-weight:700;color:#8A8A85}} .eq b{{color:{ACCENT}}}
    .nm{{font-size:190px;font-weight:900;line-height:1.05}} .nm i{{font-style:normal;color:{ACCENT}}}
    .sl{{font-size:38px;font-weight:700;margin-top:14px}}
    .ft{{margin-top:50px;font-size:30px;color:#555;line-height:1.7}}
    .cta{{margin-top:56px;background:#111;color:#fff;border-radius:80px;padding:24px 60px;font-size:38px;font-weight:900}} .cta i{{font-style:normal;color:{LIGHT}}}
    """
    body = (_chrome(d, k, n, "Neols", "오늘의 뉴스에도 어제가 있어요", "내일 또 만나요")
            + "<div class='c'><div class='eq'>News + <b>old</b> =</div><div class='nm'>Ne<i>ol</i>s</div>"
            + f"<div class='sl'>{esc(d.get('slogan', '잊혀진 뉴스와 오늘의 뉴스를 잇다'))}</div>"
            + "<div class='ft'>매일 꼭 알아야 할 국내 뉴스<br>그리고 그 뉴스의 어제까지</div>"
            + f"<div class='cta'>{esc(d['handle'])} <i>팔로우하기</i></div></div>")
    return _page(css, body)


def card_pages(d):
    """소재 1개 카드뉴스(4~8장): 표지 → 그래픽(0~2) → NOW(+THEN 상자) 또는 NOW/THEN → 추가 설명 → 홍보."""
    it = d["items"][0]; ps = photos(it)
    visuals = (it.get("visuals") or ([it["visual"]] if it.get("visual") else []))[:2]
    extras = list(it.get("extras", []))
    split = bool(it.get("split_then") or it.get("then_points"))
    cnt = lambda: 1 + len(visuals) + (2 if split else 1) + len(extras) + 1
    if cnt() < 4:
        split = True
    if cnt() < 4:
        extras.append({"kicker": "SUMMARY", "title": "한눈에 정리", "lines": it["points"]})
    while cnt() > 8 and extras:
        extras.pop()
    while cnt() > 8 and visuals:
        visuals.pop()
    n = cnt(); k = 0; pages = []
    pages.append(c_cover(d, it, ps, k, n)); k += 1
    for v in visuals:
        pages.append(c_visual(d, it, v, ps, k, n)); k += 1
    pages.append(c_now(d, it, ps, k, n, not split)); k += 1
    if split:
        pages.append(c_then(d, it, ps, k, n)); k += 1
    for ex in extras:
        pages.append(c_extra(d, it, ex, ps, k, n)); k += 1
    pages.append(c_outro(d, k, n))
    return pages


# ═════════════════════════ 릴스 ═════════════════════════
RW, RH, FPS, DUR = 1080, 1920, 30, 15.0


def reel_html(d):
    it = d["items"][0]; ps = photos(it)
    p1 = data_url(ps[0]["path"]) if ps else ""
    p2 = data_url(ps[1]["path"]) if len(ps) > 1 else p1
    c1 = f"사진 · {ps[0]['credit']}" if ps else ""
    c2 = f"사진 · {ps[1]['credit']}" if len(ps) > 1 else c1
    h = hook(it).split("\n"); h1 = esc(h[0]); h2 = esc(" ".join(h[1:])) if len(h) > 1 else ""
    st = stat(it); chips = it.get("reel", {}).get("chips", [])
    head, sub = then_parts(it)
    ny = int(d["date"][:4]); ty = year_of(it["then_label"])
    pts = it["points"]
    link_words = esc(it["link"]).split(" ")
    mid = ("<div class='abs lbl' id='lbl'>%s</div><div class='abs big' id='big'>%s</div>" % (esc(st["label"]), esc(st["value"]))
           if st else "<div class='abs pts' id='pts'>" + "".join(f"<div class='pt'>{esc(p)}</div>" for p in pts) + "</div>")
    chip_html = "".join(f"<span class='chip {'up' if c[0] == 'up' else 'dn'}' id='c{j}'>{'▲' if c[0] == 'up' else '▼'} {esc(c[1])}</span>"
                        for j, c in enumerate(chips))
    bg1 = f"background-image:url({p1})" if p1 else "background:radial-gradient(circle at 70% 25%,#1d2a66 0,#0B0B0C 60%)"
    bg2 = f"background-image:url({p2})" if p2 else "background:radial-gradient(circle at 30% 30%,#1d2a66 0,#0B0B0C 60%)"
    then_title = (f"{ty}" if ty else esc(it["then_label"]))
    css = COMMON + f"""
html,body{{width:{RW}px;height:{RH}px}}
.abs{{position:absolute}} .ph{{position:absolute;inset:0;background-size:cover;background-position:center}}
.prog{{position:absolute;top:110px;left:80px;right:80px;height:6px;background:rgba(255,255,255,.25);border-radius:6px}}
.prog b{{display:block;height:100%;background:#fff;border-radius:6px;width:0}}
.top{{position:absolute;top:150px;left:80px;right:80px;display:flex;justify-content:space-between;align-items:center}}
.top .brand{{font-size:40px}} .top .tag{{font-size:28px;padding:6px 20px}}
.hook{{left:80px;right:150px;bottom:620px;font-size:112px;font-weight:900;line-height:1.18}} .hook>span{{display:block}}
.lbl{{left:86px;top:790px;font-size:46px;font-weight:700;right:150px}} .big{{left:80px;top:860px;font-size:250px;font-weight:900;line-height:1;white-space:nowrap}}
.pts{{left:80px;right:150px;top:760px}} .pt{{font-size:58px;font-weight:900;line-height:1.3;margin-bottom:34px}}
.chips{{left:80px;top:1170px;display:flex;flex-direction:column;gap:22px;align-items:flex-start}} .chip{{font-size:46px;padding:14px 30px}}
.then{{left:80px;top:700px;font-size:80px;font-weight:900;letter-spacing:.06em;border:6px solid #fff;padding:6px 30px}}
.yr{{left:80px;top:860px;font-size:230px;font-weight:900;font-variant-numeric:tabular-nums;line-height:1}}
.tf{{left:80px;right:150px;top:1140px;font-size:60px;font-weight:900;line-height:1.35}} .tf small{{display:block;font-size:40px;font-weight:500;color:#ddd;margin-top:14px}}
.link{{left:80px;right:150px;top:760px;font-size:70px;font-weight:900;line-height:1.38}} .link .w{{opacity:.15}}
.end{{inset:0;display:flex;flex-direction:column;justify-content:center;align-items:center;background:#F7F6F2;color:#111}}
.end .lg{{font-size:200px;font-weight:900}} .end .lg i{{font-style:normal;color:{ACCENT}}}
.end p{{font-size:46px;font-weight:700;margin-top:24px;color:#555}} .end .fo{{margin-top:60px;background:#111;color:#fff;font-size:44px;font-weight:900;padding:22px 60px;border-radius:80px}}
.credit{{left:80px;bottom:300px;font-size:24px}}
.grain{{inset:-50px;opacity:0}}
"""
    body = f"""
<div class="ph" id="p1" style="{bg1}"></div><div class="ph" id="p2" style="{bg2};opacity:0"></div>
<div class="shade"></div>
<svg class="grain abs" id="gr" width="1180" height="2020"><filter id="n"><feTurbulence id="tb" type="fractalNoise" baseFrequency=".9" numOctaves="2" seed="1"/></filter><rect width="100%" height="100%" filter="url(#n)"/></svg>
<div class="prog"><b id="pb"></b></div>
<div class="top"><span class="brand">Ne<i>ol</i>s</span><span class="tag" id="tag"></span></div>
<div class="abs hook" id="hook"><span id="h1">{h1}</span>{f'<span id="h2"><span class="hl" id="hl">{h2}</span></span>' if h2 else '<span id="h2"></span>'}</div>
{mid}
<div class="abs chips">{chip_html}</div>
<div class="abs then" id="then">THEN</div>
<div class="abs yr" id="yr">{then_title}</div>
<div class="abs tf" id="tf">{esc(head)}{f'<small>{esc(sub)}</small>' if sub else ''}</div>
<div class="abs link" id="link">{' '.join(f"<span class='w'>{w}</span>" for w in link_words)}</div>
<div class="abs cred credit" id="cred"></div>
<div class="abs end" id="end"><div class="lg">Ne<i>ol</i>s</div><p>{esc(d.get('slogan', '잊혀진 뉴스와 오늘의 뉴스를 잇다'))}</p><div class="fo">{esc(d['handle'])} 팔로우</div></div>
"""
    js = f"""
const $=s=>document.querySelector(s);
const P=(t,a,b)=>Math.min(1,Math.max(0,(t-a)/(b-a)));const E=x=>1-Math.pow(1-x,3);
const BK=x=>{{const c=1.7;return 1+(c+1)*Math.pow(x-1,3)+c*Math.pow(x-1,2)}};
function set(el,o,tf,ex){{el=typeof el==='string'?$(el):el;if(!el)return;el.style.opacity=o;if(tf!==undefined)el.style.transform=tf;if(ex)Object.assign(el.style,ex)}}
function win(t,a,b,fi=.3,fo=.3){{return Math.min(P(t,a,a+fi),1-P(t,b-fo,b))}}
const NY={ny}, TY={ty if ty else 'null'}, NTAG="NOW · {d['date'][:7]}", TTAG="THEN · {esc(it['then_label'])}";
const C1={c1!r}, C2={c2!r}, NCH={len(chips)}, HASST={'true' if st else 'false'};
function draw(t){{
 $('#pb').style.width=(t/{DUR}*100)+'%';
 const gray=P(t,6.6,7.2)*(1-P(t,10.4,10.8));
 set('#p1',1-win(t,3.0,6.6,.25,.25),`scale(${{1.08+0.14*t/15}}) translateY(${{-30*t/15}}px)`,{{filter:`grayscale(${{gray}}) sepia(${{gray*.35}}) contrast(${{1+gray*.15}}) blur(${{P(t,10.4,10.9)*14}}px) brightness(${{1-P(t,10.4,10.9)*.45}})`}});
 set('#p2',win(t,3.0,6.6,.25,.25),`scale(${{1.15+0.12*P(t,3,6.6)}}) translateX(${{-40*P(t,3,6.6)}}px)`);
 $('#gr').style.opacity=gray*.55;$('#tb').setAttribute('seed',Math.floor(t*15));
 $('#tag').textContent=(t>=6.6&&t<10.5)?TTAG:NTAG;
 const out=P(t,2.7,3.0),h2=E(P(t,-.2,.35));
 set('#h1',1-out,`scale(${{1.06-0.06*E(P(t,0,.5))}}) translateY(${{-out*40}}px)`,{{transformOrigin:'left bottom'}});
 set('#h2',h2*(1-out),`translateY(${{(1-h2)*60-out*40}}px)`);
 const hl=$('#hl'); if(hl) hl.style.setProperty('--w',(E(P(t,.4,1.0))*100)+'%');
 const bo=P(t,6.3,6.6);
 if(HASST){{const bi=BK(P(t,3.15,3.6));
  set('#lbl',P(t,3.1,3.4)*(1-bo),`translateY(${{(1-P(t,3.1,3.4))*20}}px)`);
  set('#big',P(t,3.15,3.35)*(1-bo),`scale(${{0.6+0.4*bi}})`,{{transformOrigin:'left center'}});}}
 else document.querySelectorAll('.pt').forEach((p,i)=>{{const a=E(P(t,3.1+i*.6,3.5+i*.6));set(p,a*(1-bo),`translateX(${{(1-a)*-120}}px)`)}});
 for(let j=0;j<NCH;j++){{const c=E(P(t,4.0+j*.5,4.4+j*.5));set('#c'+j,c*(1-bo),`translateX(${{(1-c)*-200}}px)`)}}
 const th=BK(P(t,6.7,7.05)),tho=P(t,10.2,10.5);
 set('#then',P(t,6.7,6.8)*(1-tho),`scale(${{2-th}}) rotate(${{-4+4*th}}deg)`,{{transformOrigin:'left center'}});
 if(TY&&TY<NY){{$('#yr').textContent=Math.round(NY-(NY-TY)*E(P(t,7.0,8.0)))}}
 set('#yr',P(t,6.95,7.1)*(1-tho),'none');
 const tf=E(P(t,8.1,8.6));set('#tf',tf*(1-tho),`translateY(${{(1-tf)*40}}px)`);
 set('#link',win(t,10.5,13.0,.2,.3),'none');
 const ws=document.querySelectorAll('#link .w'),step=Math.min(.17,1.6/Math.max(1,ws.length));
 ws.forEach((w,i)=>w.style.opacity=.15+.85*E(P(t,10.6+i*step,10.85+i*step)));
 const cr=$('#cred'); cr.textContent=(t>=3&&t<6.6)?C2:C1; cr.style.opacity=(t<13)?(1-P(t,12.7,13)):0;
 const en=E(P(t,13.0,13.4));set('#end',en,`translateY(${{(1-en)*80}}px)`);
}}"""
    return f"<!DOCTYPE html><html><head><meta charset='utf-8'><style>{css}</style></head><body>{body}<script>{js}</script></body></html>"


def make_reel(d, out_mp4, frames=None, cover=None):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        br = p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
        pg = br.new_page(viewport={"width": RW, "height": RH})
        import tpl
        pg.set_content(tpl.reel_html25(d)); pg.wait_for_timeout(500)
        dur = tpl.REEL_DUR
        if cover:  # 릴스 표지: 훅 문장이 다 나온 순간
            pg.evaluate("draw25(1.4)"); pg.screenshot(path=cover, type="jpeg", quality=92)
        if frames:
            for t in frames:
                pg.evaluate(f"draw25({t})"); pg.screenshot(path=f"{out_mp4}_{t:05.2f}.png")
        else:
            tmp = out_mp4[:-4] + ".part.mp4"
            ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(FPS),
                                   "-c:v", "mjpeg", "-i", "-", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
                                   "-shortest", "-c:v", "libx264", "-crf", "20", "-preset", "veryfast",
                                   "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "64k", tmp], stdin=subprocess.PIPE)
            for i in range(int(dur * FPS)):
                pg.evaluate(f"draw25({i / FPS})")
                ff.stdin.write(pg.screenshot(type="jpeg", quality=92))
            ff.stdin.close()
            if ff.wait() == 0:
                os.replace(tmp, out_mp4)
        br.close()
    return out_mp4
