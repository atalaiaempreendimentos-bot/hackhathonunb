#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Identificação segundo o Inventário Nacional dos Bens Culturais Musealizados (INBCM).

Referência: INSTITUTO BRASILEIRO DE MUSEUS. Resolução Normativa Ibram nº 6, de 31 de agosto de 2021,
art. 7º, § 1º: 15 elementos de descrição do bem cultural de caráter museológico, 9 obrigatórios e 6
facultativos. A classificação (inciso VII) segue o "Thesaurus" para Acervos Museológicos ou outro
vocabulário controlado; aqui, o Tesauro de Objetos do Patrimônio Cultural nos Museus Brasileiros
(FERREZ, 2016), por meio de um vocabulário revisável em dados/vocabulario_tesauro.csv.

Uso: python3 codigos/identificacao_inbcm.py   (depois do extrator e, se houver, de cadastro_unb_relatorio.py)

Lê   dados/inventario.csv, dados/metadados_completos.csv, dados/vocabulario_tesauro.csv e, se existir,
     dados/valores_cadastro_unb.csv (tombamento confirmado, proposto como "outros números")
Gera dados/identificacao_inbcm.csv          um registro por linha: elementos presentes, ausentes e classificação
     dados/identificacao_inbcm_resumo.csv   preenchimento de cada elemento nos bens do acervo digital
     resultados/identificacao_inbcm.md

Só os bens são avaliados: os registros de evento da Memória Institucional não são bens de caráter
museológico (art. 6º, I) e ficam fora da contagem.
"""
import csv
import os
import re
import unicodedata
from collections import Counter

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
DADOS = os.path.join(RAIZ, "dados")
RES = os.path.join(RAIZ, "resultados")
EVENTO = "Registro de evento (não é bem)"

# (inciso, elemento, obrigatório?, campos do portal que o atendem, na ordem de preferência)
ELEMENTOS = [
    ("I", "Número de registro", True, ["Número de Registro"]),
    ("II", "Outros números", False, ["Código patrimonial"]),
    ("III", "Situação", True, ["Situação"]),
    ("IV", "Denominação", True, ["Denominação", "titulo_item"]),
    ("V", "Título", False, ["Título"]),
    ("VI", "Autor", True, ["Autoria", "Grupo indígena"]),
    ("VII", "Classificação", False, []),
    ("VIII", "Resumo descritivo", True, ["descricao_item", "Description", "Descrição"]),
    ("IX", "Dimensões", True, ["Dimensões"]),
    ("X", "Material/técnica", True, ["Material/Técnica/Suporte", "Material e técnica"]),
    ("XI", "Estado de conservação", True, ["Estado de conservação"]),
    ("XII", "Local de produção", False, ["Local de produção"]),
    ("XIII", "Data de produção", False, ["Data de produção"]),
    ("XIV", "Condições de reprodução", True, ["Condições de reprodução"]),
    ("XV", "Mídias relacionadas", False, ["url_foto", "url_foto_grande"]),
]
SITUACOES_RN = {"localizado", "nao localizado", "excluido"}  # art. 7º, § 1º, III, alíneas a a c


def norm(t):
    t = unicodedata.normalize("NFKD", str(t or ""))
    return re.sub(r"\s+", " ", "".join(c for c in t if not unicodedata.combining(c)).lower()).strip()


def valor(m, campos):
    for c in campos:
        v = (m.get(c) or "").strip()
        if v and v not in ("False", "false", "None"):
            return v
    return ""


def classificar(denominacao, vocab):
    d = re.sub(r"\(.*?\)|\d+", " ", norm(denominacao)).split()
    if not d:
        return None
    primeira = d[0]
    for v in vocab:
        if v["correspondencia"] == "exata" and " ".join(d) == v["chave"]:
            return v
    for v in vocab:
        if v["correspondencia"] == "prefixo" and primeira in (v["chave"], v["chave"] + "s"):
            return v
    return None


def main():
    ler = lambda n: list(csv.DictReader(open(os.path.join(DADOS, n), encoding="utf-8-sig")))
    inv = ler("inventario.csv")
    meta = {r["id_registro"]: r for r in ler("metadados_completos.csv")}
    vocab = ler("vocabulario_tesauro.csv")
    cad = {}
    if os.path.exists(os.path.join(DADOS, "valores_cadastro_unb.csv")):
        cad = {r["id_registro"]: r for r in ler("valores_cadastro_unb.csv") if r["confianca"] == "Confirmado"}

    saida, cont = [], Counter()
    bens = [r for r in inv if r["grupo_sugerido"] != EVENTO]
    for r in bens:
        i = r["id_registro"]
        m = dict(meta.get(i, {}))
        presentes, ausentes = [], []
        cls = classificar(valor(m, ["Denominação", "titulo_item"]), vocab)
        outros = valor(m, ["Código patrimonial"])
        outros_prop = ("tombamento " + cad[i]["tombamentos"]) if i in cad else ""
        sit = valor(m, ["Situação"])
        for inc, nome, obrig, campos in ELEMENTOS:
            v = valor(m, campos)
            if inc == "VII":
                v = ""  # o portal não tem o elemento; a classificação proposta fica em coluna própria
            if v:
                presentes.append(inc)
                cont[inc] += 1
            elif obrig:
                ausentes.append("{} {}".format(inc, nome.lower()))
        if cls:
            cont["VII_proposta"] += 1
        if outros_prop:
            cont["II_proposta"] += 1
        obrig_ok = sum(1 for inc, _, ob, _ in ELEMENTOS if ob and inc in presentes)
        saida.append({
            "id_registro": i, "colecao": r["colecao"], "grupo_sugerido": r["grupo_sugerido"],
            "numero_registro": valor(m, ["Número de Registro"]),
            "outros_numeros_portal": outros, "outros_numeros_proposto": outros_prop,
            "situacao_portal": sit,
            "situacao_conforme_rn": ("sim" if norm(sit) in SITUACOES_RN else "não: opção fora do art. 7º, § 1º, III" if sit else "ausente"),
            "denominacao": valor(m, ["Denominação", "titulo_item"]),
            "classificacao_termo": cls["termo_tesauro"] if cls else "",
            "classificacao_codigo": cls["codigo"] if cls else "",
            "classificacao_hierarquia": cls["hierarquia"] if cls else "",
            "classificacao_verificacao": cls["verificacao"] if cls else "a classificar: denominação sem termo correspondente no vocabulário",
            "obrigatorios_preenchidos": "{} de 9".format(obrig_ok),
            "obrigatorios_ausentes": "; ".join(ausentes),
            "facultativos_preenchidos": "{} de 6".format(sum(1 for inc, _, ob, _ in ELEMENTOS if not ob and inc in presentes)),
        })
    os.makedirs(DADOS, exist_ok=True)
    with open(os.path.join(DADOS, "identificacao_inbcm.csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(saida[0].keys())); w.writeheader(); w.writerows(saida)

    n = len(bens)
    pct = lambda k: round(100.0 * k / n, 1) if n else 0.0
    resumo = []
    for inc, nome, obrig, campos in ELEMENTOS:
        campo = " ou ".join(c for c in campos if not c.startswith(("url_", "titulo_item", "descricao_item"))) or "não existe no portal"
        if inc == "XV":
            campo = "imagem do item"
        resumo.append({"inciso": inc, "elemento": nome, "obrigatorio": "sim" if obrig else "não", "campo_portal": campo,
                       "bens_com_o_elemento": cont[inc], "percentual": pct(cont[inc]), "bens": n})
    resumo.append({"inciso": "II*", "elemento": "Outros números (proposta: tombamento confirmado no relatório de bens)",
                   "obrigatorio": "não", "campo_portal": "proposta da equipe", "bens_com_o_elemento": cont["II_proposta"],
                   "percentual": pct(cont["II_proposta"]), "bens": n})
    resumo.append({"inciso": "VII*", "elemento": "Classificação (proposta: Tesauro de Objetos, FERREZ, 2016)",
                   "obrigatorio": "não", "campo_portal": "proposta da equipe", "bens_com_o_elemento": cont["VII_proposta"],
                   "percentual": pct(cont["VII_proposta"]), "bens": n})
    completos = sum(1 for s in saida if s["obrigatorios_preenchidos"] == "9 de 9")
    resumo.append({"inciso": "", "elemento": "Bens com os 9 elementos obrigatórios", "obrigatorio": "", "campo_portal": "",
                   "bens_com_o_elemento": completos, "percentual": pct(completos), "bens": n})
    sit_fora = Counter(s["situacao_portal"] for s in saida if s["situacao_conforme_rn"].startswith("não"))
    with open(os.path.join(DADOS, "identificacao_inbcm_resumo.csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(resumo[0].keys())); w.writeheader(); w.writerows(resumo)

    cls_cnt = Counter(s["classificacao_hierarquia"].split(" > ")[0] if s["classificacao_hierarquia"] else "a classificar" for s in saida)
    md = ["# Identificação segundo o INBCM (Resolução Normativa Ibram nº 6/2021)\n",
          "Elementos de descrição do bem cultural de caráter museológico (art. 7º, § 1º) nos {} bens do acervo digital; "
          "os registros de evento não são bens (art. 6º, I). Script: `codigos/identificacao_inbcm.py`; registro a registro "
          "em `dados/identificacao_inbcm.csv`.\n".format("{:,}".format(n).replace(",", ".")),
          "| Inciso | Elemento | Obrigatório | Campo do portal | Bens com o elemento | % |", "|---|---|---|---|---:|---:|"]
    md += ["| {inciso} | {elemento} | {obrigatorio} | {campo_portal} | {q} | {p} |".format(
        p=str(x["percentual"]).replace(".", ","), q="{:,}".format(x["bens_com_o_elemento"]).replace(",", "."), **x) for x in resumo]
    md += ["\nSituações fora das opções da norma (localizado, não localizado, excluído): " +
           ("; ".join("{} ({})".format(k, v) for k, v in sit_fora.most_common()) or "nenhuma") + ".",
           "\nClassificação proposta por categoria do Tesauro: " +
           "; ".join("{} ({})".format(k, v) for k, v in sorted(cls_cnt.items())) + ".",
           "\nReferências: INSTITUTO BRASILEIRO DE MUSEUS. Resolução Normativa Ibram nº 6, de 31 de agosto de 2021. "
           "Diário Oficial da União, Brasília, DF, 2 set. 2021. FERREZ, Helena Dodd. Tesauro de Objetos do Patrimônio "
           "Cultural nos Museus Brasileiros. [S. l.], 2016."]
    os.makedirs(RES, exist_ok=True)
    open(os.path.join(RES, "identificacao_inbcm.md"), "w", encoding="utf-8").write("\n".join(md) + "\n")
    for x in resumo:
        print("  {} {}: {} ({}%)".format(x["inciso"], x["elemento"], x["bens_com_o_elemento"], x["percentual"]))
    print("  Situações fora da norma:", dict(sit_fora))
    print("  Classificação por categoria:", dict(cls_cnt))


if __name__ == "__main__":
    main()
