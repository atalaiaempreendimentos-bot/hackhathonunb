"""
Hackathon CULTIVA UnB 2026: busca do Acervo CAL/UnB (coleção 1565) com metadados e fotos.

Percorre as páginas da API Tainacan
  https://www.acervocal.unb.br/wp-json/tainacan/v2/collection/1565/items/?perpage=96&order=ASC&orderby=title&paged=1
  ...
  https://www.acervocal.unb.br/wp-json/tainacan/v2/collection/1565/items/?perpage=96&order=ASC&orderby=title&paged=16
e gera, na pasta "acervo_1565" ao lado deste arquivo:
  metadados_acervo_1565.csv        uma linha por obra, com TODOS os metadados e o nome do arquivo da foto
  metadados_acervo_1565_excel.csv  o mesmo, separado por ";" (abre direto no Excel em português)
  galeria_acervo_1565.html         abre no navegador: cada foto (exibida a partir do portal) ao lado
                                   de todos os seus metadados, com busca
  imagens/                         somente com autorização da CAL registrada (ver AUTORIZACAO_CAL)
  paginas_json/                    respostas originais da API (rastreabilidade)
  log_busca.txt                    data da consulta, páginas, totais e falhas

Como rodar no VS Code:
  - Com a extensão Python instalada: abra este arquivo e clique no triângulo "Run Python File".
  - Sem a extensão: Terminal > New Terminal e digite  python3 baixar_acervo_1565.py
    (na pasta onde este arquivo está).

Só usa a biblioteca padrão do Python 3.8+. Pode ser interrompido e rodado de novo:
páginas e fotos já baixadas são reaproveitadas.
"""
import csv
import datetime as dt
import html
import json
import os
import re
import ssl
import sys
import time
import unicodedata
import urllib.request

# ----------------------------------------------------------------------------------
# Configuração
# ----------------------------------------------------------------------------------
COLECAO = 1565
PRIMEIRA_PAGINA = 1
ULTIMA_PAGINA = 16          # o script também lê o total informado pela API e para quando acabar
POR_PAGINA = 96
# DIREITOS DAS IMAGENS: o portal informa, no campo "Condições de reprodução", que as fotografias
# do acervo "não podem ser baixadas e/ou reproduzidas" (Lei nº 9.610/1998), e as Regras do Hackathon
# exigem respeitar direitos autorais e restrições de uso (item 17.11). Por isso o script NÃO baixa
# as fotos: cada obra fica ligada à sua foto pelos links (url_foto_original, url_foto_1024px) e pela
# galeria. Se a equipe obtiver autorização por escrito da CAL/UnB, descreva-a abaixo (ex.: "e-mail da
# CAL de 24/11/2026 à Profa. Fátima") e mude BAIXAR_FOTOS para True; a autorização fica no log.
BAIXAR_FOTOS = False
AUTORIZACAO_CAL = ""
TAMANHO_FOTO = "grande"     # "grande" = versão de até 1024 px; "original" = arquivo integral
PAUSA_PAGINAS = 1.0         # segundos entre páginas (evita sobrecarregar o portal)
PAUSA_FOTOS = 0.5           # segundos entre fotos

URL_PAGINA = ("https://www.acervocal.unb.br/wp-json/tainacan/v2/collection/{col}/items/"
              "?perpage={pp}&order=ASC&orderby={ordem}&paged={pg}")

# O certificado do portal estava vencido em 23/11/2026. Para dados públicos e consulta
# somente de leitura, a equipe decidiu não verificar o certificado. Registre isso nas
# limitações do trabalho. Para voltar a verificar, troque para True.
VERIFICAR_CERTIFICADO = False

AQUI = os.path.dirname(os.path.abspath(__file__))
SAIDA = os.path.join(AQUI, "acervo_{}".format(COLECAO))
PASTA_JSON = os.path.join(SAIDA, "paginas_json")
PASTA_FOTOS = os.path.join(SAIDA, "imagens")
AGENTE = "CULTIVA-UnB-2026 (pesquisa academica PPGCont/UnB)"


# ----------------------------------------------------------------------------------
# Funções auxiliares
# ----------------------------------------------------------------------------------
def contexto_ssl():
    ctx = ssl.create_default_context()
    if not VERIFICAR_CERTIFICADO:
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
    return ctx


CTX = contexto_ssl()


def baixar(url, tentativas=4):
    """Retorna (conteúdo em bytes, cabeçalhos). Tenta de novo em caso de falha temporária."""
    espera = 2
    for t in range(1, tentativas + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": AGENTE})
            with urllib.request.urlopen(req, timeout=90, context=CTX) as r:
                return r.read(), dict(r.headers)
        except Exception as e:
            if t == tentativas:
                raise
            print("    falha ({}), nova tentativa em {} s".format(e, espera))
            time.sleep(espera)
            espera *= 2


def texto_limpo(v):
    if v is None:
        return ""
    t = html.unescape(str(v))
    t = re.sub(r"<[^>]+>", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def valor(m):
    """Texto legível de um metadado do Tainacan."""
    if not isinstance(m, dict):
        return texto_limpo(m)
    if m.get("value_as_string") not in (None, ""):
        return texto_limpo(m["value_as_string"])
    v = m.get("value")
    if isinstance(v, list):
        return " | ".join(texto_limpo(x.get("name") if isinstance(x, dict) else x) for x in v if x)
    if isinstance(v, dict):
        return texto_limpo(v.get("name") or v.get("title") or "")
    return texto_limpo(v)


def fotos_do_item(item):
    """Lê o document_as_html do Tainacan: href = foto original; src = versão de até 1024 px."""
    doc = item.get("document_as_html") or ""
    original = grande = ""
    m = re.search(r"<a[^>]+href=['\"]([^'\"]+)['\"]", doc)
    if m and re.search(r"\.(jpe?g|png|gif|webp|tiff?)$", m.group(1).lower().split("?")[0]):
        original = html.unescape(m.group(1))
    m = re.search(r"<img[^>]+src=['\"]([^'\"]+)['\"]", doc)
    if m:
        grande = html.unescape(m.group(1))
    return original or grande, grande or original


def apelido(txt, limite=50):
    t = unicodedata.normalize("NFKD", txt or "")
    t = "".join(c for c in t if not unicodedata.combining(c)).lower()
    t = re.sub(r"[^a-z0-9]+", "-", t).strip("-")
    return (t[:limite].strip("-")) or "sem-titulo"


def grava_csv(caminho, linhas, colunas, sep):
    with open(caminho, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=colunas, delimiter=sep, extrasaction="ignore")
        w.writeheader()
        w.writerows(linhas)


# ----------------------------------------------------------------------------------
# 1. Busca das páginas
# ----------------------------------------------------------------------------------
def buscar_paginas(log, ordem="title"):
    os.makedirs(PASTA_JSON, exist_ok=True)
    prefixo = "pagina" if ordem == "title" else "pagina_por_{}".format(ordem)
    itens, ultima, total_api = [], ULTIMA_PAGINA, None
    pg = PRIMEIRA_PAGINA
    while pg <= ultima:
        url = URL_PAGINA.format(col=COLECAO, pp=POR_PAGINA, ordem=ordem, pg=pg)
        arq = os.path.join(PASTA_JSON, "{}_{:02d}.json".format(prefixo, pg))
        if os.path.exists(arq):
            with open(arq, encoding="utf-8") as f:
                pacote = json.load(f)
            origem = "arquivo salvo"
        else:
            corpo, cab = baixar(url)
            pacote = {"url": url, "consultado_em": dt.datetime.now().isoformat(timespec="seconds"),
                      "total": cab.get("X-WP-Total"), "total_paginas": cab.get("X-WP-TotalPages"),
                      "resposta": json.loads(corpo.decode("utf-8"))}
            with open(arq, "w", encoding="utf-8") as f:
                json.dump(pacote, f, ensure_ascii=False)
            origem = "portal"
            time.sleep(PAUSA_PAGINAS)
        resp = pacote["resposta"]
        lista = resp if isinstance(resp, list) else resp.get("items", [])
        if total_api is None and pacote.get("total"):
            total_api = int(pacote["total"])
        if pacote.get("total_paginas"):
            ultima = min(ultima, int(pacote["total_paginas"])) if pg > PRIMEIRA_PAGINA else int(pacote["total_paginas"])
        print("Página {:>2}/{}: {} obras ({})".format(pg, ultima, len(lista), origem))
        log.append("pagina {} | {} itens | {} | {}".format(pg, len(lista), origem, url))
        if not lista:
            break
        itens.extend(lista)
        pg += 1
    return itens, total_api


# ----------------------------------------------------------------------------------
# 2. Metadados + fotos
# ----------------------------------------------------------------------------------
def main():
    inicio = dt.datetime.now()
    os.makedirs(SAIDA, exist_ok=True)
    log = ["Busca do Acervo CAL/UnB, coleção {}".format(COLECAO),
           "Início: {}".format(inicio.isoformat(timespec="seconds")),
           "Verificação de certificado: {}".format("sim" if VERIFICAR_CERTIFICADO else "não (decisão da equipe)")]

    print("Buscando a coleção {} no Acervo CAL/UnB...\n".format(COLECAO))
    itens, total_api = buscar_paginas(log)

    # remove eventuais repetições entre páginas (ordem por título pode variar)
    unicos, vistos = [], set()
    for it in itens:
        if str(it.get("id")) not in vistos:
            vistos.add(str(it.get("id")))
            unicos.append(it)
    if total_api and len(unicos) < total_api:
        print("\nA ordenação por título deixou {} obras de fora (títulos repetidos). "
              "Completando pela ordem de ID...\n".format(total_api - len(unicos)))
        log.append("Complemento por ID: faltavam {} obras".format(total_api - len(unicos)))
        extras, _ = buscar_paginas(log, ordem="id")
        for it in extras:
            if str(it.get("id")) not in vistos:
                vistos.add(str(it.get("id")))
                unicos.append(it)
    print("\n{} obras recuperadas (total informado pela API: {}).".format(len(unicos), total_api))

    linhas, colunas_meta = [], []
    for it in unicos:
        orig, grande = fotos_do_item(it)
        titulo = texto_limpo(it.get("title"))
        linha = {"id": it.get("id"), "titulo": titulo, "descricao": texto_limpo(it.get("description")),
                 "url_obra": it.get("url", ""), "url_foto_original": orig, "url_foto_1024px": grande,
                 "arquivo_foto": "", "data_criacao_registro": it.get("creation_date", ""),
                 "data_modificacao_registro": it.get("modification_date", "")}
        for slug, m in (it.get("metadata") or {}).items():
            nome = texto_limpo(m.get("name")) or slug
            if nome in linha and linha[nome] and linha.get("__" + nome) != slug:
                nome = "{} [{}]".format(nome, slug)
            linha[nome] = valor(m)
            linha["__" + nome] = slug
            if nome not in colunas_meta:
                colunas_meta.append(nome)
        linhas.append(linha)

    # fotos
    com_foto = [l for l in linhas if l["url_foto_original"] or l["url_foto_1024px"]]
    print("{} obras têm foto no portal.".format(len(com_foto)))
    baixadas = falhas = 0
    restritas = sum(1 for l in com_foto if "não podem ser baixadas" in " ".join(str(v) for v in l.values()))
    print("{} delas com restrição de download informada pelo portal.".format(restritas))
    log.append("Obras com foto e restrição de download informada pelo portal: {}".format(restritas))
    if BAIXAR_FOTOS and not AUTORIZACAO_CAL.strip():
        print("Fotos NÃO baixadas: preencha AUTORIZACAO_CAL com a autorização da CAL antes de baixar.")
        log.append("Fotos não baixadas: sem autorização registrada.")
    elif BAIXAR_FOTOS:
        log.append("Autorização para baixar fotos: " + AUTORIZACAO_CAL.strip())
    if BAIXAR_FOTOS and AUTORIZACAO_CAL.strip():
        os.makedirs(PASTA_FOTOS, exist_ok=True)
        for i, l in enumerate(com_foto, 1):
            url = l["url_foto_original"] if TAMANHO_FOTO == "original" else (l["url_foto_1024px"] or l["url_foto_original"])
            ext = os.path.splitext(url.split("?")[0])[1].lower() or ".jpg"
            nome = "{}_{}{}".format(l["id"], apelido(l["titulo"]), ext)
            destino = os.path.join(PASTA_FOTOS, nome)
            if not os.path.exists(destino):
                try:
                    conteudo, _ = baixar(url, tentativas=3)
                    with open(destino + ".parcial", "wb") as f:
                        f.write(conteudo)
                    os.replace(destino + ".parcial", destino)
                    baixadas += 1
                    time.sleep(PAUSA_FOTOS)
                except Exception as e:
                    falhas += 1
                    log.append("FALHA foto {} | {} | {}".format(l["id"], url, e))
                    continue
            l["arquivo_foto"] = "imagens/" + nome
            if i % 50 == 0 or i == len(com_foto):
                print("  fotos: {}/{} ({} baixadas agora, {} falhas)".format(i, len(com_foto), baixadas, falhas))

    # tabelas
    colunas = ["id", "titulo", "descricao", "url_obra", "url_foto_original", "url_foto_1024px",
               "arquivo_foto", "data_criacao_registro", "data_modificacao_registro"] + colunas_meta
    grava_csv(os.path.join(SAIDA, "metadados_acervo_{}.csv".format(COLECAO)), linhas, colunas, ",")
    grava_csv(os.path.join(SAIDA, "metadados_acervo_{}_excel.csv".format(COLECAO)), linhas, colunas, ";")

    # galeria
    dados = [{"id": str(l["id"]), "t": l["titulo"], "f": l["arquivo_foto"] or l["url_foto_1024px"],
              "u": l["url_obra"], "m": [[c, l[c]] for c in ["descricao"] + colunas_meta if l.get(c)]}
             for l in linhas]
    pagina = GALERIA.replace("__DADOS__", json.dumps(dados, ensure_ascii=False).replace("<", "\\u003c")) \
                    .replace("__DATA__", inicio.strftime("%d/%m/%Y %H:%M")).replace("__COL__", str(COLECAO))
    with open(os.path.join(SAIDA, "galeria_acervo_{}.html".format(COLECAO)), "w", encoding="utf-8") as f:
        f.write(pagina)

    log += ["Obras recuperadas: {}".format(len(unicos)), "Total informado pela API: {}".format(total_api),
            "Obras com foto: {}".format(len(com_foto)), "Fotos baixadas nesta execução: {}".format(baixadas),
            "Falhas de foto: {}".format(falhas), "Fim: {}".format(dt.datetime.now().isoformat(timespec="seconds"))]
    with open(os.path.join(SAIDA, "log_busca.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(log) + "\n")

    print("\nPronto. Arquivos em: {}".format(SAIDA))
    print("  metadados_acervo_{}.csv / _excel.csv | galeria_acervo_{}.html | log_busca.txt{}"
          .format(COLECAO, COLECAO, " | imagens/" if baixadas else ""))


GALERIA = r"""<!DOCTYPE html><html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>Acervo CAL __COL__</title>
<style>
body{margin:0;font:15px/1.5 system-ui,sans-serif;background:#fff;color:#111}
header{background:#003d7a;color:#fff;padding:16px 4vw}h1{margin:0;font-size:22px}header p{margin:4px 0 0;font-size:13px;color:#dce7f3}
.ctl{position:sticky;top:0;background:#fff;padding:10px 4vw;border-bottom:1px solid #ddd;display:flex;gap:10px;align-items:center}
input{flex:1;font:inherit;padding:8px 10px;border:1px solid #bbb;border-radius:6px}
.g{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:14px;padding:14px 4vw}
.c{border:1px solid #ddd;border-radius:6px;overflow:hidden}.f{aspect-ratio:4/3;background:#f2f4f7;display:flex;align-items:center;justify-content:center;color:#777}
.f img{width:100%;height:100%;object-fit:contain}.x{padding:8px 10px}.x b{display:block}.x small{color:#555}
table{border-collapse:collapse;width:100%;font-size:12.5px}td{border-top:1px solid #eee;padding:3px 4px;vertical-align:top}td:first-child{color:#555;width:40%}
details{padding:0 10px 8px}.p{display:flex;gap:10px;justify-content:center;padding:10px 0 30px}button{font:inherit;padding:6px 12px}
</style></head><body>
<header><h1>Acervo Digital da CAL/UnB: coleção __COL__</h1><p>Consulta em __DATA__. Imagens exibidas diretamente do portal da CAL; direitos reservados (Lei nº 9.610/1998): não baixar nem reproduzir sem autorização.</p></header>
<div class="ctl"><input id="q" type="search" placeholder="Buscar por título, autor, técnica, ID..."><span id="n"></span></div>
<div class="g" id="g"></div><div class="p"><button id="a">Anterior</button><span id="pg"></span><button id="b">Próxima</button></div>
<script>
{const D=__DADOS__;const e=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const ok=u=>/^(https:\/\/|imagens\/)/.test(u||'')?u:'';D.forEach(d=>d.s=(d.id+' '+d.t+' '+d.m.map(x=>x[1]).join(' ')).toLowerCase());
let p=0;const N=60;function r(){const q=document.getElementById('q').value.toLowerCase();const L=D.filter(d=>!q||d.s.includes(q));const tp=Math.max(1,Math.ceil(L.length/N));p=Math.min(p,tp-1);
document.getElementById('n').textContent=L.length+' obras';document.getElementById('pg').textContent='Página '+(p+1)+' de '+tp;
document.getElementById('g').innerHTML=L.slice(p*N,p*N+N).map(d=>`<div class="c"><div class="f">${ok(d.f)?`<img loading="lazy" src="${e(d.f)}" alt="">`:'sem foto'}</div><div class="x"><b>${e(d.t)}</b><small>ID ${e(d.id)}${ok(d.u)?` | <a href="${e(d.u)}" target="_blank">ver no portal</a>`:''}</small></div><details><summary>Metadados (${d.m.length})</summary><table>${d.m.map(x=>`<tr><td>${e(x[0])}</td><td>${e(x[1])}</td></tr>`).join('')}</table></details></div>`).join('')}
document.getElementById('q').addEventListener('input',()=>{p=0;r()});document.getElementById('a').onclick=()=>{if(p>0){p--;r();scrollTo(0,0)}};document.getElementById('b').onclick=()=>{p++;r();scrollTo(0,0)};r();}
</script></body></html>"""


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrompido. Rode de novo para continuar de onde parou.")
        sys.exit(1)
