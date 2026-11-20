"""Neols 템플릿 2·3: '스플릿'(NOW 컬러 ↔ THEN 흑백 대비)과 '콜라주'(밝은 종이 + 폴라로이드 + THEN 도장).
카드뉴스(1080x1350)·릴스(1080x1920) 모두. 데이터 해석은 cine.py와 같아요(photos, reel.hook/stat/chips/then_head/then_sub).
"""
import re

import cine
from cine import ACCENT, LIGHT, esc, data_url, photos, hook, stat, then_parts, year_of

RED = "#FF4B3E"
SEPIA = "filter:grayscale(1) sepia(.4) contrast(1.12)"


def _pct(s):
    m = re.search(r"[+−-]?\d+(?:\.\d+)?", s.replace("−", "-"))
    return abs(float(m.group(0))) if m else None


# ───────────── 카드 공통 ─────────────
def _page(css, body, light=False):
    base = cine.CARD_CSS + ("body{background:#F7F6F2;color:#111}.segs div{background:#DDDBD3}.segs div.on{background:#111}"
                            ".top .tag{border-color:#111}.brand i{color:%s}.cred{color:#8A8A85}.foot span:last-child{color:#111}" % ACCENT
                            if light else "")
    return f"<!DOCTYPE html><html><head><meta charset='utf-8'><style>{base}{css}</style></head><body>{body}</body></html>"


def _visual_inner(v, light):
    ink, sub, track, mute = ("#111", "#555", "#ECEBE6", "#CFCDC6") if light else ("#fff", "#ddd", "rgba(255,255,255,.14)", "rgba(255,255,255,.45)")
    acc = ACCENT if light else LIGHT
    if v["type"] == "bars":
        mx = max(x[1] for x in v["data"]) or 1; hl = v.get("highlight", len(v["data"]) - 1)
        return "".join(
            f"<div style='display:flex;align-items:center;gap:22px;padding:20px 0'><div style='width:200px;font-size:30px;color:{sub}'>{esc(l)}</div>"
            f"<div style='flex:1;height:54px;background:{track};border-radius:8px;overflow:hidden'><div style='height:100%;border-radius:8px;"
            f"width:{max(4, val / mx * 100):.1f}%;background:{ACCENT if j == hl else mute}'></div></div>"
            f"<div style='width:170px;text-align:right;font-size:36px;font-weight:900;color:{acc if j == hl else ink}'>{esc(v.get('fmt', '{}').format(val))}</div></div>"
            for j, (l, val) in enumerate(v["data"]))
    if v["type"] == "timeline":
        last = len(v["data"]) - 1
        return (f"<div style='position:relative;display:flex;flex-direction:column;gap:42px;padding-left:60px;border-left:0'>"
                f"<div style='position:absolute;left:17px;top:20px;bottom:20px;width:4px;background:{mute}'></div>" + "".join(
                    f"<div style='position:relative'><div style='position:absolute;left:-58px;top:12px;width:34px;height:34px;border-radius:50%;"
                    f"background:{ACCENT if j == last else ('#F7F6F2' if light else '#0B0B0C')};border:5px solid {ACCENT if j == last else ink}'></div>"
                    f"<div style='font-size:46px;font-weight:900;color:{acc if j == last else ink}'>{esc(y)}</div>"
                    f"<div style='font-size:31px;color:{sub};margin-top:6px;line-height:1.4'>{esc(t)}</div></div>"
                    for j, (y, t) in enumerate(v["data"])) + "</div>")
    return (f"<div><div style='font-size:230px;font-weight:900;line-height:1;letter-spacing:-0.04em;color:{acc}'>{esc(v['value'])}</div>"
            f"<div style='font-size:40px;font-weight:700;margin-top:26px'>{esc(v['label'])}</div>"
            + (f"<div style='font-size:30px;color:{sub};margin-top:14px'>{esc(v['sub'])}</div>" if v.get("sub") else "") + "</div>")


def _plan(it):
    visuals = (it.get("visuals") or ([it["visual"]] if it.get("visual") else []))[:2]
    extras = list(it.get("extras", []))
    split = True  # 두 템플릿 모두 NOW / THEN 페이지를 나눔(대비가 핵심)
    cnt = lambda: 1 + len(visuals) + 2 + len(extras) + 1
    if cnt() < 4:
        extras.append({"kicker": "SUMMARY", "title": "한눈에 정리", "lines": it["points"]})
    while cnt() > 8 and extras:
        extras.pop()
    while cnt() > 8 and visuals:
        visuals.pop()
    return visuals, extras, cnt()


def _chips(it, size=32):
    return "".join(f"<span class='chip {'up' if c[0] == 'up' else 'dn'}' style='font-size:{size}px;padding:10px 24px'>"
                   f"{'▲' if c[0] == 'up' else '▼'} {esc(c[1])}</span>" for c in it.get("reel", {}).get("chips", []))


# ═════════════ 스플릿 카드 ═════════════
def split_cards(d):
    it = d["items"][0]; ps = photos(it); visuals, extras, n = _plan(it)
    p0 = ps[0] if ps else None
    bgimg = (lambda ph, extra="": f"background-image:url({data_url(ph['path'])});{extra}") if ps else (lambda ph, extra="": "background:#222;" + extra)
    ty = year_of(it["then_label"]); head, sub = then_parts(it)
    h = hook(it).split("\n")
    ntag = f"NOW · {d['date'][:7]}"
    pages = []; k = 0
    lab = lambda word, txt, col: (f"<div style='position:absolute;left:72px;font-weight:900;color:{col}' class='lb'>"
                                  f"<b style='display:inline-block;font-size:24px;letter-spacing:.12em;padding:4px 14px;border:3px solid currentColor;"
                                  f"border-radius:30px;margin-right:14px;vertical-align:middle'>{word}</b>"
                                  f"<span style='font-size:52px;vertical-align:middle'>{esc(txt)}</span></div>")
    # 표지
    css = f"""
    .h{{position:absolute;left:0;right:0;overflow:hidden}} .h .bg{{inset:-40px}}
    .dv{{position:absolute;left:0;right:0;top:671px;height:8px;background:{ACCENT};box-shadow:0 0 26px {ACCENT}}}
    .hk{{position:absolute;left:50px;right:50px;top:675px;transform:translateY(-50%);text-align:center;font-size:84px;font-weight:900;line-height:1.16;color:#111}}
    .hk span{{background:#fff;padding:2px 22px;box-decoration-break:clone;-webkit-box-decoration-break:clone}} .hk em{{font-style:normal;color:{RED}}}
    """
    hk = f"<span>{esc(h[0])}</span>" + (f"<br><span><em>{esc(' '.join(h[1:]))}</em></span>" if len(h) > 1 else "")
    body = (f"<div class='h' style='top:0;height:675px'><div class='bg' style=\"{bgimg(p0, 'transform:scale(1.05)')}\"></div>"
            f"<div style='position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,.55),rgba(0,0,0,.1) 45%,rgba(0,0,0,.35))'></div>"
            + lab("NOW", d["date"][:7], "#fff").replace("class='lb'", "class='lb' style='top:150px'").replace("style='position", "style='top:150px;position")
            + "</div>"
            f"<div class='h' style='top:675px;height:675px'><div class='bg' style=\"{bgimg(p0, SEPIA + ';transform:scale(1.25) translateX(30px)')}\"></div>"
            f"<div style='position:absolute;inset:0;background:rgba(0,0,0,.55)'></div>"
            + lab("THEN", it["then_label"], "#E8E1C8").replace("style='position", "style='top:420px;position") + "</div>"
            + "<div class='dv'></div>" + f"<div class='hk'>{hk}</div>"
            + cine._chrome(d, k, n, ntag, f"사진 · {esc(p0['credit'])}" if p0 else "", "넘겨서 보기 →"))
    pages.append(_page(css, body)); k += 1
    # 그래픽
    for v in visuals:
        ph = ps[1] if len(ps) > 1 else p0
        css = f".band{{position:absolute;top:0;left:0;right:0;height:430px;{bgimg(ph, 'background-size:cover;background-position:center')}}}" \
              f".band:after{{content:'';position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,.55),rgba(11,11,12,1))}}" \
              f".dv{{position:absolute;top:430px;left:0;right:0;height:6px;background:{ACCENT}}}" \
              f".vk{{position:absolute;top:250px;left:72px;font-size:24px;font-weight:800;letter-spacing:.14em;color:{LIGHT}}}" \
              f".vt{{position:absolute;top:290px;left:72px;right:100px;font-size:54px;font-weight:900;line-height:1.22}}" \
              f".vb{{position:absolute;top:500px;left:72px;right:90px;bottom:140px;display:flex;flex-direction:column;justify-content:center}}"
        body = ("<div class='band'></div><div class='dv'></div>" + cine._chrome(d, k, n, ntag, f"자료 · {esc(v.get('source', it['source']))} · 그래픽 Neols")
                + f"<div class='vk'>BY THE NUMBERS</div><div class='vt'>{esc(v['title'])}</div><div class='vb'>{_visual_inner(v, False)}</div>")
        pages.append(_page(css, body)); k += 1
    # NOW
    css = f".band{{position:absolute;top:0;left:0;right:0;height:560px;{bgimg(p0, 'background-size:cover;background-position:center')}}}" \
          f".band:after{{content:'';position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,.5),rgba(0,0,0,.05) 50%,rgba(11,11,12,1))}}" \
          f".dv{{position:absolute;top:560px;left:0;right:0;height:6px;background:{ACCENT}}}" \
          f".t{{position:absolute;top:600px;left:72px;right:100px;font-size:66px;font-weight:900;line-height:1.2}}" \
          f".c{{position:absolute;left:72px;right:90px;top:0}} ul{{list-style:none}} li{{font-size:31px;line-height:1.45;padding:9px 0;display:flex;color:#eee}}" \
          f"li:before{{content:'';flex:none;width:13px;height:13px;border-radius:50%;background:{LIGHT};margin:17px 16px 0 0}}" \
          f".body{{position:absolute;left:72px;right:90px;top:600px}} .chips{{display:flex;flex-wrap:wrap;gap:12px;margin:24px 0 10px}}"
    body = ("<div class='band'></div><div class='dv'></div>"
            + lab("NOW", d["date"][:7], "#fff").replace("style='position", "style='top:170px;position")
            + cine._chrome(d, k, n, ntag, f"출처 · {esc(it['source'])}")
            + f"<div class='body'><div style='font-size:64px;font-weight:900;line-height:1.2'>{esc(it['title'])}</div>"
            + (f"<div class='chips'>{_chips(it, 30)}</div>" if it.get("reel", {}).get("chips") else "<div style='height:20px'></div>")
            + "<ul>" + "".join(f"<li>{esc(p)}</li>" for p in it["points"]) + "</ul></div>")
    pages.append(_page(css, body)); k += 1
    # THEN
    pts = "".join(f"<li>{esc(p)}</li>" for p in it.get("then_points", []))
    css = f".band{{position:absolute;top:0;left:0;right:0;height:560px;{bgimg(p0, SEPIA + ';background-size:cover;background-position:30% 60%')}}}" \
          f".band:after{{content:'';position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,.55),rgba(0,0,0,.15) 50%,rgba(11,11,12,1))}}" \
          f".dv{{position:absolute;top:560px;left:0;right:0;height:6px;background:#E8E1C8}}" \
          f".y{{position:absolute;top:330px;left:66px;font-size:190px;font-weight:900;line-height:1;color:#fff}}" \
          f".body{{position:absolute;left:72px;right:90px;top:610px}} ul{{list-style:none;margin-top:18px}} li{{font-size:30px;line-height:1.5;color:#d9d3c0;padding:5px 0}}" \
          f"li:before{{content:'— ';color:#E8E1C8}} .nw{{position:absolute;left:72px;right:100px;bottom:110px;border-top:1px solid rgba(255,255,255,.3);padding-top:22px;font-size:31px;line-height:1.5;font-weight:700}} .nw b{{color:{LIGHT}}}"
    body = ("<div class='band'></div>" + cine.GRAIN.replace("class='grain'", "class='grain' style='height:560px'") + "<div class='dv'></div>"
            + lab("THEN", it["then_label"], "#E8E1C8").replace("style='position", "style='top:170px;position")
            + (f"<div class='y'>{ty}</div>" if ty else "")
            + cine._chrome(d, k, n, f"THEN · {it['then_label']}", f"출처 · {esc(it.get('then_source', it['source']))}")
            + f"<div class='body'><div style='font-size:52px;font-weight:900;line-height:1.3'>{esc(head)}</div>"
            + (f"<div style='margin-top:14px;font-size:32px;color:#ddd;line-height:1.5'>{esc(sub)}</div>" if sub else "")
            + (f"<ul>{pts}</ul>" if pts else "") + "</div>"
            + f"<div class='nw'><b>NOW →</b> {esc(it['link'])}</div>")
    pages.append(_page(css, body)); k += 1
    for ex in extras:
        pages.append(cine.c_extra(d, it, ex, ps, k, n)); k += 1
    pages.append(cine.c_outro(d, k, n))
    return pages


# ═════════════ 콜라주 카드 ═════════════
POL = ".pol{position:absolute;background:#fff;padding:20px 20px 64px;box-shadow:0 26px 50px rgba(0,0,0,.22)}" \
      ".pol .im{width:100%;height:100%;background-size:cover;background-position:center}" \
      ".pol .cp{position:absolute;left:22px;bottom:16px;font-size:20px;color:#8A8A85}"


def _pol(ph, style, img_extra="", cap=True):
    if not ph:
        return ""
    return (f"<div class='pol' style='{style}'><div class='im' style=\"background-image:url({data_url(ph['path'])});{img_extra}\"></div>"
            + (f"<div class='cp'>사진 · {esc(ph['credit'])}</div>" if cap else "") + "</div>")


def collage_cards(d):
    it = d["items"][0]; ps = photos(it); visuals, extras, n = _plan(it)
    p0 = ps[0] if ps else None; p1 = ps[1] if len(ps) > 1 else p0
    ty = year_of(it["then_label"]); head, sub = then_parts(it)
    h = hook(it).split("\n"); ntag = f"NOW · {d['date']}"
    MK = f".mk{{background:linear-gradient(transparent 55%,#C9D4FF 55%);padding:0 4px}}"
    pages = []; k = 0
    # 표지
    css = POL + MK + ".hk{position:absolute;left:72px;right:100px;bottom:200px;font-size:92px;font-weight:900;line-height:1.18}" \
                     ".ct{position:absolute;left:72px;bottom:120px;font-size:28px;color:#555;font-weight:700}" \
                     ".ct b{color:#E0321F;letter-spacing:.1em;border:2px solid #E0321F;padding:1px 10px;margin-right:10px;font-size:22px}"
    hk = esc(h[0]) + (f"<br><span class='mk'>{esc(' '.join(h[1:]))}</span>" if len(h) > 1 else "")
    body = (_pol(p0, "left:110px;top:180px;width:860px;height:640px;transform:rotate(-2.5deg)")
            + cine._chrome(d, k, n, ntag, "", "넘겨서 보기 →")
            + f"<div class='hk'>{hk}</div><div class='ct'><b>THEN</b>{esc(it['then_label'])} — 이 뉴스의 어제까지</div>")
    pages.append(_page(css, body, True)); k += 1
    for v in visuals:
        css = POL + ".vk{position:absolute;top:190px;left:72px;font-size:24px;font-weight:800;letter-spacing:.14em;color:%s}" \
                    ".vt{position:absolute;top:236px;left:72px;right:330px;font-size:56px;font-weight:900;line-height:1.25}" \
                    ".vb{position:absolute;top:480px;left:72px;right:90px;bottom:140px;display:flex;flex-direction:column;justify-content:center}" % ACCENT
        body = (_pol(p1, "right:60px;top:170px;width:250px;height:250px;transform:rotate(4deg);padding:12px 12px 34px", cap=False)
                + cine._chrome(d, k, n, ntag, f"자료 · {esc(v.get('source', it['source']))} · 그래픽 Neols")
                + f"<div class='vk'>BY THE NUMBERS</div><div class='vt'>{esc(v['title'])}</div><div class='vb'>{_visual_inner(v, True)}</div>")
        pages.append(_page(css, body, True)); k += 1
    # NOW
    st = stat(it)
    css = POL + MK + f".k{{position:absolute;top:190px;left:72px;font-size:24px;font-weight:800;letter-spacing:.14em;color:{ACCENT}}}" \
                     ".t{position:absolute;top:236px;left:72px;right:420px;font-size:58px;font-weight:900;line-height:1.22}" \
                     ".body{position:absolute;left:72px;right:90px;top:640px} ul{list-style:none;margin-top:22px} li{font-size:31px;line-height:1.45;padding:9px 0;display:flex;color:#222}" \
                     f"li:before{{content:'';flex:none;width:13px;height:13px;border-radius:50%;background:{ACCENT};margin:17px 16px 0 0}}" \
                     ".chips{display:flex;flex-wrap:wrap;gap:12px}"
    body = (_pol(p1, "right:56px;top:200px;width:340px;height:380px;transform:rotate(3deg);padding:14px 14px 40px", cap=False)
            + cine._chrome(d, k, n, ntag, f"출처 · {esc(it['source'])}" + (f" · 사진 · {esc(p1['credit'])}" if p1 else ""))
            + f"<div class='k'>NOW · {esc(it['category'])}</div><div class='t'>{esc(it['title'])}</div>"
            + "<div class='body'>"
            + (f"<div style='font-size:28px;font-weight:700;color:#555'>{esc(st['label'])}</div><div style='font-size:120px;font-weight:900;line-height:1.05;margin-bottom:16px'><span class='mk'>{esc(st['value'])}</span></div>" if st else "")
            + (f"<div class='chips'>{_chips(it, 28)}</div>" if it.get("reel", {}).get("chips") else "")
            + "<ul>" + "".join(f"<li>{esc(p)}</li>" for p in it["points"]) + "</ul></div>")
    pages.append(_page(css, body, True)); k += 1
    # THEN
    pts = "".join(f"<li>{esc(p)}</li>" for p in it.get("then_points", []))
    css = POL + ".st{position:absolute;left:560px;top:600px;font-size:96px;font-weight:900;color:#E0321F;border:9px solid #E0321F;padding:0 26px;letter-spacing:.06em;border-radius:12px;transform:rotate(-12deg);mix-blend-mode:multiply}" \
                ".body{position:absolute;left:72px;right:90px;top:820px} ul{list-style:none;margin-top:16px} li{font-size:29px;line-height:1.5;color:#444;padding:4px 0} li:before{content:'— '}" \
                f".nw{{position:absolute;left:72px;right:100px;bottom:110px;border-top:1px solid #CFCDC6;padding-top:20px;font-size:30px;line-height:1.5;font-weight:700}} .nw b{{color:{ACCENT}}}"
    body = (_pol(p0, "left:100px;top:170px;width:700px;height:560px;transform:rotate(-2deg)", SEPIA + ";background-position:30% 65%")
            + "<div class='st'>THEN</div>"
            + cine._chrome(d, k, n, f"THEN · {it['then_label']}", f"출처 · {esc(it.get('then_source', it['source']))}")
            + f"<div class='body'><div style='font-size:34px;font-weight:900;color:#E0321F'>{esc(it['then_label'])}</div>"
            + f"<div style='font-size:52px;font-weight:900;line-height:1.3;margin-top:6px'>{esc(head)}</div>"
            + (f"<div style='margin-top:12px;font-size:31px;color:#555;line-height:1.5'>{esc(sub)}</div>" if sub else "")
            + (f"<ul>{pts}</ul>" if pts else "") + "</div>"
            + f"<div class='nw'><b>NOW →</b> {esc(it['link'])}</div>")
    pages.append(_page(css, body, True)); k += 1
    for ex in extras:
        css = f".k{{position:absolute;top:190px;left:72px;font-size:24px;font-weight:800;letter-spacing:.14em;color:{ACCENT}}}" \
              ".t{position:absolute;top:236px;left:72px;right:100px;font-size:62px;font-weight:900;line-height:1.25}" \
              "ol{position:absolute;top:500px;left:72px;right:100px;list-style:none;counter-reset:n}" \
              "ol li{counter-increment:n;font-size:34px;line-height:1.5;padding:22px 0 22px 78px;position:relative;border-top:1px solid #DEDCD5}" \
              f"ol li:before{{content:counter(n,decimal-leading-zero);position:absolute;left:0;top:22px;font-weight:900;color:{ACCENT}}}"
        body = (cine._chrome(d, k, n, ntag, f"출처 · {esc(ex.get('source', it['source']))}")
                + f"<div class='k'>{esc(ex.get('kicker', 'MORE'))}</div><div class='t'>{esc(ex['title'])}</div><ol>"
                + "".join(f"<li>{esc(x)}</li>" for x in ex["lines"]) + "</ol>")
        pages.append(_page(css, body, True)); k += 1
    # 홍보(어두운 버전으로 마무리 대비)
    out = cine.c_outro(d, k, n).replace("body{background:#F7F6F2;color:#111}", "body{background:#111;color:#fff}") \
        .replace(".segs div{background:#DDDBD3} .segs div.on{background:#111} .top .tag{border-color:#111}", ".segs div{background:#444} .segs div.on{background:#fff}") \
        .replace(".cta{margin-top:56px;background:#111;color:#fff", ".cta{margin-top:56px;background:#fff;color:#111")
    pages.append(out)
    return pages


# ═════════════ 릴스 공통 ═════════════
def _reel_frame(css, body, js):
    return (f"<!DOCTYPE html><html><head><meta charset='utf-8'><style>{cine.COMMON}"
            f"html,body{{width:1080px;height:1920px}}.abs{{position:absolute}}{css}</style></head><body>{body}<script>"
            "const $=s=>document.querySelector(s);const P=(t,a,b)=>Math.min(1,Math.max(0,(t-a)/(b-a)));const E=x=>1-Math.pow(1-x,3);"
            "const BK=x=>{const c=1.7;return 1+(c+1)*Math.pow(x-1,3)+c*Math.pow(x-1,2)};"
            "function set(el,o,tf,ex){el=typeof el==='string'?$(el):el;if(!el)return;el.style.opacity=o;if(tf!==undefined)el.style.transform=tf;if(ex)Object.assign(el.style,ex)}"
            "function win(t,a,b,fi=.3,fo=.3){return Math.min(P(t,a,a+fi),1-P(t,b-fo,b))}"
            f"{js}</script></body></html>")


END = (f".end{{inset:0;display:flex;flex-direction:column;justify-content:center;align-items:center;background:#F7F6F2;color:#111}}"
       f".end .lg{{font-size:200px;font-weight:900}} .end .lg i{{font-style:normal;color:{ACCENT}}}"
       ".end p{font-size:46px;font-weight:700;margin-top:24px;color:#555} .end .fo{margin-top:60px;background:#111;color:#fff;font-size:44px;font-weight:900;padding:22px 60px;border-radius:80px}")


def _end(d, dark=False):
    s = (f"<div class='abs end' id='end'{' style=background:#111;color:#fff' if dark else ''}><div class='lg'>Ne<i>ol</i>s</div>"
         f"<p>{esc(d.get('slogan', '잊혀진 뉴스와 오늘의 뉴스를 잇다'))}</p><div class='fo'{' style=background:#fff;color:#111' if dark else ''}>{esc(d['handle'])} 팔로우</div></div>")
    return s


# ═════════════ 스플릿 릴스 ═════════════
def split_reel_html(d):
    it = d["items"][0]; ps = photos(it); p0 = ps[0] if ps else None
    img = f"background-image:url({data_url(p0['path'])})" if p0 else "background:#333"
    h = hook(it).split("\n"); st = stat(it); chips = it.get("reel", {}).get("chips", [])
    head, sub = then_parts(it)
    mx = max([_pct(c[1]) or 0 for c in chips] + [1])
    bars = "".join(
        f"<div class='bar'><div class='t'><span>{esc(re.sub(r'[+−-]?[0-9.]+%?', '', c[1]).strip())}</span><span>{esc((re.search(r'[+−-]?[0-9.]+%?', c[1]) or [''])[0])}</span></div>"
        f"<div class='tr'><div class='fl' id='f{j}' style='background:{RED if c[0] == 'up' else LIGHT}' data-w='{(_pct(c[1]) or 0) / mx * 100:.1f}'></div></div></div>"
        for j, c in enumerate(chips))
    pts = "".join(f"<div class='pt'>{esc(p)}</div>" for p in it["points"][:3])
    css = f"""
.half{{position:absolute;left:0;right:0;overflow:hidden}} #top{{top:0}} #bot{{bottom:0}} .half .ph{{position:absolute;inset:-60px;background-size:cover;background-position:center}}
.dim{{position:absolute;inset:0}} .lab{{position:absolute;left:80px;font-weight:900}}
.lab b{{display:inline-block;font-size:30px;letter-spacing:.12em;padding:6px 18px;border:3px solid currentColor;border-radius:40px;margin-right:18px;vertical-align:middle}} .lab span{{font-size:64px;vertical-align:middle}}
.dv{{position:absolute;left:0;right:0;height:10px;background:{ACCENT};box-shadow:0 0 30px {ACCENT}}}
.hook{{position:absolute;left:60px;right:60px;text-align:center;font-size:92px;font-weight:900;line-height:1.15;color:#111}}
.hook span{{background:#fff;padding:4px 26px;box-decoration-break:clone;-webkit-box-decoration-break:clone}} .hook em{{font-style:normal;color:{RED}}}
.nf{{position:absolute;left:80px;right:150px}} .nf .k{{font-size:40px;font-weight:700}} .nf .v{{font-size:200px;font-weight:900;line-height:1.05;white-space:nowrap}}
.bars{{position:absolute;left:80px;right:150px}} .bar{{margin-bottom:28px}} .bar .t{{font-size:40px;font-weight:700;margin-bottom:10px;display:flex;justify-content:space-between}}
.bar .tr{{height:46px;background:rgba(255,255,255,.18);border-radius:8px;overflow:hidden}} .bar .fl{{height:100%;width:0;border-radius:8px}}
.pt{{font-size:46px;font-weight:800;line-height:1.35;margin-bottom:22px}}
.th{{position:absolute;left:80px;right:150px}} .th .h{{font-size:64px;font-weight:900;line-height:1.3}} .th .s{{font-size:38px;color:#ddd;margin-top:14px;line-height:1.45}}
.link{{position:absolute;left:80px;right:150px;top:760px;font-size:62px;font-weight:900;line-height:1.38}}
.brand{{position:absolute;top:150px;right:150px;font-size:40px}} .cr{{position:absolute;left:80px;font-size:24px}}
{END}"""
    body = f"""
<div class="half" id="top"><div class="ph" id="pt" style="{img}"></div><div class="dim" id="dt"></div>
 <div class="lab" style="top:150px;color:#fff"><b>NOW</b><span>{d['date'][:7]}</span></div>
 <div class="nf" id="nf" style="top:330px">{f"<div class='k'>{esc(st['label'])}</div><div class='v'>{esc(st['value'])}</div>" if st else ''}</div>
 <div class="bars" id="nb" style="top:{640 if st else 330}px">{bars if chips else pts}</div>
 <div class="cr cred" style="top:240px">{('사진 · ' + esc(p0['credit'])) if p0 else ''}</div></div>
<div class="half" id="bot"><div class="ph" id="pb" style="{img};{SEPIA}"></div><div class="dim" style="background:rgba(0,0,0,.55)"></div>
 <div class="lab" id="lb" style="top:60px;color:#E8E1C8"><b>THEN</b><span>{esc(it['then_label'])}</span></div>
 <div class="th" id="tf" style="top:210px"><div class="h">{esc(head)}</div>{f"<div class='s'>{esc(sub)}</div>" if sub else ''}</div></div>
<div class="dv" id="dv"></div><div class="brand">Ne<i>ol</i>s</div>
<div class="hook" id="hook"><span>{esc(h[0])}</span>{f"<br><span><em>{esc(' '.join(h[1:]))}</em></span>" if len(h) > 1 else ''}</div>
<div class="link" id="link">{esc(it['link'])}</div>
<div class="cr cred" id="cs" style="bottom:300px;opacity:0">출처 · {esc(it['source'])}</div>
{_end(d)}"""
    js = f"""
const NB={len(chips)};
function draw(t){{
 let s=0.5-0.2*E(P(t,7.8,8.4))+0.2*E(P(t,11.7,12.1)); const close=E(P(t,11.9,12.4));
 const th=1920*s*(1-close), bh=1920*(1-s)*(1-close);
 $('#top').style.height=th+'px';$('#bot').style.height=bh+'px';$('#dv').style.top=(th-5)+'px';$('#dv').style.opacity=1-close;
 $('#pt').style.transform=`scale(${{1.05+0.12*t/15}})`;$('#pb').style.transform=`scale(${{1.2-0.1*t/15}}) translateX(${{20*t/15}}px)`;
 const h=BK(P(t,-.25,.3)),ho=P(t,2.8,3.1);set('#hook',1-ho,`translateY(-50%) scale(${{.7+.3*h}})`);$('#hook').style.top=th+'px';
 const nI=E(P(t,3.0,3.4)),nO=1-P(t,7.6,7.9);set('#nf',nI*nO,`translateY(${{(1-nI)*40}}px)`);set('#nb',P(t,3.5,3.8)*nO,'none');
 for(let j=0;j<NB;j++){{const f=$('#f'+j);f.style.width=(E(P(t,3.8+j*.4,4.6+j*.4))*f.dataset.w)+'%'}}
 document.querySelectorAll('#nb .pt').forEach((p,i)=>{{const a=E(P(t,3.6+i*.5,4.0+i*.5));p.style.opacity=a;p.style.transform=`translateX(${{(1-a)*-80}}px)`}});
 $('#dt').style.background=`linear-gradient(180deg,rgba(0,0,0,${{.45+.4*P(t,7.8,8.3)}}),rgba(0,0,0,${{.2+.6*P(t,7.8,8.3)}}) 40%,rgba(0,0,0,.6))`;
 set('#lb',.35+.65*P(t,7.9,8.3),`translateY(${{(1-E(P(t,7.9,8.4)))*20}}px)`);
 const tf=E(P(t,8.4,8.9));set('#tf',tf,`translateY(${{(1-tf)*40}}px)`);
 const lk=win(t,12.2,13.4,.3,.3);set('#link',lk,`translateY(${{(1-E(P(t,12.2,12.6)))*40}}px)`);set('#cs',lk,'none');
 const en=E(P(t,13.3,13.7));set('#end',en,`translateY(${{(1-en)*80}}px)`);
}}"""
    return _reel_frame(css, body, js)


# ═════════════ 콜라주 릴스 ═════════════
def collage_reel_html(d):
    it = d["items"][0]; ps = photos(it); p0 = ps[0] if ps else None; p1 = ps[1] if len(ps) > 1 else p0
    h = hook(it).split("\n"); st = stat(it); head, sub = then_parts(it)
    cred = lambda ph: f"사진 · {esc(ph['credit'])}" if ph else ""
    pol = lambda i, ph, style, extra="": (f"<div class='pol' id='q{i}' style='{style}'><div class='im' style=\"background-image:url({data_url(ph['path'])});{extra}\"></div>"
                                          f"<div class='cp'>{cred(ph)}</div></div>") if ph else f"<div id='q{i}'></div>"
    chips = _chips(it, 40).replace("class='chip", "class='chip cc")
    pts = "".join(f"<div class='pt'>{esc(p)}</div>" for p in it["points"][:3])
    css = f"""
body{{background:#F7F6F2;color:#111}}
.segs{{position:absolute;top:110px;left:80px;right:80px;display:flex;gap:10px}} .segs div{{flex:1;height:7px;background:#DDDBD3;border-radius:6px;overflow:hidden}} .segs b{{display:block;height:100%;width:0;background:#111}}
.top{{position:absolute;top:150px;left:80px;right:80px;display:flex;justify-content:space-between;font-size:40px;font-weight:900}} .top i{{font-style:normal;color:{ACCENT}}} .top .d{{font-size:30px;color:#8A8A85;font-weight:600}}
{POL.replace('20px 20px 64px', '22px 22px 70px')}
.hook{{left:80px;right:150px;top:1180px;font-size:104px;font-weight:900;line-height:1.18}}
.mk{{position:relative;display:inline-block;z-index:0}} .mk:before{{content:'';position:absolute;left:-8px;width:calc(var(--w,0)*1%);top:18%;bottom:6%;background:#C9D4FF;z-index:-1;border-radius:6px}}
.big{{left:80px;top:1130px;font-size:230px;font-weight:900;line-height:1;white-space:nowrap}} .lbl{{left:84px;top:1060px;font-size:44px;font-weight:700;right:150px}}
.circ{{position:absolute;left:30px;top:1090px}} .chips{{left:80px;top:1400px;display:flex;gap:18px;flex-wrap:wrap;right:150px}}
.pts{{left:80px;right:150px;top:1120px}} .pt{{font-size:48px;font-weight:800;line-height:1.35;margin-bottom:20px}}
.stamp{{position:absolute;font-size:110px;font-weight:900;color:#E0321F;border:10px solid #E0321F;padding:0 30px;letter-spacing:.06em;border-radius:12px;mix-blend-mode:multiply}}
.tf{{left:80px;right:150px;top:1180px;font-size:62px;font-weight:900;line-height:1.3}} .tf small{{display:block;font-size:38px;font-weight:500;color:#555;margin-top:16px}} .tf .y{{font-size:40px;color:#E0321F;display:block}}
.q{{left:80px;right:150px;top:640px;font-size:66px;font-weight:900;line-height:1.4}} .q .qm{{font-size:220px;color:{ACCENT};line-height:.6;display:block;height:120px}}
.src{{left:80px;bottom:300px;font-size:24px;color:#8A8A85}}
{END}"""
    body = f"""
<div class="segs"><div><b id="s1"></b></div><div><b id="s2"></b></div><div><b id="s3"></b></div><div><b id="s4"></b></div></div>
<div class="top"><span>Ne<i>ol</i>s</span><span class="d" id="dd"></span></div>
{pol(1, p0, 'left:120px;top:290px;width:840px;height:760px')}
{pol(2, p1, 'left:150px;top:300px;width:800px;height:640px')}
{pol(3, p0, 'left:110px;top:280px;width:860px;height:780px', SEPIA + ';background-position:30% 70%;background-size:160%')}
<div class="stamp" id="st" style="left:560px;top:860px">THEN</div>
<div class="abs hook" id="hook">{esc(h[0])}{f"<br><span class='mk' id='mk'>{esc(' '.join(h[1:]))}</span>" if len(h) > 1 else "<span id='mk'></span>"}</div>
{f"<div class='abs lbl' id='lbl'>{esc(st['label'])}</div><div class='abs big' id='big'>{esc(st['value'])}</div>" if st else f"<div class='abs pts' id='pts'>{pts}</div>"}
<svg class="circ" id="cc" width="760" height="330" style="opacity:{1 if st else 0}"><ellipse cx="380" cy="165" rx="360" ry="140" fill="none" stroke="{ACCENT}" stroke-width="10" stroke-linecap="round" pathLength="100" stroke-dasharray="100" stroke-dashoffset="100" id="el" transform="rotate(-4 380 165)"/></svg>
<div class="abs chips" id="chips">{chips}</div>
<div class="abs tf" id="tf"><span class="y">{esc(it['then_label'])}</span>{esc(head)}{f'<small>{esc(sub)}</small>' if sub else ''}</div>
<div class="abs q" id="q"><span class="qm">“</span>{esc(it['link'])}</div>
<div class="abs src" id="src">출처 · {esc(it['source'])}</div>
{_end(d, dark=True)}"""
    js = f"""
const HASST={'true' if st else 'false'}, NT="NOW · {d['date']}", TT="THEN · {esc(it['then_label'])}";
function drop(id,t,a,b,rot){{const p=BK(P(t,a,a+.5)),o=P(t,b-.3,b);set(id,P(t,a,a+.12)*(1-o),`translateY(${{(1-p)*-500-o*60}}px) rotate(${{rot+(1-p)*8}}deg) scale(${{1-o*.05}})`)}}
function draw(t){{
 [[0,3],[3,7],[7,11],[11,13]].forEach(([a,b],i)=>$('#s'+(i+1)).style.width=(P(t,a,b)*100)+'%');
 $('#dd').textContent=(t>=7&&t<11)?TT:NT;
 drop('#q1',t,-.4,3.05,-3);drop('#q2',t,3.0,7.05,2.5);drop('#q3',t,7.0,11.05,-2);
 const h=E(P(t,-.3,.25)),ho=P(t,2.75,3.0);set('#hook',h*(1-ho),`translateY(${{(1-h)*50}}px)`);
 $('#mk').style.setProperty('--w',(E(P(t,.35,.95))*104).toFixed(1));
 const bo=P(t,6.7,7.0);
 if(HASST){{const bi=BK(P(t,3.3,3.75));set('#lbl',P(t,3.2,3.5)*(1-bo),'none');set('#big',P(t,3.3,3.45)*(1-bo),`scale(${{.6+.4*bi}})`,{{transformOrigin:'left center'}});
  $('#el').setAttribute('stroke-dashoffset',100-100*E(P(t,4.0,4.7)));set('#cc',1-bo,'none');}}
 else document.querySelectorAll('.pt').forEach((p,i)=>{{const a=E(P(t,3.2+i*.6,3.6+i*.6));set(p,a*(1-bo),`translateY(${{(1-a)*40}}px)`)}});
 document.querySelectorAll('.cc').forEach((c,i)=>{{const a=E(P(t,4.8+i*.4,5.2+i*.4));set(c,a*(1-bo),`translateY(${{(1-a)*40}}px)`)}});
 const sp=P(t,7.6,7.85),so=P(t,10.7,11.0),sh=(t>7.85&&t<8.1)?Math.sin(t*120)*8:0;
 set('#st',P(t,7.6,7.65)*(1-so),`translate(${{sh}}px,${{sh/2}}px) scale(${{2.6-1.6*E(sp)}}) rotate(-12deg)`);
 const tf=E(P(t,8.2,8.7));set('#tf',tf*(1-so),`translateY(${{(1-tf)*40}}px)`);
 const q=win(t,11.0,13.1,.35,.3);set('#q',q,`translateY(${{(1-E(P(t,11,11.4)))*40}}px)`);set('#src',q,'none');
 const en=E(P(t,13.0,13.4));set('#end',en,`translateY(${{(1-en)*80}}px)`);
}}"""
    return _reel_frame(css, body, js)


# ═════════════ 선택 ═════════════
TEMPLATES = ("cine", "split", "collage")


def pick(d):
    """JSON의 template 값이 있으면 그대로, 없으면 cine."""
    t = d["items"][0].get("template") or d.get("template") or "cine"
    return t if t in TEMPLATES else "cine"


def card_pages(d):
    t = pick(d)
    return {"cine": cine.card_pages, "split": split_cards, "collage": collage_cards}[t](d)


def reel_html(d):
    t = pick(d)
    return {"cine": cine.reel_html, "split": split_reel_html, "collage": collage_reel_html}[t](d)
