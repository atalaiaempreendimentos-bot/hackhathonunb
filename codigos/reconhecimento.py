#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Etapa II do Hackathon CULTIVA UnB 2026: matriz de reconhecimento aplicada a todos os registros.

Lê   dados/inventario.csv, dados/metadados_completos.csv, dados/mensuracao.csv,
     dados/conciliacao_patrimonial.csv (opcional)
Gera dados/reconhecimento.csv e dados/reconhecimento_resumo.csv

Critérios (Regras, item 8): existência do recurso; controle pela entidade; potencial de serviços;
benefícios econômicos, quando aplicáveis; evidências de aquisição, doação ou transferência; natureza e
classificação; condições para reconhecimento (inclusive mensuração confiável); investigação adicional.
Fundamento: Estrutura Conceitual (definição de ativo e critérios de reconhecimento) e NBC TSP 37 /
IPSAS 45; os parágrafos aplicáveis devem ser conferidos no texto das normas.

Regras de decisão (proposta da equipe, a revisar):
  1. Registro de evento ou atividade (coleção Memória Institucional): não identifica bem individualizado
     controlado; classe "Não reconhecimento fundamentado".
  2. Atende à definição de ativo quando há existência confirmada (situação "Localizado") e controle
     documentado (doação ou transferência com data); potencial de serviços: função museológica do acervo.
     A simples presença no portal não basta (item 8).
  3. Definição atendida + mensuração confiável (evidência nível A ou B) = "Reconhecimento sustentado".
  4. Definição atendida + mensuração monetária inviável com as evidências disponíveis (bens de
     comunidades tradicionais, item 4.3) = "Não reconhecimento fundamentado", com evidenciação em nota.
  5. Demais casos = "Pendente de verificação", com a lista do que falta.
"""
import csv
import os

AQUI = os.path.dirname(os.path.abspath(__file__))
DADOS = os.path.join(os.path.dirname(AQUI), "dados")
SUST, NAO, PEND = "Reconhecimento sustentado pelas evidências", "Não reconhecimento fundamentado", "Pendente de verificação"
REF = "Regras, item 8; NBC TSP Estrutura Conceitual (R1); NBC TSP 37 (Ativo Imobilizado) / IPSAS 45 (Property, Plant, and Equipment)"


def main():
    inv = list(csv.DictReader(open(os.path.join(DADOS, "inventario.csv"), encoding="utf-8-sig")))
    meta = {r["id_registro"]: r for r in csv.DictReader(open(os.path.join(DADOS, "metadados_completos.csv"), encoding="utf-8-sig"))}
    mens = {r["id_registro"]: r for r in csv.DictReader(open(os.path.join(DADOS, "mensuracao.csv"), encoding="utf-8-sig"))}
    conc = {}
    arq_c = os.path.join(DADOS, "conciliacao_patrimonial.csv")
    if os.path.exists(arq_c):
        conc = {r["indicador"]: r["valor"] for r in csv.DictReader(open(arq_c, encoding="utf-8-sig"))}
    vinculo_txt = ("não vinculado: os tombamentos da Lista da CAL não aparecem no portal" if conc
                   else "cadastro patrimonial não consultado")

    saida = []
    for l in inv:
        i = l["id_registro"]; m = meta.get(i, {}); ms = mens.get(i, {})
        r = {"id_registro": i, "colecao": l["colecao"], "subcolecao": l["subcolecao"], "grupo_sugerido": l["grupo_sugerido"],
             "titulo": (l["titulo"] or "").split(" | ")[0], "autoria_origem": l["autoria_origem"]}
        falta = []
        if l["colecao"] == "Memória Institucional":
            r.update(existencia="não aplicável (registro de evento)", controle="não aplicável", potencial_servicos="não aplicável",
                     beneficios_economicos="não aplicável", natureza="Registro documental de atividade institucional",
                     vinculo_cadastro="não aplicável", condicao_mensuracao="não aplicável", atende_definicao_ativo="não",
                     classe_reconhecimento=NAO,
                     justificativa="Registro de evento, exposição ou atividade da CAL (campos de evento, datas e equipe); não identifica "
                                   "bem individualizado controlado pela UnB com potencial de serviços próprio.",
                     investigacao_necessaria="Verificar se algum registro corresponde a objeto físico (cartaz, catálogo) incorporado ao acervo.")
            r["referencia_normativa"] = REF
            saida.append(r); continue

        sit = (m.get("Situação") or "").strip()
        if sit == "Localizado":
            ex, ex_ok = "atendido (situação: Localizado)", True
        elif sit == "Não localizado":
            ex, ex_ok = "não confirmado (situação: Não localizado)", False; falta.append("confirmar a existência física (bem não localizado)")
        elif sit == "Emprestado":
            ex, ex_ok = "a verificar (situação: Emprestado)", False; falta.append("verificar se o empréstimo é de saída (bem da UnB) ou de entrada (bem de terceiro)")
        else:
            foto = (m.get("Com imagem?") or "") == "Sim" or bool(l.get("url_foto"))
            ex = "indício (catalogado com fotografia; localização atual não informada)" if foto else "não informado"
            ex_ok = False; falta.append("confirmar a localização atual (inventário físico)")
        forma = (m.get("Forma de aquisição") or l.get("forma_aquisicao") or "").strip()
        data = (m.get("Data de aquisição") or "").strip()
        if forma in ("Doação", "Transferência") and data:
            ct, ct_ok = "atendido ({} em {})".format(forma, data), True
        elif forma:
            ct, ct_ok = "indício ({} sem data)".format(forma), False; falta.append("documentar a data e o ato de incorporação")
        else:
            ct, ct_ok = "não documentado", False; falta.append("documentar a forma de aquisição (doação, transferência ou compra)")
        if l["colecao"] == "Mobiliário moderno da UnB":
            ex, ex_ok = "a verificar (código patrimonial informado no portal)", False
            falta = ["localizar o código patrimonial no cadastro da UnB (não consta da Lista da CAL)"]
        definicao = "sim" if (ex_ok and ct_ok) else "pendente"
        sm = ms.get("situacao", "")
        if sm == "Mensuração fundamentada":
            cm = "atendida (nível {})".format(ms.get("nivel_evidencia"))
        elif sm == "Faixa indicativa":
            cm = "parcial (faixa indicativa, nível C)"
        elif sm == "Sem mensuração monetária fundamentada":
            cm = "inviável com as evidências disponíveis"
        else:
            cm = "pendente de evidência"
        grupo = l["grupo_sugerido"]
        natureza = {"Arte": "Bem cultural: obra de arte", "Arte contemporânea": "Bem cultural: obra de arte contemporânea",
                    "Etnográfica": "Bem cultural de comunidade tradicional (coleção etnográfica)"}.get(grupo, "Bem cultural a classificar")
        if definicao == "sim" and sm == "Mensuração fundamentada":
            classe, just = SUST, "Existência confirmada, controle documentado e mensuração com evidência nível {}.".format(ms.get("nivel_evidencia"))
        elif definicao == "sim" and sm == "Sem mensuração monetária fundamentada":
            classe = NAO
            just = ("Atende à definição de ativo (existência e controle documentados), mas não há mensuração monetária confiável e as "
                    "Regras vedam presumir que objetos de comunidades tradicionais sejam mercadorias (item 4.3). Não se reconhece no "
                    "balanço; evidencia-se em nota explicativa, com informações qualitativas.")
        else:
            classe = PEND
            if definicao == "sim":
                falta.append("obter evidência de mensuração nível A ou B" + (" (há apenas faixa indicativa)" if sm == "Faixa indicativa" else ""))
            just = "Faltam informações para concluir: " + "; ".join(falta) + "."
        restr = []
        if grupo == "Etnográfica":
            restr.append("restrições culturais e éticas (item 4.3)")
        if "não podem ser baixadas" in (m.get("Condições de reprodução") or ""):
            restr.append("direitos reservados sobre as fotografias (Lei nº 9.610/1998)")
        r.update(existencia=ex, controle=ct, potencial_servicos="atendido: bem de acervo museológico (guarda, pesquisa, exposição, ensino)",
                 beneficios_economicos="não aplicável: finalidade cultural, sem geração de caixa",
                 natureza=natureza, vinculo_cadastro=vinculo_txt,
                 condicao_mensuracao=cm, atende_definicao_ativo=definicao, classe_reconhecimento=classe, justificativa=just,
                 investigacao_necessaria="; ".join(falta + ["conciliar com o cadastro patrimonial (tombamento)"]),
                 restricoes="; ".join(restr), referencia_normativa=REF)
        saida.append(r)

    cols = ["id_registro", "colecao", "subcolecao", "grupo_sugerido", "titulo", "autoria_origem", "existencia", "controle",
            "potencial_servicos", "beneficios_economicos", "natureza", "vinculo_cadastro", "condicao_mensuracao",
            "atende_definicao_ativo", "classe_reconhecimento", "justificativa", "investigacao_necessaria", "restricoes",
            "referencia_normativa"]
    with open(os.path.join(DADOS, "reconhecimento.csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore"); w.writeheader(); w.writerows(saida)
    resumo = []
    for c in (SUST, NAO, PEND):
        resumo.append({"indicador": c, "valor": sum(1 for r in saida if r["classe_reconhecimento"] == c)})
    for c in ("sim", "pendente", "não"):
        resumo.append({"indicador": "Atende à definição de ativo: " + c, "valor": sum(1 for r in saida if r["atende_definicao_ativo"] == c)})
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
