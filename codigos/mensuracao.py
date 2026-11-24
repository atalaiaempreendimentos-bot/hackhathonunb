#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Etapa III do Hackathon CULTIVA UnB 2026: modelo de mensuração aplicado a todos os registros.

Lê   dados/inventario.csv                (gerado por extrair_acervo_cal.py)
     dados/evidencias_mensuracao.csv     (preenchido pela equipe; opcional)
Gera dados/mensuracao.csv                (uma linha por registro, nenhuma linha sem situação)
     dados/mensuracao_resumo.csv         (indicadores de mensuração do item 15 das Regras)

Princípios (Regras do Hackathon, item 9):
  - separar a BASE de mensuração (custo histórico, valor justo, valor operacional corrente; NBC TSP 38)
    da TÉCNICA de estimativa (abordagem de mercado, abordagem de custo);
  - preço anunciado não é valor justo automático (item 9.2);
  - sem evidência suficiente, registra-se "sem mensuração monetária fundamentada", resultado
    tecnicamente válido quando justificado (item 9.4); nunca se inventa valor (itens 9.4 e 17.10);
  - objetos de comunidades tradicionais não são presumidos mercadorias (item 4.3).
O reconhecimento (existência, controle, potencial de serviços) segue a NBC TSP 37 / IPSAS 45 e a
Estrutura Conceitual; a mensuração, a NBC TSP 38 / IPSAS 46. Os parágrafos aplicáveis devem ser
conferidos pela equipe no texto das normas e citados no relatório.

Formato de dados/evidencias_mensuracao.csv (uma linha por registro com evidência):
  id_registro, base_mensuracao, tecnica, valor_min, valor_central, valor_max, moeda,
  data_referencia, tipo_evidencia, nivel_evidencia, fonte, observacao
  - tipo_evidencia: transacao (leilão/venda realizada), oferta (preço anunciado), avaliacao
    (laudo/avaliação especializada), custo (documento de custo), documento (registro patrimonial)
  - nivel_evidencia: A (transação de bem diretamente comparável), B (transações com ajustes),
    C (só ofertas, catálogos ou avaliações indiretas), D (insuficiente)
  - valores em número com ponto decimal (ex.: 12000.00); moeda ISO (BRL, USD...)
"""
import csv
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
DADOS = os.path.join(RAIZ, "dados")

COLS_EVID = ["id_registro", "base_mensuracao", "tecnica", "valor_min", "valor_central", "valor_max",
             "moeda", "data_referencia", "tipo_evidencia", "nivel_evidencia", "fonte", "observacao"]

COLS_SAIDA = ["id_registro", "colecao", "subcolecao", "grupo_sugerido", "titulo", "autoria_origem",
              "forma_aquisicao", "categoria_mensuracao", "base_mensuracao", "tecnica", "situacao",
              "nivel_evidencia", "valor_min", "valor_central", "valor_max", "moeda", "data_referencia",
              "tipo_evidencia", "fonte", "valor_exibicao", "nota_metodologica"]

SIT_FUND = "Mensuração fundamentada"
SIT_FAIXA = "Faixa indicativa"
SIT_PEND = "Pendente de evidência"
SIT_SEM = "Sem mensuração monetária fundamentada"
SIT_FORA = "Fora do escopo (a confirmar no reconhecimento)"
SIT_CLASS = "Pendente de classificação"

NORMAS = ("Reconhecimento: NBC TSP 37 / IPSAS 45 e Estrutura Conceitual. Bases de mensuração: "
          "NBC TSP 38 / IPSAS 46. Critérios do Hackathon: Regras, item 9.")


def num(v):
    try:
        return float(str(v).replace(",", "."))
    except (TypeError, ValueError):
        return None


def brl(v, moeda="BRL"):
    if v is None:
        return ""
    s = "{:,.2f}".format(v).replace(",", "X").replace(".", ",").replace("X", ".")
    if s.endswith(",00"):
        s = s[:-3]
    return ("R$ " if moeda in ("", "BRL") else moeda + " ") + s


def aquisicao_txt(forma):
    f = (forma or "").strip().lower()
    if f == "doação":
        return ("Ingresso por doação: não há custo histórico de aquisição; a base deve ser escolhida "
                "entre as alternativas da NBC TSP 38 e justificada.")
    if f == "transferência":
        return ("Ingresso por transferência: verificar se há valor contábil registrado na origem "
                "(documentação patrimonial) antes de adotar outra base.")
    return "Forma de aquisição não informada no portal: a base de mensuração depende dessa informação."


def classificar(l):
    """Categoria, base, técnica, situação e nota para um registro sem evidência monetária."""
    col, grupo = l.get("colecao", ""), l.get("grupo_sugerido", "")
    autoria = (l.get("autoria_origem") or "").strip()
    aq = aquisicao_txt(l.get("forma_aquisicao"))
    if col == "Memória Institucional":
        return ("Registro documental de atividade institucional",
                "Não aplicável até o reconhecimento",
                "Não aplicável",
                SIT_FORA,
                "Registro de evento, exposição ou atividade da CAL. Antes de mensurar, a matriz de "
                "reconhecimento deve concluir se o registro corresponde a um recurso controlado com "
                "potencial de serviços (NBC TSP 37 e Estrutura Conceitual; Regras, item 8).")
    if grupo == "Etnográfica":
        return ("Bem cultural de comunidade tradicional",
                "Não monetizado por padrão (proposta da equipe)",
                "Evidenciação qualitativa",
                SIT_SEM,
                "As Regras vedam presumir que objetos de comunidades tradicionais são mercadorias "
                "livremente negociáveis (item 4.3). Sem mercado ativo, custo documentado ou avaliação "
                "especializada, registra-se a impossibilidade de estimativa confiável, resultado válido "
                "quando justificado (item 9.4). " + aq)
    if col == "Mobiliário moderno da UnB":
        return ("Mobiliário de valor histórico",
                "Custo histórico, se houver registro patrimonial com valor; senão, base alternativa da NBC TSP 38",
                "Documentação patrimonial; abordagem de custo ou de mercado",
                SIT_PEND,
                "Consultar o registro patrimonial (código patrimonial) para obter valor de entrada. "
                "Sem esse dado, buscar evidência de mercado de peças comparáveis. " + aq)
    if grupo in ("Arte", "Arte contemporânea"):
        contemporanea = grupo == "Arte contemporânea" or l.get("flag_possivel_contemporanea") == "sim"
        cat = "Obra de arte contemporânea" if contemporanea else "Obra de arte"
        tecnica = ("Abordagem de mercado (transações comparáveis); abordagem de custo se não houver comparáveis"
                   if contemporanea else "Abordagem de mercado (transações comparáveis)")
        base = "Valor justo ou valor operacional corrente (NBC TSP 38), na ausência de custo histórico"
        falta = ("Autoria não identificada, o que dificulta encontrar comparáveis. "
                 if not autoria else "")
        return (cat, base, tecnica, SIT_PEND,
                falta + "Valor só será atribuído com evidência registrada: resultados de leilão ou vendas "
                "de obras comparáveis (mesmo artista, técnica, dimensões, tiragem), avaliações técnicas ou "
                "documentos de custo, ajustados pelos fatores do item 9.2 das Regras. Preços anunciados "
                "não são tratados como valor justo. " + aq)
    return ("Não classificado",
            "A definir após classificação",
            "A definir",
            SIT_CLASS,
            "A triagem automática não identificou o grupo (arte, arte contemporânea ou etnográfica). "
            "Classificar o registro antes de definir a base de mensuração. " + aq)


def main():
    inv = os.path.join(DADOS, "inventario.csv")
    if not os.path.exists(inv):
        sys.exit("dados/inventario.csv não encontrado. Rode antes codigos/extrair_acervo_cal.py.")
    linhas = list(csv.DictReader(open(inv, encoding="utf-8-sig")))

    arq_ev = os.path.join(DADOS, "evidencias_mensuracao.csv")
    if not os.path.exists(arq_ev):
        with open(arq_ev, "w", encoding="utf-8-sig", newline="") as f:
            csv.writer(f).writerow(COLS_EVID)
        print("Criado modelo vazio: dados/evidencias_mensuracao.csv")
    evid = {}
    for e in csv.DictReader(open(arq_ev, encoding="utf-8-sig")):
        if e.get("id_registro"):
            evid[e["id_registro"].strip()] = e

    saida, avisos = [], []
    for l in linhas:
        cat, base, tecnica, sit, nota = classificar(l)
        r = {k: l.get(k, "") for k in ("id_registro", "colecao", "subcolecao", "grupo_sugerido",
                                         "autoria_origem", "forma_aquisicao")}
        r["titulo"] = (l.get("titulo") or "").split(" | ")[0]
        r.update(categoria_mensuracao=cat, base_mensuracao=base, tecnica=tecnica, situacao=sit,
                 nivel_evidencia="D", valor_min="", valor_central="", valor_max="", moeda="",
                 data_referencia="", tipo_evidencia="", fonte="", valor_exibicao="")
        e = evid.get(str(l.get("id_registro")))
        if e:
            nivel = (e.get("nivel_evidencia") or "").strip().upper()
            vmin, vcen, vmax = num(e.get("valor_min")), num(e.get("valor_central")), num(e.get("valor_max"))
            moeda = (e.get("moeda") or "BRL").strip().upper()
            if not (e.get("fonte") or "").strip():
                avisos.append("Registro {}: evidência sem fonte, ignorada.".format(l.get("id_registro")))
                e = None
            elif nivel not in ("A", "B", "C", "D"):
                avisos.append("Registro {}: nível de evidência inválido, ignorado.".format(l.get("id_registro")))
                e = None
        if e:
            r.update(base_mensuracao=e.get("base_mensuracao") or base, tecnica=e.get("tecnica") or tecnica,
                     nivel_evidencia=nivel, moeda=moeda, data_referencia=e.get("data_referencia", ""),
                     tipo_evidencia=e.get("tipo_evidencia", ""), fonte=e.get("fonte", ""),
                     valor_min=vmin if vmin is not None else "", valor_central=vcen if vcen is not None else "",
                     valor_max=vmax if vmax is not None else "")
            if nivel in ("A", "B") and vcen is not None:
                r["situacao"] = SIT_FUND
                faixa = " (intervalo {} a {})".format(brl(vmin, moeda), brl(vmax, moeda)) if vmin is not None and vmax is not None else ""
                r["valor_exibicao"] = brl(vcen, moeda)
                nota = ("Base: {}. Técnica: {}. Evidência nível {} ({}), referência {}{}. Fonte: {}. {}"
                        .format(r["base_mensuracao"], r["tecnica"], nivel, r["tipo_evidencia"] or "não informado",
                                r["data_referencia"] or "sem data", faixa, r["fonte"], e.get("observacao", "")))
            elif nivel == "C" and (vmin is not None or vmax is not None or vcen is not None):
                r["situacao"] = SIT_FAIXA
                lo = vmin if vmin is not None else vcen
                hi = vmax if vmax is not None else vcen
                r["valor_exibicao"] = "{} a {}".format(brl(lo, moeda), brl(hi, moeda)) if lo != hi else brl(lo, moeda)
                nota = ("Faixa indicativa, não é valor justo: evidência nível C ({}), referência {}. "
                        "Fonte: {}. {}".format(r["tipo_evidencia"] or "não informado", r["data_referencia"] or "sem data",
                                               r["fonte"], e.get("observacao", "")))
            else:
                r["situacao"] = SIT_SEM
                nota = ("Evidência registrada é insuficiente para estimativa confiável (nível {}). Fonte: {}. {}"
                        .format(nivel, r["fonte"], e.get("observacao", "")))
        r["nota_metodologica"] = (nota.strip() + " " + NORMAS).strip()
        saida.append(r)

    with open(os.path.join(DADOS, "mensuracao.csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLS_SAIDA)
        w.writeheader()
        w.writerows(saida)

    # resumo (Regras, item 15)
    resumo = []
    for sit in (SIT_FUND, SIT_FAIXA, SIT_PEND, SIT_SEM, SIT_FORA, SIT_CLASS):
        resumo.append({"indicador": "Registros: " + sit, "valor": sum(1 for r in saida if r["situacao"] == sit), "observacao": ""})
    fund = [r for r in saida if r["situacao"] == SIT_FUND and r["valor_central"] != ""]
    por_base = {}
    for r in fund:
        chave = (r["base_mensuracao"], r["categoria_mensuracao"], r["moeda"] or "BRL")
        por_base[chave] = por_base.get(chave, 0.0) + float(r["valor_central"])
    if por_base:
        for (b, c, m), v in sorted(por_base.items()):
            resumo.append({"indicador": "Valor agregado estimado: {} | {}".format(c, b), "valor": round(v, 2),
                           "observacao": m + "; não representa o valor total do patrimônio cultural da CAL (Regras, item 15)."})
    else:
        resumo.append({"indicador": "Valor agregado estimado", "valor": 0,
                       "observacao": "Nenhuma mensuração fundamentada registrada até o momento."})
    with open(os.path.join(DADOS, "mensuracao_resumo.csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["indicador", "valor", "observacao"])
        w.writeheader()
        w.writerows(resumo)

    print("dados/mensuracao.csv: {} registros".format(len(saida)))
    for x in resumo:
        print("  {}: {}".format(x["indicador"], x["valor"]))
    for a in avisos:
        print("AVISO: " + a)


if __name__ == "__main__":
    main()
