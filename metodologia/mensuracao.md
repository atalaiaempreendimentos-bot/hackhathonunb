# Etapa III: Mensuração e valoração

Pergunta orientadora (Regras, item 9): como mensurar os ativos culturais da CAL, considerando suas características, a finalidade da mensuração e a disponibilidade de evidências?

Fundamentação conferida em 24/11/2026 no texto publicado da NBC TSP 37 (Ativo Imobilizado), da NBC TSP 38 (Mensuração) e da NBC TSP Estrutura Conceitual (R1), todas com vigência a partir de 1º/01/2027 e aplicadas antecipadamente, como pedem as Regras. Itens e fontes em `metodologia/fundamentacao_normativa.md`.

## Modelo normativo

| Decisão | Regra adotada | Fundamento |
|---|---|---|
| Mensuração inicial de bens recebidos por doação ou transferência | Custo atribuído, pois são transações sem contraprestação e não há preço de transação | NBC TSP 37, itens 11 a 13; NBC TSP 38, itens 7, 10 e 12(b) |
| Mensuração inicial de bens comprados | Custo histórico, com documento de custo | NBC TSP 37, item 11; NBC TSP 38, item 6 |
| Base de valor corrente que determina o custo atribuído | Valor corrente operacional: o acervo é mantido por sua capacidade operacional (potencial de serviço) e não financeira; é preço de entrada, específico da entidade, que inclui os custos necessários, como prêmio do comprador e custos de transação | NBC TSP 37, item 27; NBC TSP 38, itens 6, 10 e 23 a 25 |
| Valor justo | Não é a base adotada: é medida de saída na perspectiva dos participantes do mercado, adequada a itens mantidos por capacidade financeira | NBC TSP 37, item 27; NBC TSP 38, itens 29 a 31 |
| Técnica | Abordagem de mercado com comparáveis ajustados aos aspectos únicos da obra (condição, localização, restrições); abordagem de custo só quando há substituto de utilidade comparável; abordagem de renda não se aplica, pois o acervo não gera fluxos de caixa | NBC TSP 38, itens 24, 32 e 36 a 45 |
| Dados de entrada | Preços de transações realizadas de obras similares são dados observáveis; estimativas de leiloeiro são dados não observáveis | NBC TSP 38, item 6; NBC TSP 37, item 81(c) |
| Mensuração confiável | Níveis A ou B de evidência; nível C gera faixa indicativa, cuja incerteza impede o reconhecimento | NBC TSP 37, item 6(b); Estrutura Conceitual (R1), itens 6.7 e 6.8 |
| Mensuração subsequente (proposta) | Modelo do custo histórico para a classe "acervos do patrimônio cultural", com o custo atribuído como custo | NBC TSP 37, itens 24, 26 e 34(l) |
| Depreciação (proposta) | Vida útil indefinida para obras sob guarda museológica, sem depreciação, com revisão anual de indicações de redução ao valor recuperável; a conclusão não pode depender de preservação sem probabilidade realista | NBC TSP 37, itens 52 a 56 |
| Unidade de conta | O registro individual do catálogo; séries de itens insignificantes podem ser agregadas por julgamento | NBC TSP 37, item 8; NBC TSP 38, item 35 |
| Transição dos valores já registrados pela UnB | Na aplicação inicial, o patrimônio cultural pode ser mensurado pelo custo atribuído quando não houver informação confiável sobre o custo | NBC TSP 37, item 87(a) |

## Aplicação por categoria (`codigos/mensuracao.py`)

Cada registro recebe categoria, base, técnica, nível de evidência, situação e nota metodológica; nenhum registro fica sem situação.

| Categoria | Base | Técnica | Situação sem evidência |
|---|---|---|---|
| Obra de arte | Custo atribuído pelo valor corrente operacional | Abordagem de mercado (NBC TSP 38, itens 24, 32 e 42) | Pendente de evidência |
| Obra de arte contemporânea | Idem | Abordagem de mercado; abordagem de custo só se houver substituto de utilidade comparável, como tiragens reproduzíveis (itens 43 e 44) | Pendente de evidência |
| Bem cultural de comunidade tradicional | Custo atribuído pelo valor corrente operacional, se houver dados; não monetizado por padrão | Nenhuma: mercado presumiria mercadoria (Regras, item 4.3); custo exige substituto de utilidade comparável, inexistente para objeto único; renda não se aplica | Sem mensuração monetária fundamentada, com divulgação qualitativa (NBC TSP 37, item 77) |
| Mobiliário de valor histórico | Custo histórico, se houver documento; senão, custo atribuído pelo valor corrente operacional | Abordagem de custo (custo de reposição de peça de utilidade comparável, ajustado por obsolescência) ou de mercado | Pendente de evidência |
| Registro documental (Memória Institucional) | Não aplicável: não satisfaz a definição de ativo (Estrutura Conceitual (R1), item 5.6) | Não aplicável | Não aplicável (não é ativo) |
| Não classificado | A definir | A definir | Pendente de classificação |

O portal não informa nenhum valor monetário (custo, avaliação ou seguro). Os ingressos registrados são doação (946), transferência (365) ou não informados (886).

## Evidências e níveis

Valores entram exclusivamente por `dados/evidencias_mensuracao.csv`, com fonte obrigatória:

| Nível | Evidência | Dados de entrada (NBC TSP 38, item 6) | Situação resultante |
|---|---|---|---|
| A | 3 ou mais transações realizadas de obras similares e obra da CAL com dimensões e tiragem conhecidas | Observáveis | Mensuração fundamentada (permite reconhecer) |
| B | 3 ou mais transações realizadas, com ajustes relevantes | Observáveis | Mensuração fundamentada (permite reconhecer) |
| C | 1 ou 2 transações, ou só estimativas e ofertas | Observáveis escassos ou não observáveis | Faixa indicativa: não reconhecer (Estrutura Conceitual (R1), item 6.8) |
| D | Insuficiente | Inexistentes | Sem mensuração monetária fundamentada |

Preços anunciados e estimativas não são tratados como preço de transação (item 9.2). A ausência de evidência não é substituída por estimativa arbitrária nem por valor gerado por inteligência artificial (itens 9.4 e 17.10).

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

Limitações: o portal não informa título, dimensões nem tiragem dessas obras, o que impede ajustes por dimensão e tiragem (Regras, item 9.2); há um único comparável por grupo; não se sabe se o preço arrematado inclui prêmio do comprador; os valores estão em dólar. Além disso, o valor corrente operacional é preço de entrada e deveria incluir prêmio e custos de transação (NBC TSP 38, item 25(a)). Por isso o resultado é faixa indicativa, sem mensuração confiável. Para as águas-fortes de Tarsila do Amaral, as gravuras de Clóvis Graciano e os desenhos de Athos Bulcão, as buscas de 23/11/2026 encontraram catálogos de leilão sem preço realizado, que não servem como evidência; essas obras seguem pendentes.

## Incerteza

Cada evidência pode trazer valor mínimo, central e máximo; o site e `dados/mensuracao_resumo.csv` mostram o intervalo e o valor agregado por base e categoria, que não representa o valor total do patrimônio da CAL (item 15).

## Registros sem mensuração monetária fundamentada

Registrados com justificativa na nota metodológica de cada item (item 9.4).

## Valor registrado no cadastro patrimonial (informação de comparação)

O cadastro patrimonial da UnB (Lista da CAL) atribui valor a cada uma das 232 obras de arte próprias, com total de R$ 1.765.385,00, mediana de R$ 5.000,00 e amplitude de R$ 60,00 a R$ 150.000,00. Esses valores não foram usados como mensuração dos registros do portal por três razões: (1) nenhum tombamento do cadastro aparece no portal, o que impede o vínculo item a item; (2) o cadastro não informa a base do valor, pois os campos de nota fiscal, empenho e fornecedor estão vazios e os bens foram migrados do SIPAT em 05/01/2021 (termo 209/2021); (3) o documento de ingresso indicado é um ato administrativo (ATO DO DECANATO DE ADMINISTRAÇÃO 145, ATO DA DGM 87), sem laudo de avaliação anexado. O total registrado aparece na evidenciação como valor oficialmente registrado, separado dos resultados acadêmicos (Regras, item 10). Na aplicação inicial da NBC TSP 37, em 1º/01/2027, a UnB pode tratar esses valores como custo atribuído, se não houver informação confiável sobre o custo (item 87(a)); a decisão exige antes conciliar cada tombamento com a obra física. Todas as 242 obras de arte do cadastro estão marcadas como não depreciáveis e sem vida útil informada, o que é coerente com a vida útil indefinida (NBC TSP 37, itens 52 e 53). A média de R$ 7.609,42 por obra (R$ 1.765.385,00 ÷ 232) é apenas referência agregada e não é atribuída a obras individuais, pois isso seria estimativa arbitrária (item 9.4).

## Validação de casos (Produto 4)

`codigos/validacao_casos.py` examina nove bens (três de arte, três contemporâneos e três etnográficos, um de cada subcoleção Inicial, Galvão e Chocó) e grava `dados/validacao_casos.csv` e `resultados/validacao_casos.md`, com lacunas documentais, questões éticas ou de direitos, procedimentos complementares e conclusão de cada caso.
