#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Produto 4 do Hackathon CULTIVA UnB 2026: validação aprofundada de casos (Regras, item 6.3).

Nove bens escolhidos entre os registros processados: três obras de arte, três contemporâneas e três
etnográficos (um de cada subcoleção: Inicial, Galvão, Chocó). Critérios de escolha: registro mais
completo, situação "Localizado", fotografia e, nas obras de arte, existência de comparáveis de mercado.

Gera dados/validacao_casos.csv e resultados/validacao_casos.md com o exame documental de cada caso
(identificação, reconhecimento, mensuração, evidências, lacunas e conclusão). O exame técnico físico
(dimensões, tiragem, conservação, autenticidade) depende de verificação presencial na CAL.
"""
import csv
import os

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
DADOS = os.path.join(RAIZ, "dados")

CASOS = [
    ("3102", "Obra de arte", "Comparável de mercado realizado (Bonhams, 2021)"),
    ("3599", "Obra de arte", "Comparável apenas por estimativa"),
    ("3600", "Obra de arte", "Artista com mercado, sem comparável com preço realizado"),
    ("21032", "Obra contemporânea", "Registro mais completo da coleção Triangular"),
    ("20966", "Obra contemporânea", "Fotografia contemporânea com dimensões e tiragem"),
    ("11924", "Obra contemporânea", "Videoperformance: materialidade e direitos"),
    ("1613", "Objeto etnográfico", "Coleção Inicial, com dimensões e grupo indígena identificados"),
    ("2264", "Objeto etnográfico", "Coleção Galvão"),
    ("2359", "Objeto etnográfico", "Coleção Chocó"),
]
CAMPOS = ["Número de Registro", "Título", "Denominação", "Autoria", "Grupo indígena", "Coleção", "Data de produção",
          "Local de produção", "Material/Técnica/Suporte", "Dimensões", "Tiragem", "Forma de aquisição", "Data de aquisição",
          "Procedência", "Situação", "Estado de conservação", "Condições de reprodução"]
ESSENCIAIS = ["Título", "Autoria", "Data de produção", "Material/Técnica/Suporte", "Dimensões", "Tiragem", "Estado de conservação"]


def main():
    meta = {r["id_registro"]: r for r in csv.DictReader(open(os.path.join(DADOS, "metadados_completos.csv"), encoding="utf-8-sig"))}
    rec = {r["id_registro"]: r for r in csv.DictReader(open(os.path.join(DADOS, "reconhecimento.csv"), encoding="utf-8-sig"))}
    mens = {r["id_registro"]: r for r in csv.DictReader(open(os.path.join(DADOS, "mensuracao.csv"), encoding="utf-8-sig"))}
    linhas, md = [], ["# Validação aprofundada de casos (Produto 4)\n",
                      "Nove bens examinados (Regras, item 6.3): três obras de arte, três obras contemporâneas e três objetos etnográficos. "
                      "O exame é documental, com base no registro do portal, na matriz de reconhecimento e no modelo de mensuração; "
                      "o exame físico na CAL (medidas, tiragem, conservação e autenticidade) fica indicado como procedimento complementar.\n"]
    for n, (i, tipo, motivo) in enumerate(CASOS, 1):
        m, r, s = meta.get(i, {}), rec.get(i, {}), mens.get(i, {})
        if not m:
            continue
        titulo = m.get("Título") or m.get("Denominação") or m.get("titulo_item")
        lacunas = [c for c in ESSENCIAIS if not (m.get(c) or "").strip() or (m.get(c) or "").strip() == "False"]
        if tipo == "Objeto etnográfico":
            lacunas = [c for c in lacunas if c not in ("Autoria", "Tiragem", "Título")]
        etica = ("Bem de comunidade tradicional: não se presume mercadoria (Regras, item 4.3); a evidenciação é qualitativa e o uso "
                 "de imagem e informação deve respeitar restrições culturais." if tipo == "Objeto etnográfico" else
                 ("Obra contemporânea com suporte imaterial ou reprodutível: autenticidade e direitos dependem de certificado e contrato "
                  "com o artista." if "video" in (m.get("Material/Técnica/Suporte") or "").lower() else ""))
        valor = s.get("valor_exibicao") or "sem valor"
        conclusao = "{} Mensuração: {}{}.".format(
            r.get("classe_reconhecimento", ""), s.get("situacao", ""), " ({})".format(valor) if s.get("valor_exibicao") else "")
        proc = ["conferir no local a existência e o estado de conservação"]
        video = "video" in (m.get("Material/Técnica/Suporte") or "").lower()
        if tipo == "Objeto etnográfico":
            if "Dimensões" in lacunas or "Material/Técnica/Suporte" in lacunas:
                proc.append("registrar medidas e materiais do objeto, com orientação da CAL quanto a restrições culturais")
            proc.append("documentar a procedência e o contexto de coleta junto à CAL")
        elif video:
            proc.append("registrar formato, duração, edição e certificado de autenticidade da obra")
        elif "Dimensões" in lacunas or "Tiragem" in lacunas:
            proc.append("medir a obra e registrar tiragem e assinatura")
        if tipo == "Obra contemporânea" and not s.get("valor_exibicao"):
            proc.append("pesquisar ao menos 3 transações realizadas de obras do artista ou, na falta delas, documentar o custo "
                        "de reprodução ou de aquisição (abordagem de custo, Regras, item 9), pois obras contemporâneas raramente "
                        "têm comparáveis diretos (item 4.2)")
        elif tipo != "Objeto etnográfico" and not s.get("valor_exibicao"):
            proc.append("pesquisar ao menos 3 transações realizadas de obras comparáveis")
        if tipo != "Objeto etnográfico" and s.get("situacao") == "Faixa indicativa":
            proc.append("ampliar os comparáveis para 3 transações e converter a moeda pela taxa da data, com fonte")
        proc.append("localizar o número de tombamento no cadastro patrimonial")
        linhas.append({"caso": n, "id_registro": i, "tipo": tipo, "motivo_escolha": motivo, "numero_registro": m.get("Número de Registro", ""),
                       "titulo": titulo, "autoria_ou_grupo": m.get("Autoria") or m.get("Grupo indígena") or "",
                       "subcolecao": m.get("Coleção", ""), "existencia": r.get("existencia", ""), "controle": r.get("controle", ""),
                       "classe_reconhecimento": r.get("classe_reconhecimento", ""), "situacao_mensuracao": s.get("situacao", ""),
                       "valor_ou_faixa": s.get("valor_exibicao", ""), "nivel_evidencia": s.get("nivel_evidencia", ""), "fonte": s.get("fonte", ""),
                       "lacunas_documentais": "; ".join(lacunas), "questoes_eticas_ou_de_direitos": etica,
                       "procedimentos_complementares": ("; ".join(proc))[:1].upper() + ("; ".join(proc))[1:], "conclusao": conclusao, "url_registro": m.get("url_registro", "")})
        md.append("\n## Caso {}: {} ({})\n".format(n, titulo, tipo))
        md.append("Motivo da escolha: {}. Registro no portal: [{}]({}).\n".format(motivo, m.get("Número de Registro", i), m.get("url_registro", "")))
        md.append("| Campo | Informação do portal |\n|---|---|")
        for c in CAMPOS:
            v = (m.get(c) or "").strip()
            if v and v != "False":
                md.append("| {} | {} |".format(c, v.replace("|", "/")[:220]))
        md.append("\n**Reconhecimento.** Existência: {}. Controle: {}. Classe: {}. {}\n".format(
            r.get("existencia", ""), r.get("controle", ""), r.get("classe_reconhecimento", ""), r.get("justificativa", "")))
        md.append("**Mensuração.** {}: {}. Base: {}. Técnica: {}. Nível de evidência: {}.{}\n".format(
            s.get("situacao", ""), valor, s.get("base_mensuracao", ""), s.get("tecnica", ""), s.get("nivel_evidencia", ""),
            " Fonte: {}.".format(s.get("fonte")) if s.get("fonte") else ""))
        md.append("**Lacunas documentais.** {}\n".format("; ".join(lacunas) if lacunas else "nenhuma entre os campos essenciais"))
        if etica:
            md.append("**Questões éticas ou de direitos.** {}\n".format(etica))
        md.append("**Procedimentos complementares.** {}.\n".format(("; ".join(proc))[:1].upper() + ("; ".join(proc))[1:]))
        md.append("**Conclusão.** {}\n".format(conclusao))
    with open(os.path.join(DADOS, "validacao_casos.csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(linhas[0].keys())); w.writeheader(); w.writerows(linhas)
    os.makedirs(os.path.join(RAIZ, "resultados"), exist_ok=True)
    with open(os.path.join(RAIZ, "resultados", "validacao_casos.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(md) + "\n")
    print("Casos validados:", len(linhas))
    for l in linhas:
        print("  {} | {} | {} | {}".format(l["caso"], l["tipo"], l["titulo"][:40], l["conclusao"][:90]))


if __name__ == "__main__":
    main()
