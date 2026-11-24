# Etapa III: Mensuração e valoração

Pergunta orientadora (Regras, item 9): como mensurar os ativos culturais da CAL, considerando suas características, a finalidade da mensuração e a disponibilidade de evidências?

Base normativa indicada nas Regras: NBC TSP 38 e demais normas aplicáveis (reconhecimento pela NBC TSP 37 / IPSAS 45; mensuração pela NBC TSP 38 / IPSAS 46). Os parágrafos aplicáveis devem ser conferidos no texto das normas e citados no relatório.

## Modelo aplicado (`codigos/mensuracao.py`)

O modelo separa a base de mensuração (custo histórico, valor justo, valor operacional corrente) da técnica de estimativa (abordagem de mercado, abordagem de custo), como exige o item 9 das Regras. Cada registro recebe categoria, base, técnica, nível de evidência, situação e nota metodológica; nenhum registro fica sem situação.

| Categoria | Base proposta | Técnica | Situação sem evidência |
|---|---|---|---|
| Obra de arte | Valor justo ou valor operacional corrente, na ausência de custo histórico | Abordagem de mercado (transações comparáveis) | Pendente de evidência |
| Obra de arte contemporânea | Idem | Abordagem de mercado; abordagem de custo se não houver comparáveis | Pendente de evidência |
| Bem cultural de comunidade tradicional | Não monetizado por padrão (proposta da equipe; Regras, item 4.3) | Evidenciação qualitativa | Sem mensuração monetária fundamentada |
| Mobiliário de valor histórico | Custo histórico, se houver registro patrimonial com valor | Documentação patrimonial; custo ou mercado | Pendente de evidência |
| Registro documental (Memória Institucional) | Não aplicável até o reconhecimento | Não aplicável | Fora do escopo (a confirmar no reconhecimento) |
| Não classificado | A definir | A definir | Pendente de classificação |

O portal não informa nenhum valor monetário (custo, avaliação ou seguro). Os ingressos registrados são doação (946), transferência (365) ou não informados (886).

## Evidências e níveis

Valores entram exclusivamente por `dados/evidencias_mensuracao.csv`, com fonte obrigatória:

| Nível | Evidência | Situação resultante |
|---|---|---|
| A | Transação realizada de bem diretamente comparável | Mensuração fundamentada |
| B | Transações realizadas, com ajustes relevantes (item 9.2) | Mensuração fundamentada |
| C | Somente ofertas, catálogos ou avaliações indiretas | Faixa indicativa (não é valor justo) |
| D | Insuficiente | Sem mensuração monetária fundamentada |

Preços anunciados não são tratados como valor justo (item 9.2). A ausência de evidência não é substituída por estimativa arbitrária nem por valor gerado por inteligência artificial (itens 9.4 e 17.10).

## Incerteza

Cada evidência pode trazer valor mínimo, central e máximo; o site e `dados/mensuracao_resumo.csv` mostram o intervalo e o valor agregado por base e categoria, que não representa o valor total do patrimônio da CAL (item 15).

## Registros sem mensuração monetária fundamentada

Registrados com justificativa na nota metodológica de cada item (item 9.4).
