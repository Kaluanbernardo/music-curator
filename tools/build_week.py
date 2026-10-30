import json,html,re,os
DATE=os.environ.get("ED_DATE","2026-10-23")
ed=json.load(open(f"editions/{DATE}.json"))
e=html.escape
def fmt(d):
    y,m,dd=d.split("-"); return f"{int(dd)} out {y}"
NOCRIT=re.compile(r"(ainda )?(sem|nenhuma|não há) (cr[ií]ticas?|resenhas?)[^.;]*[.;]?\s*",re.I)
def sobre(a):
    # Um texto corrido: fatos do disco/artista + opinião da crítica só se houver críticas reais.
    if a.get("texto"): t=a["texto"]
    else:
        parts=[a.get("descricao","")]
        if a.get("criticas"): parts.append(a.get("critica",""))
        t=" ".join(p.strip() for p in parts if p and p.strip())
    return NOCRIT.sub("",t).strip()
cards=[]
for a in ed["albums"]:
    n=a["n"]
    nat='<span class="b nac">🇧🇷 Nacional</span>' if a["is_brazilian"] else '<span class="b int">🌍 Internacional</span>'
    bk={"acompanha":'<span class="b acc">Você acompanha</span>',"historico":'<span class="b acc">Do seu histórico</span>'}.get(a["bucket"],'<span class="b desc">Descoberta</span>')
    src=" · ".join(f'<a href="{e(s["url"])}" target="_blank" rel="noopener">{e(s["name"])}</a>' for s in a["sources"])
    if a.get("criticas"):
        crit='<ul class="crit">'+"".join(f'<li><a href="{e(c["url"])}" target="_blank" rel="noopener">{e(c["veiculo"])}</a>'+(f' <span class="nota">{e(c["nota"])}</span>' if c.get("nota") else '')+'</li>' for c in a["criticas"][:3])+'</ul>'
    else:
        crit=''
    news=''
    if a.get("noticias"):
        news='<p class="src">Notícias: '+" · ".join(f'<a href="{e(x["url"])}" target="_blank" rel="noopener">{e(x["veiculo"])}</a>' for x in a["noticias"])+'</p>'
    texto=sobre(a)
    gen='<div class="genres">'+"".join(f'<span class="g">{e(g)}</span>' for g in a.get("generos",[]))+'</div>' if a.get("generos") else ""
    img=f'<img src="{e(a["cover_url"])}" alt="Capa de {e(a["album"])}" loading="lazy" width="640" height="640">' if a.get("cover_url") else f'<div class="nocover">{e(a["album"])}</div>'
    spot=f'<a class="spot" href="{e(a["spotify_url"])}" target="_blank" rel="noopener">▶ Ouvir no Spotify</a>' if a.get("spotify_url") else ""
    cards.append(f'''<article class="card" id="a{n}">
 <div class="top">{img}<span class="num">{n}</span></div>
 <div class="body">
  <div class="badges">{nat}{bk}</div>
  {gen}
  <h2>{e(a["album"])}</h2>
  <p class="artist">{e(a["artist"])} <span class="date">· {fmt(a["release_date"])}</span></p>
  {('<h3>Sobre o disco</h3><p>'+e(texto)+'</p>') if texto else ''}
  <h3>Parece com</h3><p>{e(a["parece_com"])}</p>
  <h3>Por que ouvir</h3><p>{e(a["por_que_ouvir"])}</p>
  {('<h3>Críticas</h3>'+crit) if crit else ''}{news}
  <p class="src">Fontes: {src}</p>
  {spot}
 </div>
</article>''')
c=ed["counts"]
page=f'''<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{e(ed.get("titulo","Discos da semana · 23 out 2026"))} · Music Curator</title>
<meta name="theme-color" content="#14121a">
<style>
:root{{--bg:#14121a;--card:#1e1b27;--fg:#f2eff7;--mut:#a9a3b8;--acc:#1ed760;--line:#2e2a3a}}
*{{box-sizing:border-box}}html{{-webkit-text-size-adjust:100%}}
body{{margin:0;background:var(--bg);color:var(--fg);font:16px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;padding:env(safe-area-inset-top) 0 40px}}
header{{padding:28px 18px 8px;max-width:760px;margin:0 auto}}
header h1{{font-size:1.7rem;line-height:1.2;margin:0 0 6px;letter-spacing:-.02em}}
header p{{color:var(--mut);margin:4px 0}}
.note{{background:#2a2438;border:1px solid #3d3552;border-radius:12px;padding:12px 14px;margin:14px 0 4px;color:var(--fg)}}
.stats{{display:flex;flex-wrap:wrap;gap:8px;margin-top:10px}}
.stats span{{background:var(--card);border:1px solid var(--line);border-radius:999px;padding:4px 10px;font-size:.82rem;color:var(--mut)}}
main{{max-width:760px;margin:0 auto;padding:8px 12px;display:grid;gap:18px}}
@media(min-width:900px){{main{{max-width:1100px;grid-template-columns:1fr 1fr}}header{{max-width:1100px}}}}
.card{{background:var(--card);border:1px solid var(--line);border-radius:18px;overflow:hidden;display:flex;flex-direction:column}}
.top{{position:relative}}.top img{{display:block;width:100%;height:auto;aspect-ratio:1/1;object-fit:cover;background:#000}}
.num{{position:absolute;top:10px;left:10px;background:rgba(0,0,0,.72);color:#fff;font-weight:800;border-radius:10px;padding:2px 10px;font-size:1.1rem}}
.body{{padding:14px 16px 18px}}
.badges{{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:8px}}
.b{{font-size:.74rem;font-weight:700;padding:3px 9px;border-radius:999px;letter-spacing:.01em}}
.nac{{background:#0f3d24;color:#7ef0a8}}.int{{background:#1f2c48;color:#9cc0ff}}
.acc{{background:#3a2a10;color:#ffcf73}}.desc{{background:#3b1834;color:#ff9ad8}}
h2{{font-size:1.3rem;line-height:1.25;margin:2px 0}}
.artist{{margin:0 0 6px;font-weight:600}}.date{{color:var(--mut);font-weight:400}}
h3{{font-size:.78rem;text-transform:uppercase;letter-spacing:.08em;color:var(--mut);margin:14px 0 2px}}
.body p{{margin:0}}.body p.desc{{margin-bottom:8px}}
.genres{{display:flex;gap:6px;flex-wrap:wrap;margin:0 0 8px}}.g{{font-size:.74rem;padding:2px 9px;border-radius:999px;border:1px solid var(--line);color:var(--mut)}}
.nocover{{aspect-ratio:1/1;display:flex;align-items:center;justify-content:center;text-align:center;padding:24px;font-size:1.4rem;font-weight:800;background:linear-gradient(135deg,#2a2438,#14121a);color:var(--mut)}}
.src{{margin-top:12px!important;font-size:.85rem;color:var(--mut)}}.src a{{color:#c9b8ff}}
.spot{{display:block;text-align:center;margin-top:14px;background:var(--acc);color:#04120a;font-weight:800;text-decoration:none;padding:12px;border-radius:12px}}
.vote{{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-top:10px}}
.v{{font:inherit;font-weight:700;border-radius:12px;padding:12px 4px;border:1px solid var(--line);background:#26222f;color:var(--fg);cursor:pointer;min-height:48px}}
.v:active{{transform:scale(.97)}}.up:hover{{border-color:#1ed760}}.mid:hover{{border-color:#ffcf73}}.down:hover{{border-color:#ff6b6b}}
.crit{{list-style:none;padding:0;margin:4px 0 0;display:flex;flex-wrap:wrap;gap:8px}}.crit a{{display:inline-block;background:#26222f;border:1px solid var(--line);border-radius:999px;padding:6px 12px;color:#c9b8ff;text-decoration:none;font-weight:600}}.nota{{color:var(--fg);font-weight:700}}
.pl{{display:block;text-align:center;margin:12px 0 4px;background:var(--acc);color:#04120a;font-weight:800;text-decoration:none;padding:12px;border-radius:12px}}
.codes{{margin-top:8px!important;font-size:.82rem;color:var(--mut);text-align:center}}
code{{background:#0e0c13;border:1px solid var(--line);border-radius:6px;padding:1px 6px;color:var(--fg);user-select:all;-webkit-user-select:all}}
.ok{{display:block;text-align:center;font-size:.85rem;color:#7ef0a8;margin-top:6px;min-height:1.2em}}
#toast{{position:fixed;left:50%;bottom:calc(18px + env(safe-area-inset-bottom));transform:translateX(-50%) translateY(120%);background:#f2eff7;color:#14121a;font-weight:700;padding:10px 16px;border-radius:999px;box-shadow:0 6px 24px rgba(0,0,0,.4);transition:transform .25s;z-index:9;max-width:92vw;text-align:center}}
#toast.show{{transform:translateX(-50%) translateY(0)}}
footer{{max-width:760px;margin:24px auto 0;padding:0 18px;color:var(--mut);font-size:.82rem}}
</style></head><body>
<header>
 <h1>{e(ed.get("titulo","Discos da semana · 23 out 2026"))}</h1>
 <p>Music Curator · edição semanal · {e(ed.get("periodo","lançamentos de 17 a 23 de outubro de 2026"))}</p>
 <a class="pl" href="{e(ed["playlist"]["url"])}" target="_blank" rel="noopener">▶ Ouvir tudo na playlist {e(ed["playlist"]["nome"])}</a>
 <div class="note">{e(ed["ratings_line"])}</div>
 <div class="stats"><span>{c["total"]} discos</span><span>{c["acompanha"]} você acompanha</span><span>{c.get("historico",0)} do seu histórico</span><span>{c["descoberta"]} descobertas</span><span>{c["brasileiros"]} nacionais ({c["pct_brasileiros"]:.0f}%)</span></div>
</header>
<main>
{chr(10).join(cards)}
</main>
<footer>Críticas resumidas e parafraseadas das fontes citadas em cada card. Datas conforme o Spotify (mercado BR).</footer>
</body></html>'''
open(f"editions/{DATE}.html","w").write(page)
print(len(page))
