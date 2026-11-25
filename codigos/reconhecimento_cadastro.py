#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Etapa II aplicada ao cadastro patrimonial da UnB: quais bens tombados da CAL são passíveis de reconhecimento.

Lê   dados/cadastro_unb_sanitizado.csv (relatório de bens da UnB sem nomes e matrículas; gerado por
     cadastro_unb_relatorio.py e mantido fora do repositório público) e dados/cadastro_patrimonial_cal.csv
     (Lista da CAL, gerada por cadastro_patrimonial.py, também fora do repositório).
Gera dados/reconhecimento_cadastro_resumo.csv (agregados por camada, publicado) e
     dados/reconhecimento_cadastro.csv (bem a bem, fora do repositório público até a autorização de divulgação).

Universo: bens das localidades da CAL (códigos 110107_ e 11010702_) e bens tombados depois de 2021 com
denominação descritiva (subgrupo dos bens recentes). Fundamento no Parecer de Reconhecimento dos Ativos da CAL v1:
  A1 doações de 2024 a 2026, com termo ou processo e valor individual: reconhecimento sustentado (custo atribuído,
     NBC TSP 37, item 12; NBC TSP 38, item 10);
  A2 obras próprias da Lista da CAL (doações de 2019 e 2020 por ato de ingresso): reconhecimento sustentado;
  A3 outros bens com valor registrado, migrados do SIPAT sem data de ingresso: pendente de verificação da base do
     valor (NBC TSP 37, item 87(a), na aplicação inicial);
  B  bens tombados por R$ 0,01: custo simbólico não é mensuração (NBC TSP 37, item 13); não reconhecimento pelo item 7;
  D  bens de terceiros (Lista da CAL) e bens baixados ou alienados: não satisfazem a definição de ativo da UnB.
Os valores são oficialmente registrados pela UnB, não estimativas da equipe (Regras, item 10).
"""
import csv
import os
import re
from collections import Counter

AQUI = os.path.dirname(os.path.abspath(__file__))
DADOS = os.path.join(os.path.dirname(AQUI), "dados")
LOCAL_CAL = re.compile(r"^(110107_|11010702_)")
SUST, NAO, PEND = "Reconhecimento sustentado pelas evidências", "Não reconhecimento fundamentado", "Pendente de verificação"

CAMADAS = [
    ("A1", "Doações de 2024 a 2026 (bens recentes)", SUST,
     "Termo de doação ou processo SEI, tombamento efetivado e valor individual registrado na incorporação",
     "Definição de ativo atendida (Estrutura Conceitual (R1), itens 5.6 a 5.13); custo atribuído na incorporação (NBC TSP 37, item 12; NBC TSP 38, item 10)",
     "NBC TSP 37, item 69; NBC TSP 38, itens 54 e 55; ressalva: confirmar no processo a base do valor",
     "IV. Reconhecido no balanço"),
    ("A2", "Lista da CAL: obras próprias doadas em 2019 e 2020", SUST,
     "Ato de ingresso (ATO DA DGM ou ATO DO DECANATO DE ADMINISTRAÇÃO), inventário de 2021 (termo 209/2021), sala 107 e valor individual",
     "Definição de ativo atendida; custo atribuído na incorporação (NBC TSP 37, item 12; NBC TSP 38, item 10)",
     "NBC TSP 37, item 69; NBC TSP 38, itens 54 e 55; ressalva: confirmar a base do valor nos atos (ato 217: 80 obras de R$ 5.000,00)",
     "IV. Reconhecido no balanço"),
    ("A3", "Outros bens com valor registrado", PEND,
     "Tombamento e ato de ingresso migrados do SIPAT, sem data de ingresso; valores, em geral, de até R$ 1.000,00 por obra",
     "Definição de ativo atendida; mensuração confiável não demonstrada (NBC TSP 37, item 6(b)); custo atribuído na aplicação inicial (item 87(a))",
     "Valor oficialmente registrado, com ressalva de base em revisão (Regras, item 10(g) e 10(h); NBC TSP 37, item 87(b))",
     "III. Definição atendida: base do valor a confirmar"),
    ("B", "Bens tombados por R$ 0,01", NAO,
     "Tombamento e ato de ingresso; custo simbólico",
     "Custo simbólico não é custo atribuído (NBC TSP 37, item 13); satisfaz a definição, mas não o item 6(b): não reconhecer (item 7)",
     "NBC TSP 37, item 77: dificuldades de mensuração e relevância dos itens",
     "III. Definição atendida, sem mensuração confiável: nota explicativa (NBC TSP 37, item 77)"),
    ("D", "Bens de terceiros e bens baixados", NAO,
     "Marcação de bem de terceiro na Lista da CAL; baixa ou alienação no relatório",
     "Sem controle pela UnB (Estrutura Conceitual (R1), itens 5.11 e 5.12)",
     "Restrição patrimonial: bens sob guarda, fora do ativo da UnB (Regras, item 10(i))",
     "II. Fora do ativo: sem controle da UnB"),
]


def main():
    arq_b, arq_l = os.path.join(DADOS, "cadastro_unb_sanitizado.csv"), os.path.join(DADOS, "cadastro_patrimonial_cal.csv")
    if not (os.path.exists(arq_b) and os.path.exists(arq_l)):
        print("  cadastro não disponível: mantido dados/reconhecimento_cadastro_resumo.csv da última execução")
        return
    lista = {r["tombamento"]: r for r in csv.DictReader(open(arq_l, encoding="utf-8-sig"))}
    bens = list(csv.DictReader(open(arq_b, encoding="utf-8-sig")))
    saida = []
    for b in bens:
        loc, dt = b.get("localidade") or "", b.get("data_tombamento") or ""
        recente = bool(dt) and not dt.endswith("2021")
        if not (LOCAL_CAL.match(loc) or recente):
            continue
        t = b["tombamento"]; v = float(b.get("valor") or 0); li = lista.get(t, {})
        if b.get("baixado") == "sim" or b.get("status") == "ALIENADO" or li.get("bem_de_terceiro") == "sim":
            cam = "D"
        elif recente:
            cam = "A1"
        elif v <= 0.01:
            cam = "B"
        elif li:
            cam = "A2"
        else:
            cam = "A3"
        c = next(x for x in CAMADAS if x[0] == cam)
        saida.append({"tombamento": t, "camada": cam, "classe_reconhecimento": c[2], "origem_sipat": b.get("origem_sipat", ""),
                      "ato_ingresso_lista": li.get("numero_ato_ingresso", ""), "documento_ingresso_lista": li.get("documento_ingresso", ""),
                      "data_tombamento": dt, "termo": b.get("termo", ""), "valor_registrado": round(v, 2),
                      "localidade": re.sub(r"^\d+_\d+ - ", "", loc) or "não informada", "status": b.get("status", ""),
                      "fundamento": c[4], "funil": c[6]})
    with open(os.path.join(DADOS, "reconhecimento_cadastro.csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(saida[0].keys())); w.writeheader(); w.writerows(saida)
    res = []
    for cam, desc, classe, evid, fund, div, fun in CAMADAS:
        s = [x for x in saida if x["camada"] == cam]
        vals = sorted(x["valor_registrado"] for x in s)
        faixa = "R$ {:,.2f} a R$ {:,.2f}".format(vals[0], vals[-1]).replace(",", "X").replace(".", ",").replace("X", ".") if vals else ""
        res.append({"camada": cam, "descricao": desc, "classe_reconhecimento": classe, "bens": len(s),
                    "valor_registrado_rs": round(sum(vals), 2), "faixa_de_valor": faixa,
                    "origens_sipat": "; ".join("{} {}".format(k or "(sem origem)", n) for k, n in Counter(x["origem_sipat"] for x in s).most_common(5)),
                    "evidencias": evid, "fundamento": fund, "divulgacao": div, "funil": fun})
    tot = {"camada": "Total", "descricao": "Bens das localidades da CAL e bens recentes", "classe_reconhecimento": "",
           "bens": len(saida), "valor_registrado_rs": round(sum(x["valor_registrado"] for x in saida), 2), "faixa_de_valor": "",
           "origens_sipat": "", "evidencias": "", "fundamento": "", "divulgacao": "", "funil": ""}
    with open(os.path.join(DADOS, "reconhecimento_cadastro_resumo.csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(tot.keys())); w.writeheader(); w.writerows(res + [tot])
    for r in res + [tot]:
        print("  {}: {} bens, R$ {:,.2f}".format(r["camada"], r["bens"], r["valor_registrado_rs"]))


if __name__ == "__main__":
    main()
