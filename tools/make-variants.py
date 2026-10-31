#!/usr/bin/env python3
"""Generate four design variants of the portfolio (시안 A–D).

Reads index.html (current live design), swaps the hero copy, injects a
variant stylesheet + micro-scripts, and writes variant-a.html … variant-d.html
at the repo root so all relative asset paths (photos/, museum/) keep working.

  python3 tools/make-variants.py
"""
import re, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
base = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()

HERO_RE = re.compile(r'<div class="hero-content">[\s\S]*?</div>')

BADGE = lambda t: ('<div style="position:fixed;top:14px;left:50%;transform:translateX(-50%);'
    'z-index:10000;font:600 10px/1 Jost,sans-serif;letter-spacing:.3em;text-transform:uppercase;'
    'padding:8px 16px;background:#16150f;color:#f4f1ea;border:1px solid #9a7b46;">'
    + t + '</div>')

SPECS = {}

# ────────────────────────────── A · Cornell Salon ─────────────────────────────
SPECS["a"] = dict(
    title="Yeonsu Ahn — 시안 A · Cornell Salon",
    badge="시안 A — Cornell Salon",
    hero='''<div class="hero-content">
<h2>Cheongshim International Academy &middot; Class of 2026</h2>
<h1>YEONSU<br>AHN</h1>
<p>&ldquo;Any person&hellip; any study.&rdquo; Eight years of plates &mdash; drawing, diplomacy, wandering &mdash; kept as one working archive: an artist who leads in Model UN and VANK, and leads on paper too.</p>
<a class="btn" href="#art">Enter the Salon</a>
</div>''',
    css='''
<style id="variant-a">
:root{ --gilt:#b31b1b; --paper:#faf8f3; }
.hero{ background:
  radial-gradient(1200px 500px at 80% -10%, rgba(179,27,27,.07), transparent 60%),
  linear-gradient(to bottom, transparent 96%, var(--rule) 96%, var(--rule) 100%), var(--paper); }
.hero::after{ content:"ANY PERSON · ANY STUDY"; position:absolute; left:50%; top:50%;
  transform:translate(-50%,-50%) rotate(-4deg); white-space:nowrap;
  font:500 clamp(4rem,13vw,12rem)/1 var(--font-display); color:transparent;
  -webkit-text-stroke:1px rgba(22,21,15,.07); letter-spacing:.08em; z-index:1; pointer-events:none; }
.hero-content h1{ font-weight:600; letter-spacing:.02em; }
.hero-content h1 span.cornell{ color:var(--gilt); }
.section-title::after{ content:""; display:block; width:54px; height:2px; background:var(--gilt); margin:22px auto 0; }
.gallery-grid{ perspective:1400px; }
.gallery-item{ transform-style:preserve-3d; will-change:transform; }
.gallery-item img{ transform:translateZ(0); }
.gallery-item .plate-badge{ position:absolute; top:-16px; left:-16px; z-index:5;
  width:46px; height:46px; border-radius:50%; background:var(--gilt); color:#faf8f3;
  font:500 11px/46px var(--font-body); letter-spacing:.08em; text-align:center;
  box-shadow:0 10px 20px -6px rgba(179,27,27,.55); }
.gallery-item{ position:relative; }
.timeline-chapter h3{ border-color:rgba(179,27,27,.35); }
.btn{ border-color:var(--gilt); color:var(--gilt); }
.btn::before{ background:var(--gilt); }
.btn:hover{ color:#faf8f3; border-color:var(--gilt); }
</style>''',
    js='''
<script>
document.querySelectorAll('.gallery-item').forEach((el,i)=>{
  const badge=document.createElement('span');badge.className='plate-badge';
  badge.textContent=String(i+1).padStart(2,'0');el.prepend(badge);
  el.addEventListener('mousemove',e=>{const r=el.getBoundingClientRect();
    const x=(e.clientX-r.left)/r.width-.5,y=(e.clientY-r.top)/r.height-.5;
    el.style.transition='transform .1s linear';
    el.style.transform='translateY(0) perspective(900px) rotateY('+(x*9).toFixed(2)+'deg) rotateX('+(-y*7).toFixed(2)+'deg) scale(1.015)';});
  el.addEventListener('mouseleave',()=>{el.style.transition='transform .9s cubic-bezier(.19,1,.22,1)';el.style.transform='';});
});
</script>''',
)

# ────────────────────────────── B · Nocturne Archive ──────────────────────────
SPECS["b"] = dict(
    title="Yeonsu Ahn — 시안 B · Nocturne Archive",
    badge="시안 B — Nocturne Archive",
    hero='''<div class="hero-content">
<h2>Artist &middot; Diplomat &middot; Collector of Rooms</h2>
<h1 style="color:transparent;-webkit-text-stroke:1px #d8c9a3;">YEONSU AHN</h1>
<p>The Cornell I am applying to is a place of &ldquo;any study&rdquo; &mdash; so this archive refuses one identity: charcoal at noon, resolution text at dusk, a museum gallery at night. Every work hung under its own light.</p>
<a class="btn" href="#art">Walk the Dark Hall</a>
</div>''',
    css='''
<style id="variant-b">
html{background:#121009;}
body{background:#121009;color:#e9e2cf;}
body::before{opacity:.05;}
nav{background:rgba(18,16,9,.9);border-bottom-color:rgba(216,201,163,.14);}
nav .logo,nav ul li a{color:#e9e2cf;}
nav ul li a{color:#b7ab8b;}
nav ul li a:hover{color:#e9e2cf;}
.hero{background:
 radial-gradient(900px 480px at 50% 30%, rgba(216,201,163,.10), transparent 65%),
 linear-gradient(to bottom, transparent 96%, rgba(216,201,163,.16) 96%, rgba(216,201,163,.16) 100%), #121009;}
.hero p{color:#cfc5a8;}
.hero h2{color:#d8c9a3;}
.section.light{background:#181509;}
.section.dark{background:#0d0b06;}
.section-title{color:#e9e2cf;}
.section-subtitle{color:#a59a7c;}
.gallery-item img{background:#1d1a10;border-color:rgba(216,201,163,.2);outline-color:rgba(216,201,163,.08);
 box-shadow:0 40px 80px -30px rgba(0,0,0,.9);}
.gallery-item{position:relative;}
.gallery-item::before{content:"";position:absolute;inset:-9vh -6vw 0;
 background:radial-gradient(360px 240px at 50% -4%, rgba(216,201,163,.16), transparent 70%);
 pointer-events:none;}
.gallery-caption{border-bottom-color:rgba(216,201,163,.22);}
.gallery-caption h3{color:#b7ab8b;}
.gallery-caption .plate{color:#d8c9a3;}
.timeline::before{background:linear-gradient(to bottom,transparent,#d8c9a3,transparent);opacity:.35;}
.timeline-chapter h3{color:#e9e2cf;background:#181509;border-color:rgba(216,201,163,.28);}
.timeline-item::after{background:#181509;border-color:#b7ab8b;}
.timeline-overlay{background:rgba(24,21,9,.94);color:#e9e2cf;border-left-color:#d8c9a3;}
.date{color:#e9e2cf;} .location{color:#b7ab8b;}
footer{background:#0d0b06;color:#8f8569;}
.btn{border-color:#d8c9a3;color:#d8c9a3;}
.btn::before{background:#d8c9a3;}
.btn:hover{color:#121009;border-color:#d8c9a3;}
</style>''',
    js='''
<script>
document.querySelectorAll('.gallery-item').forEach(el=>{
  el.addEventListener('mousemove',e=>{const r=el.getBoundingClientRect();
    const px=((e.clientX-r.left)/r.width*100).toFixed(1),py=((e.clientY-r.top)/r.height*100).toFixed(1);
    el.style.setProperty('--sx',px+'%');el.style.setProperty('--sy',py+'%');});});
const st=document.createElement('style');
st.textContent='.gallery-item::after{content:"";position:absolute;inset:0;pointer-events:none;' +
 'background:radial-gradient(240px 200px at var(--sx,50%) var(--sy,30%),rgba(255,244,214,.10),transparent 70%);}' +
 '.gallery-item img{transform-style:preserve-3d;}';
document.head.append(st);
</script>''',
)

# ────────────────────────────── C · White Cube ────────────────────────────────
SPECS["c"] = dict(
    title="Yeonsu Ahn — 시안 C · White Cube",
    badge="시안 C — White Cube",
    hero='''<div class="hero-content">
<h2>Yeonsu Ahn &middot; Cheongshim International Academy &middot; 2026</h2>
<h1>LOOKING<br>IS A DISCIPLINE.</h1>
<p>Four hundred hours of drawing, three models of the UN, sixty-one museum rooms. Cornell asks what you will do with your curiosity &mdash; this cube holds the receipts.</p>
<a class="btn" href="#art">View the Works</a>
</div>''',
    css='''
<style id="variant-c">
:root{--paper:#ffffff;--rule:rgba(22,21,15,.12);}
.hero{min-height:110vh;}
.hero h1{font-size:clamp(3rem,9vw,8.5rem);font-weight:300;letter-spacing:-.01em;line-height:1.06;}
.hero h2{margin-bottom:3rem;letter-spacing:.55em;}
.hero p{font-family:var(--font-body);font-style:normal;font-size:.95rem;letter-spacing:.06em;color:#6a665c;max-width:520px;}
.gallery-grid{gap:24vh 8vw;padding:0 2vw;}
.gallery-item img{padding:0;border:none;outline:none;background:#fff;
 box-shadow:0 2px 4px rgba(0,0,0,.04), 0 40px 60px -40px rgba(0,0,0,.25);
 transition:transform 1s cubic-bezier(.19,1,.22,1),box-shadow 1s ease;will-change:transform;}
.gallery-item:hover img{transform:translateY(-18px) scale(1.02);
 box-shadow:0 4px 8px rgba(0,0,0,.05), 0 80px 90px -50px rgba(0,0,0,.35);}
.section{padding:22vh 8%;}
.section-title{font-weight:300;letter-spacing:.02em;}
.museum-cta{border-color:#16150f;color:#16150f;}
.museum-cta:hover{background:#16150f;color:#fff;}
</style>''',
    js='''
<script>
// Scroll parallax: hero type and artworks drift at different depths.
const h1=document.querySelector('.hero h1'), hc=document.querySelector('.hero-content');
window.addEventListener('scroll',()=>{const y=window.scrollY;
  if(hc) hc.style.transform='translateY('+(y*.22).toFixed(1)+'px)';
  if(hc) hc.style.opacity=Math.max(0,1-y/700).toFixed(3);
},{passive:true});
const io=new IntersectionObserver(es=>{es.forEach(e=>{if(e.isIntersecting){
  const img=e.target.querySelector('img');
  let t=0;const tick=()=>{const y=window.scrollY;const r=e.target.getBoundingClientRect();
    if(r.top<window.innerHeight&&r.bottom>0&&img){const p=(r.top+r.height/2-window.innerHeight/2)/window.innerHeight;
      img.style.setProperty('--py',(p*-40).toFixed(1)+'px');}t=requestAnimationFrame(tick);};
  tick();}});},{threshold:.2});
document.querySelectorAll('.gallery-item').forEach(el=>io.observe(el));
const st=document.createElement('style');
st.textContent='.gallery-item img{transform:translateY(var(--py,0px));}';
document.head.append(st);
</script>''',
)

# ────────────────────────────── D · Postcard Index ────────────────────────────
SPECS["d"] = dict(
    title="Yeonsu Ahn — 시안 D · Postcard Index",
    badge="시안 D — Postcard Index",
    hero='''<div class="hero-content" style="display:grid;grid-template-columns:1.2fr .8fr;gap:6vw;align-items:center;text-align:left;max-width:1200px;">
<div>
<h2>Portfolio for Cornell &middot; Class of 2026</h2>
<h1 style="font-size:clamp(3rem,7vw,6.2rem);">YEONSU<br>AHN</h1>
<p style="margin-left:0;">An artist with a delegation&rsquo;s notebook. Model UN, VANK, eight years of drawing &mdash; mailed to you as one bundle of postcards, each stamped where it was made.</p>
<a class="btn" href="#art">Open the Bundle</a>
</div>
<div class="scatter" aria-hidden="true">
<img src="photos/art/IMG_5885.jpeg" alt="">
<img src="photos/art/IMG_1206.jpeg" alt="">
<img src="photos/art/IMG_8140.jpg" alt="">
</div>
</div>''',
    css='''
<style id="variant-d">
:root{--gilt:#d8442a;}
.hero{min-height:96vh;}
.hero-content p{margin:0 0 3rem;}
.scatter{position:relative;height:420px;}
.scatter img{position:absolute;width:64%;object-fit:cover;border:8px solid #fff;
 box-shadow:8px 10px 0 rgba(22,21,15,.14), 0 24px 40px -18px rgba(22,21,15,.4);}
.scatter img:nth-child(1){top:0;left:8%;transform:rotate(-5deg);}
.scatter img:nth-child(2){top:26%;left:26%;transform:rotate(4deg);width:58%;}
.scatter img:nth-child(3){top:52%;left:4%;transform:rotate(-2deg);width:52%;}
.gallery-item{position:relative;}
.gallery-item img{transform:rotate(var(--tilt,0deg));
 box-shadow:7px 9px 0 rgba(22,21,15,.10), 0 30px 50px -22px rgba(22,21,15,.35);}
.gallery-item:nth-child(3n+1){--tilt:-1.6deg;}
.gallery-item:nth-child(3n+2){--tilt:1.3deg;}
.gallery-item:nth-child(3n){--tilt:-.7deg;}
.gallery-item::before{content:"";position:absolute;top:-12px;left:50%;width:96px;height:26px;
 transform:translateX(-50%) rotate(-2deg);background:rgba(216,68,42,.18);
 border-left:1px dashed rgba(22,21,15,.15);border-right:1px dashed rgba(22,21,15,.15);z-index:6;}
.gallery-item:hover img{transform:rotate(0deg) translateY(-4px);}
.timeline-chapter h3{border:none;border-bottom:2px solid var(--gilt);}
.btn{border-color:#16150f;}
.btn::before{background:var(--gilt);}
.btn:hover{border-color:var(--gilt);}
nav .logo::after{content:" ✶";color:var(--gilt);}
</style>''',
    js='''
<script>
document.querySelectorAll('.scatter img').forEach((im,i)=>{
 im.addEventListener('mousemove',e=>{const r=im.getBoundingClientRect();
  const x=(e.clientX-r.left)/r.width-.5,y=(e.clientY-r.top)/r.height-.5;
  im.style.transform=(i==0?'rotate(-5deg)':i==1?'rotate(4deg)':'rotate(-2deg)')+' translate('+(x*10)+'px,'+(y*8)+'px)';});
 im.addEventListener('mouseleave',e=>{im.style.transform='';});});
</script>''',
)

def build(key):
    s = SPECS[key]
    html = HERO_RE.sub(lambda m: s["hero"], base, count=1)
    html = html.replace("<title>Yeonsu Ahn - Digital Portfolio</title>",
                        "<title>%s</title>" % s["title"])
    html = html.replace("</head>", s["css"] + "\n</head>")
    html = html.replace("</body>", BADGE(s["badge"]) + s["js"] + "\n</body>")
    out = os.path.join(ROOT, "variant-%s.html" % key)
    open(out, "w", encoding="utf-8").write(html)
    print("wrote", out, len(html), "bytes")

for k in ("a", "b", "c", "d"):
    build(k)
