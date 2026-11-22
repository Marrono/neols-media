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
    # 표지 (C안: 위 칸 = 오늘 문구, 아래 칸 = 그때 문구, 가운데 '그때는 어땠을까?')
    ans = it.get("reel", {}).get("then_head") or head
    css = f"""
    .h{{position:absolute;left:0;right:0;overflow:hidden}} .h .bg{{position:absolute;inset:-30px;background-size:cover;background-position:center}}
    .q{{position:absolute;left:72px;right:72px;bottom:70px;color:#fff}}
    .q .s{{font-size:30px;font-weight:700;color:#ddd}} .q .m{{font-size:78px;font-weight:900;line-height:1.15;margin-top:10px}}
    .a{{position:absolute;left:72px;right:72px;top:80px;color:#fff}}
    .a .s{{font-size:30px;font-weight:700;color:#E8E1C8}} .a .m{{font-size:64px;font-weight:900;line-height:1.2;margin-top:10px}}
    .mid{{position:absolute;left:50%;top:675px;transform:translate(-50%,-50%);background:{ACCENT};color:#fff;font-size:30px;font-weight:900;padding:12px 34px;border-radius:40px;box-shadow:0 0 0 8px rgba(0,0,0,.35);white-space:nowrap}}
    """
    yy, mm = (d["date"].split(".") + ["", ""])[:2]
    body = (f"<div class='h' style='top:0;height:675px'><div class='bg' style=\"{bgimg(p0)}\"></div>"
            f"<div style='position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,.4),rgba(0,0,0,.05) 40%,rgba(0,0,0,.8))'></div>"
            f"<div class='q'><div class='s'>{yy}년 {int(mm) if mm.isdigit() else mm}월, 오늘</div><div class='m'>{'<br>'.join(esc(x) for x in h)}</div></div></div>"
            f"<div class='h' style='top:675px;height:675px'><div class='bg' style=\"{bgimg(p0, SEPIA)}\"></div>"
            f"<div style='position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,.8),rgba(0,0,0,.3) 60%,rgba(0,0,0,.6))'></div>"
            f"<div class='a'><div class='s'>{esc(it['then_label'])}, 그때는</div><div class='m'>{esc(ans)}</div></div></div>"
            "<div class='mid'>그때는 어땠을까?</div>"
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
    body = (_pol(p0, "right:56px;top:200px;width:340px;height:380px;transform:rotate(3deg);padding:14px 14px 40px", "background-position:40% 50%", cap=False)
            + cine._chrome(d, k, n, ntag, f"출처 · {esc(it['source'])}" + (f" · 사진 · {esc(p0['credit'])}" if p0 else ""))
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
    pt = ps[1] if len(ps) > 1 else p0
    body = (_pol(pt, "left:100px;top:170px;width:700px;height:560px;transform:rotate(-2deg)", SEPIA + ";background-position:50% 60%")
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
    pts = "".join(f"<div class='pt'>{esc(p)}</div>" for p in it["points"][:2])
    css = f"""
.half{{position:absolute;left:0;right:0;overflow:hidden}} #top{{top:0}} #bot{{bottom:0}} .half .ph{{position:absolute;inset:-60px;background-size:cover;background-position:center}}
.dim{{position:absolute;inset:0}} .lab{{position:absolute;left:80px;font-weight:900}}
.lab b{{display:inline-block;font-size:30px;letter-spacing:.12em;padding:6px 18px;border:3px solid currentColor;border-radius:40px;margin-right:18px;vertical-align:middle}} .lab span{{font-size:64px;vertical-align:middle}}
.dv{{position:absolute;left:0;right:0;height:10px;background:{ACCENT};box-shadow:0 0 30px {ACCENT}}}
.hook{{position:absolute;left:80px;right:80px;color:#fff;text-shadow:0 4px 18px rgba(0,0,0,.5)}}
.hook .s{{font-size:40px;font-weight:700;color:#ddd}} .hook .m{{font-size:96px;font-weight:900;line-height:1.15;margin-top:12px}}
.tq{{position:absolute;left:80px;right:80px;top:120px;color:#fff}} .tq .s{{font-size:40px;font-weight:700;color:#E8E1C8}} .tq .m{{font-size:76px;font-weight:900;line-height:1.2;margin-top:12px}}
.mid{{position:absolute;left:50%;background:{ACCENT};color:#fff;font-size:40px;font-weight:900;padding:16px 44px;border-radius:50px;box-shadow:0 0 0 10px rgba(0,0,0,.35);white-space:nowrap;z-index:5}}
.nf{{position:absolute;left:80px;right:150px}} .nf .k{{font-size:40px;font-weight:700}} .nf .v{{font-size:200px;font-weight:900;line-height:1.05;white-space:nowrap}}
.bars{{position:absolute;left:80px;right:150px}} .bar{{margin-bottom:28px}} .bar .t{{font-size:40px;font-weight:700;margin-bottom:10px;display:flex;justify-content:space-between}}
.bar .tr{{height:46px;background:rgba(255,255,255,.18);border-radius:8px;overflow:hidden}} .bar .fl{{height:100%;width:0;border-radius:8px}}
.pt{{font-size:40px;font-weight:800;line-height:1.35;margin-bottom:20px}}
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
<div class="half" id="bot"><div class="ph" id="pbot" style="{img};{SEPIA}"></div><div class="dim" style="background:rgba(0,0,0,.55)"></div>
 <div class="lab" id="lb" style="top:60px;color:#E8E1C8"><b>THEN</b><span>{esc(it['then_label'])}</span></div>
 <div class="tq" id="tq"><div class="s">{esc(it['then_label'])}, 그때는</div><div class="m">{esc(it.get('reel',{}).get('then_head') or head)}</div></div>
 <div class="th" id="tf" style="top:210px"><div class="h">{esc(head)}</div>{f"<div class='s'>{esc(sub)}</div>" if sub else ''}</div></div>
<div class="dv" id="dv"></div><div class="brand">Ne<i>ol</i>s</div>
<div class="hook" id="hook"><div class="s">{d['date'][:4]}년 {int(d['date'][5:7])}월, 오늘</div><div class="m">{'<br>'.join(esc(x) for x in h)}</div></div>
<div class="mid" id="mid">그때는 어땠을까?</div>
<div class="link" id="link">{esc(it['link'])}</div>
<div class="cr cred" id="cs" style="bottom:300px;opacity:0">출처 · {esc(it['source'])}</div>
{_end(d)}"""
    js = f"""
const NB={len(chips)};
function draw(t){{
 let s=0.5-0.2*E(P(t,7.8,8.4))+0.2*E(P(t,11.7,12.1)); const close=E(P(t,11.9,12.4));
 const th=1920*s*(1-close), bh=1920*(1-s)*(1-close);
 $('#top').style.height=th+'px';$('#bot').style.height=bh+'px';$('#dv').style.top=(th-5)+'px';$('#dv').style.opacity=1-close;
 $('#pt').style.transform=`scale(${{1.05+0.12*t/15}})`;$('#pbot').style.transform=`scale(${{1.2-0.1*t/15}}) translateX(${{20*t/15}}px)`;
 const h=E(P(t,-.3,.25)),ho=P(t,2.8,3.1);set('#hook',1-ho,`translateY(calc(-100% - 90px + ${{(1-h)*30}}px))`);$('#hook').style.top=th+'px';
 const mq=E(P(t,.5,.9));set('#mid',mq*(1-ho),`translate(-50%,-50%) scale(${{.8+.2*mq}})`);$('#mid').style.top=th+'px';
 const tq=E(P(t,.9,1.4));set('#tq',tq*(1-ho),`translateY(${{(1-tq)*30}}px)`);
 const nI=E(P(t,3.0,3.4)),nO=1-P(t,7.6,7.9);set('#nf',nI*nO,`translateY(${{(1-nI)*40}}px)`);set('#nb',P(t,3.5,3.8)*nO,'none');
 for(let j=0;j<NB;j++){{const f=$('#f'+j);f.style.width=(E(P(t,3.8+j*.4,4.6+j*.4))*f.dataset.w)+'%'}}
 document.querySelectorAll('#nb .pt').forEach((p,i)=>{{const a=E(P(t,3.6+i*.5,4.0+i*.5));p.style.opacity=a;p.style.transform=`translateX(${{(1-a)*-80}}px)`}});
 $('#dt').style.background=`linear-gradient(180deg,rgba(0,0,0,${{.45+.4*P(t,7.8,8.3)}}),rgba(0,0,0,${{.2+.6*P(t,7.8,8.3)}}) 40%,rgba(0,0,0,.6))`;
 set('#lb',P(t,7.9,8.3),`translateY(${{(1-E(P(t,7.9,8.4)))*20}}px)`);
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
{pol(2, p0, 'left:150px;top:300px;width:800px;height:640px', 'background-size:150%;background-position:60% 40%')}
{pol(3, ps[1] if len(ps) > 1 else p0, 'left:110px;top:280px;width:860px;height:780px', SEPIA + ';background-position:50% 60%' + ('' if len(ps) > 1 else ';background-size:160%'))}
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


# ═════════════ 6~8장 구성 (2026-11-20 개편) ═════════════
# 1 표지 → 2 사진+핵심 숫자 → 3 THEN 사진+연도  (이미지 중심, 글 최소)
# 4 쉽게 보기(NOW 풀이) → 5 여담 → (그래픽 · THEN 자세히) → 홍보
import re as _re


def _img_stat(d, it, ps, light):
    st = stat(it); ph = (ps[1] if len(ps) > 1 else ps[0]) if ps else None
    chips = _chips(it, 30)
    big = (f"<div style='font-size:30px;font-weight:700;opacity:.85'>{esc(st['label'])}</div>"
           f"<div style='font-size:{190 if len(st['value']) <= 6 else 140}px;font-weight:900;line-height:1.02;letter-spacing:-0.04em;white-space:nowrap'>"
           + (f"<span style='background:linear-gradient(transparent 58%,#C9D4FF 58%)'>{esc(st['value'])}</span>" if light else esc(st['value'])) + "</div>"
           if st else f"<div style='font-size:62px;font-weight:900;line-height:1.3'>{esc(it['points'][0])}</div>")
    big += f"<div style='display:flex;flex-wrap:wrap;gap:12px;margin-top:22px'>{chips}</div>" if chips else ""
    if light:
        css = POL + ".b{position:absolute;left:72px;right:90px;bottom:120px}"
        body = (_pol(ph, "left:90px;top:170px;width:900px;height:700px;transform:rotate(2deg)", "background-position:50% 45%")
                + cine._chrome(d, 1, 6, f"NOW · {d['date']}", "") + f"<div class='b'>{big}</div>")
        return _page(css, body, True)
    css = ".b{position:absolute;left:72px;right:90px;bottom:120px}"
    body = (cine._bg(ph, "transform:scale(1.06)") + "<div class='shade'></div>"
            + cine._chrome(d, 1, 6, f"NOW · {d['date'][:7]}", f"사진 · {esc(ph['credit'])}" if ph else "")
            + f"<div class='b'>{big}</div>")
    return cine._page(css, body)


def _img_then(d, it, ps, light):
    ty = year_of(it["then_label"]); head, _ = then_parts(it)
    pt = (ps[1] if (light and len(ps) > 1) else ps[0]) if ps else None
    if light:
        css = POL + ".st{position:absolute;left:600px;top:640px;font-size:96px;font-weight:900;color:#E0321F;border:9px solid #E0321F;padding:0 26px;letter-spacing:.06em;border-radius:12px;transform:rotate(-12deg);mix-blend-mode:multiply}" \
                    ".b{position:absolute;left:72px;right:90px;bottom:120px}"
        body = (_pol(pt, "left:90px;top:170px;width:860px;height:660px;transform:rotate(-2deg)", SEPIA + ";background-position:50% 55%")
                + "<div class='st'>THEN</div>" + cine._chrome(d, 2, 6, f"THEN · {it['then_label']}", "")
                + f"<div class='b'><div style='font-size:150px;font-weight:900;color:#E0321F;line-height:1'>{ty or esc(it['then_label'])}</div>"
                + f"<div style='font-size:52px;font-weight:900;margin-top:16px;line-height:1.25'>{esc(head)}</div></div>")
        return _page(css, body, True)
    css = (".st{position:absolute;left:72px;bottom:470px;font-size:56px;font-weight:900;letter-spacing:.06em;border:5px solid #fff;padding:0 22px}"
           ".b{position:absolute;left:66px;right:90px;bottom:120px}")
    body = (cine._bg(pt, SEPIA + ";transform:scale(1.15)") + "<div class='shade'></div>" + cine.GRAIN
            + cine._chrome(d, 2, 6, f"THEN · {it['then_label']}", f"사진 · {esc(pt['credit'])}" if pt else "")
            + "<div class='st'>THEN</div>"
            + f"<div class='b'><div style='font-size:220px;font-weight:900;line-height:1;letter-spacing:-0.03em'>{ty or esc(it['then_label'])}</div>"
            + f"<div style='font-size:54px;font-weight:900;margin-top:14px;line-height:1.25'>{esc(head)}</div></div>")
    return cine._page(css, body)


def _fix_segs(html_, k, n, light):
    segs = "".join(f"<div class='{'on' if i <= k else ''}'></div>" for i in range(n))
    return _re.sub(r"<div class='segs'>.*?</div><div class='top'>", f"<div class='segs'>{segs}</div><div class='top'>", html_, count=1, flags=_re.S)


def card_pages6(d):
    t = pick(d); it = d["items"][0]; ps = photos(it); light = t == "collage"
    base_fn = {"cine": cine.card_pages, "split": split_cards, "collage": collage_cards}[t]
    plain = dict(it, extras=[], split_then=True, then_points=it.get("then_points") or [it["link"]])
    full = base_fn(dict(d, items=[plain]))           # [표지] + 그래픽들 + [NOW, THEN, 홍보]
    nv = len(full) - 4
    cover, visuals, then_detail, outro = full[0], full[1:1 + nv], full[-2], full[-1]
    ex = it.get("explain") or {}
    eit = dict(plain, title=ex.get("title", it["title"]), points=ex.get("lines", it["points"]),
               reel=dict(it.get("reel", {}), stat=None), visuals=[], visual=None)
    now_explain = base_fn(dict(d, items=[eit]))[-3]
    asides = list(it.get("asides") or it.get("extras") or [{"kicker": "SUMMARY", "title": "한눈에 정리", "lines": it["points"]}])
    aside_pages = []
    for a in asides:
        a = dict(a); a.setdefault("kicker", "여담")
        if light:
            pg = collage_cards(dict(d, items=[dict(plain, extras=[a], visuals=[], visual=None)]))
            aside_pages.append(pg[-2])
        else:
            aside_pages.append(cine.c_extra(d, it, a, ps, 0, 6))
    MAXC = int(d.get("max_cards", 8))
    while 5 + len(aside_pages) + len(visuals) + 1 > MAXC and len(aside_pages) > 1:
        aside_pages.pop()
    keep_then = True
    while 5 + len(aside_pages) + len(visuals) + int(keep_then) > MAXC:
        if len(visuals) > 1: visuals.pop()
        elif keep_then: keep_then = False
        else: visuals.pop()
    pages = [cover, _img_stat(d, it, ps, light), _img_then(d, it, ps, light), now_explain] + aside_pages + visuals \
            + ([then_detail] if keep_then else []) + [outro]
    n = len(pages)
    return [_fix_segs(p, k, n, light) for k, p in enumerate(pages)]


# ═════════════ 릴스 25초: 기존 15초 흐름에 '쉽게 보기'·'여담' 장면 끼워 넣기 ═════════════
REEL_DUR = 25.0
INS = {"cine": (6.6, 10.5), "split": (7.9, 12.15), "collage": (7.0, 11.0)}
EXP_LEN, ASIDE_LEN = 5.5, 4.5


def _overlay(d, it, light):
    ps = photos(it); ph = ps[-1] if ps else None
    ex = it.get("explain") or {}; lines = ex.get("lines", it["points"])[:3]
    a = (it.get("asides") or it.get("extras") or [{"title": "한눈에 정리", "lines": it["points"][:2]}])[0]
    fg, sub, acc = ("#111", "#444", ACCENT) if light else ("#fff", "#ddd", LIGHT)
    bg = ("background:#F7F6F2" if light else
          (f"background:url({data_url(ph['path'])}) center/cover" if ph else "background:#0B0B0C"))
    dim = "" if light else "<div style='position:absolute;inset:0;background:rgba(6,6,8,.78);backdrop-filter:blur(0px)'></div>"
    blur = "" if light else "filter:blur(14px);transform:scale(1.15);"
    def layer(i, kicker, title, ls):
        return (f"<div class='ov' id='ov{i}' style='position:absolute;inset:0;opacity:0;z-index:50;overflow:hidden'>"
                f"<div style='position:absolute;inset:-40px;{bg};{blur}'></div>{dim}"
                f"<div style='position:absolute;left:80px;right:150px;top:560px;color:{fg}'>"
                f"<div style='font-size:34px;font-weight:800;letter-spacing:.14em;color:{acc}'>{kicker}</div>"
                + (f"<div style='font-size:72px;font-weight:900;line-height:1.25;margin-top:18px'>{esc(title)}</div>" if title else "")
                + "".join(f"<div class='ol' style='font-size:50px;font-weight:800;line-height:1.38;margin-top:34px;color:{fg};opacity:0'>"
                          f"<span style='color:{acc}'>—</span> {esc(l)}</div>" for l in ls)
                + "</div></div>")
    out = layer(0, "쉽게 말하면", ex.get("title", ""), lines)
    al = (it.get("asides") or it.get("extras") or [a])[:max(1, int(d.get("reel_asides", 1)))]
    for k, aa in enumerate(al):
        out += layer(k + 1, aa.get("kicker", "여담"), aa.get("title", ""), aa.get("lines", [])[:2])
    return out


def reel_html25(d):
    t = pick(d); it = d["items"][0]
    html_ = reel_html(d)
    A, B = INS[t]
    dur = float(d.get("reel_sec", REEL_DUR)); na = max(1, int(d.get("reel_asides", 1)))
    extra = dur - REEL_DUR
    EL = EXP_LEN + extra * 0.4 if na > 1 else EXP_LEN + extra / 2
    AL = (dur - 15.0 - EL) / na
    js = f"""
const A={A},B={B},EL={EL},AL={AL},NA={na},DUR={dur};
function ovs(id,lt,len){{const o=document.getElementById(id);if(!o)return;const op=Math.min(1,Math.max(0,Math.min(lt/.35,(len-lt)/.35)));
 o.style.opacity=(lt>=0&&lt<=len)?op:0;o.querySelectorAll('.ol').forEach((l,i)=>{{const a=Math.min(1,Math.max(0,(lt-.5-i*.7)/.4));l.style.opacity=a;l.style.transform=`translateY(${{(1-a)*30}}px)`}})}}
function draw25(T){{
 let m, e=-1, s=-1, k=-1; const AT=AL*NA;
 if(T<A) m=T; else if(T<A+EL){{m=A;e=T-A}} else if(T<B+EL){{m=T-EL}} else if(T<B+EL+AT){{m=B;s=T-B-EL;k=Math.floor(s/AL);s=s-k*AL}} else m=T-EL-AT;
 draw(m); ovs('ov0',e,EL); for(let j=0;j<NA;j++) ovs('ov'+(j+1), j===k?s:-1, AL);
 const pb=document.getElementById('pb'); if(pb) pb.style.width=(T/DUR*100)+'%';
}}"""
    return html_.replace("</body>", _overlay(d, it, t == "collage") + f"<script>{js}</script></body>")


# ═════════════ 문구 다듬기 (2026-11-20 밤) ═════════════
# 템플릿에 박힌 영어 라벨·딱딱한 문구를 자연스러운 한국어로 바꿔요. 카드·릴스 HTML 모두 마지막에 한 번 통과.
_LIC = {"Public domain": "퍼블릭 도메인", "public domain": "퍼블릭 도메인"}
_ANON = {"me", "unknown", "미상", "작자 미상", ""}


def _credit(m):
    artist = (m.group(1) or "").strip()
    lic = _LIC.get(m.group(2).strip(), m.group(2).strip())
    crop = " · 잘라서 사용" if m.group(3) else ""
    if artist.lower() in _ANON:
        return f"위키미디어 공용 ({lic}){crop}"
    return f"{artist} ({lic}, 위키미디어 공용){crop}"


def polish(html_, d):
    y, mo, dd = (d.get("date", "") + "..").split(".")[:3]
    today = f"{int(mo)}월 {int(dd)}일 뉴스" if mo.isdigit() and dd.isdigit() else "오늘의 뉴스"
    s = html_
    # 오른쪽 위 알약: 큰 NOW/THEN 라벨과 겹치지 않게 한국어로
    s = _re.sub(r"(class='tag'>)NOW · [^<]*<", rf"\g<1>{today}<", s)
    s = _re.sub(r"(class='tag'>)THEN · ([^<]*)<", r"\g<1>다시 보는 \2<", s)
    s = s.replace("class='tag'>Neols<", "class='tag'>팔로우<")
    s = _re.sub(r'((?:NTAG|NT)=")NOW · [^"]*"', rf'\g<1>{today}"', s)
    s = _re.sub(r'((?:TTAG|TT)=")THEN · ([^"]*)"', r'\g<1>다시 보는 \2"', s)
    # 고정 문구
    rep = [
        ("넘겨서 보기 →", "옆으로 넘겨보세요 →"),
        ("BY THE NUMBERS", "숫자로 보기"),
        (">SUMMARY<", ">한눈에 보기<"), (">MORE<", ">더 알아보기<"),
        (" · 그래픽 Neols", ""),
        (" — 이 뉴스의 어제까지", "에는 무슨 일이 있었을까?"),
        ("<b>NOW →</b>", "<b>그때와 지금 →</b>"),
        ("매일 꼭 알아야 할 국내 뉴스<br>그리고 그 뉴스의 어제까지", "오늘 꼭 알아야 할 뉴스,<br>그 뉴스가 지나온 이야기까지"),
        ("<i>팔로우하기</i>", "<i>팔로우</i>"),
        ("오늘의 뉴스에도 어제가 있어요", "모든 뉴스에는 어제가 있어요"),
    ]
    for a, b in rep:
        s = s.replace(a, b)
    s = _re.sub(r"(class='k'>)NOW · ", r"\g<1>오늘의 뉴스 · ", s)
    # 사진 출처: 'Me / Wikimedia Commons / Public domain' 같은 원문 표기 정리
    s = _re.sub(r"(?:([^<>/·\"']+?) / )?Wikimedia Commons / ([^<·\"']+?)( · 잘라서 사용)?(?=[<\"']|$)", _credit, s)
    return s


_card_pages6_raw = card_pages6
_reel_html25_raw = reel_html25


def card_pages6(d):
    return [polish(p, d) for p in _card_pages6_raw(d)]


def reel_html25(d):
    return polish(_reel_html25_raw(d), d)
