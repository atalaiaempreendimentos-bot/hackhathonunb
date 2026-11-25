#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Atos de incorporação de obras de arte doadas à UnB, publicados no Boletim de Atos Oficiais (BAO).

Fonte: SEI da UnB, Publicações Eletrônicas (consulta pública), pesquisa "obra de arte doação" com
data de publicação de 01/01/2018 a 31/12/2021 (96 publicações em 25/11/2026: 95 atos e a
Instrução DAF nº 001/2018), mais 2 atos com obras de arte encontrados na pesquisa "incorporação
doados" no mesmo período (143 publicações, as demais de outros bens). A Instrução exige avaliação das obras doadas por comissão especial
(art. 19, V), valores no termo de doação (art. 4º) e publicação do extrato no BAO (art. 11).

Grava dados/atos_incorporacao_bao.csv: um bem por linha (ato, data de publicação, documento,
endereço, doador, tombamento, especificação, valor). CPF e CNPJ são descartados; as páginas
originais ficam só no cache local (--cache, por padrão na pasta temporária do sistema), fora do
repositório, porque trazem CPF.
Pausa de 1 s entre requisições (Regras, item 17.12).
"""
import argparse
import csv
import html.parser
import os
import re
import tempfile
import time
import urllib.request

URL = "https://sei.unb.br/sei/publicacoes/controlador_publicacoes.php?acao=publicacao_visualizar&id_documento={}&id_orgao_publicacao=0"
DOCUMENTOS = """6649697 6647591 6226893 6201030 6200233 6199693 6153956 6140621 6140187 6102702 6087943 6079483
6077390 6077176 6066527 6066504 6012338 6012262 6012188 5997566 5882464 5858055 5858120 5858154 5854182 5854076
5844892 5844872 5844839 5844823 5844811 5844758 5844741 5844722 5844689 5787224 5787209 5787185 5774474 5774453
5774429 5752578 5688636 5617288 5617315 5617346 5617364 5617292 5616877 5616439 5615633 5615154 5615096 5613076
5612354 5609567 5608709 5608479 5608259 5608168 5608111 5608702 5608722 5608756 5608792 5608818 5608852 5610794
5571759 5571810 5571844 5571864 5571887 5571915 5571936 5571952 5571972 5572001 5556122 5553648 5553246 5553023
5552729 5220211 5220443 5220565 5220604 5220644 5220102 5219805 5219592 5227800 5227930 5227953 4915202
4859361 4537610""".split()  # os dois últimos vieram da busca "incorporação doados" (143 publicações, 2018 a 2021)

CPF = re.compile(r"(CPF|CNPJ)\s*(?:n[º°o.]*)?\s*:?\s*[\dX]{2,3}[.\dX/-]{8,16}", re.I)
CPF_SOLTO = re.compile(r"\b[\dX]{3}\.[\dX]{3}\.[\dX]{3}-[\dX]{2}\b")
PASSAPORTE = re.compile(r",?\s*(?:Passaporte|RG|RNE)\s*(?:n[º°o.]*)?\s*:?\s*[\w.-]*\d[\w.-]*", re.I)


class Tabela(html.parser.HTMLParser):
    """Texto corrido do documento e linhas de tabela (células de td)."""

    def __init__(self):
        super().__init__()
        self.linhas, self.texto = [], []
        self._linha, self._celula = None, None

    def handle_starttag(self, tag, attrs):
        if tag == "tr":
            self._linha = []
        elif tag == "td" and self._linha is not None:
            self._celula = []

    def handle_endtag(self, tag):
        if tag == "td" and self._celula is not None:
            self._linha.append(" ".join("".join(self._celula).split()))
            self._celula = None
        elif tag == "tr" and self._linha is not None:
            self.linhas.append(self._linha)
            self._linha = None

    def handle_data(self, data):
        self.texto.append(data)
        if self._celula is not None:
            self._celula.append(data)


def sem_cpf(s):
    """Retira CPF, CNPJ, passaporte e RG."""
    return PASSAPORTE.sub("", CPF_SOLTO.sub("[omitido]", CPF.sub(r"\1 [omitido]", s)))


def valor(s):
    s = s.replace("R$", "").strip()
    try:
        return float(s.replace(".", "").replace(",", "."))
    except ValueError:
        return None


def baixar(doc, cache):
    arq = os.path.join(cache, doc + ".html")
    if os.path.exists(arq):
        return open(arq, "rb").read(), False
    req = urllib.request.Request(URL.format(doc), headers={"User-Agent": "Mozilla/5.0 (pesquisa academica)"})
    bruto = urllib.request.urlopen(req, timeout=60).read()
    os.makedirs(cache, exist_ok=True)
    open(arq, "wb").write(bruto)
    return bruto, True


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--saida", default=os.path.join("dados", "atos_incorporacao_bao.csv"))
    ap.add_argument("--cache", default=os.path.join(tempfile.gettempdir(), "cultiva_bao_cache"),
                    help="pasta das páginas originais, fora do repositório porque trazem CPF")
    ap.add_argument("--documentos", help="arquivo com outros id_documento (um por linha ou separados por espaço)")
    a = ap.parse_args()
    docs = open(a.documentos).read().split() if a.documentos else DOCUMENTOS
    linhas = []
    for doc in docs:
        bruto, novo = baixar(doc, a.cache)
        p = Tabela()
        p.feed(bruto.decode("iso-8859-1"))
        texto = sem_cpf(" ".join("".join(p.texto).split()))
        ato = re.search(r"\bATO\s+D[AO]\s+(?:(?!ATO\s+DA\s+REITORIA).){0,110}?\bN\s*[º°o.]*\s*\.?\s*\d+\s*/\s*\d{4}", texto, re.I)
        protocolo = re.search(r"SEI/UnB\s*-\s*(\d+)\s*-", texto)
        pub = re.search(r"Boletim de Atos Oficiais da UnB em (\d{2}/\d{2}/\d{4})", texto)
        doador = re.search(r"doad[oa]s?\s+(?:pel[oa]s?|por)\s+(.{3,160}?)(?:,\s*CPF|\s+CPF|,\s*CNPJ|\s+CNPJ|,?\s+para a Universidade|,?\s+à Universidade)", texto, re.I)
        itens = [l for l in p.linhas if len(l) >= 3 and re.fullmatch(r"\d{5,12}", l[0])]
        for l in itens:
            linhas.append({
                "ato": " ".join(ato.group(0).split()) if ato else "",
                "data_publicacao": pub.group(1) if pub else "",
                "protocolo_sei": protocolo.group(1) if protocolo else "",
                "id_documento": doc,
                "url": URL.format(doc),
                "doador": " ".join(doador.group(1).split()) if doador else "",
                "tombamento": l[0],
                "especificacao": sem_cpf(l[1]),
                "valor": valor(l[2]),
            })
        if novo:
            time.sleep(1)
    os.makedirs(os.path.dirname(a.saida) or ".", exist_ok=True)
    with open(a.saida, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(linhas[0].keys()))
        w.writeheader()
        w.writerows(linhas)
    print("Atos: {} | bens: {} | sem doador: {} | sem data: {}".format(
        len({l["id_documento"] for l in linhas}), len(linhas),
        sum(1 for l in linhas if not l["doador"]), sum(1 for l in linhas if not l["data_publicacao"])))


if __name__ == "__main__":
    main()
