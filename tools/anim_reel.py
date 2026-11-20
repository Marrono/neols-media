"""Neols 움직이는 릴스 템플릿 샘플 3종 (A 시네마 / B 스플릿 / C 콜라주).

사용법: python3 anim_reel.py <A|B|C> <out.mp4> [--frames t1,t2,...]  (--frames: 해당 시각 PNG만 저장)
HTML 안의 draw(t) 함수로 매 프레임을 그리고, JPEG(92)로 찍어 ffmpeg에 바로 넘겨요.
"""
import base64
import subprocess
import sys

from playwright.sync_api import sync_playwright

W, H, FPS, DUR = 1080, 1920, 30, 15.0


def b64(p):
    return "data:image/jpeg;base64," + base64.b64encode(open(p, "rb").read()).decode()


D = {
    "cab": b64("/home/claude/cardnews/ppi_cover.jpg"),
    "bok": b64("/home/claude/cardnews/bok.jpg"),
    "cab_c": "사진 · Bayartai / Wikimedia Commons / CC0",
    "bok_c": "사진 · Wikimedia Commons / Public domain",
    "src": "자료 · 한국은행 발표(뉴스핌·뉴스토마토·이투데이 보도)",
}

BASE = """
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:1080px;height:1920px;overflow:hidden}
body{font-family:'Noto Sans CJK KR',sans-serif;letter-spacing:-0.03em;word-break:keep-all;position:relative}
.abs{position:absolute}
.ph{position:absolute;background-size:cover;background-position:center;will-change:transform}
.chip{display:inline-flex;align-items:center;gap:14px;font-size:46px;font-weight:900;padding:14px 30px;border-radius:60px}
.dn{background:#2F5BFF;color:#fff}.up{background:#FF4B3E;color:#fff}
.cred{font-size:24px;color:rgba(255,255,255,.75);font-weight:500}
"""

HELP = """
const $=s=>document.querySelector(s);
const P=(t,a,b)=>Math.min(1,Math.max(0,(t-a)/(b-a)));
const E=x=>1-Math.pow(1-x,3);
const BK=x=>{const c=1.7;return 1+(c+1)*Math.pow(x-1,3)+c*Math.pow(x-1,2)};
function set(el,o,tf,extra){el=typeof el==='string'?$(el):el;el.style.opacity=o;if(tf!==undefined)el.style.transform=tf;if(extra)Object.assign(el.style,extra)}
function win(t,a,b,fi=.3,fo=.3){return Math.min(P(t,a,a+fi),1-P(t,b-fo,b))}
"""

# ───────────────────────── A. 시네마 ─────────────────────────
A = f"""
<style>{BASE}
body{{background:#000;color:#fff}}
.shade{{position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,.55) 0%,rgba(0,0,0,.05) 30%,rgba(0,0,0,.25) 55%,rgba(0,0,0,.85) 100%)}}
.top{{position:absolute;top:150px;left:80px;right:80px;display:flex;justify-content:space-between;align-items:center;font-size:40px;font-weight:900}}
.top i{{font-style:normal;color:#7D97FF}} .tag{{font-size:28px;font-weight:700;border:2px solid #fff;border-radius:40px;padding:6px 20px}}
.prog{{position:absolute;top:110px;left:80px;right:80px;height:6px;background:rgba(255,255,255,.25);border-radius:6px}}
.prog b{{display:block;height:100%;background:#fff;border-radius:6px;width:0}}
.hook{{left:80px;right:150px;top:1020px;font-size:112px;font-weight:900;line-height:1.18}}
.hook span{{display:block}} .hl{{position:relative;display:inline-block}}
.hl:after{{content:'';position:absolute;left:0;bottom:8px;height:26px;width:var(--w,0%);background:#2F5BFF;z-index:-1}}
.big{{left:80px;top:860px;font-size:270px;font-weight:900;line-height:1}} .lbl{{left:86px;top:790px;font-size:46px;font-weight:700}}
.chips{{left:80px;top:1180px;display:flex;flex-direction:column;gap:22px;align-items:flex-start}}
.then{{left:80px;top:700px;font-size:80px;font-weight:900;letter-spacing:.06em;border:6px solid #fff;padding:6px 30px}}
.yr{{left:80px;top:860px;font-size:230px;font-weight:900;font-variant-numeric:tabular-nums;line-height:1}}
.tf{{left:80px;right:150px;top:1140px;font-size:60px;font-weight:900;line-height:1.35}}
.tf small{{display:block;font-size:40px;font-weight:500;color:#ddd;margin-top:14px}}
.grain{{position:absolute;inset:-50px;opacity:0;mix-blend-mode:overlay}}
.link{{left:80px;right:150px;top:760px;font-size:70px;font-weight:900;line-height:1.38}}
.link .w{{opacity:.15}} .now{{color:#7D97FF}}
.end{{inset:0;display:flex;flex-direction:column;justify-content:center;align-items:center;background:#F7F6F2;color:#111}}
.end .lg{{font-size:200px;font-weight:900}} .end .lg i{{font-style:normal;color:#2F5BFF}}
.end p{{font-size:46px;font-weight:700;margin-top:24px;color:#555}} .end .fo{{margin-top:60px;background:#111;color:#fff;font-size:44px;font-weight:900;padding:22px 60px;border-radius:80px}}
.credit{{left:80px;bottom:300px}}
</style>
<div class="ph" id="p1" style="inset:0;background-image:url({D['cab']})"></div>
<div class="ph" id="p2" style="inset:0;background-image:url({D['bok']});opacity:0"></div>
<div class="shade"></div>
<svg class="grain" id="gr" width="1180" height="2020"><filter id="n"><feTurbulence id="tb" type="fractalNoise" baseFrequency=".9" numOctaves="2" seed="1"/></filter><rect width="100%" height="100%" filter="url(#n)"/></svg>
<div class="prog"><b id="pb"></b></div>
<div class="top"><span>Ne<i>ol</i>s</span><span class="tag" id="tag">NOW · 2026.11</span></div>
<div class="abs hook" id="hook"><span id="h1">배추는 반값,</span><span id="h2"><span class="hl" id="hl">기름은 껑충?</span></span></div>
<div class="abs lbl" id="lbl">10월 생산자물가</div>
<div class="abs big" id="big">−0.1%</div>
<div class="abs chips"><span class="chip dn" id="c1">▼ 채소 −11.2%</span><span class="chip up" id="c2">▲ 석유류 +14.9%</span></div>
<div class="abs then" id="then">THEN</div>
<div class="abs yr" id="yr">2026</div>
<div class="abs tf" id="tf">배추 −46% · 시금치 −62%<small>2024년 10월, 농산물 생산자물가<br>2년 만에 가장 크게 떨어졌어요</small></div>
<div class="abs link" id="link"></div>
<div class="abs cred credit" id="cred">{D['cab_c']}</div>
<div class="abs end" id="end"><div class="lg">Ne<i>ol</i>s</div><p>잊혀진 뉴스와 오늘의 뉴스를 잇다</p><div class="fo">@neols.news 팔로우</div></div>
<script>{HELP}
const LW="가을마다 채소값이 물가를 누르지만, 올해는 *기름값이 반대로 끌어올리고 있어요.".split(' ');
$('#link').innerHTML=LW.map(w=>w[0]==='*'?`<span class='w now'>${{w.slice(1)}}</span>`:`<span class='w'>${{w}}</span>`).join(' ');
function draw(t){{
 $('#pb').style.width=(t/{DUR}*100)+'%';
 // 사진 1: 계속 천천히 줌, THEN 구간에선 흑백
 const z1=1.08+0.14*(t/{DUR});
 const gray=P(t,6.6,7.2)*(1-P(t,10.4,10.8));
 set('#p1',1-win(t,3.0,6.6,.25,.25),`scale(${{z1}}) translateY(${{-30*t/15}}px)`,{{filter:`grayscale(${{gray}}) sepia(${{gray*.35}}) contrast(${{1+gray*.15}}) blur(${{P(t,10.4,10.9)*14}}px) brightness(${{1-P(t,10.4,10.9)*.45}})`}});
 set('#p2',win(t,3.0,6.6,.25,.25),`scale(${{1.15+0.12*P(t,3,6.6)}}) translateX(${{-40*P(t,3,6.6)}}px)`);
 const g=$('#gr');g.style.opacity=gray*.55;$('#tb').setAttribute('seed',Math.floor(t*15));
 $('#tag').textContent=(t>=6.6&&t<10.5)?'THEN · 2024.10':'NOW · 2026.11';
 // 0~3 훅
 const h1=1,h2=E(P(t,-.2,.35)),out=P(t,2.7,3.0);
 set('#h1',1-out,`scale(${{1.06-0.06*E(P(t,0,.5))}}) translateY(${{-out*40}}px)`,{{transformOrigin:'left bottom'}});
 set('#h2',h2*(1-out),`translateY(${{(1-h2)*60-out*40}}px)`);
 $('#hl').style.setProperty('--w',(E(P(t,.4,1.0))*100)+'%');
 // 3~6.6 숫자
 const bi=BK(P(t,3.15,3.6)),bo=P(t,6.3,6.6);
 set('#lbl',P(t,3.1,3.4)*(1-bo),`translateY(${{(1-P(t,3.1,3.4))*20}}px)`);
 set('#big',P(t,3.15,3.35)*(1-bo),`scale(${{(0.6+0.4*bi)}})`,{{transformOrigin:'left center'}});
 const c1=E(P(t,4.0,4.4)),c2=E(P(t,4.5,4.9));
 set('#c1',c1*(1-bo),`translateX(${{(1-c1)*-200}}px)`);set('#c2',c2*(1-bo),`translateX(${{(1-c2)*-200}}px)`);
 // 6.6~10.5 THEN
 const th=BK(P(t,6.7,7.05)),tho=P(t,10.2,10.5);
 set('#then',P(t,6.7,6.8)*(1-tho),`scale(${{2-th}}) rotate(${{-4+4*th}}deg)`,{{transformOrigin:'left center'}});
 const yp=E(P(t,7.0,8.0));$('#yr').textContent=Math.round(2026-2*yp);
 set('#yr',P(t,6.95,7.1)*(1-tho),'none');
 const tf=E(P(t,8.1,8.6));set('#tf',tf*(1-tho),`translateY(${{(1-tf)*40}}px)`);
 // 10.5~13 연결 문장 단어별
 const lk=win(t,10.5,13.0,.2,.3);set('#link',lk,'none');
 document.querySelectorAll('#link .w').forEach((w,i)=>w.style.opacity=.15+.85*E(P(t,10.6+i*.17,10.85+i*.17)));
 set('#cred',(1-P(t,12.7,13))*(t<3||t>6.6?1:0),'none');
 if(t>=3&&t<6.6){{$('#cred').textContent='{D['bok_c']}';$('#cred').style.opacity=win(t,3,6.6,.2,.2)}} else $('#cred').textContent='{D['cab_c']}';
 // 13~15 엔딩
 const en=E(P(t,13.0,13.4));set('#end',en,`translateY(${{(1-en)*80}}px)`);
}}
</script>"""

# ───────────────────────── B. 스플릿 ─────────────────────────
B = f"""
<style>{BASE}
body{{background:#111;color:#fff}}
.half{{position:absolute;left:0;right:0;overflow:hidden}}
#top{{top:0}} #bot{{bottom:0}}
.half .ph{{inset:-60px}}
.dim{{position:absolute;inset:0}}
.lab{{position:absolute;left:80px;font-weight:900}}
.lab b{{display:inline-block;font-size:30px;letter-spacing:.12em;padding:6px 18px;border:3px solid currentColor;border-radius:40px;margin-right:18px;vertical-align:middle}}
.lab span{{font-size:64px;vertical-align:middle}}
.div{{position:absolute;left:0;right:0;height:10px;background:#2F5BFF;box-shadow:0 0 30px #2F5BFF}}
.hook{{position:absolute;left:60px;right:60px;text-align:center;font-size:96px;font-weight:900;line-height:1.15;color:#111}}
.hook span{{background:#fff;padding:4px 26px;box-decoration-break:clone;-webkit-box-decoration-break:clone}}
.hook em{{font-style:normal;color:#FF4B3E}}
.nf{{position:absolute;left:80px;right:150px}}
.nf .k{{font-size:40px;font-weight:700}} .nf .v{{font-size:200px;font-weight:900;line-height:1.05}}
.bars{{position:absolute;left:80px;right:150px}}
.bar{{margin-bottom:28px}} .bar .t{{font-size:40px;font-weight:700;margin-bottom:10px;display:flex;justify-content:space-between}}
.bar .tr{{height:46px;background:rgba(255,255,255,.18);border-radius:8px;overflow:hidden}} .bar .fl{{height:100%;width:0;background:#9DB1FF;border-radius:8px}}
.link{{position:absolute;left:80px;right:150px;font-size:62px;font-weight:900;line-height:1.38}}
.link b{{color:#FF4B3E}}
.end{{position:absolute;inset:0;display:flex;flex-direction:column;justify-content:center;align-items:center;background:#F7F6F2;color:#111}}
.end .lg{{font-size:200px;font-weight:900}} .end .lg i{{font-style:normal;color:#2F5BFF}}
.end p{{font-size:46px;font-weight:700;margin-top:24px;color:#555}} .end .fo{{margin-top:60px;background:#111;color:#fff;font-size:44px;font-weight:900;padding:22px 60px;border-radius:80px}}
.brand{{position:absolute;top:150px;right:150px;font-size:40px;font-weight:900}} .brand i{{font-style:normal;color:#7D97FF}}
.cred{{position:absolute;left:80px}}
</style>
<div class="half" id="top"><div class="ph" id="pt" style="background-image:url({D['cab']})"></div><div class="dim" id="dt" style="background:linear-gradient(180deg,rgba(0,0,0,.45),rgba(0,0,0,.2) 40%,rgba(0,0,0,.6))"></div>
 <div class="lab" id="lt" style="top:150px;color:#fff"><b>NOW</b><span>2026.10</span></div>
 <div class="nf" id="nf" style="top:330px"><div class="k">생산자물가 한 달 새</div><div class="v">−0.1%</div></div>
 <div class="bars" id="nb" style="top:640px">
  <div class="bar"><div class="t"><span>채소 (소비자물가)</span><span id="v1">−11.2%</span></div><div class="tr"><div class="fl" id="f1"></div></div></div>
  <div class="bar"><div class="t"><span>석유류 (소비자물가)</span><span id="v2">+14.9%</span></div><div class="tr"><div class="fl" id="f2" style="background:#FF4B3E"></div></div></div>
 </div>
 <div class="cred" id="ct" style="top:240px">{D['cab_c']}</div>
</div>
<div class="half" id="bot"><div class="ph" id="pbt" style="background-image:url({D['cab']});filter:grayscale(1) sepia(.35) contrast(1.1)"></div><div class="dim" style="background:rgba(0,0,0,.55)"></div>
 <div class="lab" id="lb" style="top:60px;color:#E8E1C8"><b>THEN</b><span id="yr">2024.10</span></div>
 <div class="nf" id="tf" style="top:200px"><div class="k">농산물 생산자물가 2년 만에 최대 하락</div></div>
 <div class="bars" id="tb" style="top:330px">
  <div class="bar"><div class="t"><span>배추</span><span>−46%</span></div><div class="tr"><div class="fl" id="f3" style="background:#E8E1C8"></div></div></div>
  <div class="bar"><div class="t"><span>시금치</span><span>−62%</span></div><div class="tr"><div class="fl" id="f4" style="background:#E8E1C8"></div></div></div>
 </div>
</div>
<div class="div" id="dv"></div>
<div class="brand">Ne<i>ol</i>s</div>
<div class="hook" id="hook"><span>배추는 반값,</span><br><span><em>기름은 껑충?</em></span></div>
<div class="link" id="link" style="top:760px">가을마다 채소값이 물가를 누르지만,<br>올해는 <b>기름값이</b> 반대로<br>끌어올리고 있어요.</div>
<div class="cred" id="cs" style="bottom:300px;opacity:0">{D['src']}</div>
<div class="end" id="end"><div class="lg">Ne<i>ol</i>s</div><p>잊혀진 뉴스와 오늘의 뉴스를 잇다</p><div class="fo">@neols.news 팔로우</div></div>
<script>{HELP}
function draw(t){{
 // 경계선 위치(비율): 0~8초 50%, 8~12초 30%로 올라가며 THEN 확대, 12초~ 화면 닫힘
 let s=0.5-0.2*E(P(t,7.8,8.4))+0.2*E(P(t,11.7,12.1));
 const close=E(P(t,11.9,12.4));
 const th=1920*s*(1-close), bh=1920*(1-s)*(1-close);
 $('#top').style.height=th+'px';$('#bot').style.height=bh+'px';
 // 처음 등장: 위는 왼쪽에서, 아래는 오른쪽에서
 const inA=1;
 $('#top').style.transform=`translateX(${{(1-inA)*-1080}}px)`;$('#bot').style.transform=`translateX(${{(1-inA)*1080}}px)`;
 $('#dv').style.top=(th-5)+'px';$('#dv').style.opacity=1-close;$('#dv').style.transform='none';
 $('#pt').style.transform=`scale(${{1.05+0.12*t/15}})`;$('#pbt').style.transform=`scale(${{1.2-0.1*t/15}}) translateX(${{20*t/15}}px)`;
 // 훅 (경계선 위에 고정)
 const h=BK(P(t,-.25,.3)),ho=P(t,2.8,3.1);
 set('#hook',(1-ho),`translateY(-50%) scale(${{.7+.3*h}})`);$('#hook').style.top=th+'px';
 // NOW 구간 3~8
 const nI=E(P(t,3.0,3.4));set('#nf',nI*(1-P(t,7.6,7.9)),`translateY(${{(1-nI)*40}}px)`);
 set('#nb',P(t,3.6,3.9)*(1-P(t,7.6,7.9)),'none');
 $('#f1').style.width=(E(P(t,3.8,4.6))*11.2/15*100)+'%';$('#f2').style.width=(E(P(t,4.2,5.0))*14.9/15*100)+'%';
 set('#lt',1,'none');
 // THEN 구간 8~12 (위쪽 어둡게)
 $('#dt').style.background=`linear-gradient(180deg,rgba(0,0,0,${{.45+.4*P(t,7.8,8.3)}}),rgba(0,0,0,${{.2+.6*P(t,7.8,8.3)}}) 40%,rgba(0,0,0,.6))`;
 set('#lb',.35+.65*P(t,7.9,8.3),`translateY(${{(1-E(P(t,7.9,8.4)))*20}}px)`);
 set('#tf',P(t,8.4,8.8),'none');set('#tb',P(t,8.7,9.0),'none');
 $('#f3').style.width=(E(P(t,8.9,9.8))*46/70*100)+'%';$('#f4').style.width=(E(P(t,9.3,10.2))*62/70*100)+'%';
 // 연결 12~13.4
 const lk=win(t,12.2,13.4,.3,.3);set('#link',lk,`translateY(${{(1-E(P(t,12.2,12.6)))*40}}px)`);set('#cs',lk,'none');
 document.body.style.background=t>12?'#111':'#111';
 const en=E(P(t,13.3,13.7));set('#end',en,`translateY(${{(1-en)*80}}px)`);
}}
</script>"""

# ───────────────────────── C. 콜라주 ─────────────────────────
C = f"""
<style>{BASE}
body{{background:#F7F6F2;color:#111}}
.segs{{position:absolute;top:110px;left:80px;right:80px;display:flex;gap:10px}}
.segs div{{flex:1;height:7px;background:#DDDBD3;border-radius:6px;overflow:hidden}} .segs b{{display:block;height:100%;width:0;background:#111}}
.top{{position:absolute;top:150px;left:80px;right:80px;display:flex;justify-content:space-between;font-size:40px;font-weight:900}}
.top i{{font-style:normal;color:#2F5BFF}} .top span.d{{font-size:30px;color:#8A8A85;font-weight:600}}
.pol{{position:absolute;background:#fff;padding:22px 22px 70px;box-shadow:0 30px 60px rgba(0,0,0,.25)}}
.pol .im{{width:100%;height:100%;background-size:cover;background-position:center}}
.pol .cp{{position:absolute;left:24px;bottom:18px;font-size:22px;color:#8A8A85}}
.hook{{left:80px;right:150px;top:1180px;font-size:108px;font-weight:900;line-height:1.18}}
.mk{{position:relative;display:inline-block;z-index:0}} .mk:before{{content:'';position:absolute;left:-8px;right:auto;width:calc(var(--w,0)*1% + 0px);top:18%;bottom:6%;background:#C9D4FF;z-index:-1;border-radius:6px}}
.big{{left:80px;top:1130px;font-size:250px;font-weight:900;line-height:1}} .lbl{{left:84px;top:1060px;font-size:44px;font-weight:700}}
.circ{{position:absolute;left:30px;top:1090px}}
.chips{{left:80px;top:1420px;display:flex;gap:18px;flex-wrap:wrap;right:150px}}
.chip{{font-size:40px}}
.stamp{{position:absolute;font-size:110px;font-weight:900;color:#E0321F;border:10px solid #E0321F;padding:0 30px;letter-spacing:.06em;border-radius:12px;mix-blend-mode:multiply}}
.tf{{left:80px;right:150px;top:1180px;font-size:66px;font-weight:900;line-height:1.3}}
.tf small{{display:block;font-size:40px;font-weight:500;color:#555;margin-top:16px}}
.q{{left:80px;right:150px;top:640px;font-size:68px;font-weight:900;line-height:1.4}}
.q .qm{{font-size:220px;color:#2F5BFF;line-height:.6;display:block;height:120px}}
.q b{{background:linear-gradient(transparent 60%,#C9D4FF 60%)}}
.end{{inset:0;display:flex;flex-direction:column;justify-content:center;align-items:center;background:#111;color:#fff}}
.end .lg{{font-size:200px;font-weight:900}} .end .lg i{{font-style:normal;color:#7D97FF}}
.end p{{font-size:46px;font-weight:700;margin-top:24px;color:#bbb}} .end .fo{{margin-top:60px;background:#fff;color:#111;font-size:44px;font-weight:900;padding:22px 60px;border-radius:80px}}
.src{{left:80px;bottom:300px;font-size:24px;color:#8A8A85}}
</style>
<div class="segs"><div><b id="s1"></b></div><div><b id="s2"></b></div><div><b id="s3"></b></div><div><b id="s4"></b></div></div>
<div class="top"><span>Ne<i>ol</i>s</span><span class="d" id="dd">NOW · 2026.11.20</span></div>
<div class="pol" id="q1" style="left:120px;top:290px;width:840px;height:760px"><div class="im" id="i1" style="background-image:url({D['cab']})"></div><div class="cp">{D['cab_c']}</div></div>
<div class="pol" id="q2" style="left:150px;top:300px;width:800px;height:620px"><div class="im" style="background-image:url({D['bok']})"></div><div class="cp">{D['bok_c']}</div></div>
<div class="pol" id="q3" style="left:110px;top:280px;width:860px;height:780px"><div class="im" style="background-image:url({D['cab']});filter:grayscale(1) sepia(.45) contrast(1.1);background-position:30% 70%;background-size:160%"></div><div class="cp">{D['cab_c']}</div></div>
<div class="stamp" id="st" style="left:560px;top:860px">THEN</div>
<div class="abs hook" id="hook">배추는 반값,<br><span class="mk" id="mk">기름은 껑충?</span></div>
<div class="abs lbl" id="lbl">10월 생산자물가</div>
<div class="abs big" id="big">−0.1%</div>
<svg class="circ" id="cc" width="760" height="330"><ellipse cx="380" cy="165" rx="360" ry="140" fill="none" stroke="#2F5BFF" stroke-width="10" stroke-linecap="round" pathLength="100" stroke-dasharray="100" stroke-dashoffset="100" id="el" transform="rotate(-4 380 165)"/></svg>
<div class="abs chips" id="chips"><span class="chip dn" id="c1">▼ 채소 −11.2%</span><span class="chip up" id="c2">▲ 석유류 +14.9%</span></div>
<div class="abs tf" id="tf">2024.10<br>배추 −46% · 시금치 −62%<small>농산물 생산자물가가 2년 만에 가장 크게 떨어졌어요</small></div>
<div class="abs q" id="q"><span class="qm">“</span>가을마다 채소값이 물가를 누르지만, 올해는 <b>기름값이 반대로</b> 끌어올리고 있어요.</div>
<div class="abs src" id="src">{D['src']}</div>
<div class="abs end" id="end"><div class="lg">Ne<i>ol</i>s</div><p>잊혀진 뉴스와 오늘의 뉴스를 잇다</p><div class="fo">@neols.news 팔로우</div></div>
<script>{HELP}
function drop(id,t,a,b,rot){{ // 폴라로이드가 위에서 떨어져 내려앉음
 const p=BK(P(t,a,a+.5)),o=P(t,b-.3,b);
 set(id,P(t,a,a+.12)*(1-o),`translateY(${{(1-p)*-500 - o*60}}px) rotate(${{rot+(1-p)*8}}deg) scale(${{1-o*.05}})`);
}}
function draw(t){{
 [[0,3],[3,7],[7,11],[11,13]].forEach(([a,b],i)=>$('#s'+(i+1)).style.width=(P(t,a,b)*100)+'%');
 $('#dd').textContent=(t>=7&&t<11)?'THEN · 2024.10':'NOW · 2026.11.20';
 drop('#q1',t,-.4,3.05,-3); $('#i1').style.transform=`scale(${{1+0.06*P(t,0,3)}})`;$('#i1').parentElement.style.overflow='hidden';
 drop('#q2',t,3.0,7.05,2.5);
 drop('#q3',t,7.0,11.05,-2);
 // 훅
 const h=E(P(t,-.3,.25)),ho=P(t,2.75,3.0);set('#hook',h*(1-ho),`translateY(${{(1-h)*50}}px)`);
 $('#mk').style.setProperty('--w',(E(P(t,.35,.95))*104).toFixed(1));
 // 숫자
 const bo=P(t,6.7,7.0),bi=BK(P(t,3.3,3.75));
 set('#lbl',P(t,3.2,3.5)*(1-bo),'none');set('#big',P(t,3.3,3.45)*(1-bo),`scale(${{.6+.4*bi}})`,{{transformOrigin:'left center'}});
 $('#el').setAttribute('stroke-dashoffset',100-100*E(P(t,4.0,4.7)));set('#cc',1-bo,'none');
 const c1=E(P(t,4.8,5.2)),c2=E(P(t,5.2,5.6));set('#c1',c1*(1-bo),`translateY(${{(1-c1)*40}}px)`);set('#c2',c2*(1-bo),`translateY(${{(1-c2)*40}}px)`);
 // THEN 도장 쾅
 const sp=P(t,7.6,7.85),so=P(t,10.7,11.0),shake=(t>7.85&&t<8.1)?Math.sin(t*120)*8:0;
 set('#st',P(t,7.6,7.65)*(1-so),`translate(${{shake}}px,${{shake/2}}px) scale(${{2.6-1.6*E(sp)}}) rotate(-12deg)`);
 const tf=E(P(t,8.2,8.7));set('#tf',tf*(1-so),`translateY(${{(1-tf)*40}}px)`);
 // 인용 11~13
 const q=win(t,11.0,13.1,.35,.3);set('#q',q,`translateY(${{(1-E(P(t,11,11.4)))*40}}px)`);set('#src',q,'none');
 const en=E(P(t,13.0,13.4));set('#end',en,`translateY(${{(1-en)*80}}px)`);
}}
</script>"""

PAGES = {"A": A, "B": B, "C": C}


def main():
    style, out = sys.argv[1], sys.argv[2]
    frames = None
    if "--frames" in sys.argv:
        frames = [float(x) for x in sys.argv[sys.argv.index("--frames") + 1].split(",")]
    with sync_playwright() as p:
        br = p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
        pg = br.new_page(viewport={"width": W, "height": H})
        pg.set_content("<!DOCTYPE html><html><head><meta charset='utf-8'></head><body>" + PAGES[style] + "</body></html>")
        pg.wait_for_timeout(500)
        if frames:
            for t in frames:
                pg.evaluate(f"draw({t})")
                pg.screenshot(path=f"{out}_{t:05.2f}.png")
        else:
            tmp = out[:-4] + ".part.mp4"
            ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(FPS),
                                   "-c:v", "mjpeg", "-i", "-", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
                                   "-shortest", "-c:v", "libx264", "-crf", "20", "-preset", "veryfast",
                                   "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "64k", tmp], stdin=subprocess.PIPE)
            n = int(DUR * FPS)
            for i in range(n):
                pg.evaluate(f"draw({i / FPS})")
                ff.stdin.write(pg.screenshot(type="jpeg", quality=92))
            ff.stdin.close()
            if ff.wait() == 0:
                import os
                os.replace(tmp, out)
        br.close()


if __name__ == "__main__":
    main()
