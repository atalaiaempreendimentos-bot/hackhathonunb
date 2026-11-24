#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Etapa III do Hackathon CULTIVA UnB 2026: abordagem de mercado por comparáveis.

Lê   dados/comparaveis.csv            transações e estimativas de obras comparáveis, com fonte
     dados/inventario.csv             obras da CAL
Grava dados/evidencias_mensuracao.csv  (substitui só as linhas automáticas; preserva as manuais)
e roda codigos/mensuracao.py para atualizar dados/mensuracao.csv e o site.

Regras aplicadas (Regras do Hackathon, itens 9.1 a 9.4):
  - só entram comparáveis com fonte (URL) e do MESMO artista e da MESMA família de técnica
    (serigrafia, gravura em metal, litografia, xilogravura, desenho, pintura, escultura...);
  - preço arrematado (transação realizada) é distinto de estimativa ou oferta (item 9.2);
  - nível A: 3 ou mais transações realizadas e a obra da CAL com dimensões e tiragem conhecidas;
    nível B: 3 ou mais transações realizadas; nível C: 1 ou 2 transações, ou só estimativas/ofertas;
  - valor central = mediana das transações realizadas (ou ponto médio das estimativas, nível C);
    intervalo = menor e maior valor entre transações e estimativas (análise de incerteza, item 9.3);
  - moedas diferentes não são misturadas: converter antes, informando taxa e fonte (ex.: PTAX/BCB).

Colunas de dados/comparaveis.csv:
  artista, familia_tecnica, titulo_comparavel, tecnica_descrita, dimensoes, tiragem, ano_obra,
  data_evento, casa_leilao, tipo_preco (arrematado | estimativa | oferta), valor_baixo, valor_alto,
  valor_arrematado, moeda, inclui_premio (sim | não | não informado), url_fonte, observacao
"""
import csv
import os
import statistics
import sys
import unicodedata

AQUI = os.path.dirname(os.path.abspath(__file__))
DADOS = os.path.join(os.path.dirname(AQUI), "dados")
MARCA = "[auto: comparaveis.py]"
COLS_EVID = ["id_registro", "base_mensuracao", "tecnica", "valor_min", "valor_central", "valor_max",
             "moeda", "data_referencia", "tipo_evidencia", "nivel_evidencia", "fonte", "observacao"]

FAMILIAS = {
    "serigrafia": ["serigraf", "screenprint", "silk"],
    "gravura em metal": ["agua-forte", "agua forte", "agua-tinta", "gravura em metal", "talho-doce", "ponta-seca", "etching", "metal"],
    "litografia": ["litograf", "litogravura", "lithograph"],
    "xilogravura": ["xilograv", "woodcut"],
    "desenho": ["nanquim", "grafite", "lapis", "carvao", "desenho", "pastel", "aquarela", "guache"],
    "pintura": ["oleo", "acrilica", "tempera"],
    "escultura": ["escultura", "bronze", "madeira entalhada"],
}


def norm(t):
    t = unicodedata.normalize("NFKD", str(t or ""))
    return "".join(c for c in t if not unicodedata.combining(c)).lower().strip()


def familia_de(tecnica):
    t = norm(tecnica)
    for fam, chaves in FAMILIAS.items():
        if any(k in t for k in chaves):
            return fam
    return ""


def num(v):
    try:
        return float(str(v).replace(",", "."))
    except (TypeError, ValueError):
        return None


def main():
    arq_c = os.path.join(DADOS, "comparaveis.csv")
    if not os.path.exists(arq_c):
        sys.exit("dados/comparaveis.csv não encontrado.")
    comps = [c for c in csv.DictReader(open(arq_c, encoding="utf-8-sig")) if (c.get("url_fonte") or "").startswith("http")]
    inv = list(csv.DictReader(open(os.path.join(DADOS, "inventario.csv"), encoding="utf-8-sig")))

    # agrupa comparáveis por (artista, família)
    grupos = {}
    for c in comps:
        chave = (norm(c["artista"]), norm(c["familia_tecnica"]))
        grupos.setdefault(chave, []).append(c)

    novas, avisos = [], []
    for l in inv:
        fam = familia_de(" ".join([l.get("tecnica", ""), l.get("materiais", "")]))
        cs = grupos.get((norm(l.get("autoria_origem")), fam))
        if not fam or not cs:
            continue
        moedas = {(c.get("moeda") or "").upper() for c in cs}
        if len(moedas) != 1:
            avisos.append("Registro {}: comparáveis em moedas diferentes ({}); converta antes.".format(l["id_registro"], ", ".join(sorted(moedas))))
            continue
        moeda = moedas.pop()
        realizados = [num(c["valor_arrematado"]) for c in cs if c["tipo_preco"] == "arrematado" and num(c["valor_arrematado"]) is not None]
        baixos = [num(c["valor_baixo"]) for c in cs if num(c.get("valor_baixo")) is not None]
        altos = [num(c["valor_alto"]) for c in cs if num(c.get("valor_alto")) is not None]
        todos = realizados + baixos + altos
        if not todos:
            continue
        conhecidos = bool((l.get("dimensoes") or "").strip()) and bool((l.get("tiragem") or "").strip())
        if len(realizados) >= 3:
            nivel = "A" if conhecidos else "B"
        else:
            nivel = "C"
        if realizados:
            central = statistics.median(realizados)
        else:
            central = (min(baixos or todos) + max(altos or todos)) / 2.0
        datas = sorted(c["data_evento"] for c in cs if c.get("data_evento"))
        descr = "; ".join("{} ({}, {}, {}): {}{}".format(
            c["titulo_comparavel"] or "sem título", c["tecnica_descrita"] or c["familia_tecnica"], c["casa_leilao"],
            c["data_evento"], "arrematado {} {}".format(moeda, c["valor_arrematado"]) if c["tipo_preco"] == "arrematado" else c["tipo_preco"],
            ", estimativa {}-{}".format(c["valor_baixo"], c["valor_alto"]) if c.get("valor_baixo") else "") for c in cs)
        lacunas = [] if conhecidos else ["dimensões e tiragem da obra da CAL não informadas no portal"]
        if moeda != "BRL":
            lacunas.append("valores em {}; converter para BRL pela taxa da data de referência (ex.: PTAX/BCB), registrando a fonte".format(moeda))
        if any((c.get("inclui_premio") or "") == "não informado" for c in cs if c["tipo_preco"] == "arrematado"):
            lacunas.append("verificar se o preço arrematado inclui prêmio do comprador")
        obs = "{} Comparáveis: {}. Limitações: {}.".format(MARCA, descr, "; ".join(lacunas) if lacunas else "nenhuma registrada")
        novas.append({
            "id_registro": l["id_registro"],
            "base_mensuracao": "Valor justo (NBC TSP 38), na ausência de custo histórico",
            "tecnica": "Abordagem de mercado: {} transação(ões) realizada(s), {} comparável(is) no total".format(len(realizados), len(cs)),
            "valor_min": round(min(todos), 2), "valor_central": round(central, 2), "valor_max": round(max(todos), 2),
            "moeda": moeda, "data_referencia": datas[-1] if datas else "",
            "tipo_evidencia": "transacao" if realizados else "oferta",
            "nivel_evidencia": nivel,
            "fonte": " | ".join(sorted({c["url_fonte"] for c in cs})),
            "observacao": obs,
        })

    # preserva evidências manuais e substitui as automáticas
    arq_e = os.path.join(DADOS, "evidencias_mensuracao.csv")
    manuais = []
    if os.path.exists(arq_e):
        manuais = [e for e in csv.DictReader(open(arq_e, encoding="utf-8-sig")) if not (e.get("observacao") or "").startswith(MARCA)]
    ids_manuais = {e["id_registro"] for e in manuais}
    novas = [n for n in novas if n["id_registro"] not in ids_manuais]
    with open(arq_e, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLS_EVID)
        w.writeheader()
        w.writerows(manuais + novas)
    print("Comparáveis válidos: {} | obras com evidência automática: {} | evidências manuais preservadas: {}".format(len(comps), len(novas), len(manuais)))
    for a in avisos:
        print("AVISO: " + a)

    sys.path.insert(0, AQUI)
    import mensuracao
    mensuracao.main()


if __name__ == "__main__":
    main()
