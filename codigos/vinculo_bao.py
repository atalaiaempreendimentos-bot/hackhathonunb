#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vínculo entre os registros do portal e os atos de incorporação publicados no BAO.

Lê  dados/inventario.csv e dados/atos_incorporacao_bao.csv
Grava dados/vinculo_bao.csv (um registro do portal por linha) e imprime o resumo.

Chave: nome do doador (procedência no portal; doador no ato), sem acentos e sem caixa, com
conferência da ordem das datas (doação no portal até 540 dias antes da publicação do ato). Os atos
de 2019 e 2020 especificam só "OBRA DE ARTE", sem título: o vínculo se apoia em doador, data e
quantidade, não em identificador, e por isso recebe o grau "forte", abaixo de "confirmado" (reservado
ao vínculo por identificador em codigos/cadastro_unb_relatorio.py).
Tipos de vínculo:
  - "1:1": o doador tem 1 obra no portal e 1 bem nos atos: tombamento e valor da obra;
  - "valor único": o doador tem N obras no portal e N bens, todos de mesmo valor: valor individual
    definido, tombamento a escolher entre os N do doador;
  - "grupo": N obras e N bens com valores diferentes: só o total do grupo é conhecido;
  - "contagem diferente": o número de obras no portal difere do de bens nos atos.
Valores abaixo de R$ 200,00 são marcados para a equipe decidir se são simbólicos.
"""
import csv
import collections
import datetime
import os
import re
import sys
import unicodedata

D = sys.argv[1] if len(sys.argv) > 1 else "dados"


def norm(s):
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    return " ".join(re.sub(r"[^a-z ]", " ", s).split())


def data(s):
    for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.datetime.strptime(s.strip(), fmt).date()
        except (ValueError, AttributeError):
            pass
    return None


# Grafias que a regra de nomes não alcança, conferidas pelo número de obras e pela data; a equipe deve
# confirmar no termo de doação. Chave: doador no ato; valor: procedência no portal.
APELIDOS = {
    "claudio felipe de oliveira creti": "claudio cretti",
    "luiz renato pera": "renato pera",
}


def mesmo_nome(a, b):
    """Igual, ou o nome mais curto (2 termos ou mais) contido no mais longo, com o mesmo primeiro nome."""
    if not a or not b:
        return False
    if a == b or APELIDOS.get(a) == b:
        return True
    ta, tb = a.split(), b.split()
    curto, longo = (ta, tb) if len(ta) <= len(tb) else (tb, ta)
    return len(curto) >= 2 and curto[0] == longo[0] and all(t in longo for t in curto)


inv = list(csv.DictReader(open(os.path.join(D, "inventario.csv"), encoding="utf-8-sig")))
atos = list(csv.DictReader(open(os.path.join(D, "atos_incorporacao_bao.csv"), encoding="utf-8-sig")))

doadores_ato = collections.defaultdict(list)
for b in atos:
    doadores_ato[norm(b["doador"])].append(b)

portal = collections.defaultdict(list)
for r in inv:
    if r.get("proveniencia", "").strip():
        portal[norm(r["proveniencia"])].append(r)

def na_janela(r, bens):
    """Doação no portal até 540 dias antes da publicação do ato. Com só o ano, ele deve ser o do ato
    ou o anterior; registro sem nenhuma data é aceito e marcado."""
    s = r.get("data_aquisicao_padronizada") or ""
    d = data(s)
    if d is not None:
        return any(0 <= (data(b["data_publicacao"]) - d).days <= 540 for b in bens)
    ano = re.match(r"(\d{4})", s)
    if ano:
        return any(0 <= data(b["data_publicacao"]).year - int(ano.group(1)) <= 1 for b in bens)
    return True


# cada doador dos atos vai para a procedência exata do portal; sem ela, para o apelido; sem ele, para
# as procedências que contêm o nome
destino = {}
for nd in doadores_ato:
    if nd in portal:
        destino[nd] = [nd]
    elif APELIDOS.get(nd) in portal:
        destino[nd] = [APELIDOS[nd]]
    else:
        destino[nd] = [p for p in portal if mesmo_nome(nd, p)]

saida, usados = [], set()
for p, regs_p in portal.items():
    nds = [nd for nd in doadores_ato if p in destino[nd]]
    if not nds:
        continue
    bens = [b for nd in nds for b in doadores_ato[nd]]
    regs = [r for r in regs_p if na_janela(r, bens)]
    if not regs:
        continue
    usados.update(nds)
    valores = [float(b["valor"]) for b in bens]
    if len(regs) == 1 and len(bens) == 1:
        tipo = "1:1"
    elif len(regs) == len(bens) and len(set(valores)) == 1:
        tipo = "valor único"
    elif len(regs) == len(bens):
        tipo = "grupo"
    else:
        tipo = "contagem diferente"
    for r in regs:
        saida.append({
            "id_registro": r["id_registro"], "subcolecao": r["subcolecao"], "titulo": r["titulo"],
            "procedencia_portal": r["proveniencia"], "data_aquisicao_portal": r["data_aquisicao_padronizada"],
            "doador_ato": bens[0]["doador"], "atos": " | ".join(sorted({b["ato"] or b["id_documento"] for b in bens})),
            "data_publicacao": " | ".join(sorted({b["data_publicacao"] for b in bens})),
            "tipo_vinculo": tipo,
            "confianca": ("parcial: quantidade diferente" if tipo == "contagem diferente" else
                          "forte (doador, data e quantidade); grafia do nome a confirmar" if any(nd != p for nd in nds) else
                          "forte (doador, data e quantidade)"),
            "obras_portal_doador": len(regs), "bens_atos_doador": len(bens),
            "tombamento": bens[0]["tombamento"] if tipo == "1:1" else " ".join(b["tombamento"] for b in bens),
            "valor_individual": valores[0] if tipo in ("1:1", "valor único") else "",
            "valor_grupo": sum(valores),
            "valor_baixo": "sim" if min(valores) < 200 else "",
            "observacao": "; ".join(x for x in [
                "sem data de aquisição no portal" if not (r.get("data_aquisicao_padronizada") or "").strip() else "",
                "grafia diferente do nome: confirmar no termo de doação" if any(nd != p for nd in nds) else ""] if x),
            "fonte": " | ".join(sorted({b["url"] for b in bens})),
        })

with open(os.path.join(D, "vinculo_bao.csv"), "w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(saida[0].keys()))
    w.writeheader()
    w.writerows(saida)

tri = [r for r in inv if r["subcolecao"] == "Triangular"]
lig = {s["id_registro"] for s in saida}
c = collections.Counter(s["tipo_vinculo"] for s in saida)
print("Registros do portal vinculados:", len(saida), dict(c))
print("  por subcoleção:", dict(collections.Counter(s["subcolecao"] for s in saida)))
print("  com valor individual:", sum(1 for s in saida if s["valor_individual"] != ""),
      "| soma dos valores individuais: R$ {:,.2f}".format(sum(float(s["valor_individual"]) for s in saida if s["valor_individual"] != "")))
print("  com valor abaixo de R$ 200:", sum(1 for s in saida if s["valor_baixo"]))
print("Triangular: {} registros; {} vinculados; {} sem vínculo".format(len(tri), sum(1 for r in tri if r["id_registro"] in lig), sum(1 for r in tri if r["id_registro"] not in lig)))
sem = [nd for nd in doadores_ato if nd not in usados]
print("Doadores dos atos sem obra no portal:", len(sem), "| bens:", sum(len(doadores_ato[nd]) for nd in sem),
      "| valor: R$ {:,.2f}".format(sum(float(b["valor"]) for nd in sem for b in doadores_ato[nd])))
print("Doadores dos atos com obra no portal:", len(usados), "| bens:", sum(len(doadores_ato[nd]) for nd in usados))
