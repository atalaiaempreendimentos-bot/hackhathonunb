#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cadastro patrimonial dos bens localizados na CAL (Lista da CAL) e conciliação com o acervo digital.

Uso:
  python3 codigos/cadastro_patrimonial.py caminho/Lista_da_CAL.numbers   (ou um .csv exportado)

Gera (sem dados pessoais: nome de responsável e matrículas são descartados):
  dados/cadastro_patrimonial_cal.csv     um bem por linha: tombamento, bem de terceiro, denominação,
                                          estado, documento de ingresso, data de tombamento, termo, valor
  dados/conciliacao_patrimonial.csv      resumo da conciliação com o acervo digital
Regras do Hackathon: item 2 (divergências entre registros patrimoniais e bens localizados),
item 8 (evidência de controle) e item 9.1 (documentação patrimonial como evidência de mensuração).
"""
import csv, os, re, statistics, subprocess, sys, tempfile, zipfile

AQUI = os.path.dirname(os.path.abspath(__file__))
DADOS = os.path.join(os.path.dirname(AQUI), "dados")


def ler(caminho):
    if caminho.lower().endswith(".numbers"):
        tmp = tempfile.mkdtemp()
        zipfile.ZipFile(caminho).extractall(tmp)
        saida = os.path.join(tmp, "lista.csv")
        subprocess.run([sys.executable, "-I", os.path.join(AQUI, "ler_numbers.py"), tmp, saida], check=True)
        caminho = saida
    return list(csv.DictReader(open(caminho, encoding="utf-8-sig")))


def num(v):
    try:
        return float(str(v).replace(",", "."))
    except (TypeError, ValueError):
        return None


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    L = ler(sys.argv[1])
    linhas = []
    for l in L:
        tomb = l.get("Tombamento", "")
        m = re.search(r"\d+", tomb)
        doc = re.search(r"TIPO DE DOC\. INGRESSO: \d+ (.+?)(?:Empenho|$)", l.get("Observação", ""))
        origem = re.search(r"Origem: ([A-Z]+?)(?:Dados|\s|$)", l.get("Observação", ""))
        linhas.append({
            "tombamento": m.group(0) if m else tomb,
            "bem_de_terceiro": "sim" if "TERCEIRO" in tomb.upper() else "não",
            "denominacao": l.get("Denominação", ""),
            "codigo_material": l.get("Código Material", ""),
            "estado": l.get("Estado", ""),
            "status": l.get("Status", ""),
            "depreciavel": l.get("Depreciável/Amortizável", ""),
            "vida_util_meses": l.get("Vida Útil", ""),
            "documento_ingresso": doc.group(1).strip() if doc else "não informado",
            "origem_sipat": origem.group(1) if origem else "",
            "data_tombamento": l.get("Data Tombamento", ""),
            "_doc_custo": any((l.get(c) or "").strip() not in ("", "Não informado") for c in ("Nota Fiscal", "Empenho", "Fornecedor")),
            "termo": l.get("Termo", ""),
            "unidade_responsavel": l.get("Unidade Responsável", ""),
            "localidade": re.sub(r"_\d+$", "", l.get("Localidade", "")),
            "valor_registrado": l.get("Valor", ""),
        })
    os.makedirs(DADOS, exist_ok=True)
    with open(os.path.join(DADOS, "cadastro_patrimonial_cal.csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=[k for k in linhas[0] if not k.startswith("_")], extrasaction="ignore")
        w.writeheader(); w.writerows(linhas)

    # conciliação com o acervo digital: procura os tombamentos em qualquer campo do portal
    tombs = {x["tombamento"] for x in linhas}
    achados = set()
    arq_meta = os.path.join(DADOS, "metadados_completos.csv")
    if os.path.exists(arq_meta):
        for r in csv.DictReader(open(arq_meta, encoding="utf-8-sig")):
            for k, v in r.items():
                if v and not k.startswith("url"):
                    for t in re.findall(r"\b0*(\d{5,7})\b", v):
                        if t in tombs:
                            achados.add(t)
    obras = [x for x in linhas if x["denominacao"] == "OBRA DE ARTE"]
    proprias = [x for x in obras if x["bem_de_terceiro"] == "não"]
    terceiros = [x for x in obras if x["bem_de_terceiro"] == "sim"]
    vp = [num(x["valor_registrado"]) for x in proprias if num(x["valor_registrado"]) is not None]
    vt = [num(x["valor_registrado"]) for x in terceiros if num(x["valor_registrado"]) is not None]
    portal_acervo = 0
    arq_inv = os.path.join(DADOS, "inventario.csv")
    if os.path.exists(arq_inv):
        portal_acervo = sum(1 for r in csv.DictReader(open(arq_inv, encoding="utf-8-sig")) if r["colecao"] == "Acervo")
    resumo = [
        ("Bens no cadastro patrimonial localizados na CAL", len(linhas), "Lista da CAL; termo {}".format(linhas[0]["termo"])),
        ("Obras de arte no cadastro", len(obras), "Código de material 5244000000001"),
        ("Obras de arte próprias (sem marca de bem de terceiro)", len(proprias), ""),
        ("Valor registrado das obras próprias (R$)", round(sum(vp), 2), "Soma da coluna Valor do cadastro"),
        ("Obras marcadas como bem de terceiro", len(terceiros), "Ausência de controle pela UnB: não reconhecer"),
        ("Valor registrado dos bens de terceiro (R$)", round(sum(vt), 2), ""),
        ("Mediana do valor registrado das obras próprias (R$)", round(statistics.median(vp), 2) if vp else 0, ""),
        ("Menor e maior valor registrado das obras próprias (R$)", "{} a {}".format(min(vp), max(vp)) if vp else "", ""),
        ("Outros bens no cadastro (não culturais)", len(linhas) - len(obras), "Ex.: mobiliário de arquivo"),
        ("Registros da coleção Acervo no portal", portal_acervo, "Acervo digital"),
        ("Tombamentos do cadastro encontrados no portal", len(achados), "Vínculo direto pelo número de tombamento"),
        ("Data de tombamento no sistema atual", linhas[0]["data_tombamento"], "Bens migrados do SIPAT"),
        ("Obras de arte marcadas como não depreciáveis", sum(1 for x in obras if x["depreciavel"].strip().lower() in ("não", "nao")),
         "Coerente com vida útil indefinida (NBC TSP 37, itens 52 e 53)"),
        ("Obras de arte com vida útil informada", sum(1 for x in obras if x["vida_util_meses"].strip().isdigit()), ""),
        ("Obras de arte com estado diferente de 'Em uso'", sum(1 for x in obras if x["estado"].strip() != "Em uso"),
         "; ".join(sorted({x["estado"] for x in obras if x["estado"].strip() != "Em uso"}))),
        ("Obras com nota fiscal, empenho ou fornecedor informados", sum(1 for x in obras if x["_doc_custo"]),
         "Documento de custo histórico (NBC TSP 38, item 6)"),
    ]
    with open(os.path.join(DADOS, "conciliacao_patrimonial.csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f); w.writerow(["indicador", "valor", "observacao"]); w.writerows(resumo)
    for r in resumo:
        print("  {}: {}".format(r[0], r[1]))


if __name__ == "__main__":
    main()
