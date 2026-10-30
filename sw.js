// Service worker do Music Curator. O bloco entre os marcadores é gerado por tools/build_hub.py.
// <hub:gen>
const VERSION='ac65e0b686';
const SHELL=["./", "index.html", "albums.json", "manifest.webmanifest", "icon-192.png", "icon-512.png", "icon-maskable-192.png", "icon-maskable-512.png", "apple-touch-icon.png"];
const PAGES=["semana-2026-10-30.html", "50-do-ano-2026.html", "semana-2026-10-23.html", "outubro-2026.html"];
// </hub:gen>
const CACHE='mc-'+VERSION, COVERS='mc-covers', MAX_COVERS=400;

// instala tudo para uso offline: shell, índice e todas as edições (sem cache HTTP no caminho)
self.addEventListener('install',e=>{
  e.waitUntil(caches.open(CACHE).then(c=>c.addAll(SHELL.concat(PAGES).map(u=>new Request(u,{cache:'reload'})))).then(()=>self.skipWaiting()));
});

self.addEventListener('activate',e=>{
  e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k.startsWith('mc-')&&k!==CACHE&&k!==COVERS).map(k=>caches.delete(k))))
    .then(()=>self.clients.claim()));
});

self.addEventListener('message',e=>{if(e.data==='skipWaiting')self.skipWaiting()});

async function trimCovers(){
  const c=await caches.open(COVERS),ks=await c.keys();
  for(let i=0;i<ks.length-MAX_COVERS;i++)await c.delete(ks[i]);
}

// rede primeiro (com limite de tempo) para páginas e albums.json; cache como reserva offline
async function networkFirst(req){
  const c=await caches.open(CACHE);
  const net=fetch(req).then(res=>{if(res.ok)c.put(req,res.clone());return res});
  try{
    const res=await Promise.race([net,new Promise(ok=>setTimeout(ok,4000,null))]);
    if(res)return res;
    // rede lenta: usa o cache se houver, senão continua esperando a rede
    return (await c.match(req,{ignoreSearch:true}))||await net;
  }catch(err){
    const hit=await c.match(req,{ignoreSearch:true});
    if(hit)return hit;
    if(req.mode==='navigate')return (await c.match('index.html'))||Response.error();
    throw err;
  }
}

// capas (Spotify CDN): cache primeiro, guardadas num cache próprio que sobrevive às versões
async function coverFirst(req){
  const c=await caches.open(COVERS),hit=await c.match(req);
  if(hit)return hit;
  const res=await fetch(req);
  if(res.ok||res.type==='opaque'){c.put(req,res.clone()).then(trimCovers)}
  return res;
}

self.addEventListener('fetch',e=>{
  const r=e.request;if(r.method!=='GET')return;
  const u=new URL(r.url);
  if(u.origin!==location.origin){
    if(u.hostname.endsWith('scdn.co')||u.hostname.endsWith('spotifycdn.com'))e.respondWith(coverFirst(r));
    return;
  }
  e.respondWith(networkFirst(r));
});
