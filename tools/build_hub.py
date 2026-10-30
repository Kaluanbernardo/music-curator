#!/usr/bin/env python3
"""Indexa todas as edições em albums.json para o hub (index.html) e atualiza o sw.js.

Rodar após cada nova edição:  python3 tools/build_hub.py

- Edição = qualquer *.html na raiz (exceto index.html) que tenha <article class="card" id="...">.
- Garante nas páginas de edição só um bloco no <head> (manifest, ícones, registro do service
  worker, destaque do card aberto via #id) e o link "← Todas as edições". O conteúdo dos
  discos nunca é alterado.
- Reescreve no sw.js a versão do cache (hash do conteúdo) e a lista de páginas para offline.
"""
import glob, hashlib, html, json, os, re, sys
from datetime import date

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
os.chdir(ROOT)

MESES = {'janeiro': 1, 'fevereiro': 2, 'marco': 3, 'abril': 4, 'maio': 5, 'junho': 6, 'julho': 7,
         'agosto': 8, 'setembro': 9, 'outubro': 10, 'novembro': 11, 'dezembro': 12}
MES_ABR = {k[:3]: v for k, v in MESES.items()}
SHELL = ['./', 'index.html', 'albums.json', 'manifest.webmanifest', 'icon-192.png', 'icon-512.png',
         'icon-maskable-192.png', 'icon-maskable-512.png', 'apple-touch-icon.png']

HEAD_START, HEAD_END = '<!--hub:head-->', '<!--/hub:head-->'
HEAD_BLOCK = (HEAD_START +
    '<link rel="manifest" href="manifest.webmanifest"><link rel="icon" href="icon-192.png">'
    '<link rel="apple-touch-icon" href="apple-touch-icon.png">'
    '<style>.card{scroll-margin-top:12px}.card:target{outline:2px solid var(--acc);outline-offset:2px}</style>'
    "<script>if('serviceWorker' in navigator)navigator.serviceWorker.register('sw.js')</script>"
    + HEAD_END)
OLD_HEAD = '<link rel="manifest" href="manifest.webmanifest"><meta name="theme-color" content="#14121a">'
BACK_LINK = '<a href="index.html" style="color:#a9a3b8;text-decoration:none;font-size:.9rem">← Todas as edições</a>'


def strip_accents(s):
    import unicodedata
    return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')


def text(s):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', s or ''))).strip()


def first(pattern, s, default=''):
    m = re.search(pattern, s, re.S)
    return m.group(1) if m else default


def ensure_hub_bits(path, s):
    """Só acrescenta/atualiza o bloco do <head> e o link de volta; idempotente."""
    new = s
    if HEAD_START in new:
        new = re.sub(re.escape(HEAD_START) + '.*?' + re.escape(HEAD_END), lambda _: HEAD_BLOCK, new, count=1, flags=re.S)
    elif OLD_HEAD in new:
        new = new.replace(OLD_HEAD, HEAD_BLOCK + '<meta name="theme-color" content="#14121a">', 1)
    elif '</head>' in new:
        new = new.replace('</head>', HEAD_BLOCK + '</head>', 1)
    if 'href="index.html"' not in new and '<header>' in new:
        new = new.replace('<header>', '<header>' + BACK_LINK, 1)
    if new != s:
        # releitura logo antes de gravar: se outra tarefa mudou o arquivo no meio, não sobrescreve
        if open(path, encoding='utf-8').read() != s:
            print(f'aviso: {path} mudou durante o build; rode de novo', file=sys.stderr)
            return s
        tmp = path + '.tmp'
        with open(tmp, 'w', encoding='utf-8') as fh:
            fh.write(new)
        os.replace(tmp, path)
        print(f'  {path}: cabeçalho do hub atualizado')
    return new


def edition_meta(f, s):
    title = text(first(r'<h1[^>]*>(.*?)</h1>', s)) or f
    sub = text(first(r'</h1>\s*<p[^>]*>(.*?)</p>', s))
    base = strip_accents(f.lower())
    fy = first(r'(20\d\d)', base) or str(date.today().year)
    if base.startswith('semana'):
        kind, label = 'semanal', 'Semanal'
    elif '-do-ano' in base:
        kind, label = 'anual', 'Especial do ano'
    elif any(m in base for m in MESES):
        kind, label = 'mensal', 'Mensal'
    else:
        kind, label = 'especial', 'Especial'
    # data de referência: data no nome do arquivo > fim do período no subtítulo > fim do mês/ano
    d = None
    m = re.search(r'(20\d\d)-(\d\d)-(\d\d)', base)
    if m:
        d = date(*map(int, m.groups()))
    if not d:
        m = re.search(r'a (\d{1,2})(?:º)? de (\w+)(?: de (20\d\d))?', strip_accents(sub.lower()))
        if m and m.group(2) in MESES:
            try:
                d = date(int(m.group(3) or fy), MESES[m.group(2)], int(m.group(1)))
            except ValueError:
                pass
    if not d:
        mes = next((v for k, v in MESES.items() if k in base), 12)
        nxt = date(int(fy) + (mes == 12), mes % 12 + 1, 1)
        d = date.fromordinal(nxt.toordinal() - 1)
    return dict(file=f, title=title, kind=kind, label=label, date=d.isoformat(), subtitle=sub,
                playlist=html.unescape(first(r'<a class="pl" href="([^"]+)"', s)))


def parse_album(f, ed_date, pos, aid, c):
    badges = re.findall(r'class="b (\w+)"[^>]*>([^<]*)', c)
    bt = [b[1] for b in badges]
    artist_html = first(r'<p class="artist"[^>]*>(.*?)</p>', c)
    rel = text(first(r'<span class="date"[^>]*>(.*?)</span>', artist_html)).lstrip('·').strip()
    m = re.search(r'(\d{1,2})\s+(\w{3})\w*\.?\s+(20\d\d)', strip_accents(rel.lower()))
    rel_iso = ''
    if m and m.group(2) in MES_ABR:
        try:
            rel_iso = date(int(m.group(3)), MES_ABR[m.group(2)], int(m.group(1))).isoformat()
        except ValueError:
            pass
    year = first(r'(20\d\d|19\d\d)', rel) or ed_date[:4]
    body = re.sub(r'<div class="vote".*?</div>', ' ', c, flags=re.S)
    body = re.sub(r'<a class="spot".*?</a>', ' ', body, flags=re.S)
    sections = re.findall(r'<h3[^>]*>(.*?)</h3>\s*<(?:p|ul)[^>]*>(.*?)</(?:p|ul)>', body, re.S)
    summary = next((text(v) for k, v in sections if re.search(r'Sobre|crítica', text(k), re.I)),
                   text(sections[0][1]) if sections else '')
    return dict(
        ed=f, id=aid, pos=pos,
        album=text(first(r'<h2[^>]*>(.*?)</h2>', c)),
        artist=text(re.sub(r'<span class="date".*?</span>', '', artist_html, flags=re.S)),
        date=rel, rel=rel_iso, year=year,
        cover=html.unescape(first(r'<img[^>]*\ssrc="([^"]+)"', c)),
        nac=any(b[0] == 'nac' or 'Nacional' in b[1] for b in badges),
        known=any(b[0] == 'acc' for b in badges),
        hist=any('histórico' in b for b in bt),
        genres=[text(x) for x in re.findall(r'<span class="g"[^>]*>(.*?)</span>', c, re.S)],
        reviews='class="crit"' in c or bool(re.search(r'<h3[^>]*>[^<]*crítica', c, re.I)),
        spotify=html.unescape(first(r'<a class="spot" href="([^"]+)"', c)),
        summary=summary[:280],
        text=' '.join(text(k) + ': ' + text(v) for k, v in sections)[:2000],
    )


def main():
    eds, albums = [], []
    for f in sorted(glob.glob('*.html')):
        if f == 'index.html' or f.endswith('.tmp'):
            continue
        s = open(f, encoding='utf-8').read()
        cards = re.findall(r'<article\b[^>]*\bclass="card"[^>]*\bid="([^"]+)"[^>]*>(.*?)</article>', s, re.S)
        cards += re.findall(r'<article\b[^>]*\bid="([^"]+)"[^>]*\bclass="card"[^>]*>(.*?)</article>', s, re.S)
        if not cards:
            print(f'  ignorado (sem cards): {f}')
            continue
        s = ensure_hub_bits(f, s)
        e = edition_meta(f, s)
        al = [parse_album(f, e['date'], i + 1, aid, c) for i, (aid, c) in enumerate(cards)]
        bad = [a['id'] for a in al if not a['album'] or not a['artist']]
        if bad:
            print(f'  aviso: {f} cards sem título/artista: {bad}', file=sys.stderr)
        e.update(count=len(al), nac=sum(a['nac'] for a in al), known=sum(a['known'] for a in al),
                 covers=[a['cover'] for a in al if a['cover']][:4])
        eds.append(e)
        albums += al
    if not eds:
        sys.exit('nenhuma edição encontrada')
    eds.sort(key=lambda e: (e['date'], e['file']), reverse=True)
    order = {e['file']: i for i, e in enumerate(eds)}
    albums.sort(key=lambda a: (order[a['ed']], a['pos']))

    data = dict(editions=eds, albums=albums)
    payload = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
    json.loads(payload)
    with open('albums.json.tmp', 'w', encoding='utf-8') as fh:
        fh.write(payload)
    os.replace('albums.json.tmp', 'albums.json')

    # sw.js: versão = hash de tudo que vai para o cache; lista de páginas gerada
    pages = [e['file'] for e in eds]
    h = hashlib.sha256()
    for p in ['index.html', 'albums.json', 'manifest.webmanifest'] + pages:
        if os.path.exists(p):
            h.update(open(p, 'rb').read())
    version = h.hexdigest()[:10]
    sw = open('sw.js', encoding='utf-8').read()
    gen = (f"const VERSION='{version}';\n"
           f"const SHELL={json.dumps(SHELL)};\n"
           f"const PAGES={json.dumps(pages)};\n")
    sw2, n = re.subn(r'// <hub:gen>\n.*?// </hub:gen>', lambda _: '// <hub:gen>\n' + gen + '// </hub:gen>', sw, flags=re.S)
    if not n:
        sys.exit('sw.js sem marcadores // <hub:gen> … // </hub:gen>')
    if sw2 != sw:
        open('sw.js', 'w', encoding='utf-8').write(sw2)
    missing = [p for p in SHELL[1:] if not os.path.exists(p)]
    if missing:
        print('  aviso: arquivos do shell ausentes:', missing, file=sys.stderr)
    print(f'{len(eds)} edições, {len(albums)} discos · cache {version}')


if __name__ == '__main__':
    main()
