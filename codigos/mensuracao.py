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
Fundamentação conferida no texto publicado das normas (metodologia/fundamentacao_normativa.md):
  - doações e transferências são transações sem contraprestação: mensuração inicial pelo CUSTO
    ATRIBUÍDO (NBC TSP 37, itens 11 a 13; NBC TSP 38, itens 7, 10 e 12(b)), determinado por base de
    valor corrente;
  - o acervo é mantido por sua capacidade operacional (potencial de serviço), não financeira: a base
    de valor corrente é o VALOR CORRENTE OPERACIONAL (NBC TSP 37, item 27; NBC TSP 38, itens 6 e 23 a
    25), preço de entrada que inclui os custos necessários (prêmio do comprador, custos de transação);
  - técnicas (NBC TSP 38, itens 36 a 45): abordagem de mercado com comparáveis ajustados aos aspectos
    únicos da obra (itens 24, 32 e 42); abordagem de custo (itens 43 e 44) só onde existe substituto
    de utilidade comparável (mobiliário); abordagem de renda não se aplica (sem fluxos de caixa);
  - mensuração confiável (NBC TSP 37, item 6(b); Estrutura Conceitual, itens 6.7 e 6.8) = níveis A ou
    B; nível C é faixa indicativa, com incerteza elevada demais para reconhecimento;
  - mensuração subsequente proposta: modelo do custo histórico (NBC TSP 37, itens 24 e 26), vida útil
    indefinida sem depreciação (itens 52 e 53) e revisão anual de redução ao valor recuperável (56).

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
SIT_FORA = "Não aplicável (não é ativo)"
SIT_CLASS = "Pendente de classificação"
# Valor oficial que a UnB registrou no ato de incorporação publicado no Boletim de Atos Oficiais
# (codigos/vinculo_bao.py). Não é estimativa da equipe: fica fora do valor agregado estimado (Regras, itens 10 e 15).
SIT_REG = "Custo atribuído registrado no ato de incorporação"
# Grupo: o ato dá o valor de cada tombamento do doador, mas não diz qual tombamento é qual obra do portal.
SIT_REG_G = "Custo atribuído registrado no ato de incorporação, por grupo"
BASE_REG = ("Custo atribuído registrado pela UnB na incorporação da doação (NBC TSP 37, itens 12 e 13; aplicação "
            "inicial, item 87(a))")
TEC_REG = ("Valor do ato de incorporação publicado no Boletim de Atos Oficiais, fixado com a avaliação da comissão "
           "especial prevista para obras de arte (Instrução DAF nº 001/2018, arts. 4º, 19, V, e 21)")

NORMAS = ("Fundamento: NBC TSP 37, itens 6, 7, 11 a 13 e 27; NBC TSP 38, itens 6, 10, 23 a 25 e 36 a 45; "
          "Estrutura Conceitual (R1), itens 6.7 e 6.8; Regras, item 9.")
BASE_DOACAO = ("Custo atribuído pelo valor corrente operacional (NBC TSP 37, itens 12 e 27; NBC TSP 38, itens 10, "
               "12(b) e 23 a 25)")


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
        return ("Ingresso por doação, transação sem contraprestação: mensuração inicial pelo custo atribuído "
                "(NBC TSP 37, item 12; NBC TSP 38, itens 10 e 12(b)).")
    if f == "transferência":
        return ("Ingresso por transferência sem custo: mensuração inicial pelo custo atribuído (NBC TSP 37, "
                "item 12; NBC TSP 38, item 12(b)); verificar antes o valor registrado na origem.")
    if f == "compra":
        return "Ingresso por compra: custo histórico, se houver documento de custo (NBC TSP 37, item 11)."
    return ("Forma de aquisição não informada no portal: sem ela não se define entre custo histórico "
            "(item 11) e custo atribuído (item 12) da NBC TSP 37.")


def classificar(l):
    """Categoria, base, técnica, situação e nota para um registro sem evidência monetária."""
    col, grupo = l.get("colecao", ""), l.get("grupo_sugerido", "")
    autoria = (l.get("autoria_origem") or "").strip()
    aq = aquisicao_txt(l.get("forma_aquisicao"))
    if col == "Memória Institucional":
        return ("Registro documental de atividade institucional",
                "Não aplicável: o registro não satisfaz a definição de ativo",
                "Não aplicável",
                SIT_FORA,
                "Registro de evento, exposição ou atividade da CAL, sem recurso individualizado controlado "
                "(Estrutura Conceitual (R1), item 5.6). Não há o que mensurar.")
    if grupo == "Etnográfica":
        return ("Bem cultural de comunidade tradicional",
                "Custo atribuído pelo valor corrente operacional, se houver dados; não monetizado por padrão",
                "Nenhuma técnica aplicável: evidenciação qualitativa (NBC TSP 37, item 77)",
                SIT_SEM,
                "A abordagem de mercado (NBC TSP 38, item 42) presumiria que o objeto é mercadoria, o que as "
                "Regras vedam (item 4.3); a abordagem de custo (itens 43 e 44) exige substituto de utilidade "
                "comparável, inexistente para objeto único de comunidade tradicional; a de renda (item 45) não "
                "se aplica. Sem mensuração confiável, o bem não é reconhecido e é divulgado em nota (NBC TSP 37, "
                "itens 7 e 77; Regras, item 9.4). " + aq)
    if col == "Mobiliário moderno da UnB":
        return ("Mobiliário de valor histórico",
                "Custo histórico, se houver documento de custo (NBC TSP 37, item 11); senão, custo atribuído pelo valor corrente operacional",
                "Abordagem de custo: custo de reposição de peça de utilidade comparável, ajustado por obsolescência "
                "(NBC TSP 38, itens 43 e 44); abordagem de mercado para peças de design com transações",
                SIT_PEND,
                "Consultar o registro patrimonial (código patrimonial) para obter valor de entrada. "
                "Sem esse dado, aplicar a abordagem de custo ou buscar transações de peças comparáveis. " + aq)
    if grupo in ("Arte", "Arte contemporânea"):
        contemporanea = grupo == "Arte contemporânea" or l.get("flag_possivel_contemporanea") == "sim"
        cat = "Obra de arte contemporânea" if contemporanea else "Obra de arte"
        tecnica = ("Abordagem de mercado: transações de obras comparáveis ajustadas aos aspectos únicos da obra "
                   "(NBC TSP 38, itens 24, 32 e 42); abordagem de custo só se houver substituto de utilidade "
                   "comparável, como em tiragens reproduzíveis (itens 43 e 44)"
                   if contemporanea else
                   "Abordagem de mercado: transações de obras comparáveis ajustadas aos aspectos únicos da obra "
                   "(NBC TSP 38, itens 24, 32 e 42)")
        base = BASE_DOACAO
        falta = ("Autoria não identificada, o que dificulta encontrar comparáveis. "
                 if not autoria else "")
        return (cat, base, tecnica, SIT_PEND,
                falta + "Valor só será atribuído com evidência registrada: preços de entrada (arrematação com "
                "prêmio do comprador e custos) de obras comparáveis do mesmo artista, técnica, dimensões e "
                "tiragem, ajustados por condição, localização e restrições (NBC TSP 38, itens 24, 25 e 32; "
                "Regras, item 9.2). Sem mensuração confiável, a obra não é reconhecida e é divulgada em nota "
                "(NBC TSP 37, itens 6(b), 7 e 77). " + aq)
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

    arq_bao = os.path.join(DADOS, "vinculo_bao.csv")
    bao = {b["id_registro"]: b for b in csv.DictReader(open(arq_bao, encoding="utf-8-sig"))} if os.path.exists(arq_bao) else {}
    grupos = {}  # doador -> total do grupo, contado uma vez por doador

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
                nota = ("Faixa indicativa, não é mensuração confiável: evidência nível C ({}), referência {}. A "
                        "incerteza é elevada demais para reconhecimento (Estrutura Conceitual (R1), item 6.8; NBC "
                        "TSP 37, item 6(b)). Fonte: {}. {}".format(r["tipo_evidencia"] or "não informado", r["data_referencia"] or "sem data",
                                               r["fonte"], e.get("observacao", "")))
            else:
                r["situacao"] = SIT_SEM
                nota = ("Evidência registrada é insuficiente para estimativa confiável (nível {}). Fonte: {}. {}"
                        .format(nivel, r["fonte"], e.get("observacao", "")))
        b = bao.get(str(l.get("id_registro")))
        if b and r["situacao"] != SIT_FUND:
            ato = "{}, publicado em {}, doador {}".format(b["atos"], b["data_publicacao"], b["doador_ato"])
            if b["tipo_vinculo"] in ("1:1", "valor único") and b["valor_individual"] != "":
                v = float(b["valor_individual"])
                r.update(situacao=SIT_REG, base_mensuracao=BASE_REG, tecnica=TEC_REG, nivel_evidencia="Registro oficial",
                         valor_min=v, valor_central=v, valor_max=v, moeda="BRL", data_referencia=b["data_publicacao"],
                         tipo_evidencia="ato de incorporação", fonte=b["fonte"], valor_exibicao=brl(v, "BRL"))
                nota = ("Valor registrado pela UnB no ato de incorporação ({}; tombamento {}{}). Vínculo {}: {}. Bem da "
                        "camada A2 do cadastro patrimonial: o valor já está no total oficialmente registrado e não é somado ao "
                        "valor agregado estimado (Regras, itens 10 e 15). Base do valor: avaliação da comissão especial, no "
                        "processo do SEI, não examinado.{}").format(
                            ato, b["tombamento"], ", entre os do mesmo doador" if b["tipo_vinculo"] == "valor único" else "",
                            b["tipo_vinculo"], b["confianca"],
                            " Valor abaixo de R$ 200,00: a equipe decide se é simbólico." if v < 200 else "")
            elif b["tipo_vinculo"] == "grupo":
                vg = float(b["valor_grupo"])
                r.update(situacao=SIT_REG_G, base_mensuracao=BASE_REG, tecnica=TEC_REG, nivel_evidencia="Registro oficial (grupo)",
                         moeda="BRL", data_referencia=b["data_publicacao"], tipo_evidencia="ato de incorporação",
                         fonte=b["fonte"], valor_exibicao="Grupo: {} ({} obras)".format(brl(vg, "BRL"), b["bens_atos_doador"]))
                grupos[b["doador_ato"]] = vg
                nota = ("Uma das {} obras do doador no ato de incorporação ({}; tombamentos {}), que somam {}. Cada tombamento "
                        "tem valor próprio no cadastro patrimonial (camada A2), mas o ato não diz qual corresponde a qual "
                        "registro do portal: o valor individual não é identificado nem rateado (Regras, item 9.4). O valor já "
                        "está no total oficialmente registrado e não é somado ao valor agregado estimado (Regras, itens 10 e "
                        "15). Base do valor: avaliação da comissão especial, no processo do SEI, não examinado.{}").format(
                            b["bens_atos_doador"], ato, b["tombamento"], brl(vg, "BRL"),
                            " Há valor abaixo de R$ 200,00 no grupo: a equipe decide se é simbólico." if b["valor_baixo"] else "")
            else:
                nota = (nota.strip() + " Ato de incorporação publicado ({}): {} bem(ns), total de {}, para {} obra(s) do "
                        "doador no portal; o valor individual não é identificado (vínculo: {}).").format(
                            ato, b["bens_atos_doador"], brl(float(b["valor_grupo"]), "BRL"), b["obras_portal_doador"],
                            b["tipo_vinculo"])
        r["nota_metodologica"] = (nota.strip() + " " + NORMAS).strip()
        saida.append(r)

    with open(os.path.join(DADOS, "mensuracao.csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLS_SAIDA)
        w.writeheader()
        w.writerows(saida)

    # resumo (Regras, item 15)
    resumo = []
    for sit in (SIT_FUND, SIT_REG, SIT_REG_G, SIT_FAIXA, SIT_PEND, SIT_SEM, SIT_FORA, SIT_CLASS):
        resumo.append({"indicador": "Registros: " + sit, "valor": sum(1 for r in saida if r["situacao"] == sit), "observacao": ""})
    resumo.append({"indicador": "Valor registrado nos atos de incorporação (registros vinculados)",
                   "valor": round(sum(float(r["valor_central"]) for r in saida if r["situacao"] == SIT_REG), 2),
                   "observacao": "Valor oficial já contido no cadastro patrimonial (camada A2); não é somado ao valor agregado estimado."})
    resumo.append({"indicador": "Valor registrado nos atos de incorporação, por grupo (total dos doadores)",
                   "valor": round(sum(grupos.values()), 2),
                   "observacao": "{} doadores; valor oficial já contido no cadastro patrimonial (camada A2), sem rateio entre as obras.".format(len(grupos))})
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
