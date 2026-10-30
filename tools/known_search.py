"""Per-artist Spotify SEARCH fallback (when /artists/{id}/albums is 429-blocked).
Usage: START=YYYY-MM-DD END=YYYY-MM-DD python3 known_search.py -> known-search-<END>.json"""
import sys,json,time,os,urllib.request,urllib.error,urllib.parse
sys.path.insert(0,'/home/box/.spotify'); from sp import tok
S=os.environ['START'];E=os.environ['END']
K=json.load(open('known-artists.json'))['artists']
out=[];seen=set()
for i,a in enumerate(K):
    q=urllib.parse.quote(f'artist:"{a["name"]}" year:{E[:4]}')
    u=f"https://api.spotify.com/v1/search?q={q}&type=album&market=BR&limit=10"
    for t in range(3):
        try: d=json.loads(urllib.request.urlopen(urllib.request.Request(u,headers={"Authorization":"Bearer "+tok()})).read()); break
        except urllib.error.HTTPError as e:
            if e.code==429:
                w=int(e.headers.get('Retry-After') or 30); print('429',w,flush=True)
                if w>120: json.dump(out,open(f'known-search-{E}.json','w'),ensure_ascii=False,indent=1); sys.exit(2)
                time.sleep(w+1)
            else: d=None; break
    else: d=None
    for x in (d or {}).get('albums',{}).get('items',[]) or []:
        if not x: continue
        ids=[y['id'] for y in x['artists']]
        if S<=x['release_date']<=E and (a.get('spotify_artist_id') in ids or a['name'].lower() in [y['name'].lower() for y in x['artists']]) and x['id'] not in seen:
            seen.add(x['id']); out.append(dict(artist=a['name'],aid=a.get('spotify_artist_id'),source=a['source'],title=x['name'],type=x['album_type'],date=x['release_date'],tracks=x['total_tracks'],id=x['id'],img=(x['images'][0]['url'] if x['images'] else None),all_artists=[y['name'] for y in x['artists']]))
    if i%100==0: print(i,len(out),flush=True)
    time.sleep(0.3)
json.dump(out,open(f'known-search-{E}.json','w'),ensure_ascii=False,indent=1); print('done',len(out))
