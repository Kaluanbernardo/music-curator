#!/usr/bin/env python3
"""Indexa todas as edições (*.html exceto index) em albums.json para o hub. Rodar após cada nova edição."""
import re,json,glob,html,os
os.chdir(os.path.dirname(os.path.abspath(__file__))+'/..')
def T(s): return html.unescape(re.sub(r'<[^>]+>','',s)).strip()
eds=[];albums=[]
for f in sorted(glob.glob('*.html')):
  if f=='index.html': continue
  s=open(f,encoding='utf-8').read()
  m=re.search(r'<h1>(.*?)</h1>',s,re.S); title=T(m.group(1)) if m else f
  kind='semanal' if f.startswith('semana') else 'especial'
  d=re.search(r'(\d{4})-(\d\d)-(\d\d)',f); date='-'.join(d.groups()) if d else ('2026-10-31' if 'outubro' in f else '2026-12-31')
  cards=re.findall(r'<article class="card" id="([^"]+)">(.*?)</article>',s,re.S)
  eds.append(dict(file=f,title=title,kind=kind,date=date,count=len(cards)))
  for aid,c in cards:
    g=lambda p:(re.search(p,c,re.S) or [None,''])[1]
    badges=re.findall(r'class="b (\w+)">([^<]*)',c)
    bt=[b[1] for b in badges]
    yr=re.search(r'class="date">[^<]*?(\d{4})',c)
    albums.append(dict(ed=f,id=aid,album=T(g(r'<h2>(.*?)</h2>')),artist=T(re.sub(r'<span class="date">.*?</span>','',g(r'<p class="artist">(.*?)</p>'))),
      date=T(g(r'<span class="date">(.*?)</span>')).lstrip('· '),year=yr.group(1) if yr else date[:4],
      cover=g(r'<img src="([^"]+)"'),nac=any('Nacional' in b for b in bt),
      known=any(b[0]=='acc' for b in badges),hist=any('histórico' in b for b in bt),
      genres=[T(x) for x in re.findall(r'<span class="g">(.*?)</span>',c)],
      reviews='class="crit"' in c or 'O que a crítica diz' in c,
      text=T(c)[:1500]))
eds.sort(key=lambda e:e['date'],reverse=True)
json.dump(dict(editions=eds,albums=albums),open('albums.json','w',encoding='utf-8'),ensure_ascii=False)
print(len(eds),'edições',len(albums),'discos')
