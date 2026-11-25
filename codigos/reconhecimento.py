#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Etapa II do Hackathon CULTIVA UnB 2026: matriz de reconhecimento aplicada a todos os registros.

Lê   dados/inventario.csv, dados/metadados_completos.csv, dados/mensuracao.csv,
     dados/conciliacao_patrimonial.csv (opcional)
Gera dados/reconhecimento.csv e dados/reconhecimento_resumo.csv

Critérios (Regras, item 8), com a fundamentação conferida no texto publicado das normas
(metodologia/fundamentacao_normativa.md):
  Definição de ativo, Estrutura Conceitual (R1):
    - recurso com potencial de serviços (itens 5.6A, 5.8 e 5.9: o patrimônio cultural é exemplo);
    - controle no presente (itens 5.11 e 5.12), por quatro indicadores não conclusivos: (a) propriedade
      legal, (b) acesso ou capacidade de restringir o acesso, (c) meios que assegurem o uso para os
      objetivos, (d) direito legítimo ao potencial de serviços;
    - evento passado (item 5.13), inclusive transação sem contraprestação (doação, transferência).
  Critérios de reconhecimento, NBC TSP 37 (Ativo Imobilizado):
    - item 6(a): provável potencial de serviços; item 6(b): mensuração confiável (Estrutura Conceitual
      (R1), itens 6.2, 6.7 e 6.8);
    - item 7: patrimônio cultural tangível que satisfaz a definição de ativo, mas não o item 6(b), não é
      reconhecido e é divulgado conforme o item 77; deve ser reconhecido quando o custo ou o valor corrente
      estiver disponível;
    - item 8: unidade de reconhecimento por julgamento (aqui, o registro individual do catálogo);
    - itens 5 e 34(l): ativo imobilizado tangível, classe "acervos do patrimônio cultural".

Regras de decisão (proposta da equipe):
  1. Registro de evento (Memória Institucional): não satisfaz a definição de ativo (EC 5.6):
     "Não reconhecimento fundamentado".
  2. Definição de ativo atendida quando há acesso confirmado (situação "Localizado", EC 5.12(b)) e
     ingresso documentado por doação ou transferência com data (EC 5.12(a) e 5.13). Presença no portal
     não basta (Regras, item 8).
  3. Definição atendida e mensuração confiável (nível A ou B): "Reconhecimento sustentado pelas
     evidências" (NBC TSP 37, item 6), com mensuração inicial pelo custo atribuído (itens 12 e 13).
  4. Definição atendida sem mensuração confiável: "Não reconhecimento fundamentado" (NBC TSP 37, item 7),
     com divulgação do item 77 e reavaliação quando houver custo ou valor corrente confiável.
  5. Existência ou controle sem evidência suficiente: "Pendente de verificação" (EC 5.11 a 5.13).
"""
import csv
import os

AQUI = os.path.dirname(os.path.abspath(__file__))
DADOS = os.path.join(os.path.dirname(AQUI), "dados")
SUST, NAO, PEND = "Reconhecimento sustentado pelas evidências", "Não reconhecimento fundamentado", "Pendente de verificação"
REF_BASE = "Regras, item 8; NBC TSP Estrutura Conceitual (R1), itens 5.6 a 5.13 e 6.2; NBC TSP 37, itens 5 a 8 e 34(l)"
CLASSE = "Ativo imobilizado, classe acervos do patrimônio cultural (NBC TSP 37, itens 5 e 34(l))"
CONC = ("conciliar com o cadastro patrimonial: se o bem corresponder a um tombamento, já está reconhecido pela UnB e o "
        "valor registrado pode ser tratado como custo atribuído na aplicação inicial (NBC TSP 37, item 87(a))")

COLS = ["id_registro", "colecao", "subcolecao", "grupo_sugerido", "titulo", "autoria_origem",
        "recurso_potencial_servicos", "controle_propriedade_legal", "controle_acesso", "controle_meios_uso",
        "evento_passado", "existencia", "controle", "potencial_servicos", "beneficios_economicos",
        "atende_definicao_ativo", "classificacao_contabil", "unidade_reconhecimento", "criterio_6a", "criterio_6b",
        "condicao_mensuracao", "vinculo_cadastro", "classe_reconhecimento", "enquadramento_normativo",
        "divulgacao_exigida", "justificativa", "investigacao_necessaria", "restricoes", "referencia_normativa"]


def main():
    inv = list(csv.DictReader(open(os.path.join(DADOS, "inventario.csv"), encoding="utf-8-sig")))
    meta = {r["id_registro"]: r for r in csv.DictReader(open(os.path.join(DADOS, "metadados_completos.csv"), encoding="utf-8-sig"))}
    mens = {r["id_registro"]: r for r in csv.DictReader(open(os.path.join(DADOS, "mensuracao.csv"), encoding="utf-8-sig"))}
    arq_c = os.path.join(DADOS, "conciliacao_patrimonial.csv")
    tem_cadastro = os.path.exists(arq_c)
    vinculo_txt = ("não vinculado: os tombamentos da Lista da CAL não aparecem no portal" if tem_cadastro
                   else "cadastro patrimonial não consultado")
    arq_v = os.path.join(DADOS, "valores_cadastro_unb.csv")
    cad = {r["id_registro"]: r for r in csv.DictReader(open(arq_v, encoding="utf-8-sig"))} if os.path.exists(arq_v) else {}

    def vinculo(i):
        c = cad.get(i)
        if not c:
            return vinculo_txt, ""
        if c["confianca"] == "Confirmado":
            t = "confirmado: tombamento(s) {}, valor registrado {}".format(c["tombamentos"], c["valor_exibicao"])
        elif c["confianca"] == "Provável":
            t = "provável: origem SIPAT {}, valor registrado {} (vínculo por procedência)".format(c["origem_sipat"], c["valor_exibicao"])
        else:
            return "sem vínculo com o relatório de bens da UnB" + (": " + c["observacao"] if c["observacao"] else ""), ""
        simb = (" O bem consta do cadastro patrimonial da UnB por {}, valor simbólico que não constitui custo histórico nem custo "
                "atribuído (NBC TSP 37, itens 12 e 13).".format(c["valor_exibicao"])) if float(c["valor_registrado"] or 0) <= 0.05 else ""
        return t, simb

    saida = []
    for l in inv:
        i = l["id_registro"]; m = meta.get(i, {}); ms = mens.get(i, {})
        r = {"id_registro": i, "colecao": l["colecao"], "subcolecao": l["subcolecao"], "grupo_sugerido": l["grupo_sugerido"],
             "titulo": (l["titulo"] or "").split(" | ")[0], "autoria_origem": l["autoria_origem"],
             "unidade_reconhecimento": "registro individual do catálogo (NBC TSP 37, item 8)"}
        if l["colecao"] == "Memória Institucional":
            na = "não aplicável (registro de evento)"
            r.update(recurso_potencial_servicos=na, controle_propriedade_legal=na, controle_acesso=na, controle_meios_uso=na,
                     evento_passado=na, existencia=na, controle=na, potencial_servicos=na, beneficios_economicos=na,
                     atende_definicao_ativo="não", classificacao_contabil="Não é ativo: registro documental de atividade institucional",
                     criterio_6a="não aplicável", criterio_6b="não aplicável", condicao_mensuracao="não aplicável",
                     vinculo_cadastro="não aplicável", classe_reconhecimento=NAO,
                     enquadramento_normativo="Não satisfaz a definição de ativo (Estrutura Conceitual (R1), item 5.6)",
                     divulgacao_exigida="Nenhuma como ativo; pode ser citado na caracterização das coleções",
                     justificativa="Registro de evento, exposição ou atividade da CAL (campos de evento, datas e equipe): não "
                                   "identifica recurso individualizado controlado pela UnB com potencial de serviços próprio.",
                     investigacao_necessaria="Verificar se algum registro corresponde a objeto físico (cartaz, catálogo) incorporado ao acervo.",
                     restricoes="", referencia_normativa="Regras, item 8; NBC TSP Estrutura Conceitual (R1), item 5.6")
            saida.append(r)
            continue

        falta = []
        sit = (m.get("Situação") or "").strip()
        if sit == "Localizado":
            acesso, ex, ex_ok = "atendido: bem localizado sob guarda da CAL (EC 5.12(b))", "atendido (situação: Localizado)", True
        elif sit == "Não localizado":
            acesso, ex, ex_ok = "não atendido: bem não localizado (EC 5.12(b))", "não confirmado (situação: Não localizado)", False
            falta.append("confirmar a existência física (bem não localizado)")
        elif sit == "Emprestado":
            acesso, ex, ex_ok = "a verificar: bem emprestado (EC 5.12(b))", "a verificar (situação: Emprestado)", False
            falta.append("verificar se o empréstimo é de saída (bem da UnB) ou de entrada (bem de terceiro)")
        else:
            foto = (m.get("Com imagem?") or "") == "Sim" or bool(l.get("url_foto"))
            acesso = "indício: catalogado{}, sem localização atual informada (EC 5.12(b))".format(" com fotografia" if foto else "")
            ex = "indício (catalogado com fotografia; localização atual não informada)" if foto else "não informado"
            ex_ok = False
            falta.append("confirmar a localização atual (inventário físico)")
        forma = (m.get("Forma de aquisição") or l.get("forma_aquisicao") or "").strip()
        data = (m.get("Data de aquisição") or "").strip()
        if forma in ("Doação", "Transferência") and data:
            prop = "indício forte: ingresso por {} em {} (EC 5.12(a))".format(forma.lower(), data)
            evento = "atendido: {} em {}, transação sem contraprestação (EC 5.13)".format(forma.lower(), data)
            ct, ct_ok = "atendido ({} em {})".format(forma, data), True
        elif forma:
            prop = "indício: ingresso por {}, sem data (EC 5.12(a))".format(forma.lower())
            evento = "parcial: {} sem data (EC 5.13)".format(forma.lower())
            ct, ct_ok = "indício ({} sem data)".format(forma), False
            falta.append("documentar a data e o ato de incorporação")
        elif data:
            prop = "não documentado: forma de aquisição não informada (EC 5.12(a))"
            evento = "parcial: ingresso em {}, sem forma de aquisição (EC 5.13)".format(data)
            ct, ct_ok = "indício (ingresso em {}, sem forma)".format(data), False
            falta.append("documentar a forma de aquisição (doação, transferência ou compra)")
        else:
            prop, evento = "não documentado (EC 5.12(a))", "não documentado (EC 5.13)"
            ct, ct_ok = "não documentado", False
            falta.append("documentar a forma de aquisição (doação, transferência ou compra)")
        c_cad = cad.get(i, {})
        if not ct_ok and c_cad.get("confianca") == "Confirmado" and c_cad.get("status_cadastro") not in ("ALIENADO",):
            prop = "indício forte: tombamento {} no cadastro patrimonial da UnB (EC 5.12(a))".format(c_cad["tombamentos"])
            evento = "atendido: incorporação ao patrimônio da UnB registrada no cadastro (EC 5.13)"
            ct, ct_ok = "atendido (tombamento {} no cadastro patrimonial)".format(c_cad["tombamentos"]), True
            falta = [f for f in falta if not f.startswith(("documentar a data", "documentar a forma"))]
        if l["colecao"] == "Mobiliário moderno da UnB":
            ex, ex_ok, acesso = "a verificar (código patrimonial informado no portal)", False, "a verificar (EC 5.12(b))"
            falta = ["localizar o código patrimonial no cadastro da UnB (não consta da Lista da CAL)"]
        definicao = "sim" if (ex_ok and ct_ok) else "pendente"
        sm, nivel = ms.get("situacao", ""), ms.get("nivel_evidencia", "")
        grupo = l["grupo_sugerido"]
        if sm == "Mensuração fundamentada":
            cm, c6b, ok6b = "atendida (nível {})".format(nivel), "atendido: mensuração confiável, nível {} (NBC TSP 37, item 6(b))".format(nivel), True
        elif sm == "Faixa indicativa":
            cm = "parcial (faixa indicativa, nível C)"
            c6b, ok6b = "não atendido: faixa indicativa de nível C, incerteza elevada demais (EC 6.8)", False
        elif sm == "Sem mensuração monetária fundamentada":
            cm = "inviável com as evidências disponíveis"
            c6b, ok6b = "não atendido: nenhuma técnica de mensuração aplicável sem presumir mercadoria (Regras, item 4.3)", False
        else:
            cm = "pendente de evidência"
            c6b, ok6b = "não atendido: sem custo ou valor corrente confiável disponível", False
        tecnica = (m.get("Material/Técnica/Suporte") or l.get("tecnica") or "").lower()
        classe_cont = CLASSE + ("; confirmar se o bem é tangível (obra em suporte digital ou performance, item 5)"
                                if any(k in tecnica for k in ("video", "vídeo", "digital", "performance")) else "")
        restr = []
        if grupo == "Etnográfica":
            restr.append("restrições culturais e éticas (Regras, item 4.3)")
        if "não podem ser baixadas" in (m.get("Condições de reprodução") or ""):
            restr.append("direitos reservados sobre as fotografias (Lei nº 9.610/1998)")
        refs = REF_BASE
        if definicao == "sim" and ok6b:
            classe = SUST
            enq = "Reconhecer (NBC TSP 37, item 6), com mensuração inicial pelo custo atribuído (itens 12 e 13)"
            div = "Divulgação por classe do item 69 da NBC TSP 37 e base, técnicas e dados de entrada (NBC TSP 38, itens 54 e 55)"
            just = ("Satisfaz a definição de ativo (acesso confirmado e ingresso documentado) e há mensuração confiável, "
                    "nível {}.".format(nivel))
            refs += "; NBC TSP 37, itens 12 e 13"
        elif definicao == "sim":
            classe = NAO
            enq = ("Não reconhecer: satisfaz a definição de ativo, mas não o critério de mensuração confiável do item 6(b) "
                   "(NBC TSP 37, item 7)")
            div = ("Nota explicativa, NBC TSP 37, item 77: (a) dificuldades na obtenção de mensuração confiável e (b) "
                   "relevância dos itens para os objetivos da UnB")
            if grupo == "Etnográfica":
                just = ("Satisfaz a definição de ativo (acesso confirmado e ingresso documentado), mas não há técnica de "
                        "mensuração aplicável sem tratar o objeto como mercadoria, o que as Regras vedam (item 4.3). Pelo item 7 "
                        "da NBC TSP 37, não se reconhece no balanço e divulgam-se as informações do item 77.")
            else:
                just = ("Satisfaz a definição de ativo (acesso confirmado e ingresso documentado), mas ainda não há custo nem "
                        "valor corrente mensurável com confiabilidade{}. Pelo item 7 da NBC TSP 37, não se reconhece por ora, "
                        "divulgam-se as informações do item 77 e a obra deve ser reconhecida quando houver evidência de nível A "
                        "ou B.".format(" (há apenas faixa indicativa de nível C)" if sm == "Faixa indicativa" else ""))
                falta.append("obter ao menos 3 transações realizadas de obras comparáveis (nível B) para reconhecer (item 7)")
            refs += "; NBC TSP 37, itens 6(b), 7 e 77"
        else:
            classe = PEND
            enq = ("Definição de ativo não confirmada: existência ou controle sem evidência suficiente (Estrutura Conceitual "
                   "(R1), itens 5.11 a 5.13)")
            div = "Evidenciar como registro pendente de verificação (Regras, item 10(g))"
            just = "Faltam informações para concluir: " + "; ".join(falta) + "."
            refs += "; NBC TSP Estrutura Conceitual (R1), itens 5.11 a 5.13"
        r.update(recurso_potencial_servicos="atendido: bem de acervo museológico, com potencial de serviços culturais e educacionais (EC 5.6A, 5.8 e 5.9)",
                 controle_propriedade_legal=prop, controle_acesso=acesso,
                 controle_meios_uso="atendido: guarda, documentação e exposição pela CAL (EC 5.12(c))",
                 evento_passado=evento, existencia=ex, controle=ct,
                 potencial_servicos="atendido: bem de acervo museológico (guarda, pesquisa, exposição, ensino)",
                 beneficios_economicos="não aplicável: finalidade cultural, sem geração de caixa (EC 5.8)",
                 atende_definicao_ativo=definicao, classificacao_contabil=classe_cont,
                 criterio_6a=("atendido: provável potencial de serviços (NBC TSP 37, item 6(a))" if definicao == "sim"
                              else "a confirmar com a existência e o controle"),
                 criterio_6b=c6b, condicao_mensuracao=cm, vinculo_cadastro=vinculo(i)[0], classe_reconhecimento=classe,
                 enquadramento_normativo=enq, divulgacao_exigida=div, justificativa=just + vinculo(i)[1],
                 investigacao_necessaria="; ".join(falta + [CONC]), restricoes="; ".join(restr), referencia_normativa=refs)
        saida.append(r)

    with open(os.path.join(DADOS, "reconhecimento.csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLS, extrasaction="ignore"); w.writeheader(); w.writerows(saida)
    resumo = []
    for c in (SUST, NAO, PEND):
        resumo.append({"indicador": c, "valor": sum(1 for r in saida if r["classe_reconhecimento"] == c)})
    for c in ("sim", "pendente", "não"):
        resumo.append({"indicador": "Atende à definição de ativo: " + c, "valor": sum(1 for r in saida if r["atende_definicao_ativo"] == c)})
    for e in sorted({r["enquadramento_normativo"] for r in saida}):
        resumo.append({"indicador": "Enquadramento: " + e, "valor": sum(1 for r in saida if r["enquadramento_normativo"] == e)})
    for g in sorted({r["grupo_sugerido"] for r in saida}):
        for c in (SUST, NAO, PEND):
            n = sum(1 for r in saida if r["grupo_sugerido"] == g and r["classe_reconhecimento"] == c)
            if n:
                resumo.append({"indicador": "{} | {}".format(g, c), "valor": n})
    with open(os.path.join(DADOS, "reconhecimento_resumo.csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["indicador", "valor"]); w.writeheader(); w.writerows(resumo)
    for x in resumo:
        print("  {}: {}".format(x["indicador"], x["valor"]))


if __name__ == "__main__":
    main()
