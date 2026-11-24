#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vínculo entre o relatório de bens da UnB (obras de arte, código de material 5244000000001) e os
registros do Acervo Digital da CAL, para exibir o valor registrado de cada bem no site.

Uso: python3 codigos/cadastro_unb_relatorio.py relatorio_bens_UnB_Total.xlsx

Lê   o relatório (.xlsx, lido sem dependências externas), dados/inventario.csv e dados/metadados_completos.csv
Gera dados/valores_cadastro_unb.csv   (um registro do portal por linha: valor registrado e critério de vínculo)
     dados/cadastro_unb_resumo.csv    (totais por localidade e por origem, sem dados pessoais)
     resultados/conciliacao_cadastro_unb.md
     dados/cadastro_unb_sanitizado.csv (relatório sem nomes e matrículas; fica fora do repositório público)

Privacidade: nomes do responsável pela localidade e do detentor, lotação do detentor e o texto da
observação (que traz matrículas) são descartados; da observação aproveitam-se só o número de registro
do SIPAT e a sigla de origem.

Critérios de vínculo, do mais forte ao mais fraco:
  1. Identificador: o "Número de Registro" numérico do portal é igual ao tombamento ou ao número de
     registro do SIPAT de um bem do relatório. Quando o registro do SIPAT foi desmembrado em vários
     tombamentos, todos são listados e o valor é a soma.
  2. Procedência: a procedência informada no portal corresponde à sigla de origem do SIPAT (tabela
     PROCEDENCIA_ORIGEM, interpretação da equipe) e todos os bens dessa origem nas localidades da CAL
     têm o mesmo valor registrado. O valor do bem é então determinado sem estimativa; o vínculo é
     classificado como provável, e há ressalva quando o portal tem mais registros que o cadastro.
  3. Sem vínculo: o valor individual não é identificável; informa-se, quando houver, a faixa de valores
     do grupo de origem, que não é atribuída ao bem (Regras, item 9.4).
"""
import csv
import os
import re
import sys
import unicodedata
import zipfile
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
DADOS = os.path.join(RAIZ, "dados")
NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
LOCAL_CAL = re.compile(r"^(110107_|11010702_)")  # localidades da CAL no relatório

# Procedência no portal -> sigla de origem no SIPAT (interpretação da equipe; conferir com a Coordenação de Patrimônio)
PROCEDENCIA_ORIGEM = {
    "funai": "FUNAI", "embaixada de cuba": "EMCUBA", "embaixada do uruguai": "EMURU", "pnda": "PNDA",
    "governo de roraima": "GR", "embaixada do paraguai": "EMPAR", "embaixada do mexico": "EMEX",
    "embaixada do chile": "EMCHILE", "banco central": "BACEN", "banco central do equador": "EMEQUA",
    "embaixada do equador": "EMEQUA", "embaixada da venezuela": "EMVENEZ", "embaixada do panama": "EMPANA",
    "embaixada da bolivia": "EMBOL", "finatec": "FINATEC",
}


# Procedência institucional (sem sigla no relatório): o bem pode não estar tombado. As demais procedências são,
# em regra, nomes de pessoas; doações de pessoas físicas aparecem no relatório com a origem PESFIS.
INSTITUICAO = re.compile(r"\b(embaixada|governo|banco|fundac|instituto|iphan|funai|museu|universidade|ministerio|secretaria|"
                         r"prefeitura|cedoc|dex|fub|flaac|finatec|associac|centro|consulado)")


def norm(t):
    t = unicodedata.normalize("NFKD", str(t or ""))
    return re.sub(r"\s+", " ", "".join(c for c in t if not unicodedata.combining(c)).lower()).strip()


def ler_xlsx(caminho):
    """Lê a primeira planilha de um .xlsx com a biblioteca padrão (zipfile + xml)."""
    z = zipfile.ZipFile(caminho)
    comp = []
    if "xl/sharedStrings.xml" in z.namelist():
        for si in ET.fromstring(z.read("xl/sharedStrings.xml")).findall("m:si", NS):
            comp.append("".join(t.text or "" for t in si.iter("{%s}t" % NS["m"])))
    folhas = sorted(n for n in z.namelist() if re.match(r"xl/worksheets/sheet\d+\.xml$", n))
    linhas = []
    for row in ET.fromstring(z.read(folhas[0])).iter("{%s}row" % NS["m"]):
        lin = {}
        for c in row.findall("m:c", NS):
            col = re.match(r"[A-Z]+", c.get("r")).group(0)
            idx = 0
            for ch in col:
                idx = idx * 26 + ord(ch) - 64
            v = c.find("m:v", NS)
            if c.get("t") == "s" and v is not None:
                val = comp[int(v.text)]
            elif c.get("t") == "inlineStr":
                val = "".join(t.text or "" for t in c.iter("{%s}t" % NS["m"]))
            else:
                val = v.text if v is not None else ""
            lin[idx - 1] = val
        if lin:
            linhas.append([lin.get(i, "") for i in range(max(lin) + 1)])
    return linhas


def num(v):
    try:
        return float(str(v).replace(",", "."))
    except ValueError:
        return None


def brl(v):
    return "R$ " + "{:,.2f}".format(v).replace(",", "X").replace(".", ",").replace("X", ".")


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    linhas = ler_xlsx(sys.argv[1])
    ini = next(i for i, l in enumerate(linhas) if "Tombamento" in l and "Valor" in l)
    cab = linhas[ini]
    bens = []
    for l in linhas[ini + 1:]:
        d = dict(zip(cab, l + [""] * (len(cab) - len(l))))
        if not str(d.get("Tombamento", "")).strip():
            continue
        obs = str(d.get("Observação", ""))
        reg = re.search(r"Registro:\s*(\d+)", obs)
        org = re.search(r"Origem:\s*([A-Z]+?)Dados", obs)
        tomb = str(d["Tombamento"]).strip()
        bens.append({
            "tombamento": re.sub(r"\D", "", tomb.split(" ")[0]), "baixado": "sim" if "BAIXADO" in tomb.upper() else "não",
            "registro_sipat": reg.group(1) if reg else "", "origem_sipat": org.group(1) if org else "",
            "unidade_responsavel": d.get("Unidade Responsável", ""), "localidade": d.get("Localidade", ""),
            "data_tombamento": d.get("Data Tombamento", ""), "denominacao": d.get("Denominação", ""),
            "estado": d.get("Estado", ""), "status": d.get("Status", ""), "depreciavel": d.get("Depreciável/Amortizável", ""),
            "vida_util": d.get("Vida Útil", ""), "termo": d.get("Termo", ""), "valor": num(d.get("Valor", "")),
        })
    cols_b = list(bens[0].keys())
    with open(os.path.join(DADOS, "cadastro_unb_sanitizado.csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols_b); w.writeheader(); w.writerows(bens)

    cal = [b for b in bens if LOCAL_CAL.match(b["localidade"] or "")]
    por_chave = defaultdict(list)
    for b in bens:
        for k in {b["tombamento"].lstrip("0"), b["registro_sipat"].lstrip("0")}:
            if k:
                por_chave[k].append(b)
    grupo = defaultdict(list)
    for b in cal:
        grupo[b["origem_sipat"]].append(b)

    inv = list(csv.DictReader(open(os.path.join(DADOS, "inventario.csv"), encoding="utf-8-sig")))
    meta = {r["id_registro"]: r for r in csv.DictReader(open(os.path.join(DADOS, "metadados_completos.csv"), encoding="utf-8-sig"))}
    # 1ª passagem: vínculos por identificador (os tombamentos usados saem da capacidade dos grupos de origem)
    por_id, usados = {}, set()
    for r in inv:
        nr = (meta.get(r["id_registro"], {}).get("Número de Registro") or "").strip()
        if r["colecao"] == "Acervo" and re.fullmatch(r"\d{5,}", nr):
            ach = list({id(b): b for b in por_chave.get(nr.lstrip("0"), [])}.values())
            if ach:
                por_id[r["id_registro"]] = ach
                usados.update(id(b) for b in ach)
    portal_proc = Counter(norm(meta[r["id_registro"]].get("Procedência")) for r in inv
                          if r["colecao"] == "Acervo" and r["id_registro"] not in por_id)

    pesfis = grupo.get("PESFIS", [])
    vpes = [b["valor"] for b in pesfis if b["valor"] is not None]
    saida = []
    for r in inv:
        i = r["id_registro"]; m = meta.get(i, {})
        if r["colecao"] != "Acervo":
            continue
        nr = (m.get("Número de Registro") or "").strip()
        proc = norm(m.get("Procedência"))
        o = {"id_registro": i, "numero_registro_portal": nr, "procedencia_portal": m.get("Procedência", "") if m.get("Procedência") != "False" else "",
             "tombamentos": "", "origem_sipat": "", "localidade": "", "status_cadastro": "", "valor_registrado": "",
             "valor_exibicao": "", "criterio_vinculo": "", "confianca": "", "observacao": ""}
        achados = por_id.get(i, [])
        if achados:
            v = sum(b["valor"] or 0 for b in achados)
            o.update(tombamentos="; ".join(b["tombamento"] for b in achados), origem_sipat=achados[0]["origem_sipat"],
                     localidade=achados[0]["localidade"], status_cadastro=achados[0]["status"], valor_registrado=round(v, 2),
                     valor_exibicao=brl(v), criterio_vinculo="Identificador: número de registro do portal = tombamento ou registro SIPAT",
                     confianca="Confirmado")
            if len(achados) > 1:
                o["observacao"] = "Registro do SIPAT desmembrado em {} tombamentos de {} cada.".format(
                    len(achados), " e ".join(sorted({brl(b["valor"] or 0) for b in achados})))
        else:
            sig = PROCEDENCIA_ORIGEM.get(proc)
            g = grupo.get(sig, []) if sig else []
            vals = sorted({b["valor"] for b in g if b["valor"] is not None})
            if g and len(vals) == 1:
                np_, nc = portal_proc[proc], sum(1 for b in g if id(b) not in usados)
                o.update(origem_sipat=sig, localidade="localidades da CAL", valor_registrado=vals[0], valor_exibicao=brl(vals[0]),
                         criterio_vinculo="Procedência: todos os {} bens de origem {} na CAL têm o mesmo valor registrado".format(len(g), sig),
                         confianca="Provável")
                if np_ > nc:
                    o["observacao"] = ("O portal tem {} registros com essa procedência sem vínculo por identificador e o cadastro, {} "
                                       "tombamentos ainda não vinculados: ao menos {} desses registros não estão tombados, sem que se "
                                       "saiba quais.".format(np_, nc, np_ - nc))
            elif g:
                o.update(origem_sipat=sig, confianca="Sem vínculo",
                         criterio_vinculo="Procedência com valores variados no cadastro: valor individual não identificável",
                         observacao="Grupo de origem {} na CAL: {} tombamentos, de {} a {} (total {}); a faixa não é atribuída ao bem.".format(
                             sig, len(g), brl(vals[0]), brl(vals[-1]), brl(sum(b["valor"] or 0 for b in g))))
            else:
                o.update(confianca="Sem vínculo", criterio_vinculo="Sem identificador nem procedência correspondente no cadastro")
                if proc and not sig and INSTITUICAO.search(proc):
                    o["observacao"] = "Procedência institucional sem sigla correspondente no relatório de bens: o bem pode não estar tombado."
                elif proc and not sig:
                    o["observacao"] = ("Procedência sem sigla de origem no relatório. Doações de pessoas físicas aparecem no relatório "
                                       "com a origem PESFIS: {} bens nas localidades da CAL, de {} a {}. Sem identificador comum com "
                                       "o portal, o valor individual não é identificável.").format(
                        len(pesfis), brl(min(vpes)) if vpes else "?", brl(max(vpes)) if vpes else "?")
        saida.append(o)

    cols = list(saida[0].keys())
    with open(os.path.join(DADOS, "valores_cadastro_unb.csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(saida)

    # resumo (sem dados pessoais)
    res = [("Bens no relatório (obras de arte da UnB)", len(bens), round(sum(b["valor"] or 0 for b in bens), 2)),
           ("Bens nas localidades da CAL", len(cal), round(sum(b["valor"] or 0 for b in cal), 2)),
           ("Bens da CAL com valor de R$ 0,01", sum(1 for b in cal if b["valor"] == 0.01), round(sum(b["valor"] for b in cal if b["valor"] == 0.01), 2))]
    for loc, n_ in Counter(b["localidade"] for b in cal).most_common():
        res.append(("Localidade: " + loc, n_, round(sum(b["valor"] or 0 for b in cal if b["localidade"] == loc), 2)))
    for org, n_ in Counter(b["origem_sipat"] or "(sem origem)" for b in cal).most_common():
        vs = [b["valor"] or 0 for b in cal if (b["origem_sipat"] or "(sem origem)") == org]
        res.append(("Origem SIPAT na CAL: " + org, n_, round(sum(vs), 2)))
    conf = [s for s in saida if s["confianca"] == "Confirmado"]
    prov = [s for s in saida if s["confianca"] == "Provável"]
    res += [("Registros do Acervo com vínculo confirmado", len(conf), round(sum(s["valor_registrado"] for s in conf), 2)),
            ("Tombamentos vinculados por identificador", sum(len(s["tombamentos"].split("; ")) for s in conf), ""),
            ("Registros do Acervo com vínculo provável (procedência)", len(prov), round(sum(s["valor_registrado"] for s in prov), 2)),
            ("Registros do Acervo sem vínculo", len(saida) - len(conf) - len(prov), "")]
    with open(os.path.join(DADOS, "cadastro_unb_resumo.csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f); w.writerow(["indicador", "quantidade", "valor_registrado_rs"]); w.writerows(res)

    sem = Counter(s["procedencia_portal"] or "(não informada)" for s in saida if s["confianca"] == "Sem vínculo")
    md = ["# Conciliação com o relatório de bens da UnB (obras de arte)\n",
          "Fonte: relatório de bens da UnB, código de material 5244000000001 (obras de arte), fornecido pela professora da disciplina "
          "em 24/11/2026. Script: `codigos/cadastro_unb_relatorio.py`; vínculo por registro em `dados/valores_cadastro_unb.csv`. "
          "Nomes e matrículas do relatório foram descartados.\n",
          "| Indicador | Quantidade | Valor registrado |", "|---|---:|---:|"]
    md += ["| {} | {} | {} |".format(a, "{:,}".format(b).replace(",", "."), brl(c) if c != "" else "") for a, b, c in res]
    md += ["\n## Registros do Acervo sem vínculo, por procedência\n", "| Procedência no portal | Registros |", "|---|---:|"]
    md += ["| {} | {} |".format(k, v) for k, v in sem.most_common(15)]
    md += ["\n## Critérios\n",
           "1. **Confirmado:** o número de registro do portal (formato numérico) é igual ao tombamento ou ao registro do SIPAT de um bem do relatório.",
           "2. **Provável:** a procedência do portal corresponde à sigla de origem do SIPAT (correspondência interpretada pela equipe) e todos os bens "
           "dessa origem nas localidades da CAL têm o mesmo valor; o valor do bem fica determinado sem estimativa, mas o tombamento individual não é identificado.",
           "3. **Sem vínculo:** não há identificador comum e o valor varia dentro do grupo de origem, ou a procedência não aparece no relatório; nenhum valor é atribuído (Regras, item 9.4).",
           "\nO valor de R$ 0,01 registrado para a maior parte dos bens vinculados é simbólico: não representa custo histórico nem custo atribuído "
           "(NBC TSP 37, itens 12 e 13), e reforça a conclusão de que esses bens não têm mensuração confiável."]
    os.makedirs(os.path.join(RAIZ, "resultados"), exist_ok=True)
    with open(os.path.join(RAIZ, "resultados", "conciliacao_cadastro_unb.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(md) + "\n")
    for a, b, c in res:
        print("  {}: {} | {}".format(a, b, c))


if __name__ == "__main__":
    main()
