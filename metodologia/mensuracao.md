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

## Abordagem de mercado por comparáveis (`codigos/comparaveis.py`)

1. Cada transação ou estimativa de obra comparável é registrada em `dados/comparaveis.csv`, com artista, família de técnica, título, técnica, dimensões, tiragem, data, casa de leilão, tipo de preço (arrematado, estimativa ou oferta), valores, moeda, indicação de prêmio do comprador e URL da fonte.
2. O script associa os comparáveis às obras da CAL do mesmo artista e da mesma família de técnica (serigrafia, gravura em metal, litografia, xilogravura, desenho, pintura, escultura).
3. Nível A: 3 ou mais transações realizadas e obra da CAL com dimensões e tiragem conhecidas; nível B: 3 ou mais transações realizadas; nível C: 1 ou 2 transações, ou só estimativas e ofertas.
4. Valor central: mediana das transações realizadas (nível C sem transação: ponto médio das estimativas). Intervalo: menor e maior valor entre transações e estimativas.
5. Moedas não são misturadas; a conversão para BRL deve usar a taxa da data de referência (por exemplo, PTAX do Banco Central), com a fonte registrada.
6. O resultado é gravado em `dados/evidencias_mensuracao.csv` (linhas automáticas, sem apagar as manuais) e o modelo é recalculado.

### Evidências registradas em 23/11/2026

| Artista e técnica | Comparável | Tipo | Valores | Fonte | Obras da CAL | Nível |
|---|---|---|---|---|---|---|
| Cícero Dias, serigrafia | Untitled, 1987, serigrafia sobre papel Arches, 50/50, Denise René Editions; Bonhams, Nova York, 22/02/2021 | Arrematado | Estimativa USD 600 a 800; arrematado USD 2.040 | art.salon (lote AID507301) e invaluable.com | 14 | C |
| Tarsila do Amaral, serigrafia | Floresta, 1972; 03/02/2026 | Estimativa | USD 300 a 600 | invaluable.com | 1 | C |

Limitações: o portal não informa título, dimensões nem tiragem dessas obras, o que impede ajustes por dimensão e tiragem (Regras, item 9.2); há um único comparável por grupo; não se sabe se o preço arrematado inclui prêmio do comprador; os valores estão em dólar. Por isso o resultado é faixa indicativa, não valor justo. Para as águas-fortes de Tarsila do Amaral, as gravuras de Clóvis Graciano e os desenhos de Athos Bulcão, as buscas de 23/11/2026 encontraram catálogos de leilão sem preço realizado, que não servem como evidência; essas obras seguem pendentes.

## Incerteza

Cada evidência pode trazer valor mínimo, central e máximo; o site e `dados/mensuracao_resumo.csv` mostram o intervalo e o valor agregado por base e categoria, que não representa o valor total do patrimônio da CAL (item 15).

## Registros sem mensuração monetária fundamentada

Registrados com justificativa na nota metodológica de cada item (item 9.4).

## Valor registrado no cadastro patrimonial (informação de comparação)

O cadastro patrimonial da UnB (Lista da CAL) atribui valor a cada uma das 232 obras de arte próprias, com total de R$ 1.765.385,00, mediana de R$ 5.000,00 e amplitude de R$ 60,00 a R$ 150.000,00. Esses valores não foram usados como mensuração dos registros do portal por três razões: (1) nenhum tombamento do cadastro aparece no portal, o que impede o vínculo item a item; (2) o cadastro não informa a base do valor, pois os campos de nota fiscal, empenho e fornecedor estão vazios e os bens foram migrados do SIPAT em 05/01/2021 (termo 209/2021); (3) o documento de ingresso indicado é um ato administrativo (ATO DO DECANATO DE ADMINISTRAÇÃO 145, ATO DA DGM 87), sem laudo de avaliação anexado. O total registrado aparece na evidenciação como valor oficialmente registrado, separado dos resultados acadêmicos (Regras, item 10). A média de R$ 7.609,42 por obra (R$ 1.765.385,00 ÷ 232) é apenas referência agregada e não é atribuída a obras individuais, pois isso seria estimativa arbitrária (item 9.4).

## Validação de casos (Produto 4)

`codigos/validacao_casos.py` examina nove bens (três de arte, três contemporâneos e três etnográficos, um de cada subcoleção Inicial, Galvão e Chocó) e grava `dados/validacao_casos.csv` e `resultados/validacao_casos.md`, com lacunas documentais, questões éticas ou de direitos, procedimentos complementares e conclusão de cada caso.
