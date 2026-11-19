"""Neols 릴스 생성기: 뉴스 JSON -> 1080x1920 무음 MP4 (음악은 인스타에서 추가).

사용법: python3 reel.py news.json out_dir
씬 구성: 인트로 → 뉴스마다 [NOW 화면 → THEN 상자 등장] → 아웃트로
"""
import html
import json
import os
import subprocess
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

W, H, FPS = 1080, 1920, 30
ACCENT = "#2F5BFF"
ENC = ["-c:v", "libx264", "-crf", "20", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-r", str(FPS)]

CSS = f"""
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:{W}px;height:{H}px}}
body{{font-family:'Pretendard','Noto Sans CJK KR',sans-serif;background:#F7F6F2;color:#111;
 letter-spacing:-0.02em;word-break:keep-all;position:relative;overflow:hidden}}
.top{{position:absolute;top:150px;left:90px;right:90px;display:flex;justify-content:space-between;
 align-items:center;border-bottom:3px solid #111;padding-bottom:26px}}
.brand{{font-size:52px;font-weight:900}} .brand i{{font-style:normal;color:{ACCENT}}}
.date{{font-size:34px;color:#8A8A85;font-weight:500}}
.main{{position:absolute;top:310px;left:90px;right:90px;bottom:330px;display:flex;flex-direction:column}}
.row{{display:flex;justify-content:space-between;align-items:center}}
.num{{font-size:40px;font-weight:800;color:{ACCENT}}} .num span{{color:#B5B3AC}}
.cat{{font-size:34px;font-weight:700;border:3px solid #111;border-radius:50px;padding:8px 32px}}
.title{{margin-top:44px;font-size:80px;font-weight:900;line-height:1.2}}
ul{{margin-top:40px;list-style:none}}
li{{font-size:42px;line-height:1.45;padding:14px 0;display:flex;color:#222}}
.dot{{flex:none;width:18px;height:18px;border-radius:50%;background:{ACCENT};margin:23px 22px 0 0}}
.then{{margin-top:auto;background:#111;color:#fff;padding:46px 52px;border-radius:12px}}
.then.hide{{visibility:hidden}}
.lab{{font-size:54px;font-weight:900;margin-bottom:18px}}
.lab span{{font-size:28px;font-weight:800;letter-spacing:.14em;color:#9DB1FF;border:2px solid #9DB1FF;
 border-radius:40px;padding:6px 20px;margin-right:22px;vertical-align:middle}}
.old{{font-size:39px;line-height:1.5;color:#E8E8E4}}
.now{{margin-top:22px;padding-top:22px;border-top:1px solid #3A3A3A;font-size:37px;line-height:1.5}}
.now b{{color:#9DB1FF}}
.src{{margin-top:26px;font-size:28px;color:#8A8A85}}
.center{{position:absolute;inset:0;display:flex;flex-direction:column;justify-content:center;padding:0 90px}}
.hero{{font-size:230px;font-weight:900;line-height:1}} .hero i{{font-style:normal;color:{ACCENT}}}
.hsub{{font-size:58px;font-weight:800;margin-top:50px;line-height:1.35}}
.hsm{{font-size:40px;color:#8A8A85;margin-top:30px}}
"""


def esc(s):
    return html.escape(s).replace("\n", "<br>")


def page(body):
    return f"<!DOCTYPE html><html><head><meta charset='utf-8'><style>{CSS}</style></head><body>{body}</body></html>"


def top(d):
    return f"<div class='top'><span class='brand'>Ne<i>ol</i>s</span><span class='date'>{d['date']} ({d['weekday']})</span></div>"


def intro(d):
    m, day = d["date"][5:].split(".")
    return page(top(d) + f"<div class='center'><div class='hsm'>{int(m)}월 {int(day)}일의 뉴스</div>"
                f"<div class='hero'>Ne<i>ol</i>s<i>.</i></div>"
                f"<div class='hsub'>오늘의 뉴스에도<br>어제가 있어요</div>"
                + (f"<div class='hsm'>{len(d['items'])}개의 뉴스, 그리고 그 뉴스의 어제</div></div>" if len(d['items']) > 1
                   else f"<div class='hsm' style='color:#111;font-weight:700'>{esc(d['items'][0]['title'].replace(chr(10), ' '))}</div></div>"))


def news(d, i, it, with_then):
    n = len(d["items"])
    pts = "".join(f"<li><span class='dot'></span>{esc(p)}</li>" for p in it["points"])
    hide = "" if with_then else " hide"
    then = (f"<div class='then{hide}'><div class='lab'><span>THEN</span>{esc(it['then_label'])}</div>"
            f"<p class='old'>{esc(it['then'])}</p><p class='now'><b>NOW →</b> {esc(it['link'])}</p></div>")
    return page(top(d) + f"<div class='main'><div class='row'><div class='num'>{i+1:02d} <span>/ {n:02d}</span></div>"
                f"<div class='cat'>{esc(it['category'])}</div></div><div class='title'>{esc(it['title'])}</div>"
                f"<ul>{pts}</ul>{then}<div class='src'>출처 · {esc(it['source'])}</div></div>")


def outro(d):
    return page(top(d) + "<div class='center'><div class='hsub' style='font-size:96px;margin:0'>"
                "오늘 뉴스는<br>여기까지<span style='color:%s'>.</span></div>"
                "<div class='hsm'>잊혀진 뉴스와 오늘의 뉴스를 잇는<br><b style='color:#111'>Neols</b>를 팔로우하세요</div>"
                "<div class='hsm' style='color:#111;font-weight:700'>%s</div></div>" % (ACCENT, d["handle"]))


def ff(args):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *args], check=True)


def still(png, dur, out, fade_in=False):
    vf = f"format=yuv420p,loop=-1:1,trim=duration={dur}"
    if fade_in:
        vf += ",fade=t=in:st=0:d=0.4"
    tmp = str(out) + ".tmp.mp4"
    ff(["-framerate", str(FPS), "-i", str(png), "-vf", vf, *ENC, tmp])
    os.replace(tmp, out)


def two_step(a, b, da, db, out):
    """A를 보여주다 B(THEN 상자 등장)로 크로스페이드 — 한 파일 안에서."""
    xd = 0.5
    tmp = str(out) + ".tmp.mp4"
    ff(["-framerate", str(FPS), "-i", str(a), "-framerate", str(FPS), "-i", str(b),
        "-filter_complex",
        f"[0]format=yuv420p,loop=-1:1,trim=duration={da + xd},setpts=PTS-STARTPTS[a];"
        f"[1]format=yuv420p,loop=-1:1,trim=duration={db},setpts=PTS-STARTPTS[b];"
        f"[a][b]xfade=transition=fade:duration={xd}:offset={da}[v]",
        "-map", "[v]", *ENC, tmp])
    os.replace(tmp, out)


def build(d, out_dir):
    out = Path(out_dir)
    (out / "frames").mkdir(parents=True, exist_ok=True)
    pages = {"intro": intro(d), "outro": outro(d)}
    for i, it in enumerate(d["items"]):
        pages[f"n{i}a"] = news(d, i, it, False)
        pages[f"n{i}b"] = news(d, i, it, True)
    with sync_playwright() as p:
        br = p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
        pg = br.new_page(viewport={"width": W, "height": H})
        for k, h in pages.items():
            pg.set_content(h)
            pg.wait_for_timeout(120)
            pg.screenshot(path=str(out / "frames" / f"{k}.png"))
        br.close()
    f = out / "frames"
    scenes = [out / "s_intro.mp4"]
    still(f / "intro.png", 2.5, scenes[0], fade_in=True)
    for i in range(len(d["items"])):
        s = out / f"s_n{i}.mp4"
        two_step(f / f"n{i}a.png", f / f"n{i}b.png", 2.8, 4.2, s)
        scenes.append(s)
    so = out / "s_outro.mp4"
    still(f / "outro.png", 2.5, so)
    scenes.append(so)
    lst = out / "list.txt"
    lst.write_text("".join(f"file '{s.resolve()}'\n" for s in scenes))
    joined = out / "joined.mp4"
    ff(["-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(joined)])
    final = out / f"neols_reel_{d['date'].replace('.', '')}.mp4"
    tmp = str(final) + ".tmp.mp4"
    # 무음 오디오 트랙 추가(업로드 호환성), 음악은 인스타에서 선택
    ff(["-i", str(joined), "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
        "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-shortest", "-movflags", "+faststart", tmp])
    os.replace(tmp, final)
    return final


if __name__ == "__main__":
    d = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    print(build(d, sys.argv[2]))
