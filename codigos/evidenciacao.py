#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Etapa IV do Hackathon CULTIVA UnB 2026: evidenciação (Regras, itens 10 e 15).

Lê os resultados das etapas I a III e gera:
  resultados/demonstrativos/quadro_consolidado.csv
  resultados/indicadores/indicadores_item15.csv
  resultados/nota_explicativa/minuta_nota_explicativa.md   (com notas de rodapé metodológicas)
Os valores acadêmicos são separados do valor registrado no cadastro patrimonial da UnB (item 10).
"""
import csv
import os
import re
from collections import Counter, defaultdict

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
DADOS = os.path.join(RAIZ, "dados")
RES = os.path.join(RAIZ, "resultados")


def ler(nome):
    p = os.path.join(DADOS, nome)
    return list(csv.DictReader(open(p, encoding="utf-8-sig"))) if os.path.exists(p) else []


def kv(nome):
    return {r["indicador"]: r["valor"] for r in ler(nome)}


def brl(v):
    s = "{:,.2f}".format(float(v)).replace(",", "X").replace(".", ",").replace("X", ".")
    return "R$ " + s


def n(x):
    try:
        return "{:,}".format(int(x)).replace(",", ".")
    except (TypeError, ValueError):
        return x


def main():
    inv = ler("inventario.csv"); rec = {r["id_registro"]: r for r in ler("reconhecimento.csv")}
    mens = {r["id_registro"]: r for r in ler("mensuracao.csv")}
    ind = kv("indicadores.csv"); conc = kv("conciliacao_patrimonial.csv")
    dup = {r["criterio"]: r["registros"] for r in ler("verificacao_duplicidades_resumo.csv")}
    rel = {r["indicador"]: (r["quantidade"], r["valor_registrado_rs"]) for r in ler("cadastro_unb_resumo.csv")}
    val = ler("validacao_casos.csv")
    camadas = {r["camada"]: r for r in ler("reconhecimento_cadastro_resumo.csv")}
    log_data = (inv[0]["data_consulta"] if inv else "")
    if len(log_data) >= 16 and log_data[4] == "-":
        log_data = "{}/{}/{}, {}h{}".format(log_data[8:10], log_data[5:7], log_data[:4], log_data[11:13], log_data[14:16])

    grupos = ["Arte", "Arte contemporânea", "Etnográfica", "Registro de evento (não é bem)", "A classificar"]
    linhas = []
    for g in grupos + ["TOTAL"]:
        ids = [r["id_registro"] for r in inv if g == "TOTAL" or r["grupo_sugerido"] == g]
        c_rec = Counter(rec[i]["classe_reconhecimento"] for i in ids if i in rec)
        c_def = Counter(rec[i]["atende_definicao_ativo"] for i in ids if i in rec)
        c_men = Counter(mens[i]["situacao"] for i in ids if i in mens)
        faixa = defaultdict(lambda: [0.0, 0.0])
        fund = 0.0
        for i in ids:
            m = mens.get(i, {})
            if m.get("situacao") == "Faixa indicativa":
                faixa[m["moeda"]][0] += float(m["valor_min"] or 0); faixa[m["moeda"]][1] += float(m["valor_max"] or 0)
            if m.get("situacao") == "Mensuração fundamentada" and m.get("moeda") in ("", "BRL"):
                fund += float(m["valor_central"] or 0)
        linhas.append({
            "grupo": g, "registros_analisados": len(ids),
            "atende_definicao_sim": c_def.get("sim", 0), "atende_definicao_pendente": c_def.get("pendente", 0), "atende_definicao_nao": c_def.get("não", 0),
            "reconhecimento_sustentado": c_rec.get("Reconhecimento sustentado pelas evidências", 0),
            "nao_reconhecimento_fundamentado": c_rec.get("Não reconhecimento fundamentado", 0),
            "pendente_verificacao": c_rec.get("Pendente de verificação", 0),
            "mensuracao_fundamentada": c_men.get("Mensuração fundamentada", 0),
            "valor_fundamentado_brl": round(fund, 2),
            "faixa_indicativa": c_men.get("Faixa indicativa", 0),
            "faixa_indicativa_soma": "; ".join("{} {:,.0f} a {:,.0f}".format(k, v[0], v[1]).replace(",", ".") for k, v in faixa.items()),
            "sem_mensuracao_monetaria": c_men.get("Sem mensuração monetária fundamentada", 0),
            "mensuracao_pendente": c_men.get("Pendente de evidência", 0) + c_men.get("Pendente de classificação", 0),
            "fora_do_escopo": c_men.get("Não aplicável (não é ativo)", 0),
        })
    os.makedirs(os.path.join(RES, "demonstrativos"), exist_ok=True)
    with open(os.path.join(RES, "demonstrativos", "quadro_consolidado.csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(linhas[0].keys())); w.writeheader(); w.writerows(linhas)
    T = linhas[-1]

    # reconhecidos no acervo digital: pelo ato de incorporação (bens já no cadastro) ou pela mensuração da equipe
    sit_de = lambda i: mens.get(i, {}).get("situacao", "")
    sust_ids = [i for i, r in rec.items() if r["classe_reconhecimento"] == "Reconhecimento sustentado pelas evidências"]
    sa_n = sum(1 for i in sust_ids if sit_de(i).startswith("Custo atribuído registrado"))
    eq = [i for i in sust_ids if sit_de(i) == "Mensuração fundamentada"]
    vcad = {r["id_registro"]: r for r in ler("valores_cadastro_unb.csv")}
    inv_id = {r["id_registro"]: r for r in inv}
    eq4 = []
    for i in eq:
        c, r = vcad.get(i, {}), inv_id.get(i, {})
        if c.get("valor_registrado") == "0.01":
            eq4.append("Entre esses bens tombados por R$ 0,01 está, provavelmente, a obra do registro {} do acervo digital ({}; procedência: {}; "
                       "vínculo {} pela origem {} no cadastro). A equipe obteve para ela mensuração de nível {} pela abordagem de mercado "
                       "(seção 6): esse valor é a base proposta para o custo atribuído na aplicação inicial (NBC TSP 37, itens 13 e 87(a)) e "
                       "não é somado aos totais do cadastro (Regras, item 10).".format(
                           i, r.get("autoria_origem", ""), r.get("proveniencia", ""), (c.get("confianca") or "").lower(), c.get("origem_sipat", ""),
                           mens[i].get("nivel_evidencia", "")))
        else:
            eq4.append("A obra do registro {} do acervo digital ({}) não tem vínculo com o cadastro; a mensuração de nível {} obtida pela "
                       "equipe (seção 6) é a base proposta para o custo atribuído na aplicação inicial (NBC TSP 37, item 87(a)).".format(
                           i, r.get("autoria_origem", ""), mens[i].get("nivel_evidencia", "")))
    ev_obs = {e["id_registro"]: e.get("observacao", "") for e in ler("evidencias_mensuracao.csv")}
    fund_txt = []
    for i, m in mens.items():
        if m.get("situacao") != "Mensuração fundamentada":
            continue
        k = re.search(r"(\d+) transação", m.get("tecnica", ""))
        fund_txt.append("Registro {} ({}, {}): nível {}; valor central de {} (mediana de {} transações realizadas); intervalo de {} a {}, "
                        "entre transações e estimativas{}; demais limitações em `dados/evidencias_mensuracao.csv`.".format(
                            i, m.get("autoria_origem", ""), inv_id.get(i, {}).get("tecnica", "") or m.get("titulo", ""), m.get("nivel_evidencia", ""),
                            brl(m["valor_central"] or 0), k.group(1) if k else "?", brl(m["valor_min"] or 0), brl(m["valor_max"] or 0),
                            "; o portal grafa o nome do artista de forma diferente do mercado; a identidade deve ser conferida na "
                            "assinatura da obra" if "grafa o nome" in ev_obs.get(i, "") else ""))

    # indicadores obrigatórios (item 15)
    rastreaveis = sum(1 for r in inv if r["url_registro"] and r["id_registro"] in rec and r["id_registro"] in mens)
    i15 = [
        ("Registros identificados", ind.get("Registros identificados", ""), "Total de registros públicos no portal"),
        ("Registros recuperados", ind.get("Registros recuperados", ""), "Total recuperado e organizado"),
        ("Cobertura (%)", ind.get("Cobertura (%)", ""), "Recuperados / identificados no universo digital"),
        ("Completude cadastral (%)", ind.get("Completude cadastral média (%)", ""), "Preenchimento médio das 13 variáveis principais"),
        ("Registros duplicados", dup.get("Registros possivelmente duplicados (indicador do item 15)", ind.get("Registros com possível duplicidade", "")),
         "Registros possivelmente duplicados: {} em provável duplicidade (Memória Institucional) e {} a conferir no Acervo (imagem ou descrição idêntica); nenhum identificador repetido (dados/verificacao_duplicidades.csv)".format(
             dup.get("Registros em provável duplicidade", "?"), dup.get("Registros a conferir", "?"))),
        ("Reconhecimento sustentado", T["reconhecimento_sustentado"], "Registros do acervo digital com fundamentação suficiente para reconhecer: {} obras identificadas pelo ato de incorporação publicado no Boletim de Atos Oficiais como bens já reconhecidos no cadastro patrimonial (camada A2), cujo valor está no total do cadastro e não é somado de novo{}".format(
            n(sa_n), "; e {} com mensuração de nível A ou B obtida pela equipe pela abordagem de mercado, base proposta para o custo atribuído (NBC TSP 37, itens 13 e 87(a)), estimativa acadêmica que não é somada aos valores do cadastro (Regras, item 10)".format(n(len(eq))) if eq else "")),
        ("Reconhecimento sustentado no cadastro patrimonial", sum(int(camadas[k]["bens"]) for k in ("A1", "A2") if k in camadas),
         "Bens tombados com controle, ingresso e valor documentados (camadas A1 e A2): {} em valores oficialmente registrados, não estimados pela equipe (dados/reconhecimento_cadastro_resumo.csv)".format(
             brl(sum(float(camadas[k]["valor_registrado_rs"]) for k in ("A1", "A2") if k in camadas)))),
        ("Reconhecimento pendente", T["pendente_verificacao"], "Necessitam de informações complementares"),
        ("Mensuração fundamentada", T["mensuracao_fundamentada"], "Valores com evidência nível A ou B"),
        ("Mensuração pendente", T["mensuracao_pendente"] + T["faixa_indicativa"], "Sem evidência suficiente (inclui {} com faixa indicativa)".format(T["faixa_indicativa"])),
        ("Valor agregado estimado", brl(T["valor_fundamentado_brl"]), "Soma dos valores fundamentados (detalhe por base e categoria em resultados/demonstrativos/valor_agregado_por_base.csv); não é o valor total do patrimônio da CAL"),
        ("Rastreabilidade (%)", round(100.0 * rastreaveis / len(inv), 1) if inv else 0, "Registros com fonte, decisão de reconhecimento e de mensuração documentadas"),
        ("Validação", len(val), "Casos examinados em profundidade (mínimo de nove)"),
    ]
    # valor agregado por base de mensuração e categoria (item 15)
    agg = defaultdict(lambda: [0, 0.0])
    for m in mens.values():
        if m.get("situacao") == "Mensuração fundamentada":
            k = (m.get("base_mensuracao", ""), m.get("categoria_mensuracao", ""), m.get("moeda", "") or "BRL")
            agg[k][0] += 1; agg[k][1] += float(m.get("valor_central") or 0)
    with open(os.path.join(RES, "demonstrativos", "valor_agregado_por_base.csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f); w.writerow(["base_mensuracao", "categoria", "moeda", "registros", "valor_agregado"])
        for (b_, c_, mo), (n_, v_) in sorted(agg.items()):
            w.writerow([b_, c_, mo, n_, round(v_, 2)])
        if not agg:
            w.writerow(["(nenhuma mensuração fundamentada)", "", "", 0, 0])
    os.makedirs(os.path.join(RES, "indicadores"), exist_ok=True)
    with open(os.path.join(RES, "indicadores", "indicadores_item15.csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f); w.writerow(["indicador", "valor", "descricao"]); w.writerows(i15)

    # minuta de nota explicativa (NBC TSP 37, itens 69 e 77; NBC TSP 38, itens 54 e 55; Regras, item 10)
    vp = conc.get("Valor registrado das obras próprias (R$)", "0")
    vt = conc.get("Valor registrado dos bens de terceiro (R$)", "0")
    termo = ((ler("conciliacao_patrimonial.csv") or [{}])[0].get("observacao", "").replace("Lista da CAL; termo ", "") or "?")
    R = list(rec.values())
    nao77 = lambda g: sum(1 for r in R if r["grupo_sugerido"] == g and r["enquadramento_normativo"].startswith("Não reconhecer"))
    pend_todos = [r for r in R if r["classe_reconhecimento"] == "Pendente de verificação"]
    pend = [r for r in pend_todos if r["atende_definicao_ativo"] != "sim"]
    vinc = [r for r in pend_todos if r["atende_definicao_ativo"] == "sim"]
    cq = lambda k, c: camadas.get(k, {}).get(c, "0")
    cam_tab = "\n".join("| {} {} | {} | {} | {} | {} |".format(k, camadas[k]["descricao"], n(camadas[k]["bens"]), brl(camadas[k]["valor_registrado_rs"]),
                                                            camadas[k]["classe_reconhecimento"], camadas[k]["fundamento"])
                        for k in ("A1", "A2", "A3", "B", "D") if k in camadas)
    p_ex = sum(1 for r in pend if not r["existencia"].startswith("atendido") and r["controle"].startswith("atendido"))
    p_ct = sum(1 for r in pend if r["existencia"].startswith("atendido") and not r["controle"].startswith("atendido"))
    p_ambos = len(pend) - p_ex - p_ct
    faixa_obs = sum(1 for m in mens.values() if m.get("situacao") == "Faixa indicativa" and "observáveis (preços" in m.get("tecnica", ""))
    faixa_nobs = T["faixa_indicativa"] - faixa_obs
    rq = lambda k: n(rel.get(k, ("?", ""))[0])
    rv = lambda k: brl(rel.get(k, ("", "0"))[1] or 0)
    rel_txt = ("No relatório de bens da UnB com todas as obras de arte, há {} bens nas localidades da CAL ({}), {} deles registrados por "
               "R$ 0,01, valor simbólico que não constitui custo atribuído (NBC TSP 37, itens 12 e 13). Desse relatório, {} tombamentos "
               "têm o mesmo número de registro de {} registros do portal; outros {} registros têm vínculo provável por procedência, todos "
               "com valor de R$ 0,01. Outros {} bens, tombados mais recentemente, têm denominação que descreve a obra (título, ano, "
               "material e técnica) e não têm registro no acervo digital ({}).[^8] ".format(rq("Bens nas localidades da CAL"), rv("Bens nas localidades da CAL"),
                                                   rq("Bens da CAL com valor de R$ 0,01"), rq("Tombamentos vinculados por identificador"),
                                                   rq("Registros do Acervo com vínculo confirmado"),
                                                   rq("Registros do Acervo com vínculo provável (procedência)"),
                                                   rq("Bens com denominação descritiva (recentes, sem registro no acervo digital)"),
                                                   rv("Bens com denominação descritiva (recentes, sem registro no acervo digital)"))) if rel else ""
    V = dict(rel_txt=rel_txt, cam_tab=cam_tab,
        cad_n=n(cq("Total", "bens")), cad_v=brl(cq("Total", "valor_registrado_rs")),
        sust_n=n(int(cq("A1", "bens")) + int(cq("A2", "bens"))), sust_v=brl(float(cq("A1", "valor_registrado_rs")) + float(cq("A2", "valor_registrado_rs"))),
        a1_n=n(cq("A1", "bens")), a2_n=n(cq("A2", "bens")), a3_n=n(cq("A3", "bens")), a3_v=brl(cq("A3", "valor_registrado_rs")),
        b_n=n(cq("B", "bens")), d_n=n(cq("D", "bens")), d_v=brl(cq("D", "valor_registrado_rs")),
        gal=n(sum(1 for r in R if r["subcolecao"] == "Galvão" and r["enquadramento_normativo"].startswith("Não reconhecer"))),
        ini=n(sum(1 for r in R if r["subcolecao"] == "Inicial" and r["enquadramento_normativo"].startswith("Não reconhecer"))),
        vinc=n(len(vinc)), tri=n(sum(1 for r in vinc if r["subcolecao"] == "Triangular")), arte=n(sum(1 for r in vinc if r["grupo_sugerido"] == "Arte")),
        pdef=n(len(pend)),
        reg=n(len(inv)), acervo=n(sum(1 for r in inv if r["colecao"] == "Acervo")), mem=n(sum(1 for r in inv if r["colecao"] == "Memória Institucional")),
        cob=str(ind.get("Cobertura (%)", "")).replace(".", ","), comp=str(ind.get("Completude cadastral média (%)", "")).replace(".", ","),
        sust=n(T["reconhecimento_sustentado"]), nao=n(T["nao_reconhecimento_fundamentado"]), pend=n(T["pendente_verificacao"]),
        mem_n=n(sum(1 for r in R if r["colecao"] == "Memória Institucional")),
        n77=n(sum(1 for r in R if r["enquadramento_normativo"].startswith("Não reconhecer"))),
        a77=n(nao77("Arte")), c77=n(nao77("Arte contemporânea")), e77=n(nao77("Etnográfica")),
        defs=n(T["atende_definicao_sim"]), fund=n(T["mensuracao_fundamentada"]), faixa=n(T["faixa_indicativa"]),
        faixa_obs=n(faixa_obs), faixa_nobs=n(faixa_nobs),
        vfund=brl(T["valor_fundamentado_brl"]), fsoma=T["faixa_indicativa_soma"] or "nenhuma",
        obras_cad=conc.get("Obras de arte no cadastro", "?"), proprias=conc.get("Obras de arte próprias (sem marca de bem de terceiro)", "?"),
        vp=brl(vp), terc=conc.get("Obras marcadas como bem de terceiro", "?"), vt=brl(vt),
        ndep=conc.get("Obras de arte marcadas como não depreciáveis", "?"), nvu=conc.get("Obras de arte com vida útil informada", "?"),
        ndoc=conc.get("Obras com nota fiscal, empenho ou fornecedor informados", "?"),
        nestado=conc.get("Obras de arte com estado diferente de 'Em uso'", "?"),
        mpend=n(T["mensuracao_pendente"] + T["faixa_indicativa"]), data=log_data,
        cad=conc.get("Bens no cadastro patrimonial localizados na CAL", "?"), dt_tomb=conc.get("Data de tombamento no sistema atual", "?"),
        termo=termo, p_ex=n(p_ex), p_ct=n(p_ct), p_ambos=n(p_ambos),
        nloc=n(sum(1 for r in pend if r["existencia"].startswith("não confirmado"))),
        nemp=n(sum(1 for r in pend if r["existencia"].startswith("a verificar"))),
        achados_txt=("nenhum aparece" if str(conc.get("Tombamentos do cadastro encontrados no portal", "?")) == "0"
                     else "{} aparecem".format(conc.get("Tombamentos do cadastro encontrados no portal", "?"))),
        pesfis=conc.get("Obras de arte com origem PESFIS (pessoa física)", "?"),
        atos=conc.get("Atos de ingresso distintos das obras próprias", "?"),
        recentes=conc.get("Registros do portal com aquisição a partir de 2016", "?"),
        eq4=(" " + " ".join(eq4)) if eq4 else "", fund_txt=(" " + " ".join(fund_txt)) if fund_txt else "")
    nota = """# Minuta de nota explicativa: acervos do patrimônio cultural sob guarda da Casa da Cultura da América Latina (CAL/UnB)

**Resultado acadêmico do Hackathon CULTIVA UnB 2026. Não constitui registro contábil oficial da Universidade de Brasília (Regras, item 17.13).**

Estrutura: a nota segue os requisitos de divulgação da NBC TSP 37 (itens 69 e 77) e da NBC TSP 38 (itens 54 e 55) e cobre os conteúdos a) a j) do item 10 das Regras, indicados entre colchetes em cada seção.[^1]

## 1 Caracterização das coleções [a, b]

A CAL guarda coleções de arte, arte contemporânea e etnográficas. O acervo digital público reúne {reg} registros em três coleções: Acervo ({acervo} registros, com as subcoleções Arte, Triangular, Inicial, Galvão e Chocó), Memória Institucional ({mem}) e Mobiliário moderno da UnB (1). Foram analisados todos os {reg} registros ({cob}% do universo digital identificável), com completude cadastral média de {comp}%.[^2] A Coleção CNRC, listada no item 4.3 das Regras, não aparece no portal. A cobertura digital não equivale ao patrimônio físico da CAL (Regras, item 4.4).

## 2 Política contábil proposta [c, d]

- **Classe:** "acervos do patrimônio cultural", classe do ativo imobilizado (NBC TSP 37, itens 5 e 34(l)); unidade de reconhecimento: o registro individual do catálogo (item 8).
- **Reconhecimento:** o bem é reconhecido quando satisfaz a definição de ativo (recurso com potencial de serviços, controlado no presente, resultante de evento passado) e pode ser mensurado com confiabilidade (Estrutura Conceitual (R1), itens 5.6 a 5.13 e 6.2; NBC TSP 37, item 6). O patrimônio cultural que satisfaz a definição, mas não pode ser mensurado com confiabilidade, não é reconhecido e é divulgado nesta nota; deve ser reconhecido quando o custo ou o valor corrente estiver disponível (NBC TSP 37, item 7).[^3]
- **Mensuração inicial:** os bens recebidos por doação ou transferência são mensurados pelo custo atribuído (NBC TSP 37, itens 11 a 13; NBC TSP 38, itens 10 e 12(b)), determinado pelo valor corrente operacional, porque o acervo é mantido por sua capacidade operacional e não financeira (NBC TSP 37, item 27; NBC TSP 38, itens 23 a 25).[^4]
- **Mensuração subsequente:** modelo do custo histórico para a classe (NBC TSP 37, itens 24 e 26).
- **Depreciação:** obras sob guarda museológica com vida útil indefinida, sem depreciação, e revisão anual de indicações de redução ao valor recuperável (NBC TSP 37, itens 52 a 56).
- **Vigência:** a NBC TSP 37, a NBC TSP 38 e a Estrutura Conceitual (R1) aplicam-se a partir de 1º/01/2027; na aplicação inicial, o patrimônio cultural sem informação confiável de custo pode ser mensurado pelo custo atribuído (NBC TSP 37, item 87(a)).

## 3 Acervos reconhecidos no cadastro patrimonial da UnB [c, f] (NBC TSP 37, item 69)

O reconhecimento contábil ocorre no cadastro patrimonial da UnB, que registra {cad_n} bens nas localidades da CAL e no subgrupo de bens recentes, com valor registrado de {cad_v}. A análise por camada separa os bens cujo reconhecimento é sustentado pelas evidências dos que dependem de verificação ou não satisfazem os critérios:[^5]

| Camada | Bens | Valor registrado | Classe | Fundamento |
|---|---:|---:|---|---|
{cam_tab}

Os {sust_n} bens das camadas A1 ({a1_n} doações de 2024 a 2026) e A2 ({a2_n} obras próprias da Lista da CAL, doadas em 2019 e 2020), com {sust_v}, têm controle, evento passado e valor atribuído na incorporação documentados; esse valor faz as vezes do custo atribuído (NBC TSP 37, item 12; NBC TSP 38, item 10). Ressalvas: a base de cada valor (avaliação ou declaração do doador) está nos processos e atos de ingresso, não examinados; no ato 217, 80 obras têm o mesmo valor de R$ 5.000,00, o que sugere valor convencionado, a confirmar. Os {d_n} bens de terceiros ({d_v}) não compõem o ativo da UnB por falta de controle (Estrutura Conceitual (R1), item 5.11).

| Requisito do item 69 | Informação disponível na Lista da CAL (camada A2) |
|---|---|
| (a) critérios de mensuração do valor contábil bruto | Valor atribuído no ingresso por doação, sem documento de avaliação anexado; bens migrados do SIPAT em {dt_tomb} (termo {termo}); obras com nota fiscal, empenho ou fornecedor informados: {ndoc} |
| (b) métodos de depreciação | {ndep} obras marcadas como não depreciáveis |
| (c) vidas úteis | Obras com vida útil informada: {nvu}; tratamento coerente com vida útil indefinida (itens 52 e 53) |
| (d) valor contábil bruto e depreciação acumulada | {vp} (obras próprias da Lista); sem depreciação; saldos de início e fim de período não constam da Lista |
| (e) conciliação do período | Não disponível: a Lista não traz movimentações |

Nenhum número de tombamento da Lista aparece no acervo digital. {rel_txt}Esses totais são valores oficialmente registrados e não são somados às estimativas acadêmicas desta nota (Regras, item 10).

## 4 Itens do patrimônio cultural não reconhecidos [e, g, h] (NBC TSP 37, itens 7 e 77)

Satisfazem a definição de ativo, mas não têm mensuração confiável e, por isso, não são reconhecidos: {b_n} bens do cadastro tombados por R$ 0,01, custo simbólico que não é custo atribuído (NBC TSP 37, item 13), e {n77} registros etnográficos do acervo digital, {gal} da Coleção Galvão e {ini} da Coleção Inicial.[^3]{eq4}

| Classe | Itens | (a) Dificuldades na obtenção de mensuração confiável | (b) Relevância para os objetivos da entidade |
|---|---:|---|---|
| Bens do cadastro tombados por R$ 0,01 | {b_n} | Valor simbólico registrado na migração do SIPAT; sem vínculo obra a obra com o acervo digital; para os objetos etnográficos, nenhuma técnica aplicável sem tratá-los como mercadoria (Regras, item 4.3) | Acervo de referência para exposições da CAL e para atividades de ensino, pesquisa e extensão da Universidade[^6] |
| Objetos etnográficos do acervo digital | {n77} | Nenhuma técnica aplicável sem tratar o objeto como mercadoria: a abordagem de custo exige substituto de utilidade comparável, inexistente para objeto único (NBC TSP 38, itens 43 e 44); a Coleção Galvão não consta do cadastro patrimonial | Documentação da cultura material de povos indígenas e comunidades tradicionais, com restrições culturais e éticas |

A Coleção Galvão foi formada na UnB nos anos 1960, depositada no Centro Nacional de Referência Cultural em 1977 e devolvida à UnB em 2002 por rescisão do acordo de guarda; 17 peças estão emprestadas ao Museu das Bandeiras e ao Museu do Descobrimento.[^10] Não foram identificados gastos subsequentes reconhecidos com esses itens (NBC TSP 37, item 78). Os {mem_n} registros de evento da Memória Institucional não satisfazem a definição de ativo (Estrutura Conceitual (R1), item 5.6).

## 5 Registros pendentes de verificação [g]

No acervo digital, {pend} registros estão pendentes. Destes, {vinc} satisfazem a definição de ativo e aguardam o vínculo com bens já reconhecidos no cadastro: {tri} da subcoleção Triangular, provável contrapartida da Lista da CAL, e {arte} de Arte, com provável tombamento nas origens de pessoa física e do Banco Central. Os outros {pdef} ainda não permitem concluir se satisfazem a definição de ativo: {p_ex} têm ingresso documentado, mas localização atual não confirmada (entre eles, {nloc} não localizados e {nemp} com situação a verificar); {p_ct} estão localizados, mas sem forma ou data de ingresso; {p_ambos} carecem das duas informações. No cadastro, {a3_n} bens ({a3_v}) aguardam a confirmação da base do valor registrado ou a mensuração pelo custo atribuído na aplicação inicial (NBC TSP 37, item 87(a)). Pendências de mensuração no acervo digital: {mpend} registros.[^3]

Dificuldade comum: o acervo digital, mantido no software Tainacan, identifica as obras pelo número de registro museológico e não informa o número de tombamento patrimonial; o cadastro patrimonial identifica as obras apenas pelo tombamento, sem título ou autoria. Dos {cad} tombamentos da Lista da CAL, {achados_txt} no acervo digital. Há indícios de que a lista corresponde, em grande parte, à subcoleção Triangular: as {pesfis} obras da lista têm origem "pessoa física" no SIPAT, as próprias ingressaram por {atos} atos de ingresso, e os únicos registros do acervo digital adquiridos a partir de 2016 são {recentes} doações dessa subcoleção. O vínculo obra a obra depende dos atos de doação.[^9]

## 6 Mensuração: base, técnicas, dados de entrada e incerteza [d, e, f, h] (NBC TSP 38, itens 54 e 55)

Registros com mensuração fundamentada: {fund}. Valor agregado das mensurações fundamentadas: {vfund}. Esse montante não representa o valor total do patrimônio cultural da CAL (Regras, item 15).{fund_txt}

Há {faixa} obras com faixa indicativa (nível C), obtida pela abordagem de mercado (NBC TSP 38, item 42): {faixa_obs} a partir de uma ou duas transações realizadas (dados observáveis) e {faixa_nobs} só com estimativas de leiloeiro ou preços de oferta de galeria (dados não observáveis). Somadas, em reais (valores em moeda estrangeira convertidos pela PTAX de venda do Banco Central na data de cada transação): {fsoma}. A incerteza é elevada demais para reconhecimento (Estrutura Conceitual (R1), item 6.8).[^7] Sem vínculo obra a obra com o cadastro, não é possível avaliar se o valor corrente difere materialmente do valor registrado (NBC TSP 37, item 76(d)).

## 7 Restrições patrimoniais, culturais e documentais [i]

Bens etnográficos sujeitos a restrições culturais e éticas (Regras, item 4.3); fotografias com direitos reservados (Lei nº 9.610/1998); {terc} bens no cadastro marcados como de terceiros; {nestado} obra do cadastro em estado diferente de "Em uso"; registros do portal com situação "Não localizado" ou "Emprestado".

## 8 Limitações dos resultados [j]

Certificado TLS do portal vencido na data da coleta ({data}), feita sem verificação do certificado. Triagem de grupos automática e sujeita a revisão. Ausência de chave comum entre o acervo digital e o cadastro patrimonial (seção 4). Apêndices de orientação de aplicação da NBC TSP 37 e da NBC TSP 38 não consultados. Regras de decisão propostas pela equipe, a validar com a CAL e com a contabilidade da UnB.[^2][^3][^4]

---

[^1]: Normas conferidas no texto publicado em 24/11/2026: NBC TSP 37, de 11/12/2025 (DOU de 17/03/2026); NBC TSP 38, de 09/04/2026 (DOU de 17/04/2026); NBC TSP Estrutura Conceitual (R1), de 13/11/2025 (DOU de 07/04/2026). Itens e fontes em `metodologia/fundamentacao_normativa.md`.
[^2]: Identificação: extração pela API pública do Tainacan em {data} (`codigos/extrair_acervo_cal.py`); base em `dados/inventario.csv`, dicionário em `dados/dicionario_dados.md` e diagnóstico em `dados/diagnostico_qualidade.csv`.
[^3]: Reconhecimento: matriz aplicada a todos os registros (`codigos/reconhecimento.py`, `dados/reconhecimento.csv`). Controle avaliado pelos indicadores do item 5.12 da Estrutura Conceitual (R1): propriedade legal (ingresso por doação ou transferência com data), acesso (situação "Localizado") e meios de uso (guarda museológica). A presença no portal, sozinha, não basta (Regras, item 8). Reconhecimento sustentado exige mensuração confiável (NBC TSP 37, item 6(b)): no acervo digital, nível A ou B; no cadastro, valor atribuído na incorporação. Obras de arte com definição atendida aguardam o vínculo com o cadastro, porque provavelmente já estão reconhecidas (Parecer de Reconhecimento dos Ativos da CAL v1, 24/11/2026). A exceção são as obras com mensuração de nível A ou B obtida pela equipe cuja provável contrapartida no cadastro está tombada por R$ 0,01: o valor de mercado é a base proposta para o custo atribuído (NBC TSP 37, itens 13 e 87(a)) e não é somado ao cadastro. Na subcoleção Triangular (provável contrapartida da Lista da CAL) e nas obras sem esse vínculo, o valor fica só como informação, para não contar a mesma obra duas vezes.
[^4]: Mensuração: `codigos/mensuracao.py` e `metodologia/mensuracao.md`. O valor corrente operacional é o valor que a entidade pagaria pelo potencial de serviço remanescente; é preço de entrada, reflete o uso atual e inclui os custos necessários (NBC TSP 38, itens 6 e 25). Sem evidência suficiente, o registro recebe a classificação do item 9.4 das Regras, sem valor arbitrário.
[^5]: Cadastro patrimonial por camada: `codigos/reconhecimento_cadastro.py` e `dados/reconhecimento_cadastro_resumo.csv` (a versão bem a bem fica fora do repositório público). Lista da CAL fornecida pela equipe, com {cad} bens tombados em {dt_tomb} (termo {termo}), migrados do SIPAT; conciliação agregada em `dados/conciliacao_patrimonial.csv` (`codigos/cadastro_patrimonial.py`); a versão item a item, sem dados pessoais, fica fora do repositório público até a confirmação da autorização de divulgação (Regras, item 12).
[^6]: Constituição Federal de 1988, art. 207: as universidades obedecem ao princípio de indissociabilidade entre ensino, pesquisa e extensão. O potencial de serviços do patrimônio cultural está previsto nos itens 5.8 e 5.9 da Estrutura Conceitual (R1).
[^7]: Comparáveis do mesmo artista e da mesma família de técnica, com fonte (`dados/comparaveis.csv`, `codigos/comparaveis.py`). Nível A: 3 ou mais transações e obra com dimensões e tiragem conhecidas; B: 3 ou mais transações; C: 1 ou 2 transações, ou só estimativas e ofertas. Só contam para A e B vendas do próprio artista em casa de leilão ou galeria; vendas em plataforma aberta, comparáveis de artista similar e obras em condição não confirmada só formam faixa indicativa; edições de outro período e lotes de técnica incerta ficam registrados, fora da conta. Valor central: mediana das transações; intervalo: menor e maior valor entre transações e estimativas. Valores em moeda estrangeira convertidos pela PTAX de venda do Banco Central na data de cada transação (`metodologia/mensuracao.md`).
[^8]: Relatório de bens da UnB (obras de arte, código de material 5244000000001), fornecido pela professora da disciplina em 24/11/2026; vínculo em `dados/valores_cadastro_unb.csv` e conciliação em `resultados/conciliacao_cadastro_unb.md` (`codigos/cadastro_unb_relatorio.py`). Vínculo confirmado: número de registro do portal igual ao tombamento ou ao registro do SIPAT. Vínculo provável: procedência do portal correspondente à sigla de origem do SIPAT, com valor único no grupo. Nomes e matrículas do relatório foram descartados.
[^9]: Correlação entre fontes: `metodologia/identificacao.md` e `dados/conciliacao_patrimonial.csv`. Os tombamentos foram procurados em todos os metadados de todos os registros do acervo digital (`codigos/cadastro_patrimonial.py`). Sobre o software: TAINACAN. **Tainacan**: uma plataforma de repositórios flexível e poderosa para WordPress. [S. l.], 2026. Disponível em: https://tainacan.org/. Acesso em: 24 nov. 2026.
[^10]: PINTO, Tamine Alana Oliveira. **Classificação museológica e coleções etnográficas**: trajetória da Coleção Galvão da Casa da Cultura da América Latina da Universidade de Brasília. 2019. Trabalho de Conclusão de Curso (Graduação em Museologia), Universidade de Brasília, Brasília, 2019, p. 44 e 49; ENTIDADES e peles: desvendando máscaras dos povos originários: exposição do acervo da Casa da Cultura da América Latina. Brasília, DF: Ed. dos Autores, 2025. E-book. ISBN 978-65-01-60206-6.
""".format(**V)
    os.makedirs(os.path.join(RES, "nota_explicativa"), exist_ok=True)
    with open(os.path.join(RES, "nota_explicativa", "minuta_nota_explicativa.md"), "w", encoding="utf-8") as f:
        f.write(nota)
    for x in i15:
        print("  {}: {}".format(x[0], x[1]))


if __name__ == "__main__":
    main()
