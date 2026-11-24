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
    if len(log_data) >= 16 and log_data[4] == "-":
        log_data = "{}/{}/{}, {}h{}".format(log_data[8:10], log_data[5:7], log_data[:4], log_data[11:13], log_data[14:16])

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
            "fora_do_escopo": c_men.get("Não aplicável (não é ativo)", 0),
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

    # minuta de nota explicativa (NBC TSP 37, itens 69 e 77; NBC TSP 38, itens 54 e 55; Regras, item 10)
    vp = conc.get("Valor registrado das obras próprias (R$)", "0")
    vt = conc.get("Valor registrado dos bens de terceiro (R$)", "0")
    termo = ((ler("conciliacao_patrimonial.csv") or [{}])[0].get("observacao", "").replace("Lista da CAL; termo ", "") or "?")
    R = list(rec.values())
    nao77 = lambda g: sum(1 for r in R if r["grupo_sugerido"] == g and r["enquadramento_normativo"].startswith("Não reconhecer"))
    pend = [r for r in R if r["classe_reconhecimento"] == "Pendente de verificação"]
    p_ex = sum(1 for r in pend if not r["existencia"].startswith("atendido") and r["controle"].startswith("atendido"))
    p_ct = sum(1 for r in pend if r["existencia"].startswith("atendido") and not r["controle"].startswith("atendido"))
    p_ambos = len(pend) - p_ex - p_ct
    faixa_obs = sum(1 for m in mens.values() if m.get("situacao") == "Faixa indicativa" and "observáveis (preços" in m.get("tecnica", ""))
    faixa_nobs = T["faixa_indicativa"] - faixa_obs
    V = dict(
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
        nemp=n(sum(1 for r in pend if r["existencia"].startswith("a verificar"))))
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

## 3 Acervos registrados no cadastro patrimonial da UnB [f] (NBC TSP 37, item 69)

O cadastro patrimonial da UnB registra, na localidade da CAL, {obras_cad} obras de arte, das quais {proprias} próprias, com valor registrado de {vp}, e {terc} marcadas como bem de terceiro ({vt}), que não compõem o ativo da UnB por falta de controle (Estrutura Conceitual (R1), item 5.11).[^5]

| Requisito do item 69 | Informação disponível na Lista da CAL |
|---|---|
| (a) critérios de mensuração do valor contábil bruto | Não informados: bens migrados do SIPAT em {dt_tomb} (termo {termo}); obras com nota fiscal, empenho ou fornecedor informados: {ndoc} |
| (b) métodos de depreciação | {ndep} obras marcadas como não depreciáveis |
| (c) vidas úteis | Obras com vida útil informada: {nvu}; tratamento coerente com vida útil indefinida (itens 52 e 53) |
| (d) valor contábil bruto e depreciação acumulada | {vp} (obras próprias); sem depreciação; saldos de início e fim de período não constam da Lista |
| (e) conciliação do período | Não disponível: a Lista não traz movimentações |

Nenhum número de tombamento desse cadastro aparece no acervo digital, o que impede vincular os valores registrados às obras catalogadas. Esse total é valor oficialmente registrado e não é somado às estimativas acadêmicas desta nota (Regras, item 10).

## 4 Itens do patrimônio cultural não reconhecidos [e, g, h] (NBC TSP 37, itens 7 e 77)

{n77} registros satisfazem a definição de ativo, com localização confirmada e ingresso documentado, mas não têm mensuração confiável e, por isso, não são reconhecidos.[^3]

| Classe | Itens | (a) Dificuldades na obtenção de mensuração confiável | (b) Relevância para os objetivos da entidade |
|---|---:|---|---|
| Obras de arte | {a77} | Poucas transações realizadas de obras comparáveis; portal sem dimensões e tiragem de muitas obras; preços em moeda estrangeira e sem indicação de prêmio do comprador, que integra o preço de entrada (NBC TSP 38, item 25(a)) | Acervo de referência para exposições da CAL e para atividades de ensino, pesquisa e extensão da Universidade[^6] |
| Obras de arte contemporânea | {c77} | Ausência de comparáveis diretos; obras em suporte digital, fotográfico ou de performance, com autenticidade e direitos dependentes de documentação do artista | Idem |
| Objetos etnográficos | {e77} | Nenhuma técnica aplicável sem tratar o objeto como mercadoria, o que as Regras vedam (item 4.3): a abordagem de custo exige substituto de utilidade comparável, inexistente para objeto único (NBC TSP 38, itens 43 e 44) | Documentação da cultura material de povos indígenas e comunidades tradicionais, com restrições culturais e éticas |

Não foram identificados gastos subsequentes reconhecidos com esses itens (NBC TSP 37, item 78). Os demais {mem_n} registros de não reconhecimento são eventos e atividades da Memória Institucional, que não satisfazem a definição de ativo (Estrutura Conceitual (R1), item 5.6).

## 5 Registros pendentes de verificação [g]

{pend} registros ainda não permitem concluir se satisfazem a definição de ativo: {p_ex} têm ingresso documentado, mas localização atual não confirmada (entre eles, {nloc} não localizados e {nemp} emprestados ou a verificar); {p_ct} estão localizados, mas sem forma ou data de ingresso; {p_ambos} carecem das duas informações. Pendências de mensuração: {mpend} registros.[^3]

## 6 Mensuração: base, técnicas, dados de entrada e incerteza [d, e, f, h] (NBC TSP 38, itens 54 e 55)

Registros com mensuração fundamentada: {fund}. Valor agregado das mensurações fundamentadas: {vfund}. Esse montante não representa o valor total do patrimônio cultural da CAL (Regras, item 15).

Há {faixa} obras com faixa indicativa (nível C), obtida pela abordagem de mercado (NBC TSP 38, item 42): {faixa_obs} a partir de uma única transação realizada (dados observáveis) e {faixa_nobs} a partir de estimativa de leiloeiro (dados não observáveis). Somadas por moeda, sem conversão: {fsoma}. A incerteza é elevada demais para reconhecimento (Estrutura Conceitual (R1), item 6.8).[^7] Como não há vínculo com o cadastro, não é possível avaliar se o valor corrente difere materialmente do valor registrado (NBC TSP 37, item 76(d)).

## 7 Restrições patrimoniais, culturais e documentais [i]

Bens etnográficos sujeitos a restrições culturais e éticas (Regras, item 4.3); fotografias com direitos reservados (Lei nº 9.610/1998); {terc} bens no cadastro marcados como de terceiros; {nestado} obra do cadastro em estado diferente de "Em uso"; registros do portal com situação "Não localizado" ou "Emprestado".

## 8 Limitações dos resultados [j]

Certificado TLS do portal vencido na data da coleta ({data}), feita sem verificação do certificado. Triagem de grupos automática e sujeita a revisão. Apêndices de orientação de aplicação da NBC TSP 37 e da NBC TSP 38 não consultados. Regras de decisão propostas pela equipe, a validar com a CAL e com a contabilidade da UnB.[^2][^3][^4]

---

[^1]: Normas conferidas no texto publicado em 24/11/2026: NBC TSP 37, de 11/12/2025 (DOU de 17/03/2026); NBC TSP 38, de 09/04/2026 (DOU de 17/04/2026); NBC TSP Estrutura Conceitual (R1), de 13/11/2025 (DOU de 07/04/2026). Itens e fontes em `metodologia/fundamentacao_normativa.md`.
[^2]: Identificação: extração pela API pública do Tainacan em {data} (`codigos/extrair_acervo_cal.py`); base em `dados/inventario.csv`, dicionário em `dados/dicionario_dados.md` e diagnóstico em `dados/diagnostico_qualidade.csv`.
[^3]: Reconhecimento: matriz aplicada a todos os registros (`codigos/reconhecimento.py`, `dados/reconhecimento.csv`). Controle avaliado pelos indicadores do item 5.12 da Estrutura Conceitual (R1): propriedade legal (ingresso por doação ou transferência com data), acesso (situação "Localizado") e meios de uso (guarda museológica). A presença no portal, sozinha, não basta (Regras, item 8). Reconhecimento sustentado exige mensuração de nível A ou B (NBC TSP 37, item 6(b)).
[^4]: Mensuração: `codigos/mensuracao.py` e `metodologia/mensuracao.md`. O valor corrente operacional é o valor que a entidade pagaria pelo potencial de serviço remanescente; é preço de entrada, reflete o uso atual e inclui os custos necessários (NBC TSP 38, itens 6 e 25). Sem evidência suficiente, o registro recebe a classificação do item 9.4 das Regras, sem valor arbitrário.
[^5]: Cadastro patrimonial: Lista da CAL fornecida pela equipe, com {cad} bens tombados em {dt_tomb} (termo {termo}), migrados do SIPAT; conciliação agregada em `dados/conciliacao_patrimonial.csv` (`codigos/cadastro_patrimonial.py`); a versão item a item, sem dados pessoais, fica fora do repositório público até a confirmação da autorização de divulgação (Regras, item 12).
[^6]: Constituição Federal de 1988, art. 207: as universidades obedecem ao princípio de indissociabilidade entre ensino, pesquisa e extensão. O potencial de serviços do patrimônio cultural está previsto nos itens 5.8 e 5.9 da Estrutura Conceitual (R1).
[^7]: Comparáveis do mesmo artista e da mesma família de técnica, com fonte (`dados/comparaveis.csv`, `codigos/comparaveis.py`). Nível A: 3 ou mais transações e obra com dimensões e tiragem conhecidas; B: 3 ou mais transações; C: 1 ou 2 transações, ou só estimativas. Valor central: mediana das transações; intervalo: menor e maior valor. Conversão para reais só com taxa e fonte da data de referência.
""".format(**V)
    os.makedirs(os.path.join(RES, "nota_explicativa"), exist_ok=True)
    with open(os.path.join(RES, "nota_explicativa", "minuta_nota_explicativa.md"), "w", encoding="utf-8") as f:
        f.write(nota)
    for x in i15:
        print("  {}: {}".format(x[0], x[1]))


if __name__ == "__main__":
    main()
