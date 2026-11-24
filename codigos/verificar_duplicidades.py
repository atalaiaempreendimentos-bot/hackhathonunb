#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verificação de registros duplicados (Regras, itens 7(g) e 15) no Acervo Digital da CAL.

Lê   dados/inventario.csv, dados/metadados_completos.csv, acervo_1565/fotos_publicadas.csv e as fotos
Gera dados/verificacao_duplicidades.csv          (um registro por linha, com grupo e classificação)
     dados/verificacao_duplicidades_resumo.csv   (contagens por critério)
     resultados/verificacao_duplicidades.md      (método, resultados e interpretação)

Critérios, do mais forte ao mais fraco:
  1. Identificador repetido: ID do Tainacan, URL do registro, número de registro da CAL (CAL.xxxx,
     CE.xxx) ou código patrimonial. Um mesmo identificador em dois registros é duplicidade.
  2. Memória Institucional: mesmo nome de evento, mesmas datas e ano. É provável duplicidade quando
     artista e local coincidem e as descrições são quase iguais (semelhança >= 0,8); caso contrário,
     são registros distintos do mesmo evento (por exemplo, exposições coletivas, um registro por artista).
  3. Acervo, imagem idêntica (mesmo arquivo, byte a byte) em registros com números diferentes:
     a conferir; pode ser foto de conjunto (arco e flecha, par de colheres) ou foto copiada por engano.
  4. Acervo, descrição idêntica (título, autoria, técnica, dimensões e tiragem, com dimensões
     preenchidas) em registros com números diferentes: a conferir; pode ser série de objetos iguais.
  5. Acervo, mesmo título e autoria com números diferentes: homônimos, tratados como objetos distintos.
A triagem anterior do extrator (título, autoria e dimensões, mesmo vazias) indicava 427 registros;
esta verificação a substitui no indicador do item 15.
"""
import csv
import difflib
import hashlib
import os
import re
import unicodedata
from collections import defaultdict

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
DADOS = os.path.join(RAIZ, "dados")

PROV, CONF, DIST, HOM = ("Provável duplicidade", "A conferir", "Registros distintos (mesmo evento)",
                         "Homônimos (objetos distintos)")


def n(t):
    t = unicodedata.normalize("NFKD", str(t or ""))
    t = "".join(c for c in t if not unicodedata.combining(c)).lower().strip()
    return "" if t in ("false", "") else re.sub(r"\s+", " ", t)


def main():
    inv = {r["id_registro"]: r for r in csv.DictReader(open(os.path.join(DADOS, "inventario.csv"), encoding="utf-8-sig"))}
    meta = {r["id_registro"]: r for r in csv.DictReader(open(os.path.join(DADOS, "metadados_completos.csv"), encoding="utf-8-sig"))}
    arq_f = os.path.join(RAIZ, "acervo_1565", "fotos_publicadas.csv")
    fotos = {r["id"]: r for r in csv.DictReader(open(arq_f, encoding="utf-8-sig"))} if os.path.exists(arq_f) else {}
    tit = lambda m: m.get("Título") or m.get("Denominação") or m.get("titulo_item") or ""
    aut = lambda m: m.get("Autoria") or m.get("Grupo indígena") or m.get("Artista") or ""
    linhas, resumo, grupo_n = [], [], [0]

    def registra(criterio, classe, ids, obs):
        grupo_n[0] += 1
        for i in sorted(ids, key=int):
            m, l = meta.get(i, {}), inv.get(i, {})
            linhas.append({"grupo": grupo_n[0], "criterio": criterio, "classificacao": classe, "id_registro": i,
                           "colecao": l.get("colecao", ""), "numero_registro": m.get("Número de Registro", "") if m.get("Número de Registro") != "False" else "",
                           "titulo": tit(m), "autoria_ou_grupo": aut(m) if aut(m) != "False" else "",
                           "tecnica": m.get("Material/Técnica/Suporte", ""), "dimensoes": m.get("Dimensões", ""),
                           "tiragem": m.get("Tiragem", ""), "data_evento_ou_aquisicao": " a ".join(x for x in (m.get("Início", ""), m.get("Término", "")) if x) or m.get("Data de aquisição", ""),
                           "situacao": m.get("Situação", ""), "url_registro": l.get("url_registro", ""), "observacao": obs})

    def grupos(ids, chave):
        d = defaultdict(list)
        for i in ids:
            k = chave(meta.get(i, {}), inv.get(i, {}))
            if k:
                d[k].append(i)
        return [v for v in d.values() if len(v) > 1]

    todos = list(inv)
    acervo = [i for i in todos if inv[i]["colecao"] == "Acervo"]
    memoria = [i for i in todos if inv[i]["colecao"] == "Memória Institucional"]

    # 1. identificadores
    ident = {
        "ID do Tainacan": grupos(todos, lambda m, l: l.get("id_registro")),
        "URL do registro": grupos(todos, lambda m, l: l.get("url_registro")),
        "Número de registro da CAL": grupos(acervo, lambda m, l: n(m.get("Número de Registro"))),
        "Código patrimonial": grupos(todos, lambda m, l: n(m.get("Código patrimonial"))),
    }
    for crit, gs in ident.items():
        for g in gs:
            registra("Identificador repetido: " + crit, PROV, g, "Mesmo identificador em registros diferentes.")
        resumo.append(("Identificador repetido: " + crit, len(gs), sum(len(g) for g in gs)))

    # 2. eventos da Memória Institucional
    prov_ev = dist_ev = 0
    for g in grupos(memoria, lambda m, l: (n(m.get("Nome do evento") or m.get("titulo_item")), n(m.get("Início")),
                                           n(m.get("Término")), n(m.get("Ano"))) if n(m.get("Nome do evento") or m.get("titulo_item")) else None):
        a, b = meta[g[0]], meta[g[1]]
        sim = difflib.SequenceMatcher(None, n(a.get("Descrição do evento")), n(b.get("Descrição do evento"))).ratio()
        iguais = all(n(meta[x].get("Artista")) == n(a.get("Artista")) and n(meta[x].get("Local")) == n(a.get("Local")) for x in g)
        if iguais and sim >= 0.8:
            prov_ev += 1
            registra("Memória Institucional: mesmo evento e mesmas datas", PROV, g,
                     "Artista e local iguais; descrições com semelhança de {:.2f}. Um registro parece cópia do outro.".format(sim))
        else:
            dist_ev += 1
            registra("Memória Institucional: mesmo evento e mesmas datas", DIST, g,
                     "Artista, local ou descrição diferentes (semelhança {:.2f}): registros distintos do mesmo evento.".format(sim))
    resumo.append(("Memória Institucional: provável duplicidade (mesmo evento, datas, artista e local)", prov_ev, 2 * prov_ev))
    resumo.append(("Memória Institucional: registros distintos do mesmo evento", dist_ev, 2 * dist_ev))

    # 3. imagem idêntica no Acervo
    hashes = {}
    for i, f in fotos.items():
        p = os.path.join(RAIZ, "acervo_1565", f["arquivo"])
        if os.path.exists(p):
            hashes[i] = hashlib.md5(open(p, "rb").read()).hexdigest()
    conferir = set()
    gs = grupos([i for i in acervo if i in hashes], lambda m, l: hashes.get(l.get("id_registro")))
    for g in gs:
        conferir.update(g)
        registra("Acervo: imagem idêntica com números de registro diferentes", CONF, g,
                 "A mesma fotografia documenta registros diferentes: foto de conjunto ou cópia por engano. Conferir na CAL.")
    resumo.append(("Acervo: imagem idêntica com números de registro diferentes", len(gs), sum(len(g) for g in gs)))

    # 4. descrição idêntica no Acervo
    chave_desc = lambda m, l: (n(tit(m)), n(aut(m)), n(m.get("Material/Técnica/Suporte")), n(m.get("Dimensões")),
                               n(m.get("Tiragem"))) if n(tit(m)) and n(m.get("Dimensões")) else None
    gs = grupos(acervo, chave_desc)
    for g in gs:
        conferir.update(g)
        registra("Acervo: descrição idêntica com números de registro diferentes", CONF, g,
                 "Título, autoria, técnica, dimensões e tiragem iguais, números diferentes: série de objetos iguais ou "
                 "catalogação repetida. Conferir na CAL.")
    resumo.append(("Acervo: descrição idêntica com números de registro diferentes", len(gs), sum(len(g) for g in gs)))

    # 5. homônimos
    gs = grupos(acervo, lambda m, l: (n(tit(m)), n(aut(m))) if n(tit(m)) else None)
    hom = [g for g in gs if not set(g) <= conferir]
    for g in hom:
        registra("Acervo: mesmo título e autoria", HOM, g, "Números de registro diferentes: objetos distintos com o mesmo nome.")
    resumo.append(("Acervo: homônimos (mesmo título e autoria, números diferentes)", len(hom), sum(len(g) for g in hom)))

    prov_regs = len({l["id_registro"] for l in linhas if l["classificacao"] == PROV})
    resumo.append(("Registros em provável duplicidade", "", prov_regs))
    resumo.append(("Registros a conferir", "", len(conferir)))
    resumo.append(("Registros possivelmente duplicados (indicador do item 15)", "", prov_regs + len(conferir)))

    cols = ["grupo", "criterio", "classificacao", "id_registro", "colecao", "numero_registro", "titulo", "autoria_ou_grupo",
            "tecnica", "dimensoes", "tiragem", "data_evento_ou_aquisicao", "situacao", "url_registro", "observacao"]
    with open(os.path.join(DADOS, "verificacao_duplicidades.csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(linhas)
    with open(os.path.join(DADOS, "verificacao_duplicidades_resumo.csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f); w.writerow(["criterio", "grupos", "registros"]); w.writerows(resumo)

    fmt = lambda x: "{:,}".format(x).replace(",", ".") if isinstance(x, int) else x
    md = ["# Verificação de registros duplicados\n",
          "Universo: {} registros do Acervo Digital da CAL. Script: `codigos/verificar_duplicidades.py`; lista completa em "
          "`dados/verificacao_duplicidades.csv`.\n".format(fmt(len(todos))),
          "| Critério | Grupos | Registros |", "|---|---:|---:|"]
    md += ["| {} | {} | {} |".format(c, fmt(g), fmt(r)) for c, g, r in resumo]
    md.append("\n## Grupos de provável duplicidade e a conferir\n")
    for crit in sorted({l["criterio"] for l in linhas if l["classificacao"] in (PROV, CONF)}):
        md.append("### " + crit + "\n")
        md.append("| Grupo | ID | Nº de registro | Título | Autoria ou grupo | Dimensões | Classificação |")
        md.append("|---:|---:|---|---|---|---|---|")
        for l in linhas:
            if l["criterio"] == crit and l["classificacao"] in (PROV, CONF):
                md.append("| {} | [{}]({}) | {} | {} | {} | {} | {} |".format(l["grupo"], l["id_registro"], l["url_registro"], l["numero_registro"],
                          l["titulo"].replace("|", "/")[:60], l["autoria_ou_grupo"][:30], l["dimensoes"][:20], l["classificacao"]))
        md.append("")
    md.append("## Interpretação\n")
    md.append("- Nenhum identificador se repete: cada registro tem ID, URL e, no Acervo, número de registro próprios. Não há, portanto, "
              "duplicidade de catalogação pelo número de registro.")
    md.append("- Na Memória Institucional, registros com o mesmo evento e as mesmas datas só foram tratados como provável duplicidade "
              "quando artista, local e descrição também coincidem; nos demais casos, a CAL registrou um evento por artista ou por sessão.")
    md.append("- No Acervo, imagens idênticas e descrições idênticas com números diferentes não provam duplicidade: podem ser fotos de "
              "conjunto ou séries de objetos iguais. Esses registros ficam a conferir na CAL antes de qualquer baixa.")
    md.append("- Homônimos (por exemplo, várias peças chamadas \"Tear\" ou \"Gravura\" do mesmo artista) são objetos distintos.")
    md.append("- Para o reconhecimento contábil, a unidade é o registro do catálogo (NBC TSP 37, item 8): uma duplicidade confirmada "
              "deve ser excluída antes da mensuração, para não contar o mesmo bem duas vezes.")
    os.makedirs(os.path.join(RAIZ, "resultados"), exist_ok=True)
    with open(os.path.join(RAIZ, "resultados", "verificacao_duplicidades.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(md) + "\n")
    for c, g, r in resumo:
        print("  {}: grupos {} | registros {}".format(c, g, r))


if __name__ == "__main__":
    main()
