/*
 * Coleta do Acervo Digital da CAL/UnB pelo navegador (alternativa ao Python)
 * Hackathon CULTIVA UnB 2026, PPGCont/UnB.
 *
 * Quando usar: quando o Python não consegue acessar o portal (por exemplo, certificado do
 * site vencido) mas o seu navegador abre a página normalmente.
 *
 * Como usar:
 *   1. Abra https://www.acervocal.unb.br/ no Chrome (ou outro navegador).
 *   2. Abra o Console: Cmd+Option+J (Mac) ou Ctrl+Shift+J (Windows).
 *   3. Se o Chrome pedir, digite "allow pasting" e tecle Enter.
 *   4. Cole TODO este arquivo e tecle Enter. Acompanhe o progresso no Console.
 *   5. Ao final, o navegador baixa "acervo_cal_bruto_AAAAMMDD_HHMM.json".
 *   6. No terminal:  python3 extrair_acervo_cal.py --importar acervo_cal_bruto_....json
 *
 * O trecho só lê a API pública do Tainacan, com pausa entre requisições, e não envia nada.
 */
(async () => {
  const ORIGEM = location.origin;
  const API = ORIGEM + '/wp-json/tainacan/v2';
  const PAUSA_MS = 800;
  const registros = [];
  const espera = (ms) => new Promise((r) => setTimeout(r, ms));

  async function get(caminho, params) {
    const qs = new URLSearchParams(params || {}).toString();
    const url = API + caminho + (qs ? '?' + qs : '');
    for (let t = 1; t <= 4; t++) {
      await espera(PAUSA_MS * t);
      try {
        const r = await fetch(url, { credentials: 'omit', headers: { Accept: 'application/json' } });
        let corpo;
        try { corpo = await r.json(); } catch (e) { corpo = { erro: 'resposta não JSON' }; }
        if ([429, 500, 502, 503, 504].includes(r.status) && t < 4) continue;
        const cab = {};
        ['X-WP-Total', 'X-WP-TotalPages', 'Date', 'Content-Type'].forEach((h) => {
          const v = r.headers.get(h);
          if (v !== null) cab[h] = v;
        });
        registros.push({ url, consultado_em: new Date().toISOString(), status: r.status, cabecalhos: cab, corpo });
        return { corpo, cab, status: r.status };
      } catch (e) {
        if (t === 4) {
          registros.push({ url, consultado_em: new Date().toISOString(), status: 599, cabecalhos: {}, corpo: { erro: String(e) } });
          return { corpo: null, cab: {}, status: 599 };
        }
      }
    }
  }
  const lista = (corpo) => (Array.isArray(corpo) ? corpo : (corpo && corpo.items) || []);

  console.log('%cCULTIVA UnB: iniciando coleta em ' + ORIGEM, 'font-weight:bold');

  // 1. Coleções
  const colecoes = [];
  for (let pg = 1; ; pg++) {
    const { corpo, cab } = await get('/collections', { perpage: 100, paged: pg });
    const l = lista(corpo);
    if (!l.length) break;
    colecoes.push(...l);
    if (pg >= parseInt(cab['X-WP-TotalPages'] || '1', 10)) break;
  }
  console.log(colecoes.length + ' coleções encontradas');

  // 2. Total do repositório
  await get('/items', { perpage: 1, paged: 1 });

  // 3. Itens de cada coleção
  for (const c of colecoes) {
    await get('/collection/' + c.id + '/metadata', { perpage: 200 });
    let acumulado = 0, semMetadados = null;
    for (let pg = 1; ; pg++) {
      const { corpo, cab, status } = await get('/collection/' + c.id + '/items',
        { perpage: 96, paged: pg, orderby: 'id', order: 'asc' });
      if (status >= 400) { console.warn('Coleção ' + c.id + ': HTTP ' + status); break; }
      const l = lista(corpo);
      if (!l.length) break;
      if (semMetadados === null) semMetadados = !l.some((i) => i.metadata && Object.keys(i.metadata).length);
      if (semMetadados) for (const i of l) await get('/item/' + i.id + '/metadata');
      acumulado += l.length;
      const tp = parseInt(cab['X-WP-TotalPages'] || '1', 10);
      console.log(c.name + ': página ' + pg + '/' + tp + ' (' + acumulado + ' itens)');
      if (pg >= tp) break;
    }
  }

  // 4. Download do pacote
  const agora = new Date();
  const p = (n) => String(n).padStart(2, '0');
  const nome = 'acervo_cal_bruto_' + agora.getFullYear() + p(agora.getMonth() + 1) + p(agora.getDate()) +
    '_' + p(agora.getHours()) + p(agora.getMinutes()) + '.json';
  const pacote = { origem: ORIGEM, gerado_em: agora.toISOString(), ferramenta: 'coletar_no_navegador.js v1.0.0',
    navegador: navigator.userAgent, registros };
  const blob = new Blob([JSON.stringify(pacote)], { type: 'application/json' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = nome;
  document.body.appendChild(a);
  a.click();
  a.remove();
  console.log('%cConcluído: ' + registros.length + ' respostas salvas em ' + nome, 'font-weight:bold;color:green');
})();
