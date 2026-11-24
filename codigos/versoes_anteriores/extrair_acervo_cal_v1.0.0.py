#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extrator do Acervo Digital da CAL/UnB (plataforma Tainacan)
Hackathon CULTIVA UnB 2026, PPGCont/UnB, disciplina 318710.

O que faz
  1. Descobre todas as coleções públicas do portal (API REST oficial do Tainacan).
  2. Baixa todos os itens públicos de cada coleção, com todos os metadados.
  3. Guarda as respostas brutas (rastreabilidade) e gera:
       dados/inventario.csv            base padronizada com as variáveis das Regras (item 7)
       dados/inventario_excel.csv      a mesma base, separada por ";" (Excel em português)
       dados/inventario_bruto_longo.csv todos os metadados, um valor por linha (sem perda)
       dados/por_colecao/*.csv         uma planilha larga por coleção, com os campos originais
       dados/colecoes.csv              universo: registros declarados x recuperados, por coleção
       dados/metadados_colecoes.csv    definição dos campos de cada coleção
       dados/mapeamento_campos.csv     de-para campo original -> variável padronizada (editável)
       dados/diagnostico_qualidade.csv completude de cada variável, por coleção
       dados/duplicidades.csv          possíveis registros duplicados
       dados/indicadores.csv           indicadores obrigatórios da etapa de identificação (item 15)
       dados/dicionario_dados.md       dicionário de dados gerado automaticamente
       dados/log_extracao.json         data, parâmetros, requisições, erros e limitações
       dados/CULTIVA_acervo_CAL.xlsx   tudo em abas (somente se openpyxl estiver instalado)

Requisitos
  Python 3.8 ou superior. Não precisa instalar nada (somente biblioteca padrão).
  openpyxl é opcional, apenas para gerar o .xlsx.

Uso
  python extrair_acervo_cal.py                      # coleta completa, saída em ./dados
  python extrair_acervo_cal.py --saida ../dados     # escolhe a pasta de saída
  python extrair_acervo_cal.py --offline            # refaz as tabelas só com o cache, sem rede
  python extrair_acervo_cal.py --mapa dados/mapeamento_campos.csv --offline
                                                    # reaplica um de-para revisado pela equipe
  python extrair_acervo_cal.py --base https://outro-acervo.exemplo.br
                                                    # funciona em qualquer portal Tainacan
  python extrair_acervo_cal.py --importar acervo_cal_bruto.json
                                                    # monta as tabelas a partir do JSON baixado
                                                    # pelo trecho coletar_no_navegador.js

Boas práticas de coleta (Regras, item 17.12): intervalo padrão de 1 s entre requisições,
identificação do robô no User-Agent, novas tentativas com espera crescente e cache local
(uma página nunca é baixada duas vezes, salvo com --atualizar).
"""

import argparse
import csv
import datetime as dt
import hashlib
import html
import json
import os
import re
import ssl
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request

VERSAO = "1.0.0"
BASE_PADRAO = "https://www.acervocal.unb.br"
API = "/wp-json/tainacan/v2"
USER_AGENT = ("CULTIVA-UnB-2026/{} (pesquisa academica PPGCont/UnB; coleta com "
              "intervalo entre requisicoes)").format(VERSAO)
POR_PAGINA = 96

# --------------------------------------------------------------------------------------
# Variáveis padronizadas (Regras do Hackathon, item 7, "Informações a serem recuperadas")
# --------------------------------------------------------------------------------------
VARIAVEIS = [
    # (coluna, descrição para o dicionário de dados)
    ("id_registro", "Identificador interno do item no Tainacan (preservado do portal)."),
    ("colecao_id", "Identificador da coleção no Tainacan."),
    ("colecao", "Nome da coleção no portal."),
    ("subcolecao", "Conjunto ou subcoleção informado nos metadados (ex.: Coleção Galvão, Chocó)."),
    ("grupo_sugerido", "Triagem automática: Arte, Arte contemporânea, Etnográfica ou A classificar. Sujeita a revisão."),
    ("criterio_grupo", "Termo que motivou a triagem do grupo (rastreabilidade da regra)."),
    ("flag_possivel_contemporanea", "'sim' quando técnica, categoria ou suporte indicam obra contemporânea (vídeo, instalação, arte postal etc.)."),
    ("categoria", "Categoria, tipologia ou classificação do bem."),
    ("titulo", "Título ou denominação."),
    ("autoria_origem", "Artista, autor ou grupo de origem (inclui etnia ou povo, nas coleções etnográficas)."),
    ("ano_periodo", "Ano, data ou período de produção, como consta no portal."),
    ("ano_inicial_extraido", "Primeiro ano com quatro dígitos encontrado em ano_periodo (apoio a filtros; não substitui o dado original)."),
    ("tecnica", "Técnica."),
    ("materiais", "Materiais ou suporte."),
    ("dimensoes", "Dimensões, como constam no portal."),
    ("tiragem", "Tiragem, edição ou numeração de exemplar (gravuras, fotografias, múltiplos)."),
    ("proveniencia", "Proveniência, procedência ou local de origem."),
    ("forma_aquisicao", "Forma de aquisição ou incorporação (compra, doação, transferência etc.)."),
    ("localizacao", "Localização atual do bem."),
    ("estado_conservacao", "Estado de conservação."),
    ("numero_patrimonio", "Número de patrimônio ou de tombo."),
    ("outros_identificadores", "Outros números de registro, inventário ou código."),
    ("direitos_restricoes", "Direitos, licenças ou restrições de acesso e divulgação."),
    ("descricao", "Descrição histórica ou cultural (descrição do item somada a campos descritivos)."),
    ("url_registro", "Endereço eletrônico do registro no portal."),
    ("fonte", "Fonte do dado."),
    ("data_consulta", "Data e hora da consulta (UTC-3)."),
    ("data_criacao_registro", "Data de criação do registro no Tainacan."),
    ("data_modificacao_registro", "Data da última modificação do registro no Tainacan."),
    ("tipo_documento", "Tipo do documento principal do item no Tainacan (imagem, url, texto, vazio)."),
    ("url_documento", "Endereço do documento principal, quando houver (imagens não são baixadas)."),
    ("campos_principais_preenchidos", "Quantidade de variáveis principais preenchidas (ver completude)."),
    ("completude_pct", "Percentual de preenchimento das variáveis principais."),
    ("possivel_duplicata", "Indica possível duplicidade e o critério usado."),
    ("chave_duplicidade", "Chave normalizada título+autoria+dimensões usada na detecção."),
]
COLUNAS = [c for c, _ in VARIAVEIS]

# Variáveis principais para a completude cadastral (Regras, itens 7 e 15)
PRINCIPAIS = ["categoria", "titulo", "autoria_origem", "ano_periodo", "tecnica", "materiais",
              "dimensoes", "proveniencia", "forma_aquisicao", "localizacao",
              "estado_conservacao", "numero_patrimonio", "descricao"]

# Regras de de-para por palavra-chave, na ordem de prioridade.
# Cada regra: (variavel, padrões que casam, padrões que excluem)
REGRAS_MAPA = [
    ("numero_patrimonio", [r"patrimon", r"\btombo", r"tombamento"], []),
    ("estado_conservacao", [r"conserva", r"estado fisico", r"estado do (bem|objeto|item)", r"\bcondicao"], []),
    ("forma_aquisicao", [r"aquisi", r"incorpora", r"\bdoa(cao|dor)", r"forma de entrada",
                         r"modo de entrada", r"entrada no acervo", r"\bcompra"], []),
    ("localizacao", [r"localiza", r"local atual", r"reserva tecnica", r"acondiciona", r"armazen",
                     r"\bsala\b", r"\bestante", r"mapoteca"], [r"assinatura", r"inscri"]),
    ("tiragem", [r"tiragem", r"\bedicao\b", r"exemplar", r"numeracao", r"\bprova\b"], []),
    ("direitos_restricoes", [r"direito", r"licenc", r"copyright", r"restric", r"acesso"], []),
    ("dimensoes", [r"dimens", r"\baltura", r"largura", r"profundidade", r"comprimento",
                   r"diametro", r"\bmedida", r"\bpeso\b", r"\bespessura"], []),
    ("tecnica", [r"tecnica"], []),
    ("materiais", [r"materia", r"\bsuporte"], []),
    ("proveniencia", [r"proveni", r"procedencia", r"\borigem", r"local de (producao|coleta|fabricacao|criacao)",
                      r"\bregiao", r"\bpais\b", r"\bcidade", r"localidade", r"\bcoleta\b", r"coletor"], []),
    ("subcolecao", [r"\bcolec", r"\bconjunto", r"\bfundo\b", r"nucleo"], []),
    ("autoria_origem", [r"\bautor", r"artista", r"criador", r"\betnia", r"\bpovo", r"grupo (etnico|cultural|de origem)",
                        r"comunidade", r"fabricante", r"realizador", r"nome artistico"],
     [r"biografia", r"sinonimo"]),
    ("ano_periodo", [r"\bdata\b", r"\bano\b", r"periodo", r"datacao", r"\bepoca", r"\bseculo"],
     [r"preenchimento", r"cadastro", r"catalogacao", r"publicacao", r"digitaliza", r"modifica"]),
    ("categoria", [r"categoria", r"classifica", r"tipologia", r"\btipo\b", r"\bclasse\b", r"\bgenero\b",
                   r"\bnatureza\b", r"\bobjeto\b"], [r"midia", r"documento"]),
    ("titulo", [r"titulo", r"denomina", r"nome do (objeto|bem|item)"], []),
    ("descricao", [r"descri", r"historic", r"observa", r"contexto", r"\bnota", r"biografia",
                   r"resumo", r"significado", r"\bfuncao", r"\buso\b", r"inscri", r"assinatura"], []),
    ("outros_identificadores", [r"identifica", r"codigo", r"registro", r"inventario", r"\bnumero",
                                r"\bn[ou]?\b"], []),
]

# Mapeamento Dublin Core (campo "mapping"/"exposer_mapping" do Tainacan), usado como reserva
DUBLIN_CORE = {
    "title": "titulo", "creator": "autoria_origem", "date": "ano_periodo", "created": "ano_periodo",
    "description": "descricao", "abstract": "descricao", "extent": "dimensoes", "medium": "materiais",
    "provenance": "proveniencia", "spatial": "proveniencia", "coverage": "proveniencia",
    "rights": "direitos_restricoes", "accessrights": "direitos_restricoes", "license": "direitos_restricoes",
    "identifier": "outros_identificadores", "type": "categoria", "subject": "categoria",
}

# Triagem dos três conjuntos obrigatórios (Regras, item 4)
TERMOS_ETNOGRAFICA = [r"etnogr", r"indigen", r"\bchoco\b", r"galvao", r"\bcnrc\b", r"colecao inicial",
                      r"povos? (originario|tradiciona)", r"etnia"]
TERMOS_CONTEMPORANEA = [r"contempor", r"triangular", r"video", r"multimidia", r"instalac",
                        r"arte postal", r"mail art", r"conceitual", r"performance", r"\bdigital\b",
                        r"\bnet ?art", r"site specific", r"intervenc"]
TERMOS_ARTE = [r"\barte", r"gravura", r"pintura", r"desenho", r"escultura", r"fotograf", r"litograf",
               r"serigraf", r"xilogravura", r"aquarela", r"\bobras?\b", r"artist"]


# --------------------------------------------------------------------------------------
# Utilidades
# --------------------------------------------------------------------------------------
def agora():
    return dt.datetime.now(dt.timezone(dt.timedelta(hours=-3)))


def para_brasilia(iso):
    """Converte um texto ISO 8601 (com Z ou fuso) para datetime em UTC-3."""
    if not iso:
        return None
    try:
        d = dt.datetime.fromisoformat(str(iso).replace("Z", "+00:00"))
    except ValueError:
        return None
    if d.tzinfo is None:
        d = d.replace(tzinfo=dt.timezone.utc)
    return d.astimezone(dt.timezone(dt.timedelta(hours=-3)))


def chave_url(url):
    """URL normalizada (parâmetros em ordem alfabética) para indexar o cache."""
    u = urllib.parse.urlsplit(url)
    q = urllib.parse.urlencode(sorted(urllib.parse.parse_qsl(u.query, keep_blank_values=True)))
    return "{}://{}{}?{}".format(u.scheme, u.netloc.lower(), u.path.rstrip("/"), q)


def importar_json_navegador(caminho, pasta_cache, log):
    """Grava no cache as respostas coletadas pelo trecho coletar_no_navegador.js."""
    with open(caminho, encoding="utf-8") as f:
        pacote = json.load(f)
    regs = pacote.get("registros", []) if isinstance(pacote, dict) else pacote
    os.makedirs(pasta_cache, exist_ok=True)
    for r in regs:
        arq = os.path.join(pasta_cache, hashlib.sha1(chave_url(r["url"]).encode("utf-8")).hexdigest() + ".json")
        with open(arq, "w", encoding="utf-8") as f:
            json.dump(r, f, ensure_ascii=False)
    log["importacao_navegador"] = {"arquivo": os.path.basename(caminho), "registros": len(regs),
                                   "gerado_em": pacote.get("gerado_em") if isinstance(pacote, dict) else None,
                                   "origem": pacote.get("origem") if isinstance(pacote, dict) else None}
    base = pacote.get("origem") if isinstance(pacote, dict) else None
    return len(regs), base


def normaliza(txt):
    """minúsculas, sem acento, só letras/números/espaços"""
    if txt is None:
        return ""
    t = unicodedata.normalize("NFKD", str(txt))
    t = "".join(c for c in t if not unicodedata.combining(c)).lower()
    t = re.sub(r"[^a-z0-9]+", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def limpa_texto(v):
    if v is None:
        return ""
    t = html.unescape(str(v))
    t = re.sub(r"<[^>]+>", " ", t)
    t = t.replace(" ", " ")
    return re.sub(r"\s+", " ", t).strip()


def casa(padroes, texto):
    """Retorna o termo legível do primeiro padrão que casar (ou None)."""
    for p in padroes:
        m = re.search(p, texto)
        if m:
            return m.group(0).strip()
    return None


def valor_metadado(m):
    """Extrai um texto legível de um metadado do Tainacan."""
    if not isinstance(m, dict):
        return limpa_texto(m)
    vs = m.get("value_as_string")
    if vs not in (None, ""):
        return limpa_texto(vs)
    v = m.get("value")
    if v in (None, "", [], {}):
        return ""
    if isinstance(v, list):
        partes = []
        for e in v:
            if isinstance(e, dict):
                partes.append(limpa_texto(e.get("name") or e.get("value_as_string") or e.get("title") or json.dumps(e, ensure_ascii=False)))
            else:
                partes.append(limpa_texto(e))
        return " | ".join(p for p in partes if p)
    if isinstance(v, dict):
        return limpa_texto(v.get("name") or v.get("title") or json.dumps(v, ensure_ascii=False))
    return limpa_texto(v)


def extrai_mapping_dc(m):
    """Retorna o termo Dublin Core (ex.: 'creator') se houver mapeamento."""
    mp = m.get("mapping") or m.get("exposer_mapping") or {}
    if isinstance(mp, dict):
        for _, uri in mp.items():
            if isinstance(uri, str) and uri:
                termo = re.split(r"[/#:]", uri.strip("/"))[-1].lower()
                if termo in DUBLIN_CORE:
                    return termo
    return None


def primeiro_ano(txt):
    m = re.search(r"\b(1[0-9]{3}|20[0-9]{2})\b", txt or "")
    return m.group(1) if m else ""


def junta(valores):
    vistos, saida = set(), []
    for v in valores:
        v = (v or "").strip()
        if v and normaliza(v) not in vistos:
            vistos.add(normaliza(v))
            saida.append(v)
    return " | ".join(saida)


# --------------------------------------------------------------------------------------
# Cliente HTTP educado, com cache e registro
# --------------------------------------------------------------------------------------
class ErroSSL(Exception):
    pass


class Cliente:
    def __init__(self, base, pasta_cache, intervalo=1.0, verificar_ssl=True, offline=False,
                 atualizar=False, log=None):
        self.base = base.rstrip("/")
        self.cache = pasta_cache
        self.intervalo = intervalo
        self.offline = offline
        self.atualizar = atualizar
        self.log = log
        self.ultimo = 0.0
        self.primeira_consulta = None
        os.makedirs(self.cache, exist_ok=True)
        if verificar_ssl:
            self.ctx = ssl.create_default_context()
        else:
            self.ctx = ssl.create_default_context()
            self.ctx.check_hostname = False
            self.ctx.verify_mode = ssl.CERT_NONE

    def url(self, caminho, params=None):
        u = self.base + API + caminho
        if params:
            u += "?" + urllib.parse.urlencode(params)
        return u

    def _arquivo_cache(self, url):
        return os.path.join(self.cache, hashlib.sha1(chave_url(url).encode("utf-8")).hexdigest() + ".json")

    def _marca_consulta(self, quando):
        if quando and (self.primeira_consulta is None or quando < self.primeira_consulta):
            self.primeira_consulta = quando

    def get(self, caminho, params=None, tentativas=4):
        url = self.url(caminho, params)
        arq = self._arquivo_cache(url)
        if os.path.exists(arq) and not self.atualizar:
            with open(arq, encoding="utf-8") as f:
                reg = json.load(f)
            self.log["requisicoes_cache"] += 1
            self._marca_consulta(para_brasilia(reg.get("consultado_em")))
            if int(reg.get("status") or 200) >= 400:
                raise RuntimeError("HTTP {} em {} (registrado no cache)".format(reg.get("status"), url))
            return reg["corpo"], reg.get("cabecalhos", {}), reg.get("status", 200)
        if self.offline:
            raise FileNotFoundError("Sem cache para {} (modo --offline)".format(url))

        espera = 2.0
        ultimo_erro = None
        for t in range(1, tentativas + 1):
            dif = time.time() - self.ultimo
            if dif < self.intervalo:
                time.sleep(self.intervalo - dif)
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT,
                                                       "Accept": "application/json"})
            try:
                self.ultimo = time.time()
                with urllib.request.urlopen(req, timeout=60, context=self.ctx) as r:
                    corpo_txt = r.read().decode("utf-8", errors="replace")
                    cab = {k: v for k, v in r.headers.items()
                           if k.lower() in ("x-wp-total", "x-wp-totalpages", "date", "content-type")}
                    status = r.status
                corpo = json.loads(corpo_txt)
                with open(arq, "w", encoding="utf-8") as f:
                    json.dump({"url": url, "consultado_em": agora().isoformat(), "status": status,
                               "cabecalhos": cab, "corpo": corpo}, f, ensure_ascii=False)
                self.log["requisicoes_rede"] += 1
                self._marca_consulta(agora())
                return corpo, cab, status
            except urllib.error.HTTPError as e:
                ultimo_erro = "HTTP {} em {}".format(e.code, url)
                if e.code in (429, 500, 502, 503, 504) and t < tentativas:
                    ra = e.headers.get("Retry-After")
                    time.sleep(float(ra) if ra and ra.isdigit() else espera)
                    espera *= 2
                    continue
                raise
            except (ssl.SSLError, ssl.CertificateError) as e:
                raise ErroSSL(str(e))
            except urllib.error.URLError as e:
                if isinstance(e.reason, (ssl.SSLError, ssl.CertificateError)):
                    raise ErroSSL(str(e.reason))
                ultimo_erro = "Falha de rede em {}: {}".format(url, e.reason)
                if t < tentativas:
                    time.sleep(espera)
                    espera *= 2
                    continue
                raise
            except json.JSONDecodeError:
                ultimo_erro = "Resposta não é JSON em {}".format(url)
                if t < tentativas:
                    time.sleep(espera)
                    espera *= 2
                    continue
                raise RuntimeError(ultimo_erro)
        raise RuntimeError(ultimo_erro or "Falha em " + url)


def cabecalho_int(cab, nome):
    for k, v in cab.items():
        if k.lower() == nome.lower():
            try:
                return int(v)
            except (TypeError, ValueError):
                return None
    return None


# --------------------------------------------------------------------------------------
# Coleta
# --------------------------------------------------------------------------------------
def coletar_colecoes(cli):
    colecoes, pagina = [], 1
    while True:
        corpo, cab, _ = cli.get("/collections", {"perpage": 100, "paged": pagina})
        lista = corpo if isinstance(corpo, list) else corpo.get("items", [])
        if not lista:
            break
        colecoes.extend(lista)
        total_pag = cabecalho_int(cab, "X-WP-TotalPages") or 1
        if pagina >= total_pag:
            break
        pagina += 1
    return colecoes


def total_publico(col):
    ti = col.get("total_items")
    if isinstance(ti, dict):
        try:
            return int(ti.get("publish") or 0)
        except (TypeError, ValueError):
            return None
    try:
        return int(ti)
    except (TypeError, ValueError):
        return None


def metadados_do_item_por_endpoint(cli, item_id):
    corpo, _, _ = cli.get("/item/{}/metadata".format(item_id))
    meta = {}
    for e in corpo if isinstance(corpo, list) else []:
        md = e.get("metadatum") or {}
        slug = md.get("slug") or str(md.get("id"))
        meta[slug] = {"id": md.get("id"), "name": md.get("name"), "value": e.get("value"),
                      "value_as_string": e.get("value_as_string"),
                      "mapping": md.get("exposer_mapping") or {}}
    return meta


def coletar_itens(cli, col_id, log):
    itens, pagina, total_api = [], 1, None
    precisa_fallback = None
    while True:
        corpo, cab, _ = cli.get("/collection/{}/items".format(col_id),
                                {"perpage": POR_PAGINA, "paged": pagina, "orderby": "id", "order": "asc"})
        lista = corpo if isinstance(corpo, list) else corpo.get("items", [])
        if total_api is None:
            total_api = cabecalho_int(cab, "X-WP-Total")
        if not lista:
            break
        if precisa_fallback is None:
            precisa_fallback = not any(isinstance(i.get("metadata"), dict) and i.get("metadata") for i in lista)
            if precisa_fallback:
                log["avisos"].append("Coleção {}: itens sem metadados na listagem; usando /item/<id>/metadata.".format(col_id))
        if precisa_fallback:
            for i in lista:
                try:
                    i["metadata"] = metadados_do_item_por_endpoint(cli, i.get("id"))
                except Exception as e:  # registra e segue
                    log["erros"].append("Item {}: metadados indisponíveis ({})".format(i.get("id"), e))
                    i["metadata"] = {}
        itens.extend(lista)
        total_pag = cabecalho_int(cab, "X-WP-TotalPages") or 1
        print("    página {}/{}: {} itens acumulados".format(pagina, total_pag, len(itens)))
        if pagina >= total_pag:
            break
        pagina += 1
    return itens, total_api


# --------------------------------------------------------------------------------------
# De-para e padronização
# --------------------------------------------------------------------------------------
def classificar_metadado(nome, slug, dc=None):
    texto = normaliza("{} {}".format(nome or "", (slug or "").replace("-", " ")))
    texto = re.sub(r"\b\d+\b", "", texto).strip()  # tira sufixos numéricos de slug
    for var, padroes, exclui in REGRAS_MAPA:
        p = casa(padroes, texto)
        if p and not casa(exclui, texto):
            extra = []
            if var == "tecnica" and casa([r"materia", r"\bsuporte"], texto):
                extra = ["materiais"]
            return [var] + extra, "palavra-chave: " + p
    if dc:
        return [DUBLIN_CORE[dc]], "Dublin Core: " + dc
    return [], "sem correspondência"


def carregar_mapa_manual(caminho):
    """Lê um mapeamento_campos.csv revisado: colecao_id, metadado_slug, variavel_padronizada."""
    mapa = {}
    with open(caminho, encoding="utf-8-sig", newline="") as f:
        for lin in csv.DictReader(f):
            chave = (str(lin.get("colecao_id", "")).strip(), lin.get("metadado_slug", "").strip())
            vars_ = [v.strip() for v in (lin.get("variavel_padronizada") or "").split("+") if v.strip()]
            mapa[chave] = [v for v in vars_ if v in COLUNAS]
    return mapa


def triagem_grupo(colecao_nome, subcol, categoria, tecnica, materiais, titulo):
    base_col = normaliza(colecao_nome + " " + subcol)
    p = casa(TERMOS_ETNOGRAFICA, base_col)
    if p:
        return "Etnográfica", "coleção/subcoleção: " + p
    p = casa(TERMOS_CONTEMPORANEA, base_col)
    if p:
        return "Arte contemporânea", "coleção/subcoleção: " + p
    p = casa(TERMOS_ARTE, base_col)
    if p:
        return "Arte", "coleção/subcoleção: " + p
    resto = normaliza(" ".join([categoria, tecnica, materiais]))
    p = casa(TERMOS_ETNOGRAFICA, resto)
    if p:
        return "Etnográfica", "categoria/técnica: " + p
    p = casa(TERMOS_ARTE + TERMOS_CONTEMPORANEA, resto)
    if p:
        return "Arte", "categoria/técnica: " + p
    return "A classificar", "sem termo indicativo"


# --------------------------------------------------------------------------------------
# Escrita
# --------------------------------------------------------------------------------------
def grava_csv(caminho, linhas, colunas, sep=",", bom=True):
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, "w", encoding="utf-8-sig" if bom else "utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=colunas, delimiter=sep, extrasaction="ignore")
        w.writeheader()
        for l in linhas:
            w.writerow(l)


def nome_arquivo(txt):
    return (normaliza(txt).replace(" ", "_") or "colecao")[:60]


def main():
    ap = argparse.ArgumentParser(description="Extrator do Acervo Digital da CAL/UnB (Tainacan).")
    ap.add_argument("--base", default=BASE_PADRAO, help="URL do portal Tainacan (padrão: %(default)s)")
    ap.add_argument("--saida", default="dados", help="pasta de saída (padrão: ./dados)")
    ap.add_argument("--intervalo", type=float, default=1.0, help="segundos entre requisições (padrão: 1.0)")
    ap.add_argument("--offline", action="store_true", help="não acessa a rede; usa só o cache")
    ap.add_argument("--atualizar", action="store_true", help="ignora o cache e baixa tudo de novo")
    ap.add_argument("--mapa", help="mapeamento_campos.csv revisado pela equipe (tem prioridade sobre as regras)")
    ap.add_argument("--importar", help="JSON gerado por coletar_no_navegador.js (implica --offline)")
    ap.add_argument("--colecoes", help="IDs de coleções separados por vírgula (padrão: todas)")
    ap.add_argument("--sem-verificar-ssl", action="store_true",
                    help="NÃO verifica o certificado do site. Use só se a equipe decidir aceitar o risco "
                         "(dados públicos, somente leitura). Fica registrado no log.")
    args = ap.parse_args()

    inicio = agora()
    saida = args.saida
    os.makedirs(saida, exist_ok=True)
    log = {"script": "extrair_acervo_cal.py", "versao": VERSAO, "base": args.base,
           "inicio": inicio.isoformat(), "python": sys.version.split()[0],
           "parametros": vars(args), "verificacao_ssl": not args.sem_verificar_ssl,
           "requisicoes_rede": 0, "requisicoes_cache": 0, "avisos": [], "erros": [],
           "limitacoes": []}
    if args.sem_verificar_ssl:
        msg = ("Coleta realizada SEM verificação do certificado TLS do portal (opção "
               "--sem-verificar-ssl), por decisão da equipe.")
        log["limitacoes"].append(msg)
        print("ATENÇÃO: " + msg)

    if args.importar:
        n, base_imp = importar_json_navegador(args.importar, os.path.join(saida, "brutos"), log)
        args.offline = True
        if base_imp and args.base == BASE_PADRAO:
            args.base = base_imp
            log["base"] = base_imp
        log["limitacoes"].append("Respostas da API coletadas no navegador (coletar_no_navegador.js) e importadas "
                                 "de {} ({} respostas).".format(os.path.basename(args.importar), n))
        print("Importadas {} respostas de {}".format(n, args.importar))

    cli = Cliente(args.base, os.path.join(saida, "brutos"), args.intervalo,
                  verificar_ssl=not args.sem_verificar_ssl, offline=args.offline,
                  atualizar=args.atualizar, log=log)

    def salva_log():
        log["fim"] = agora().isoformat()
        with open(os.path.join(saida, "log_extracao.json"), "w", encoding="utf-8") as f:
            json.dump(log, f, ensure_ascii=False, indent=2)

    # 1. Coleções -------------------------------------------------------------------
    print("Consultando coleções em", args.base)
    try:
        colecoes = coletar_colecoes(cli)
    except ErroSSL as e:
        log["erros"].append("Erro de certificado TLS: " + str(e))
        salva_log()
        print("\nERRO DE CERTIFICADO (SSL/TLS): " + str(e))
        print("Possíveis causas e saídas:\n"
              " 1. O certificado do portal está vencido ou inválido. Avise a CAL/UnB e os professores e\n"
              "    registre a limitação. Se a equipe decidir aceitar o risco (dados públicos, só leitura),\n"
              "    rode de novo com --sem-verificar-ssl; a opção fica registrada no log_extracao.json.\n"
              " 2. No macOS com Python do python.org, rode antes 'Install Certificates.command'\n"
              "    (pasta Aplicativos > Python 3.x) quando a mensagem citar 'unable to get local issuer'.")
        sys.exit(2)
    except Exception as e:
        log["erros"].append("Falha ao listar coleções: " + str(e))
        salva_log()
        print("ERRO ao listar coleções:", e)
        sys.exit(1)

    if args.colecoes:
        quero = {s.strip() for s in args.colecoes.split(",")}
        colecoes = [c for c in colecoes if str(c.get("id")) in quero]
    print("{} coleções públicas encontradas.".format(len(colecoes)))

    # Total do repositório (todas as coleções), para o indicador de cobertura
    total_repositorio = None
    try:
        _, cab, _ = cli.get("/items", {"perpage": 1, "paged": 1})
        total_repositorio = cabecalho_int(cab, "X-WP-Total")
    except Exception as e:
        log["avisos"].append("Não foi possível obter o total do repositório: {}".format(e))

    mapa_manual = carregar_mapa_manual(args.mapa) if args.mapa else {}
    data_consulta = (cli.primeira_consulta or inicio).strftime("%Y-%m-%d %H:%M")
    log["data_consulta_portal"] = data_consulta

    tab_colecoes, tab_metadados, tab_mapa, longo, inventario = [], [], [], [], []
    por_colecao = {}

    for col in colecoes:
        cid, cnome = col.get("id"), limpa_texto(col.get("name"))
        print("\nColeção {} | {}".format(cid, cnome))
        reg_col = {"colecao_id": cid, "colecao": cnome, "slug": col.get("slug"),
                   "url": col.get("url"), "itens_publicos_declarados": total_publico(col),
                   "itens_total_api": None, "itens_recuperados": 0, "status_acesso": "ok", "erro": ""}

        # 1a. definição de metadados (auxiliar para o dicionário)
        defs = {}
        try:
            corpo, _, _ = cli.get("/collection/{}/metadata".format(cid), {"perpage": 200})
            for md in corpo if isinstance(corpo, list) else []:
                defs[md.get("slug")] = md
        except Exception as e:
            log["avisos"].append("Coleção {}: definição de metadados indisponível ({})".format(cid, e))

        # 1b. itens
        try:
            itens, total_api = coletar_itens(cli, cid, log)
        except ErroSSL as e:
            log["erros"].append("Coleção {}: erro TLS ({})".format(cid, e))
            itens, total_api = [], None
            reg_col.update(status_acesso="erro", erro="TLS: " + str(e))
        except Exception as e:
            log["erros"].append("Coleção {}: {}".format(cid, e))
            itens, total_api = [], None
            reg_col.update(status_acesso="erro", erro=str(e))
        reg_col["itens_total_api"] = total_api
        reg_col["itens_recuperados"] = len(itens)

        # 1c. de-para dos campos desta coleção
        campos = {}  # slug -> (nome, id, dc)
        for slug, md in defs.items():
            campos[slug] = (limpa_texto(md.get("name")), md.get("id"), extrai_mapping_dc(md), md)
        for it in itens:
            for slug, m in (it.get("metadata") or {}).items():
                if slug not in campos:
                    campos[slug] = (limpa_texto(m.get("name")), m.get("id"), extrai_mapping_dc(m), {})
        mapa_col = {}
        for slug, (nome, mid, dc, md) in campos.items():
            if (str(cid), slug) in mapa_manual:
                vars_, regra = mapa_manual[(str(cid), slug)], "manual (arquivo --mapa)"
            else:
                vars_, regra = classificar_metadado(nome, slug, dc)
            mapa_col[slug] = vars_
            tab_mapa.append({"colecao_id": cid, "colecao": cnome, "metadado_id": mid, "metadado_slug": slug,
                             "metadado_nome": nome, "variavel_padronizada": "+".join(vars_), "regra": regra})
            tipo = md.get("metadata_type") or ""
            tab_metadados.append({"colecao_id": cid, "colecao": cnome, "metadado_id": mid, "metadado_slug": slug,
                                  "metadado_nome": nome, "tipo": tipo.split("\\")[-1] if tipo else "",
                                  "multiplo": md.get("multiple", ""), "obrigatorio": md.get("required", ""),
                                  "mapeamento_dublin_core": dc or "",
                                  "descricao": limpa_texto(md.get("description")),
                                  "variavel_padronizada": "+".join(vars_)})

        # 1d. linhas
        larga = []
        for it in itens:
            meta = it.get("metadata") or {}
            acum = {c: [] for c in COLUNAS}
            linha_larga = {"id_registro": it.get("id"), "titulo_item": limpa_texto(it.get("title")),
                           "url_registro": it.get("url")}
            for slug, m in meta.items():
                val = valor_metadado(m)
                linha_larga[slug] = val
                longo.append({"id_registro": it.get("id"), "colecao_id": cid, "colecao": cnome,
                              "metadado_slug": slug, "metadado_nome": limpa_texto(m.get("name")),
                              "valor": val})
                for var in mapa_col.get(slug, []):
                    if val:
                        acum[var].append(val)
            larga.append(linha_larga)

            l = {c: junta(acum[c]) for c in COLUNAS}
            l["titulo"] = junta([limpa_texto(it.get("title"))] + acum["titulo"])
            l["descricao"] = junta([limpa_texto(it.get("description"))] + acum["descricao"])
            l.update({"id_registro": it.get("id"), "colecao_id": cid, "colecao": cnome,
                      "url_registro": it.get("url") or "",
                      "fonte": "Acervo Digital da CAL/UnB (Tainacan), {}".format(args.base),
                      "data_consulta": data_consulta,
                      "data_criacao_registro": it.get("creation_date") or "",
                      "data_modificacao_registro": it.get("modification_date") or "",
                      "tipo_documento": it.get("document_type") or "",
                      "url_documento": it.get("document") if isinstance(it.get("document"), str)
                      and str(it.get("document")).startswith("http") else ""})
            l["ano_inicial_extraido"] = primeiro_ano(l["ano_periodo"])
            grupo, crit = triagem_grupo(cnome, l["subcolecao"], l["categoria"], l["tecnica"],
                                        l["materiais"], l["titulo"])
            l["grupo_sugerido"], l["criterio_grupo"] = grupo, crit
            pc = casa(TERMOS_CONTEMPORANEA, normaliza(" ".join([l["categoria"], l["tecnica"], l["materiais"],
                                                                  l["subcolecao"], cnome])))
            l["flag_possivel_contemporanea"] = "sim" if (pc or grupo == "Arte contemporânea") else ""
            n = sum(1 for c in PRINCIPAIS if l.get(c))
            l["campos_principais_preenchidos"] = n
            l["completude_pct"] = round(100.0 * n / len(PRINCIPAIS), 1)
            l["chave_duplicidade"] = "|".join(normaliza(l[c]) for c in ("titulo", "autoria_origem", "dimensoes"))
            inventario.append(l)

        por_colecao[(cid, cnome)] = larga
        tab_colecoes.append(reg_col)
        if reg_col["itens_publicos_declarados"] not in (None, reg_col["itens_recuperados"]):
            log["avisos"].append("Coleção {}: {} itens declarados e {} recuperados.".format(
                cid, reg_col["itens_publicos_declarados"], reg_col["itens_recuperados"]))

    # 2. Duplicidades -----------------------------------------------------------------
    grupos_pat, grupos_chave, grupos_id = {}, {}, {}
    for l in inventario:
        grupos_id.setdefault(str(l["id_registro"]), []).append(l)
        if l["numero_patrimonio"]:
            grupos_pat.setdefault(normaliza(l["numero_patrimonio"]), []).append(l)
        if normaliza(l["titulo"]) and (normaliza(l["autoria_origem"]) or normaliza(l["dimensoes"])):
            grupos_chave.setdefault(l["chave_duplicidade"], []).append(l)
    tab_dup = []
    for criterio, grupos in (("mesmo id_registro", grupos_id), ("mesmo número de patrimônio", grupos_pat),
                             ("mesmo título+autoria+dimensões", grupos_chave)):
        for chave, ls in grupos.items():
            if len(ls) > 1:
                for l in ls:
                    marca = l["possivel_duplicata"]
                    l["possivel_duplicata"] = (marca + "; " if marca else "") + "sim (" + criterio + ")"
                    tab_dup.append({"criterio": criterio, "chave": chave, "id_registro": l["id_registro"],
                                    "colecao": l["colecao"], "titulo": l["titulo"],
                                    "autoria_origem": l["autoria_origem"], "dimensoes": l["dimensoes"],
                                    "numero_patrimonio": l["numero_patrimonio"], "url_registro": l["url_registro"]})

    # 3. Diagnóstico de qualidade ------------------------------------------------------
    diag = []
    def bloco(nome, ls):
        lin = {"colecao": nome, "registros": len(ls)}
        for c in PRINCIPAIS:
            lin[c] = round(100.0 * sum(1 for l in ls if l.get(c)) / len(ls), 1) if ls else 0.0
        lin["completude_media"] = round(sum(l["completude_pct"] for l in ls) / len(ls), 1) if ls else 0.0
        return lin
    for (cid, cnome), _ in por_colecao.items():
        diag.append(bloco(cnome, [l for l in inventario if l["colecao_id"] == cid]))
    for g in ("Arte", "Arte contemporânea", "Etnográfica", "A classificar"):
        ls = [l for l in inventario if l["grupo_sugerido"] == g]
        if ls:
            diag.append(bloco("GRUPO: " + g, ls))
    diag.append(bloco("TOTAL", inventario))

    # 4. Indicadores (etapa de identificação) -----------------------------------------
    declarados = sum(c["itens_publicos_declarados"] or 0 for c in tab_colecoes)
    universo = max([v for v in (declarados, total_repositorio) if v] or [0])
    recuperados = len({str(l["id_registro"]) for l in inventario})
    ids_dup = {str(d["id_registro"]) for d in tab_dup}
    rastreaveis = sum(1 for l in inventario if l["url_registro"] and l["data_consulta"])
    indicadores = [
        ("Registros identificados", universo,
         "Maior valor entre a soma dos itens públicos declarados pelas coleções ({}) e o total do repositório na API ({})."
         .format(declarados, total_repositorio)),
        ("Registros recuperados", recuperados, "Itens distintos efetivamente baixados e organizados."),
        ("Cobertura (%)", round(100.0 * recuperados / universo, 1) if universo else "",
         "Recuperados / identificados, no universo digital público."),
        ("Completude cadastral média (%)", diag[-1]["completude_media"] if diag else "",
         "Média do preenchimento das {} variáveis principais.".format(len(PRINCIPAIS))),
        ("Registros com possível duplicidade", len(ids_dup), "Ver duplicidades.csv; requer conferência manual."),
        ("Rastreabilidade da fonte (%)", round(100.0 * rastreaveis / recuperados, 1) if recuperados else "",
         "Registros com URL de origem e data de consulta. Decisões de reconhecimento e mensuração entram nas etapas II e III."),
    ]
    for g in ("Arte", "Arte contemporânea", "Etnográfica", "A classificar"):
        indicadores.append(("Registros no grupo sugerido: " + g,
                            sum(1 for l in inventario if l["grupo_sugerido"] == g), "Triagem automática, sujeita a revisão."))
    indicadores.append(("Registros com indício de obra contemporânea",
                        sum(1 for l in inventario if l["flag_possivel_contemporanea"]), "flag_possivel_contemporanea = sim"))
    tab_ind = [{"indicador": a, "valor": b, "observacao": c} for a, b, c in indicadores]

    # 5. Gravação ---------------------------------------------------------------------
    print("\nGravando arquivos em", os.path.abspath(saida))
    grava_csv(os.path.join(saida, "inventario.csv"), inventario, COLUNAS)
    grava_csv(os.path.join(saida, "inventario_excel.csv"), inventario, COLUNAS, sep=";")
    grava_csv(os.path.join(saida, "inventario_bruto_longo.csv"), longo,
              ["id_registro", "colecao_id", "colecao", "metadado_slug", "metadado_nome", "valor"])
    grava_csv(os.path.join(saida, "colecoes.csv"), tab_colecoes,
              ["colecao_id", "colecao", "slug", "url", "itens_publicos_declarados", "itens_total_api",
               "itens_recuperados", "status_acesso", "erro"])
    grava_csv(os.path.join(saida, "metadados_colecoes.csv"), tab_metadados,
              ["colecao_id", "colecao", "metadado_id", "metadado_slug", "metadado_nome", "tipo", "multiplo",
               "obrigatorio", "mapeamento_dublin_core", "variavel_padronizada", "descricao"])
    grava_csv(os.path.join(saida, "mapeamento_campos.csv"), tab_mapa,
              ["colecao_id", "colecao", "metadado_id", "metadado_slug", "metadado_nome",
               "variavel_padronizada", "regra"])
    grava_csv(os.path.join(saida, "diagnostico_qualidade.csv"), diag,
              ["colecao", "registros"] + PRINCIPAIS + ["completude_media"])
    grava_csv(os.path.join(saida, "duplicidades.csv"), tab_dup,
              ["criterio", "chave", "id_registro", "colecao", "titulo", "autoria_origem", "dimensoes",
               "numero_patrimonio", "url_registro"])
    grava_csv(os.path.join(saida, "indicadores.csv"), tab_ind, ["indicador", "valor", "observacao"])
    for (cid, cnome), larga in por_colecao.items():
        cols = ["id_registro", "titulo_item", "url_registro"]
        for l in larga:
            for k in l:
                if k not in cols:
                    cols.append(k)
        grava_csv(os.path.join(saida, "por_colecao", "{}_{}.csv".format(cid, nome_arquivo(cnome))), larga, cols)

    # dicionário de dados
    with open(os.path.join(saida, "dicionario_dados.md"), "w", encoding="utf-8") as f:
        f.write("# Dicionário de dados: Acervo Digital da CAL/UnB\n\n")
        f.write("Gerado automaticamente por `extrair_acervo_cal.py` v{} em {}. Fonte: {}.\n\n".format(
            VERSAO, data_consulta, args.base))
        f.write("## inventario.csv (base padronizada)\n\n| Coluna | Descrição |\n|---|---|\n")
        for c, d in VARIAVEIS:
            f.write("| `{}` | {} |\n".format(c, d))
        f.write("\nAs variáveis padronizadas são preenchidas pelo de-para em `mapeamento_campos.csv`. "
                "Quando mais de um campo original alimenta a mesma variável, os valores são unidos por ` | `. "
                "Campos vazios significam que o dado não consta no portal; nada é inferido ou inventado.\n\n")
        f.write("## Campos originais por coleção\n\n")
        for (cid, cnome), _ in por_colecao.items():
            f.write("### {} (id {})\n\n| Campo original | Slug | Tipo | Variável padronizada |\n|---|---|---|---|\n"
                    .format(cnome, cid))
            for m in [m for m in tab_metadados if m["colecao_id"] == cid]:
                f.write("| {} | `{}` | {} | {} |\n".format(m["metadado_nome"], m["metadado_slug"], m["tipo"],
                                                         m["variavel_padronizada"] or "(não mapeado)"))
            f.write("\n")
        f.write("## Demais arquivos\n\n"
                "- `inventario_bruto_longo.csv`: todos os metadados de todos os itens, um valor por linha.\n"
                "- `por_colecao/`: uma planilha por coleção, com os campos originais.\n"
                "- `colecoes.csv`: itens declarados, total da API e itens recuperados por coleção.\n"
                "- `diagnostico_qualidade.csv`: percentual de preenchimento por variável e coleção.\n"
                "- `duplicidades.csv`: possíveis duplicidades e critério.\n"
                "- `indicadores.csv`: indicadores da etapa de identificação.\n"
                "- `brutos/`: respostas originais da API (JSON), com URL e data de consulta.\n"
                "- `log_extracao.json`: parâmetros, requisições, avisos, erros e limitações.\n")

    # planilha opcional
    try:
        import openpyxl  # noqa
        from openpyxl.utils import get_column_letter
        wb = openpyxl.Workbook()
        def aba(nome, linhas, cols, primeira=False):
            ws = wb.active if primeira else wb.create_sheet()
            ws.title = nome[:31]
            ws.append(cols)
            for l in linhas:
                ws.append([l.get(c, "") if not isinstance(l.get(c, ""), (list, dict)) else str(l.get(c)) for c in cols])
            ws.freeze_panes = "A2"
            for i, c in enumerate(cols, 1):
                ws.column_dimensions[get_column_letter(i)].width = min(45, max(10, len(c) + 2))
        aba("inventario", inventario, COLUNAS, primeira=True)
        aba("colecoes", tab_colecoes, list(tab_colecoes[0].keys()) if tab_colecoes else ["colecao_id"])
        aba("indicadores", tab_ind, ["indicador", "valor", "observacao"])
        aba("diagnostico", diag, ["colecao", "registros"] + PRINCIPAIS + ["completude_media"])
        aba("duplicidades", tab_dup, ["criterio", "chave", "id_registro", "colecao", "titulo",
                                      "autoria_origem", "dimensoes", "numero_patrimonio", "url_registro"])
        aba("mapeamento", tab_mapa, ["colecao_id", "colecao", "metadado_id", "metadado_slug", "metadado_nome",
                                     "variavel_padronizada", "regra"])
        wb.save(os.path.join(saida, "CULTIVA_acervo_CAL.xlsx"))
    except ImportError:
        log["avisos"].append("openpyxl não instalado: CULTIVA_acervo_CAL.xlsx não gerado (CSVs gerados normalmente).")

    log["resumo"] = {"colecoes": len(tab_colecoes), "registros_identificados": universo,
                     "registros_recuperados": recuperados, "total_repositorio_api": total_repositorio}
    log["limitacoes"].append("A cobertura refere-se ao universo digital público do portal; não equivale ao "
                             "patrimônio físico da CAL (Regras, item 4.4).")
    log["limitacoes"].append("Imagens e documentos não são baixados; apenas seus endereços são registrados.")
    salva_log()

    print("\nResumo")
    for i in tab_ind[:6]:
        print("  {}: {}".format(i["indicador"], i["valor"]))
    if log["erros"]:
        print("  Erros registrados: {} (ver log_extracao.json)".format(len(log["erros"])))
    print("Concluído.")


if __name__ == "__main__":
    main()
