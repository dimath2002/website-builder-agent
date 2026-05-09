"""
🤖 Builder Agent — Website Generator
Παίρνει leads από leads.json και δημιουργεί live websites στο GitHub Pages.

Χρειάζεται environment variables:
  GEMINI_API_KEY  — από aistudio.google.com
  GITHUB_TOKEN    — Personal Access Token με 'repo' scope
  GITHUB_USERNAME — το github username σου
"""

import os
import json
import re
import time
import base64
import requests
from datetime import datetime

# ===== CONFIG =====
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN', '')
GITHUB_USERNAME = os.environ.get('GITHUB_USERNAME', '')

LEADS_FILE = 'leads.json'
PROCESSED_FILE = 'processed.json'
RESULTS_FILE = 'results.md'

if not all([GEMINI_API_KEY, GITHUB_TOKEN, GITHUB_USERNAME]):
    print("❌ Λείπουν environment variables! Ορίστε τα secrets στο GitHub.")
    exit(1)


# ===== HELPERS =====
def slugify(text: str) -> str:
    """Greek-friendly slug generator."""
    greek_to_latin = str.maketrans(
        'άέήίόύώΆΈΉΊΌΎΏαβγδεζηθικλμνξοπρστυφχψωΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩϊϋΐΰς',
        'aeiouoAEIOUOavgdezithiklmnxoprstyfchpsoAVGDEZITHIKLMNXOPRSTYFCHPSOiyiis'
    )
    text = text.translate(greek_to_latin)
    text = re.sub(r'[^a-zA-Z0-9\s-]', '', text)
    text = re.sub(r'\s+', '-', text.strip().lower())
    return text[:40]


def call_gemini(business: dict) -> dict:
    """Καλεί Gemini για να παράγει copy + theme."""
    prompt = f"""You are a senior Greek copywriter. Generate website copy for this business.

BUSINESS NAME: {business['business_name']}
TYPE: {business['business_type']}
LOCATION: {business.get('address', 'Χανιά')}
DESCRIPTION: {business.get('description', '')}

Return ONLY valid JSON (no markdown, no code blocks):
{{
  "hero_title": "main 4-6 word headline in Greek",
  "hero_accent": "2-3 word accent phrase in Greek",
  "hero_subtitle": "compelling 15-25 word description in Greek",
  "about_title": "about section title in Greek",
  "about_p1": "first paragraph 30-50 words in Greek",
  "about_p2": "second paragraph 30-50 words in Greek",
  "services": [
    {{"title": "service name", "desc": "15-20 word description in Greek"}},
    {{"title": "service name", "desc": "15-20 word description in Greek"}},
    {{"title": "service name", "desc": "15-20 word description in Greek"}},
    {{"title": "service name", "desc": "15-20 word description in Greek"}}
  ],
  "theme_color": "hex color that fits the business (e.g. #C9A96E for wood, #2A6F4D for nature, #B8312F for restaurants)",
  "meta_description": "SEO description 140-160 chars in Greek"
}}"""

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.7,
            "responseMimeType": "application/json"
        }
    }

    try:
        r = requests.post(url, json=payload, timeout=60)
        r.raise_for_status()
        text = r.json()['candidates'][0]['content']['parts'][0]['text']
        return json.loads(text)
    except Exception as e:
        print(f"⚠️ Gemini error: {e} — Χρησιμοποιώ fallback content.")
        return {
            "hero_title": business['business_name'],
            "hero_accent": business['business_type'],
            "hero_subtitle": business.get('description', f"Επαγγελματίες στην περιοχή {business.get('city', 'Χανιά')}"),
            "about_title": "Σχετικά με εμάς",
            "about_p1": business.get('description', "Η επιχείρησή μας προσφέρει υψηλής ποιότητας υπηρεσίες."),
            "about_p2": "Επικοινωνήστε μαζί μας σήμερα για περισσότερες πληροφορίες.",
            "services": [
                {"title": "Υπηρεσία 1", "desc": "Ποιοτική εξυπηρέτηση από επαγγελματίες"},
                {"title": "Υπηρεσία 2", "desc": "Άμεση εξυπηρέτηση με συνέπεια"},
                {"title": "Υπηρεσία 3", "desc": "Προσιτές τιμές σε όλη την γκάμα"},
                {"title": "Υπηρεσία 4", "desc": "Εμπειρία στον χώρο μας"}
            ],
            "theme_color": "#C9A96E",
            "meta_description": f"{business['business_name']} - {business['business_type']}"
        }


def build_html(data: dict) -> str:
    """Παράγει το HTML με 3D animations."""
    services_html = '\n'.join([
        f'''<div class="service-item reveal">
              <div class="service-num">0{i+1}</div>
              <h3>{s["title"]}</h3>
              <p>{s["desc"]}</p>
            </div>'''
        for i, s in enumerate(data['services'])
    ])

    phone_nav = f'<a href="tel:{data["phone"]}" class="nav-cta">{data["phone"]}</a>' if data.get('phone') else ''
    phone_contact = f'<div class="contact-detail"><strong>Τηλέφωνο</strong><a href="tel:{data["phone"]}">{data["phone"]}</a></div>' if data.get('phone') else ''
    email_contact = f'<div class="contact-detail"><strong>Email</strong><a href="mailto:{data["email"]}">{data["email"]}</a></div>' if data.get('email') else ''
    address_contact = f'<div class="contact-detail"><strong>Διεύθυνση</strong><span>{data["address"]}</span></div>' if data.get('address') else ''

    return f'''<!DOCTYPE html>
<html lang="el">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{data['business_name']} | {data['business_type']}</title>
<meta name="description" content="{data['meta_description']}">
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700;900&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
:root{{--accent:{data['theme_color']};--dark:#0A0705;--dark2:#110E0A;--text:#F5EDD8;--muted:#9A8B78}}
html{{scroll-behavior:smooth}}
body{{background:var(--dark);color:var(--text);font-family:'Inter',sans-serif;overflow-x:hidden}}
#canvas-hero{{position:fixed;top:0;left:0;width:100%;height:100%;z-index:0;pointer-events:none}}
nav{{position:fixed;top:0;width:100%;z-index:100;padding:18px 60px;display:flex;justify-content:space-between;align-items:center;transition:all .4s}}
nav.scrolled{{background:rgba(10,7,5,.93);backdrop-filter:blur(14px);border-bottom:1px solid rgba(201,169,110,.12)}}
.nav-logo{{font-family:'Playfair Display',serif;font-size:1.3rem;font-weight:700;color:var(--accent);text-decoration:none;letter-spacing:.04em}}
.nav-links{{display:flex;gap:32px;list-style:none}}
.nav-links a{{color:var(--muted);text-decoration:none;font-size:.82rem;letter-spacing:.1em;text-transform:uppercase;transition:color .3s}}
.nav-links a:hover{{color:var(--accent)}}
.nav-cta{{background:var(--accent);color:var(--dark);padding:10px 22px;font-size:.8rem;letter-spacing:.1em;text-transform:uppercase;font-weight:600;text-decoration:none;border-radius:2px;transition:all .3s}}
.nav-cta:hover{{transform:translateY(-2px)}}
#hero{{position:relative;height:100vh;display:flex;align-items:center;z-index:1}}
.hero-content{{padding:0 10vw;max-width:680px}}
.hero-badge{{display:inline-flex;align-items:center;gap:8px;background:rgba(201,169,110,.1);border:1px solid var(--accent);border-radius:100px;padding:6px 16px;margin-bottom:28px;opacity:.8}}
.hero-badge::before{{content:'';width:6px;height:6px;border-radius:50%;background:var(--accent);animation:pulse 2s infinite}}
@keyframes pulse{{0%,100%{{opacity:1;transform:scale(1)}}50%{{opacity:.5;transform:scale(.8)}}}}
.hero-badge span{{font-size:.72rem;color:var(--accent);letter-spacing:.14em;text-transform:uppercase}}
.hero-title{{font-family:'Playfair Display',serif;font-size:clamp(2.6rem,6vw,5rem);line-height:1.06;font-weight:900;margin-bottom:22px}}
.hero-title em{{font-style:normal;color:var(--accent);display:block}}
.hero-sub{{font-size:1.05rem;color:var(--muted);line-height:1.75;max-width:480px;margin-bottom:42px;font-weight:300}}
.hero-btns{{display:flex;gap:14px;flex-wrap:wrap}}
.btn-primary{{background:var(--accent);color:var(--dark);padding:15px 34px;font-size:.85rem;letter-spacing:.1em;text-transform:uppercase;font-weight:600;text-decoration:none;border-radius:2px;transition:all .3s;display:inline-block}}
.btn-primary:hover{{transform:translateY(-2px);box-shadow:0 10px 36px rgba(201,169,110,.3)}}
.btn-ghost{{border:1px solid var(--accent);color:var(--accent);padding:15px 34px;font-size:.85rem;letter-spacing:.1em;text-transform:uppercase;text-decoration:none;border-radius:2px;transition:all .3s;display:inline-block}}
.btn-ghost:hover{{background:rgba(201,169,110,.07)}}
section{{position:relative;z-index:2}}
.section-label{{font-size:.68rem;letter-spacing:.3em;text-transform:uppercase;color:var(--accent);margin-bottom:14px;display:block}}
.section-title{{font-family:'Playfair Display',serif;font-size:clamp(1.9rem,3.8vw,3rem);line-height:1.15;font-weight:700}}
#about{{background:var(--dark2);padding:110px 10vw;display:grid;grid-template-columns:1fr 1fr;gap:72px;align-items:center}}
.about-left p{{color:var(--muted);line-height:1.8;font-size:.97rem;margin-bottom:16px;font-weight:300}}
.about-visual{{height:440px;position:relative}}
#about-canvas{{width:100%;height:100%}}
#services{{padding:110px 10vw;background:var(--dark)}}
.services-grid{{display:grid;grid-template-columns:repeat(2,1fr);gap:28px;margin-top:56px}}
.service-item{{padding:36px;border:1px solid rgba(201,169,110,.1);transition:all .4s;border-radius:4px;position:relative;overflow:hidden}}
.service-item::after{{content:'';position:absolute;left:0;bottom:0;height:2px;width:0;background:var(--accent);transition:width .4s}}
.service-item:hover{{background:rgba(201,169,110,.04)}}
.service-item:hover::after{{width:100%}}
.service-item h3{{font-family:'Playfair Display',serif;font-size:1.25rem;margin-bottom:10px}}
.service-item p{{color:var(--muted);font-size:.88rem;line-height:1.7;font-weight:300}}
.service-num{{font-size:2.6rem;font-family:'Playfair Display',serif;color:rgba(201,169,110,.1);font-weight:900;line-height:1;margin-bottom:14px}}
#contact{{background:var(--dark2);padding:110px 10vw;text-align:center}}
.contact-details{{display:flex;justify-content:center;gap:48px;margin-top:48px;flex-wrap:wrap}}
.contact-detail{{text-align:center}}
.contact-detail strong{{display:block;font-size:.76rem;letter-spacing:.1em;text-transform:uppercase;color:var(--accent);margin-bottom:6px}}
.contact-detail span,.contact-detail a{{color:var(--muted);font-size:1rem;text-decoration:none}}
footer{{background:var(--dark);padding:36px 10vw;text-align:center;border-top:1px solid rgba(201,169,110,.1);color:var(--muted);font-size:.8rem}}
.reveal{{opacity:0;transform:translateY(36px);transition:opacity .75s ease,transform .75s ease}}
.reveal.visible{{opacity:1;transform:translateY(0)}}
@media(max-width:900px){{nav{{padding:14px 22px}}.nav-links{{display:none}}#about{{grid-template-columns:1fr}}.services-grid{{grid-template-columns:1fr}}.contact-details{{gap:28px}}}}
</style>
</head>
<body>
<canvas id="canvas-hero"></canvas>
<nav id="nav">
  <a href="#" class="nav-logo">{data['business_name']}</a>
  <ul class="nav-links">
    <li><a href="#about">Σχετικά</a></li>
    <li><a href="#services">Υπηρεσίες</a></li>
    <li><a href="#contact">Επικοινωνία</a></li>
  </ul>
  {phone_nav}
</nav>
<section id="hero">
  <div class="hero-content reveal">
    <div class="hero-badge"><span>{data.get('city', 'Χανιά')} · {data['business_type']}</span></div>
    <h1 class="hero-title">{data['hero_title']}<em>{data['hero_accent']}</em></h1>
    <p class="hero-sub">{data['hero_subtitle']}</p>
    <div class="hero-btns">
      <a href="#contact" class="btn-primary">Επικοινωνία</a>
      <a href="#services" class="btn-ghost">Υπηρεσίες</a>
    </div>
  </div>
</section>
<section id="about">
  <div class="about-left reveal">
    <span class="section-label">Σχετικά</span>
    <h2 class="section-title">{data['about_title']}</h2>
    <p style="margin-top:20px">{data['about_p1']}</p>
    <p>{data['about_p2']}</p>
  </div>
  <div class="about-visual reveal"><canvas id="about-canvas"></canvas></div>
</section>
<section id="services">
  <div class="reveal" style="text-align:center;margin-bottom:24px">
    <span class="section-label">Υπηρεσίες</span>
    <h2 class="section-title">Τι Προσφέρουμε</h2>
  </div>
  <div class="services-grid">{services_html}</div>
</section>
<section id="contact">
  <div class="reveal">
    <span class="section-label">Επικοινωνία</span>
    <h2 class="section-title">Ελάτε σε Επαφή</h2>
    <div class="contact-details">
      {phone_contact}
      {email_contact}
      {address_contact}
      <div class="contact-detail"><strong>Ωράριο</strong><span>{data.get('hours', 'Δευ-Σαβ 9:00-21:00')}</span></div>
    </div>
  </div>
</section>
<footer>© 2025 {data['business_name']} · {data.get('address', '')}</footer>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
window.addEventListener('scroll',()=>document.getElementById('nav').classList.toggle('scrolled',scrollY>60));
const tc=parseInt('{data['theme_color']}'.replace('#',''),16);
(function(){{
  const c=document.getElementById('canvas-hero');
  const r=new THREE.WebGLRenderer({{canvas:c,antialias:true,alpha:true}});
  r.setPixelRatio(Math.min(devicePixelRatio,2));r.setSize(innerWidth,innerHeight);r.setClearColor(0,0);
  const s=new THREE.Scene(),cam=new THREE.PerspectiveCamera(60,innerWidth/innerHeight,.1,100);cam.position.z=10;
  s.add(new THREE.AmbientLight(0x554433,.6));
  const dl=new THREE.DirectionalLight(tc,1.3);dl.position.set(5,8,5);s.add(dl);
  const objs=[];
  for(let i=0;i<14;i++){{
    const g=new THREE.IcosahedronGeometry(.4+Math.random()*.5,0);
    const m=new THREE.MeshStandardMaterial({{color:tc,roughness:.7,metalness:.1,transparent:true,opacity:.4+Math.random()*.4}});
    const o=new THREE.Mesh(g,m);
    o.position.set((Math.random()-.5)*16,(Math.random()-.5)*10,(Math.random()-.5)*8-2);
    s.add(o);objs.push({{o,sp:.2+Math.random()*.5,ph:Math.random()*Math.PI*2,ry:Math.random()*.01,rx:Math.random()*.01}});
  }}
  const dp=new Float32Array(400*3);for(let i=0;i<400;i++){{dp[i*3]=(Math.random()-.5)*22;dp[i*3+1]=(Math.random()-.5)*14;dp[i*3+2]=(Math.random()-.5)*8-2}}
  const dg=new THREE.BufferGeometry();dg.setAttribute('position',new THREE.BufferAttribute(dp,3));
  s.add(new THREE.Points(dg,new THREE.PointsMaterial({{color:tc,size:.03,transparent:true,opacity:.5}})));
  let mx=0,my=0;
  document.addEventListener('mousemove',e=>{{mx=(e.clientX/innerWidth-.5)*2;my=-(e.clientY/innerHeight-.5)*2}});
  let t=0;
  (function a(){{requestAnimationFrame(a);t+=.01;
    objs.forEach(p=>{{p.o.position.y+=Math.sin(t*p.sp+p.ph)*.005;p.o.rotation.x+=p.rx;p.o.rotation.y+=p.ry}});
    cam.position.x+=(mx*.5-cam.position.x)*.02;cam.position.y+=(my*.3-cam.position.y)*.02;
    r.render(s,cam)}})();
  window.addEventListener('resize',()=>{{cam.aspect=innerWidth/innerHeight;cam.updateProjectionMatrix();r.setSize(innerWidth,innerHeight)}});
}})();
(function(){{
  const c=document.getElementById('about-canvas');if(!c)return;
  const r=new THREE.WebGLRenderer({{canvas:c,antialias:true,alpha:true}});
  r.setPixelRatio(Math.min(devicePixelRatio,2));r.setClearColor(0,0);
  const upd=()=>{{r.setSize(c.parentElement.offsetWidth,c.parentElement.offsetHeight);cam.aspect=c.parentElement.offsetWidth/c.parentElement.offsetHeight;cam.updateProjectionMatrix()}};
  const s=new THREE.Scene(),cam=new THREE.PerspectiveCamera(50,1,.1,100);cam.position.z=6;upd();
  s.add(new THREE.AmbientLight(0x554433,.7));
  const dl=new THREE.DirectionalLight(tc,1.4);dl.position.set(4,6,4);s.add(dl);
  const g=new THREE.Group();
  const sh=new THREE.Mesh(new THREE.TorusKnotGeometry(1.2,.4,100,16),new THREE.MeshStandardMaterial({{color:tc,roughness:.4,metalness:.3}}));
  g.add(sh);s.add(g);
  let t=0;(function a(){{requestAnimationFrame(a);t+=.01;g.rotation.x=t*.3;g.rotation.y=t*.4;r.render(s,cam)}})();
  window.addEventListener('resize',upd);
}})();
const o=new IntersectionObserver(es=>es.forEach(e=>{{if(e.isIntersecting)e.target.classList.add('visible')}}),{{threshold:.1}});
document.querySelectorAll('.reveal').forEach(el=>o.observe(el));
</script>
</body>
</html>'''


def github_request(method: str, url: str, **kwargs):
    """GitHub API call wrapper."""
    headers = kwargs.pop('headers', {})
    headers.update({
        'Authorization': f'Bearer {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28'
    })
    return requests.request(method, url, headers=headers, timeout=30, **kwargs)


def create_repo_and_deploy(repo_name: str, html: str, business_name: str) -> str:
    """Δημιουργεί repo, ανεβάζει το HTML, ενεργοποιεί Pages."""

    # 1. Create repo
    r = github_request('POST', 'https://api.github.com/user/repos', json={
        'name': repo_name,
        'description': f'Auto-generated website for {business_name}',
        'homepage': f'https://{GITHUB_USERNAME}.github.io/{repo_name}',
        'private': False,
        'auto_init': True
    })

    if r.status_code == 422:
        print(f"  ⚠️ Repo {repo_name} υπάρχει ήδη — προσπερνώ.")
        return f'https://{GITHUB_USERNAME}.github.io/{repo_name}/'
    elif r.status_code != 201:
        raise Exception(f"Failed to create repo: {r.status_code} {r.text}")

    print(f"  ✓ Δημιουργήθηκε το repo")
    time.sleep(2)

    # 2. Push HTML
    content_b64 = base64.b64encode(html.encode('utf-8')).decode('utf-8')
    r = github_request('PUT',
        f'https://api.github.com/repos/{GITHUB_USERNAME}/{repo_name}/contents/index.html',
        json={
            'message': f'Initial website for {business_name}',
            'content': content_b64
        })
    if r.status_code not in (200, 201):
        raise Exception(f"Failed to push HTML: {r.status_code} {r.text}")
    print(f"  ✓ Ανέβηκε το HTML")

    # 3. Enable Pages
    r = github_request('POST',
        f'https://api.github.com/repos/{GITHUB_USERNAME}/{repo_name}/pages',
        json={'source': {'branch': 'main', 'path': '/'}})
    if r.status_code in (201, 204, 409):  # 409 = already enabled
        print(f"  ✓ Ενεργοποιήθηκε το GitHub Pages")
    else:
        print(f"  ⚠️ Pages warning: {r.status_code} {r.text[:100]}")

    return f'https://{GITHUB_USERNAME}.github.io/{repo_name}/'


# ===== MAIN =====
def main():
    # Φόρτωσε leads
    if not os.path.exists(LEADS_FILE):
        print(f"📝 Δεν υπάρχει {LEADS_FILE}. Φτιάξε το αρχείο και πρόσθεσε leads.")
        return

    with open(LEADS_FILE, 'r', encoding='utf-8') as f:
        leads = json.load(f)

    # Φόρτωσε ήδη επεξεργασμένα leads
    processed = {}
    if os.path.exists(PROCESSED_FILE):
        with open(PROCESSED_FILE, 'r', encoding='utf-8') as f:
            processed = json.load(f)

    new_results = []

    for lead in leads:
        bname = lead['business_name']
        if bname in processed:
            print(f"⏭️  Παραλείπω (έχει ήδη γίνει): {bname}")
            continue

        print(f"\n🏗️  Επεξεργάζομαι: {bname}")
        try:
            # Παράγω content με AI
            content = call_gemini(lead)
            data = {**lead, **content}

            # Φτιάχνω HTML
            html = build_html(data)

            # Φτιάχνω repo name
            slug = slugify(bname)
            repo_name = f"{slug}-{int(time.time()) % 1000000}"

            # Deploy
            url = create_repo_and_deploy(repo_name, html, bname)

            processed[bname] = {
                'url': url,
                'repo': f'https://github.com/{GITHUB_USERNAME}/{repo_name}',
                'created': datetime.utcnow().isoformat() + 'Z'
            }
            new_results.append((bname, url))
            print(f"✅ Επιτυχία: {url}")

        except Exception as e:
            print(f"❌ Σφάλμα στο {bname}: {e}")
            processed[bname] = {'error': str(e), 'created': datetime.utcnow().isoformat() + 'Z'}

    # Αποθήκευσε processed
    with open(PROCESSED_FILE, 'w', encoding='utf-8') as f:
        json.dump(processed, f, ensure_ascii=False, indent=2)

    # Φτιάξε results.md
    with open(RESULTS_FILE, 'w', encoding='utf-8') as f:
        f.write('# 🌐 Generated Websites\n\n')
        f.write(f'_Last update: {datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")}_\n\n')
        f.write('| Επιχείρηση | Live URL | Status |\n')
        f.write('|------------|----------|--------|\n')
        for bname, info in processed.items():
            if 'url' in info:
                f.write(f'| {bname} | [Άνοιξε →]({info["url"]}) | ✅ |\n')
            else:
                f.write(f'| {bname} | — | ❌ {info.get("error", "")[:60]} |\n')

    print(f"\n🎉 Τελείωσα! {len(new_results)} νέα websites φτιάχτηκαν.")


if __name__ == '__main__':
    main()
