# Procedimento semanal de curadoria (Music Curator)

## Por que Suede e Panchiko "faltaram" na semana 43 (2026-10-23)
- **Nenhum dos dois lançou disco novo de estúdio na janela.** Suede: o único lançamento foi a reedição de 30 anos de *Coming Up* (vinil zoetrope do National Album Day, 17/10/2026), que é excluída pela regra de "sem reedições". O último álbum de estúdio é *Antidepressants* (2025; edição *Expanded* em 10/07/2026); o 11º disco ainda está sendo composto (NME, 23/10/2026). Panchiko: *Chimera* (3º álbum de estúdio, Nettwerk) foi **anunciado** em 23/10/2026 com o single "One Car Hits Another" (part. Mei Semones) e **sai em 09/04/2027**.
- Mesmo assim, o pipeline tinha buracos reais:
  1. Nenhum dos dois estava em `known-artists.json` (não são seguidos/top no Spotify; não havia id). → adicionados com `source:["manual"]` e `spotify_artist_id:null`.
  2. `/workspace/fol/run.py` nunca chegou na varredura por artista: baixou os 869 artistas (847 seguidos), aí levou um 429 com Retry-After de 84388 s e parou (`fol/log`). `cache.json` tem **0** chamadas `/artists/{id}/albums`. Ou seja, a varredura do Spotify não cobriu ninguém nesta semana.
  3. O fallback (`week43-known-candidates.json`) usou MusicBrainz + listas na web, mas só achou ao vivo/reedições de artistas conhecidos e não fez um cruzamento sistemático por nome com as listas semanais.
  4. A janela estava fixa no código (`'2026-10-17'..'2026-10-23'`). → agora é `WEEK_END` (padrão: hoje) menos `LOOKBACK_DAYS` (padrão: 10).

## Rotina (toda sexta)
1. Rodar `fol/run.py` (`WEEK_END=AAAA-MM-DD LOOKBACK_DAYS=10`). Se ele parar por 429, **não esperar**: seguir pelo passo 2 e marcar a fila de pendências do Spotify.
2. **Cruzamento por nome (obrigatório, mesmo quando o Spotify funcionar):** colar num `roundup.txt` as listas da semana: Pitchfork (new-album-releases), AOTY (releases desta semana), Metacritic (new releases), Stereogum, Brooklyn Vegan, NPR New Music Friday, Shatter the Standards, Official Charts, JamBase; e as brasileiras: Popline (lançamentos da semana), G1/Mauro Ferreira, Rolling Stone Brasil, Monkeybuzz, Scream & Yell, Tenho Mais Discos Que Amigos!. Rodar `python3 crosscheck.py roundup.txt`.
3. Para cada artista citado pelo Kaluan que não está em `known-artists.json`, adicionar com `source:["manual"]`.
4. Filtros: só álbuns/EPs de estúdio novos; excluir ao vivo, reedição, deluxe/expanded, edição de aniversário e coletâneas; excluir o que já está em `history.json`/`heard.json`.
5. Prioridade: (a) artistas conhecidos, (b) histórico, (c) descobertas. Manter **≥30% brasileiros** e mirar em 18–20 discos.
6. Cada card: `texto` (UM texto corrido em pt-BR que mistura fatos do disco, fatos do artista e, **só se houver críticas reais**, a opinião da crítica; nunca inventar opiniões; só dados do JSON ou de fontes confiáveis verificadas), `descricao` (fatos: conceito, produção, participações, contexto), `critica` (resumo pt-BR, vazio se não houver resenhas), `parece_com`, `por_que_ouvir`, `generos` (de AOTY/AllMusic/Pitchfork/selo/imprensa; nunca inventar), até 3 `criticas` reais verificadas (ou vazio), `noticias` para matérias que não são resenhas.
7. Recalcular `counts`, rodar `python3 build_week.py`, copiar `editions/<data>.html` para `music-curator-site/semana-<data>.html`, conferir, commitar e dar push (comando de push documentado; nunca imprimir o token).
8. Spotify (capas, links, playlist) fica para quando o rate limit liberar; o template aceita `cover_url`/`spotify_url` vazios.

## Regra: álbum sem críticas (desde 24/10/2026)
- **Nunca** escrever "ainda sem críticas publicadas" ou aviso parecido, em nenhum campo. Se não há resenhas, o texto fica só com as informações do disco e do artista.
- A seção "Críticas" só aparece quando `criticas` tem itens; notícias aparecem à parte, como "Notícias".
- O card tem uma única seção "Sobre o disco" (campo `texto`). Se `texto` faltar, `build_week.py` junta `descricao` + `critica` (esta só quando há `criticas`) e remove por regex qualquer aviso de "sem críticas/resenhas".


## Fallback quando /v1/artists/{id}/albums dá 429 (2026-10-30)
- Usar crosscheck.py + busca tag:new; depois `START=... END=... python3 known_search.py` (busca por artista, para em 429 >120s). A busca também pode cair em 429 após ~300 artistas; nesse caso seguir com o que houver e avisar.
- build_week.py agora lê ED_DATE (ex.: `ED_DATE=2026-10-30 python3 build_week.py`) e os campos titulo/periodo do JSON.
