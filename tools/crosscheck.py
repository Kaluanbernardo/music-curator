"""Cross-check weekly release roundups against known-artists.json BY NAME (no Spotify needed).
Usage: python3 crosscheck.py roundup.txt   (one 'Artist: Title [tags]' or 'Artist – Title' per line, pasted from AOTY/Metacritic/Pitchfork/Stereogum/BrooklynVegan/NPR/Popline/G1/RS Brasil)
Prints known-artist hits and flags live/reissue/deluxe titles."""
import json,sys,re,unicodedata
def n(s): return ''.join(c for c in unicodedata.normalize('NFD',s.lower()) if c.isalnum())
K={n(a['name']):a for a in json.load(open('known-artists.json'))['artists']}
BAD=re.compile(r'ao vivo|\blive\b|anniversary|deluxe|remaster|reissue|expanded|edition|edição',re.I)
for line in open(sys.argv[1],encoding='utf-8'):
    m=re.split(r'\s*(?::|–|—| - )\s*',line.strip(),1)
    if len(m)<2: continue
    artists=re.split(r'\s*(?:&|,| and | e | feat\.? | x )\s*',m[0])
    hits=[a for a in artists if n(a) in K]
    flag=' [EXCLUIR: live/reedição]' if BAD.search(m[1]) else ''
    if hits: print('KNOWN',hits,'|',line.strip(),flag)
