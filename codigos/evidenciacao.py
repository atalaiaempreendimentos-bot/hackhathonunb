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
    val = ler("validacao_casos.csv")
    log_data = (inv[0]["data_consulta"] if inv else "")

    grupos = ["Arte", "Arte contemporânea", "Etnográfica", "A classificar"]
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
            "fora_do_escopo": c_men.get("Fora do escopo (a confirmar no reconhecimento)", 0),
        })
    os.makedirs(os.path.join(RES, "demonstrativos"), exist_ok=True)
    with open(os.path.join(RES, "demonstrativos", "quadro_consolidado.csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(linhas[0].keys())); w.writeheader(); w.writerows(linhas)
    T = linhas[-1]

    # indicadores obrigatórios (item 15)
    rastreaveis = sum(1 for r in inv if r["url_registro"] and r["id_registro"] in rec and r["id_registro"] in mens)
    i15 = [
        ("Registros identificados", ind.get("Registros identificados", ""), "Total de registros públicos no portal"),
        ("Registros recuperados", ind.get("Registros recuperados", ""), "Total recuperado e organizado"),
        ("Cobertura (%)", ind.get("Cobertura (%)", ""), "Recuperados / identificados no universo digital"),
        ("Completude cadastral (%)", ind.get("Completude cadastral média (%)", ""), "Preenchimento médio das 13 variáveis principais"),
        ("Registros duplicados", ind.get("Registros com possível duplicidade", ""), "Possíveis duplicidades (conferência manual)"),
        ("Reconhecimento sustentado", T["reconhecimento_sustentado"], "Fundamentação suficiente para reconhecer"),
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

    # minuta de nota explicativa
    q = {l["grupo"]: l for l in linhas}
    vp = conc.get("Valor registrado das obras próprias (R$)", "0")
    vt = conc.get("Valor registrado dos bens de terceiro (R$)", "0")
    nota = """# Minuta de nota explicativa: bens culturais sob guarda da Casa da Cultura da América Latina (CAL/UnB)

**Resultado acadêmico do Hackathon CULTIVA UnB 2026. Não constitui registro contábil oficial da Universidade de Brasília (Regras, item 17.13).**

## a) Caracterização das coleções

A CAL guarda coleções de arte, arte contemporânea e etnográficas. O acervo digital público reúne {reg} registros em três coleções: Acervo ({acervo} registros, com as subcoleções Arte, Triangular, Inicial, Galvão e Chocó), Memória Institucional ({mem}) e Mobiliário moderno da UnB (1).[^1] A Coleção CNRC, listada no item 4.3 das Regras, não aparece em nenhum registro do portal.

## b) Quantidade de registros analisados

Foram analisados {reg} registros, {cob}% do universo digital identificável, com completude cadastral média de {comp}%.[^1] A cobertura digital não equivale ao patrimônio físico da CAL (Regras, item 4.4).

## c) Critérios de reconhecimento

Cada registro foi examinado quanto a existência, controle, potencial de serviços, natureza e condições de reconhecimento, inclusive mensuração confiável.[^2] Resultado: {sust} registros com reconhecimento sustentado, {nao} com não reconhecimento fundamentado (dos quais {mem_n} são registros de eventos e {etno_n} são bens etnográficos sem mensuração monetária confiável) e {pend} pendentes de verificação. {defs} registros atendem à definição de ativo, com existência confirmada e controle documentado.

## d) Bases de mensuração

Na ausência de custo histórico (os ingressos registrados no portal são doações e transferências), a base proposta para obras de arte é o valor justo ou o valor operacional corrente, estimado pela abordagem de mercado com obras comparáveis.[^3] Para bens de comunidades tradicionais não se atribui valor monetário por padrão (Regras, item 4.3).

## e) Quantidade de ativos com mensuração fundamentada

{fund} registros. Há {faixa} obras com faixa indicativa (nível C de evidência), que não constitui valor justo.[^4]

## f) Montantes estimados

Valor agregado das mensurações fundamentadas: {vfund}. Faixas indicativas, somadas por moeda e sem conversão: {fsoma}.[^4] Esses montantes não representam o valor total do patrimônio cultural da CAL (Regras, item 15).

Para comparação, o cadastro patrimonial da UnB registra, na localidade da CAL, {obras_cad} obras de arte, das quais {proprias} próprias, com valor registrado de {vp}, e {terc} marcadas como bem de terceiro ({vt}).[^5] Nenhum número de tombamento desse cadastro aparece no acervo digital, o que impede vincular os valores registrados às obras do portal.

## g) Registros pendentes de reconhecimento ou mensuração

{pend} registros pendentes de reconhecimento e {mpend} pendentes de mensuração. As pendências mais frequentes são a localização atual não informada no portal e a ausência de transações comparáveis.[^2][^3]

## h) Incerteza

As estimativas trazem intervalo (mínimo e máximo) e nível de evidência (A a D). Os comparáveis disponíveis são poucos, e o portal não informa dimensões nem tiragem das obras, o que impede os ajustes do item 9.2 das Regras.[^4]

## i) Restrições patrimoniais, culturais e documentais

Bens etnográficos sujeitos a restrições culturais e éticas (Regras, item 4.3); fotografias com direitos reservados (Lei nº 9.610/1998); {terc} bens no cadastro marcados como de terceiros; 39 registros do portal com situação "Não localizado" e 10 "Emprestado".[^2][^5]

## j) Limitações dos resultados

Certificado TLS do portal vencido em {data}; coleta realizada sem verificação do certificado. Triagem de grupos automática e sujeita a revisão. Regras de reconhecimento e mensuração propostas pela equipe, a validar com a fundamentação normativa e com a CAL.[^1][^2][^3]

---

[^1]: Identificação: extração pela API pública do Tainacan em {data} (`codigos/extrair_acervo_cal.py`); base padronizada em `dados/inventario.csv`, dicionário em `dados/dicionario_dados.md` e diagnóstico em `dados/diagnostico_qualidade.csv`.
[^2]: Reconhecimento: matriz aplicada a todos os registros (`codigos/reconhecimento.py`, `dados/reconhecimento.csv`). Atende à definição de ativo o registro com existência confirmada (situação "Localizado") e controle documentado (doação ou transferência com data); a presença no portal, sozinha, não basta (Regras, item 8). Reconhecimento sustentado exige ainda mensuração com evidência nível A ou B. Fundamento indicado nas Regras (item 19.2): NBC TSP Estrutura Conceitual (R1) e NBC TSP 37, Ativo Imobilizado (convergente à IPSAS 45); os parágrafos aplicáveis devem ser conferidos no texto das normas.
[^3]: Mensuração: base (custo histórico, valor justo ou valor operacional corrente; NBC TSP 38 / IPSAS 46) separada da técnica (abordagem de mercado ou de custo), conforme o item 9 das Regras (`codigos/mensuracao.py`, `metodologia/mensuracao.md`). Bens sem evidência suficiente recebem a classificação do item 9.4, sem valor arbitrário.
[^4]: Abordagem de mercado: comparáveis do mesmo artista e da mesma família de técnica, com fonte (`dados/comparaveis.csv`, `codigos/comparaveis.py`). Nível A: 3 ou mais transações e obra com dimensões e tiragem conhecidas; B: 3 ou mais transações; C: 1 ou 2 transações, ou só estimativas. Valor central: mediana das transações; intervalo: menor e maior valor. Moedas não convertidas sem taxa e fonte. Preço anunciado não é valor justo (Regras, item 9.2).
[^5]: Cadastro patrimonial: Lista da CAL fornecida pela equipe, com {cad} bens tombados em {dt_tomb} (termo {termo}), migrados do SIPAT; conciliação agregada em `dados/conciliacao_patrimonial.csv` (`codigos/cadastro_patrimonial.py`); a versão item a item, sem dados pessoais, fica fora do repositório público até a confirmação da autorização de divulgação (Regras, item 12).
""".format(
        reg=n(len(inv)), acervo=n(sum(1 for r in inv if r["colecao"] == "Acervo")), mem=n(sum(1 for r in inv if r["colecao"] == "Memória Institucional")),
        cob=str(ind.get("Cobertura (%)", "")).replace(".", ","), comp=str(ind.get("Completude cadastral média (%)", "")).replace(".", ","),
        sust=n(T["reconhecimento_sustentado"]), nao=n(T["nao_reconhecimento_fundamentado"]), pend=n(T["pendente_verificacao"]),
        mem_n=n(sum(1 for r in rec.values() if r["colecao"] == "Memória Institucional")),
        etno_n=sum(1 for r in rec.values() if r["grupo_sugerido"] == "Etnográfica" and r["classe_reconhecimento"] == "Não reconhecimento fundamentado"),
        defs=n(T["atende_definicao_sim"]), fund=n(T["mensuracao_fundamentada"]), faixa=n(T["faixa_indicativa"]),
        vfund=brl(T["valor_fundamentado_brl"]), fsoma=T["faixa_indicativa_soma"] or "nenhuma",
        obras_cad=conc.get("Obras de arte no cadastro", "?"), proprias=conc.get("Obras de arte próprias (sem marca de bem de terceiro)", "?"),
        vp=brl(vp), terc=conc.get("Obras marcadas como bem de terceiro", "?"), vt=brl(vt),
        mpend=n(T["mensuracao_pendente"] + T["faixa_indicativa"]), data=log_data,
        cad=conc.get("Bens no cadastro patrimonial localizados na CAL", "?"), dt_tomb=conc.get("Data de tombamento no sistema atual", "?"),
        termo=((ler("conciliacao_patrimonial.csv") or [{}])[0].get("observacao", "").replace("Lista da CAL; termo ", "") or "?"))
    os.makedirs(os.path.join(RES, "nota_explicativa"), exist_ok=True)
    with open(os.path.join(RES, "nota_explicativa", "minuta_nota_explicativa.md"), "w", encoding="utf-8") as f:
        f.write(nota)
    for x in i15:
        print("  {}: {}".format(x[0], x[1]))


if __name__ == "__main__":
    main()
