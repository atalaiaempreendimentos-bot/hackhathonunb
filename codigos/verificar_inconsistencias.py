#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Inconsistências cadastrais dos bens do acervo digital (Regras, item 7(g)).

Uso: python3 codigos/verificar_inconsistencias.py   (depois do extrator)

Lê   dados/inventario.csv e dados/metadados_completos.csv
Gera dados/inconsistencias.csv          uma linha por registro e tipo de inconsistência
     dados/inconsistencias_resumo.csv   registros por tipo, com exemplo
     resultados/inconsistencias.md      relatório, com a heterogeneidade de formatos de datas e dimensões

Ausências de dados ficam no diagnóstico de completude (dados/diagnostico_qualidade.csv) e duplicidades na
verificação própria (dados/verificacao_duplicidades.csv). Aqui entram valores presentes, mas incoerentes
entre si, fora do padrão da própria coleção ou fora das opções do INBCM (Resolução Normativa Ibram nº 6/2021).
Nada é corrigido: o arquivo aponta o registro, o campo, o valor e o que conferir.
"""
import csv
import difflib
import os
import re
import unicodedata
from collections import Counter, defaultdict

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
DADOS = os.path.join(RAIZ, "dados")
RES = os.path.join(RAIZ, "resultados")
EVENTO = "Registro de evento (não é bem)"
SITUACOES_RN = {"localizado", "nao localizado", "excluido"}


def norm(t):
    t = unicodedata.normalize("NFKD", str(t or ""))
    return re.sub(r"\s+", " ", "".join(c for c in t if not unicodedata.combining(c)).lower()).strip()


def formato(v):
    """Forma do valor, com dígitos trocados por 9 e palavras por a (para contar padrões)."""
    return re.sub(r"\b(?!x\b)[a-zç]+\b", "a", re.sub(r"\d+([.,]\d+)?", "9", norm(v)))


def main():
    ler = lambda n: list(csv.DictReader(open(os.path.join(DADOS, n), encoding="utf-8-sig")))
    inv = [r for r in ler("inventario.csv") if r["grupo_sugerido"] != EVENTO]
    meta = {m["id_registro"]: m for m in ler("metadados_completos.csv")}
    linhas = []

    def add(r, tipo, campo, valor, obs):
        linhas.append({"id_registro": r["id_registro"], "colecao": r["colecao"], "grupo_sugerido": r["grupo_sugerido"],
                       "titulo": r["titulo"].split(" | ")[0], "tipo": tipo, "campo": campo, "valor": valor,
                       "o_que_conferir": obs, "url_registro": r["url_registro"]})

    # padrão de número de registro de cada subcoleção
    padroes = defaultdict(Counter)
    for r in inv:
        padroes[r["subcolecao"] or r["colecao"]][re.sub(r"\d", "n", r["outros_identificadores"].split(" | ")[0])] += 1

    for r in inv:
        m = meta.get(r["id_registro"], {})
        # datas
        if r["precisao_data_aquisicao"] == "ilegível":
            add(r, "Data de aquisição ilegível", "Data de aquisição", r["data_aquisicao"],
                "o campo traz texto que não é data; conferir se o valor pertence a outro campo (procedência, por exemplo)")
        elif r["precisao_data_aquisicao"] == "ano incerto":
            add(r, "Data de aquisição incerta", "Data de aquisição", r["data_aquisicao"],
                "o portal marca o ano com \"(?)\"; confirmar no processo de incorporação")
        if r["data_aquisicao"] and not r["forma_aquisicao"]:
            add(r, "Data de aquisição sem forma de aquisição", "Forma de aquisição", r["data_aquisicao"],
                "há data de ingresso, mas não a forma (doação, transferência, compra)")
        anos_aq = re.findall(r"\d{4}", r["data_aquisicao_padronizada"])
        anos_pr = re.findall(r"\d{4}", r["ano_periodo"])
        if anos_aq and anos_pr and int(anos_aq[0]) < int(anos_pr[0]):
            add(r, "Aquisição anterior à produção", "Data de aquisição e data de produção",
                "{} / {}".format(r["data_aquisicao"], r["ano_periodo"]), "a data de aquisição é anterior ao ano de produção")
        if r["ano_periodo"] and not re.search(r"\d{4}", r["ano_periodo"]):
            add(r, "Data de produção sem ano legível", "Data de produção", r["ano_periodo"], "informar ano ou período")
        # dimensões
        d = r["dimensoes"]
        if d and not re.search(r"\b(cm|mm|m|km|kg|g)\b|dura[cç][aã]o|min|seg|'", norm(d)):
            add(r, "Dimensões sem unidade de medida", "Dimensões", d, "informar a unidade (cm, mm, m) e a ordem dos eixos")
        elif d and re.search(r"\d\s*[aldc]\b", norm(d)):
            add(r, "Dimensões com convenção própria de eixos", "Dimensões", d,
                "as letras (a, l, d, c) não seguem a ordem altura x largura x profundidade do INBCM (inciso IX)")
        # imagem
        tem_img = bool(r["url_foto"] or r["url_foto_grande"])
        ci = (m.get("Com imagem?") or "").strip()
        if (ci == "Sim" and not tem_img) or (ci == "Não" and tem_img):
            add(r, "\"Com imagem?\" divergente da imagem publicada", "Com imagem?", ci,
                "o campo diz \"{}\", mas o registro {} imagem".format(ci, "tem" if tem_img else "não tem"))
        # situação
        if r["situacao"] and norm(r["situacao"]) not in SITUACOES_RN:
            add(r, "Situação fora das opções do INBCM", "Situação", r["situacao"],
                "a Resolução Normativa Ibram nº 6/2021 prevê localizado, não localizado ou excluído (art. 7º, § 1º, III)")
        # subcoleção
        if r["colecao"] == "Acervo" and (m.get("Coleção") or "").strip() == "False":
            add(r, "Subcoleção não informada", "Coleção", "False",
                "taxonomia vazia no portal; a triagem atribuiu a subcoleção provável (ver criterio_grupo)")
        # número de registro
        nr = r["outros_identificadores"].split(" | ")[0]
        if not nr:
            add(r, "Número de registro ausente", "Número de Registro", "",
                "elemento obrigatório do INBCM (inciso I); o item tem só o código patrimonial" if r["numero_patrimonio"] else
                "elemento obrigatório do INBCM (inciso I)")
        else:
            dominante, q = padroes[r["subcolecao"] or r["colecao"]].most_common(1)[0]
            if re.sub(r"\d", "n", nr) != dominante and q >= 10:
                add(r, "Número de registro fora do padrão da subcoleção", "Número de Registro", nr,
                    "a subcoleção usa o padrão {}; números só numéricos coincidem com tombamentos ou registros do SIPAT".format(dominante))

    # variantes de grafia na denominação
    den = defaultdict(list)
    for r in inv:
        den[r["titulo"].split(" | ")[0].strip().lower()].append(r)
    chaves = sorted(den)
    for i, a in enumerate(chaves):
        for b in chaves[i + 1:]:
            na, nb = norm(a), norm(b)
            if na == nb:
                tipo = "acento ou caixa"
            elif na.rstrip("s") == nb.rstrip("s"):
                tipo = "singular e plural"
            elif len(na) >= 8 and difflib.SequenceMatcher(None, na, nb).ratio() >= 0.92:
                tipo = "grafia próxima"
            else:
                continue
            for x, y in ((a, b), (b, a)):
                for r in den[x]:
                    add(r, "Denominação com variante de grafia", "Denominação", x,
                        "variante de \"{}\" ({}); padronizar o termo, de preferência pelo Tesauro".format(y, tipo))

    os.makedirs(DADOS, exist_ok=True)
    cols = ["id_registro", "colecao", "grupo_sugerido", "titulo", "tipo", "campo", "valor", "o_que_conferir", "url_registro"]
    with open(os.path.join(DADOS, "inconsistencias.csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(linhas)
    por_tipo = defaultdict(list)
    for x in linhas:
        por_tipo[x["tipo"]].append(x)
    resumo = [{"tipo": t, "registros": len({x["id_registro"] for x in ls}), "exemplo": "ID {}: {}".format(ls[0]["id_registro"], ls[0]["valor"])}
              for t, ls in sorted(por_tipo.items(), key=lambda kv: -len(kv[1]))]
    total = len({x["id_registro"] for x in linhas})
    resumo.append({"tipo": "Registros com ao menos uma inconsistência", "registros": total, "exemplo": ""})
    with open(os.path.join(DADOS, "inconsistencias_resumo.csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["tipo", "registros", "exemplo"]); w.writeheader(); w.writerows(resumo)

    fmt_aq = Counter(r["precisao_data_aquisicao"] or "não informada" for r in inv)
    fmt_pr = Counter(formato(r["ano_periodo"]) for r in inv if r["ano_periodo"])
    fmt_dm = Counter(formato(r["dimensoes"])[:30] for r in inv if r["dimensoes"])
    q = lambda v: "{:,}".format(v).replace(",", ".")
    md = ["# Inconsistências cadastrais dos bens do acervo digital\n",
          "Regras, item 7(g). Script: `codigos/verificar_inconsistencias.py`; registro a registro em `dados/inconsistencias.csv`. "
          "Ausências ficam no diagnóstico de completude e duplicidades na verificação própria; aqui entram valores presentes, "
          "mas incoerentes, fora do padrão da coleção ou fora das opções do INBCM. Nada foi corrigido.\n",
          "| Tipo | Registros | Exemplo |", "|---|---:|---|"]
    md += ["| {} | {} | {} |".format(x["tipo"], q(x["registros"]), x["exemplo"].replace("|", "/")) for x in resumo]
    md += ["\n## Heterogeneidade de formatos\n",
           "Data de aquisição, pela precisão da forma padronizada (`data_aquisicao_padronizada`): " +
           "; ".join("{} ({})".format(k, q(v)) for k, v in fmt_aq.most_common()) + ".",
           "\nData de produção, por formato (9 = dígitos): " + "; ".join("`{}` ({})".format(k, q(v)) for k, v in fmt_pr.most_common(6)) + ".",
           "\nDimensões, por formato (9 = número, a = palavra ou letra): " +
           "; ".join("`{}` ({})".format(k.replace("|", "/"), q(v)) for k, v in fmt_dm.most_common(8)) + "."]
    os.makedirs(RES, exist_ok=True)
    open(os.path.join(RES, "inconsistencias.md"), "w", encoding="utf-8").write("\n".join(md) + "\n")
    for x in resumo:
        print("  {}: {}".format(x["tipo"], x["registros"]))


if __name__ == "__main__":
    main()
