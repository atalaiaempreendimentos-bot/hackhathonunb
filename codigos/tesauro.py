# -*- coding: utf-8 -*-
"""
Classificação proposta pelo Tesauro de Objetos do Patrimônio Cultural nos Museus Brasileiros (FERREZ, 2016),
a partir da denominação do bem, com o vocabulário revisável dados/vocabulario_tesauro.csv.

Usado por extrair_acervo_cal.py (colunas classificacao_tesauro e categoria_tesauro do inventário) e por
identificacao_inbcm.py (inciso VII da Resolução Normativa Ibram nº 6/2021). A classificação é proposta da
equipe e fica fora do cálculo da completude cadastral, que mede apenas o que consta no portal.
"""
import csv
import os
import re
import unicodedata


def _norm(t):
    t = unicodedata.normalize("NFKD", str(t or ""))
    return re.sub(r"\s+", " ", "".join(c for c in t if not unicodedata.combining(c)).lower()).strip()


def carregar_vocabulario(caminho):
    if not caminho or not os.path.exists(caminho):
        return []
    with open(caminho, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def classificar(denominacao, vocab):
    """Devolve a linha do vocabulário que corresponde à denominação, ou None.

    Correspondência exata: a denominação normalizada é igual à chave. Correspondência por prefixo: a
    primeira palavra da denominação (no singular ou no plural com "s") é igual à chave.
    """
    d = re.sub(r"\(.*?\)|\d+", " ", _norm(denominacao)).split()
    if not d or not vocab:
        return None
    for v in vocab:
        if v["correspondencia"] == "exata" and " ".join(d) == v["chave"]:
            return v
    for v in vocab:
        if v["correspondencia"] == "prefixo" and d[0] in (v["chave"], v["chave"] + "s"):
            return v
    return None
