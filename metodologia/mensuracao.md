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
| B | 3 ou mais transações realizadas, com ajustes relevantes; ou 2 ou mais preços de entrada do próprio artista, vendas realizadas ou preços pedidos por galeria (regra 16, acrescentada em 25/11/2026) | Observáveis; o preço pedido por galeria é preço de entrada, não transação | Mensuração fundamentada (permite reconhecer) |
| C | Um único preço de entrada, ou só estimativas | Observáveis escassos ou não observáveis | Faixa indicativa: não reconhecer (Estrutura Conceitual (R1), item 6.8) |
| D | Insuficiente | Inexistentes | Sem mensuração monetária fundamentada |

Preços anunciados e estimativas não são tratados como preço de transação (item 9.2). A ausência de evidência não é substituída por estimativa arbitrária nem por valor gerado por inteligência artificial (itens 9.4 e 17.10).

Fora dos níveis A a D, há uma situação própria para o valor oficial: "Custo atribuído registrado no ato de incorporação". Ela vale para as obras doadas a partir de 2019 que o ato de incorporação publicado no Boletim de Atos Oficiais identifica uma a uma, com o valor fixado pela UnB após a avaliação da comissão especial (Instrução DAF nº 001/2018, art. 19, V). São 73 registros e R$ 897.600,00 (`codigos/vinculo_bao.py`; `metodologia/reconhecimento.md`). Quando o ato lista várias obras do mesmo doador com valores diferentes, a situação é "Custo atribuído registrado no ato de incorporação, por grupo": 45 registros de 16 doadores, R$ 307.085,00 no total, sem rateio entre as obras. Esses valores já estão no total do cadastro patrimonial e não entram no valor agregado estimado, que soma só as mensurações da equipe.

## Abordagem de mercado por comparáveis (`codigos/comparaveis.py`)

1. Cada transação ou estimativa de obra comparável é registrada em `dados/comparaveis.csv`, com artista, família de técnica, título, técnica, dimensões, tiragem, data, casa de leilão, tipo de preço (arrematado, estimativa ou oferta), valores, moeda, indicação de prêmio do comprador e URL da fonte.
2. O script associa os comparáveis às obras da CAL do mesmo artista e da mesma família de técnica (serigrafia, gravura em metal, litografia, xilogravura, desenho, pintura, escultura).
3. Nível A: 3 ou mais transações realizadas e obra da CAL com dimensões e tiragem conhecidas; nível B: 3 ou mais transações realizadas; nível C: 1 ou 2 transações, ou só estimativas e ofertas. A regra 16 amplia o nível B.
4. Valor central: mediana das transações realizadas (nível C sem transação: ponto médio das estimativas). Intervalo: menor e maior valor entre transações e estimativas.
5. Moedas não são misturadas; a conversão para BRL deve usar a taxa da data de referência (por exemplo, PTAX do Banco Central), com a fonte registrada.
6. O resultado é gravado em `dados/evidencias_mensuracao.csv` (linhas automáticas, sem apagar as manuais) e o modelo é recalculado.

Regras acrescentadas em 25/11/2026, registradas antes do uso dos resultados da busca em bases gratuitas:

7. Contam para os níveis A e B só as vendas realizadas do próprio artista, em casa de leilão ou galeria, com a obra em condição comparável. As colunas `artista_comparavel` e `tipo_comparavel` registram de quem é a venda; `artista` continua sendo o artista da obra da CAL.
8. Artista similar entra só como faixa indicativa (nível C) e só quando atende a quatro critérios: a mesma família de técnica; produção no mesmo período da obra da CAL; a mesma cena (Brasília e Centro-Oeste, ou a gravura brasileira do período); e nível de carreira comparável, sem retrospectiva em grande museu e sem recordes de leilão muito acima dos do artista da CAL. Artista que não atende aos quatro é descartado.
9. Venda em plataforma aberta (como o eBay) é transação realizada, mas sem verificação de autenticidade e estado; também fica no nível C.
10. Obra cuja condição não se confirma (por exemplo, tiragem em vida ou póstuma não identificada) fica no nível C, mesmo com três vendas do artista. É o caso das nove águas-fortes de Tarsila do Amaral doadas pelo Banco Central em 1997, sem título, tiragem nem dimensões no portal.
11. Valores em moeda estrangeira são convertidos para BRL pela PTAX de venda do Banco Central na data da venda (ou no último dia útil anterior), com a taxa e a data registradas na observação.
12. O valor do ato de incorporação publicado prevalece sobre qualquer mensuração da equipe. Na subcoleção Triangular, contrapartida provável da camada A2, que já está no balanço, a mensuração da equipe aparece só como informação e não leva ao reconhecimento, para não contar a mesma obra duas vezes (Regras, item 10).

Regras acrescentadas em 25/11/2026 depois da busca, ao conferir os lotes na fonte:

13. Linhas com `tipo_comparavel` iniciado por "excluído" ficam em `dados/comparaveis.csv`, com o motivo na observação, mas fora da conta: edições produzidas muito depois do ingresso da obra da CAL, de outro período e de outro mercado (NBC TSP 38, itens 24 e 32); lotes cuja técnica a própria casa descreve de duas formas.
14. Quando o portal grafa o nome do artista de forma diferente do mercado, a identidade é inferida pela procedência e pela técnica. A evidência registra a diferença como limitação, a conferir na assinatura da obra.
15. Fora da Triangular, a mensuração da equipe leva ao reconhecimento só quando o vínculo provável com o cadastro é um bem tombado por R$ 0,01, custo simbólico que não é custo atribuído (NBC TSP 37, item 13): o valor de mercado é a base proposta para o custo atribuído na aplicação inicial (item 87(a)) e não se soma aos valores do cadastro. Sem esse vínculo, a obra pode já estar no balanço por valor registrado; o valor da equipe fica como informação.

Regra acrescentada em 25/11/2026 a pedido de Lucas, para aplicar só o que as normas exigem (a NBC TSP 37, item 6(b), pede mensuração confiável, sem fixar número de vendas):

16. O nível B também se alcança com dois ou mais preços de entrada do próprio artista na mesma família de técnica. Preço de entrada é a venda realizada em casa de leilão ou galeria ou o preço pedido por galeria: o valor corrente operacional é o preço que a UnB pagaria por obra equivalente (NBC TSP 38, item 25). O preço pedido não é transação (Regras, item 9.2); fica registrado como oferta, com a limitação de que pode ficar acima do preço de venda. Estimativa de leiloeiro não é preço. Com um único preço, a obra fica no nível C. O valor central é a mediana dos preços de entrada. Passam ao nível B Stoyan Tsanev (duas vendas) e Milan Dusek (dois preços de galeria); Maciej Babinski e Cícero Dias (uma venda cada) e Tarsila do Amaral (só estimativa) continuam no nível C.

### Evidências registradas em 23/11/2026

| Artista e técnica | Comparável | Tipo | Valores | Fonte | Obras da CAL | Nível |
|---|---|---|---|---|---|---|
| Cícero Dias, serigrafia | Untitled, 1987, serigrafia sobre papel Arches, 50/50, Denise René Editions; Bonhams, Nova York, 22/02/2021 | Arrematado | Estimativa USD 600 a 800; arrematado USD 2.040 | art.salon (lote AID507301) e invaluable.com | 14 | C |
| Tarsila do Amaral, serigrafia | Floresta, 1972; 03/02/2026 | Estimativa | USD 300 a 600 | invaluable.com | 1 | C |

Limitações: o portal não informa título, dimensões nem tiragem dessas obras, o que impede ajustes por dimensão e tiragem (Regras, item 9.2); há um único comparável por grupo; não se sabe se o preço arrematado inclui prêmio do comprador; os valores estão em dólar. Além disso, o valor corrente operacional é preço de entrada e deveria incluir prêmio e custos de transação (NBC TSP 38, item 25(a)). Por isso o resultado é faixa indicativa, sem mensuração confiável. Para as águas-fortes de Tarsila do Amaral, as gravuras de Clóvis Graciano e os desenhos de Athos Bulcão, as buscas de 23/11/2026 encontraram catálogos de leilão sem preço realizado, que não servem como evidência; essas obras seguem pendentes.

### Busca em fontes externas (24/11/2026)

A busca procurou transações realizadas que levassem as obras pendentes ao nível A ou B. Cobriu os artistas com mais obras pendentes e as fontes de preços de arte de acesso público. Nenhum registro passou do nível C.

Só 638 registros podem receber mensuração pela abordagem de mercado: 475 da subcoleção Arte, 162 da Triangular e 1 de mobiliário. Os 860 bens de comunidades tradicionais ficam fora pelo item 4.3 das Regras; os 699 registros de evento não são ativos. Dos 638, 322 têm a definição de ativo pendente, entre eles as 14 serigrafias de Cícero Dias, 46 das 69 obras de Maciej Babinski e 29 das 50 de Milan Dusek. Para esses registros, um preço externo serviria apenas como informação de comparação. Os outros 316 atendem à definição, como as 81 obras de Zeila Navarro Swain, 23 de Babinski, 21 de Dusek e 10 de Tarsila do Amaral. O portal informa dimensões e tiragem de apenas 14 dos 638 registros, nenhum dos artistas com mais obras. O nível A só é possível para esses 14; para os demais, o teto é o nível B (três ou mais transações realizadas do mesmo artista na mesma família de técnica).

| Fonte | Acesso | O que informa | Resultado da consulta | Por que não alcança o nível B |
|---|---|---|---|---|
| Bolsa de Arte, cotações por artista | Aberto | Estimativa e último lance | 161 lotes de Cícero Dias, nenhum de gravura, litografia ou serigrafia; a página de cotações de Maciej Babinski (endereço `maciej-babinski`) não trouxe lotes | A própria página avisa que o último lance não significa arrematação; lance não é preço de transação (Regras, item 9.2) |
| Catálogo das Artes | Preço e fonte só para assinantes | Preço da última avaliação ou do último lance | Não consultado, por exigir assinatura | Mesmo com assinatura, o campo junta avaliação e lance, sem confirmar a venda |
| LeilõesBR | Aberto | Lotes em pregão e lance atual | Uma obra de Babinski em pregão (Martha Burle Escritório de Arte, leilão em 26/11/2026; lance de R$ 550,00 em 24/11/2026) | Mostra só leilões em andamento; o lance ainda não é venda |
| iArremate | Aberto | Catálogos de leilões abertos | Os lotes de leilões encerrados ficam indisponíveis para consulta | Sem histórico público de arremates |
| Busca aberta na web (Invaluable, Art.Salon, casas de leilão internacionais) | Parcial | Estimativas e alguns preços realizados | Nenhuma venda realizada de Babinski, Dusek ou Swain; para serigrafia de Cícero Dias, apenas o lote da Bonhams já registrado em `dados/comparaveis.csv` | Menos de três transações realizadas por artista e família de técnica |

Os 623 registros pendentes de evidência continuam pendentes. Os 15 com faixa indicativa continuam no nível C. O valor agregado estimado segue em R$ 0,00.

Caminhos que podem produzir evidência mais forte, a decidir pela equipe:

1. Documentos da própria UnB: valor de seguro nos termos de empréstimo das 10 obras cedidas a outros museus; valor declarado nos termos de doação das obras doadas.
2. Laudo de avaliação de leiloeiro ou avaliador para uma amostra, por exemplo as obras de Tarsila do Amaral e de Zeila Navarro Swain. Tem custo.
3. Assinatura do Catálogo das Artes, com a ressalva de que lance e avaliação não são preço de transação.
4. Tabelas de preço de galerias ou dos próprios artistas para a subcoleção Triangular, em geral de artistas vivos. Pela regra atual, oferta é dado não observável (NBC TSP 38, item 6) e leva no máximo ao nível C; usá-la para reconhecer exige mudar a regra e justificar a mudança.

Os níveis A a D são definidos hoje pelo número de transações realizadas. Um valor de seguro ou um laudo não se encaixa em nenhum deles. Antes de usar os caminhos 1 e 2, a equipe precisa definir em que nível essas evidências entram.

Ordem dos testes em `codigos/reconhecimento.py`, resolvida em 25/11/2026 pelas regras 12 e 15: o teste de mensuração confiável vem antes do ramo que mantém as obras de arte pendentes de vínculo com o cadastro. Uma obra que chegue ao nível A ou B pela equipe só é reconhecida quando o vínculo provável é um bem tombado por R$ 0,01; na Triangular e sem esse vínculo, o valor fica como informação. `codigos/evidenciacao.py` apresenta o valor da equipe em linha separada, sem somá-lo aos valores do cadastro.

Páginas consultadas em 24/11/2026: https://www.bolsadearte.com/artistas/cotacoes/cicero-dias/, https://www.bolsadearte.com/artistas/cotacoes/maciej-babinski/, https://www.catalogodasartes.com.br/, https://www.leiloesbr.com.br/ (busca por "babinski") e https://www.iarremate.com/.

### Busca em bases gratuitas nacionais e internacionais (25/11/2026)

A pedido de Lucas, a busca procurou vendas realizadas em bases gratuitas, no Brasil e no exterior, inclusive de artistas similares. Cada venda usada foi conferida na página do lote em 25/11/2026. Os valores em moeda estrangeira foram convertidos pela PTAX de venda do Banco Central na data da venda (regra 11). As URLs estão em `dados/comparaveis.csv`.

| Fonte | Acesso | Uso |
|---|---|---|
| Barnebys (preços realizados) | Aberto | Vendas de Tomás Sánchez (Skinner, Omega, Antiques Supermarket, Elite) e de Maciej Babinski (Capo); a página mostra estimativa e preço de martelo |
| Phillips, Rago e Waddington's | Aberto, página do lote | Vendas de Tomás Sánchez |
| Artmark (Sófia) | Aberto, página do lote | Vendas de Stoyan Tsanev |
| Oto Reifschneider Galeria de Arte | Aberto, loja on-line | Preços de oferta de Milan Dusek |
| LiveAuctioneers, Invaluable, eBay, MutualArt, Catálogo das Artes, LeilõesBR (leilões encerrados), Heritage, LotSearch, Dorotheum, Kunstveiling | Login, assinatura ou bloqueio | Sem uso |

| Artista (grafia do portal) | Obras da CAL com evidência | Evidência | Nível |
|---|---|---|---|
| Tomás Sánches (Tomás Sánchez, Cuba, 1948) | 1: registro 3609, serigrafia, doação da Embaixada de Cuba em 1993 | 5 vendas realizadas, de 2016 a 2025, de serigrafias de 1985, de 1994 ou sem data: de R$ 956,86 a R$ 3.957,80; mediana de R$ 2.916,27 | B |
| Stoyam Tzanev (Stoyan Tsanev, Bulgária, 1946–2019) | 1: registro 3597, água-forte e água-tinta, doação da Embaixada da Bulgária em 1993 | 2 vendas na Artmark em 2026, de gravuras em metal de 1979: € 1.600 e € 700 (R$ 9.659,84 e R$ 4.123,42) | B pela regra 16 (era C) |
| Milan Dusek | 42 gravuras em metal | Nenhuma venda; 2 preços de oferta da galeria (R$ 680,00 e R$ 4.800,00) | B pela regra 16 (era C) |
| Maciej Babinski | 38 gravuras em metal | 1 venda (Capo, 2015, US$ 40,00, ou R$ 103,42) | C |

Tomás Sánchez. Ficaram fora da conta, registradas em `dados/comparaveis.csv` (regra 13), as duas vendas de "Meditador en la orilla", edição de 2020 da Avant Arte (Phillips, 2021, US$ 2.016; Rago, 2024, US$ 4.032), de outro período; ficou fora também a venda da Elite (2015, US$ 700), cujo lote se diz litografia no título e serigrafia na descrição. Com as edições de 2020, a mediana seria R$ 3.548,38 (sete vendas), também no nível B. Não foram usadas duas vendas de "Orilla" descritas como litografia (Omega, 2016; Ansorena, 2021, com valor convertido pela própria Barnebys) nem uma estimativa da Cutler Bay sem página do lote. Limitações: o portal não informa título, ano, dimensões nem tiragem da obra da CAL, o que impede o nível A; quatro das cinco vendas são preços de martelo, sem o prêmio do comprador (NBC TSP 38, item 25(a)), o que pode subestimar o valor; a identidade do artista foi inferida pela procedência e pela técnica (regra 14); as vendas vão de 2016 a 2025, sem atualização para a data de referência.

Artista similar. Para as 81 obras de Zeila Navarro Swain (37 litografias), a busca achou vendas de artistas brasileiros do período com preço público na Barnebys: Glênio Bianchetti, Zoravia Bettiol, Augusto Rodrigues e Adir Sodré, de US$ 33,88 a US$ 425. Nenhum atende à regra 8, porque o portal não informa o ano das obras de Swain e não há como conferir o período. Ficam só como contexto, fora de `dados/comparaveis.csv`.

Outros artistas. Marcello Grassmann e Wagner Hermuche têm vendas públicas, mas de famílias de técnica diferentes das obras da CAL. Para Tarsila do Amaral, só apareceu um lote misto, com obra de Alfredo Volpi, sem preço separável. Não houve venda pública de Lenora de Barros, dos demais artistas da Triangular, de Tupynambá, de Tuneu nem de Vicente Martinez.

Resultado: 1 obra passa ao nível B e é reconhecida pela equipe, com valor agregado estimado de R$ 2.916,27, estimativa acadêmica que não se soma aos valores do cadastro. As obras com faixa indicativa passam de 15 para 96.

Com a regra 16, Stoyan Tsanev (1 obra) e Milan Dusek (42) também passam ao nível B: são 44 mensurações fundamentadas e valor agregado estimado de R$ 124.887,90, dos quais R$ 115.080,00 vêm das obras de Dusek, pela mediana de dois preços de galeria. Só a obra de Tomás Sánchez leva ao reconhecimento; as outras 43 ficam como informação até o vínculo com o cadastro ou a confirmação da definição de ativo (regra 15). As faixas indicativas passam a 53.

## Incerteza

Cada evidência pode trazer valor mínimo, central e máximo; o site e `dados/mensuracao_resumo.csv` mostram o intervalo e o valor agregado por base e categoria, que não representa o valor total do patrimônio da CAL (item 15).

## Registros sem mensuração monetária fundamentada

Registrados com justificativa na nota metodológica de cada item (item 9.4).

## Valor registrado no cadastro patrimonial (informação de comparação)

O cadastro patrimonial da UnB (Lista da CAL) atribui valor a cada uma das 232 obras de arte próprias, com total de R$ 1.765.385,00, mediana de R$ 5.000,00 e amplitude de R$ 60,00 a R$ 150.000,00. Esses valores não foram usados como mensuração dos registros do portal por três razões: (1) nenhum tombamento do cadastro aparece no portal, o que impede o vínculo item a item; (2) o cadastro não informa a base do valor, pois os campos de nota fiscal, empenho e fornecedor estão vazios e os bens foram migrados do SIPAT em 05/01/2021 (termo 209/2021); (3) o documento de ingresso indicado é um ato administrativo (ATO DO DECANATO DE ADMINISTRAÇÃO 145, ATO DA DGM 87), sem laudo de avaliação anexado. O total registrado aparece na evidenciação como valor oficialmente registrado, separado dos resultados acadêmicos (Regras, item 10). Na aplicação inicial da NBC TSP 37, em 1º/01/2027, a UnB pode tratar esses valores como custo atribuído, se não houver informação confiável sobre o custo (item 87(a)); a decisão exige antes conciliar cada tombamento com a obra física. Todas as 242 obras de arte do cadastro estão marcadas como não depreciáveis e sem vida útil informada, o que é coerente com a vida útil indefinida (NBC TSP 37, itens 52 e 53).

O relatório de bens da UnB com todas as obras de arte (1.127 bens; 1.009 nas localidades da CAL, R$ 2.266.832,63) registra 303 bens da CAL por R$ 0,01. Esse valor é simbólico: não representa preço de transação nem custo atribuído determinado por base de valor corrente (NBC TSP 37, itens 12 e 13; NBC TSP 38, item 10), e não é tratado como mensuração. O valor registrado de cada registro vinculado aparece no site apenas como informação do cadastro (`codigos/cadastro_unb_relatorio.py`). A média de R$ 7.609,42 por obra (R$ 1.765.385,00 ÷ 232) é apenas referência agregada e não é atribuída a obras individuais, pois isso seria estimativa arbitrária (item 9.4).

## Validação de casos (Produto 4)

`codigos/validacao_casos.py` examina nove bens (três de arte, três contemporâneos e três etnográficos, um de cada subcoleção Inicial, Galvão e Chocó) e grava `dados/validacao_casos.csv` e `resultados/validacao_casos.md`, com lacunas documentais, questões éticas ou de direitos, procedimentos complementares e conclusão de cada caso.
