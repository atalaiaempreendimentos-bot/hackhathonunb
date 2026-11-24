# Fundamentação normativa dos modelos (conferida em 24/11/2026)

Textos consultados na íntegra, na versão publicada no Diário Oficial da União, em 24/11/2026:

| Norma | Ato e publicação | Vigência | Texto consultado |
|---|---|---|---|
| NBC TSP Estrutura Conceitual (R1) | Norma de 13/11/2025; DOU de 07/04/2026, seção 1, p. 199 a 209 | Exercícios iniciados a partir de 1º/01/2027 | https://legismap.com.br/leis-e-normas/norma-brasileira-de-contabilidade-nbc-tsp-estrutura-conceitual-r1-de-13-11-2025 |
| NBC TSP 37, Ativo Imobilizado (convergente à IPSAS 45) | Norma de 11/12/2025; DOU de 17/03/2026 | A partir de 1º/01/2027; revoga a NBC TSP 07 na mesma data | https://www.legisweb.com.br/legislacao/?id=492508 |
| NBC TSP 38, Mensuração (convergente à IPSAS 46) | Norma de 09/04/2026; DOU de 17/04/2026 | A partir de 1º/01/2027 (item 56), de forma prospectiva (item 58) | https://www.legisweb.com.br/legislacao/?id=494368 |

As três normas são as indicadas no item 19.2 das Regras e entram em vigor em 1º/01/2027. O modelo as aplica antecipadamente, como exigem as Regras. Os apêndices de orientação de aplicação da NBC TSP 37 (itens A1 em diante) e da NBC TSP 38 não constam das páginas consultadas e não foram usados.

## Itens usados e onde se aplicam

### Estrutura Conceitual (R1)

| Item | Conteúdo (síntese fiel) | Uso no modelo |
|---|---|---|
| 5.6 e 5.6A | Ativo é recurso controlado no presente pela entidade como resultado de evento passado; recurso é direito ao potencial de serviço ou à capacidade de gerar benefícios econômicos | Teste da definição de ativo (`reconhecimento.py`) |
| 5.8 e 5.9 | Potencial de serviços é a capacidade de prestar serviços que contribuam para os objetivos da entidade, sem necessariamente gerar caixa; ativos do patrimônio cultural são exemplo | Critério de potencial de serviços |
| 5.11 e 5.12 | Controle é a capacidade de usar o recurso; indicadores: (a) propriedade legal, (b) acesso ou capacidade de negar ou restringir o acesso, (c) meios que assegurem o uso para os objetivos, (d) direito legítimo ao potencial de serviços; indicadores não são conclusivos | Critério de controle, com os quatro indicadores |
| 5.13 | O recurso deve decorrer de transação ou evento passado, inclusive transação sem contraprestação | Evidência de ingresso (doação, transferência) |
| 6.2 | Reconhece-se o item que satisfaz a definição de elemento e pode ser mensurado de forma que observe as características qualitativas | Critérios de reconhecimento |
| 6.7 e 6.8 | Reconhecer exige atribuir valor monetário com base adequada; se a incerteza da estimativa for tão grande que comprometa relevância e representação fidedigna, o item não deve ser reconhecido; intervalos e evidenciação das técnicas ajudam | Limite de confiabilidade (níveis A e B) e tratamento das faixas indicativas |

### NBC TSP 37, Ativo Imobilizado

| Item | Conteúdo (síntese fiel) | Uso no modelo |
|---|---|---|
| 5 | Ativo imobilizado é ativo tangível mantido para uso na produção ou no fornecimento de bens ou serviços e que se espera usar por mais de um período | Classificação; obras em suporte digital exigem confirmar a tangibilidade |
| 6 | Reconhece-se se, e somente se, (a) for provável o fluxo de benefícios econômicos ou potencial de serviços e (b) o item puder ser mensurado confiavelmente | Critérios 6(a) e 6(b) da matriz |
| 7 | Itens tangíveis do patrimônio cultural que satisfazem a definição de ativo, mas não o item 6(b), não são reconhecidos e têm as informações do item 77 divulgadas; quando o custo ou o valor corrente estiver disponível, a entidade deve reconhecê-los a partir dessa data | Classe "Não reconhecimento fundamentado" com divulgação e reavaliação |
| 8 | A norma não define a unidade de reconhecimento; exige julgamento, podendo agregar itens individualmente insignificantes | Unidade adotada: o registro individual do catálogo |
| 11 a 13 | Mensuração inicial pelo custo; se adquirido sem contraprestação, pelo custo atribuído, segundo a NBC TSP 38; essa mensuração não é reavaliação | Base inicial das doações e transferências: custo atribuído |
| 24, 26 e 27 | Escolha, por classe, entre modelo do custo histórico e modelo do valor corrente; no valor corrente, item mantido por capacidade operacional é mensurado pelo valor corrente operacional, e por capacidade financeira, pelo valor justo | Base corrente: valor corrente operacional; modelo subsequente proposto: custo histórico |
| 34(l) | "Acervos do patrimônio cultural" é exemplo de classe de ativo imobilizado | Classe contábil proposta |
| 52 a 56 | Vida útil definida ou indefinida; item com vida útil indefinida não é depreciado; indefinido não é infinito e não pode depender de preservação sem probabilidade realista; revisão anual de indicações de redução ao valor recuperável | Proposta de vida útil indefinida para obras sob guarda museológica |
| 69 | Divulgação por classe: critérios de mensuração, métodos de depreciação, vidas úteis, valor contábil bruto e depreciação acumulada, conciliação do período | Nota explicativa, parte dos itens reconhecidos pela UnB |
| 76(d) | Encoraja divulgar o valor corrente quando materialmente diferente do valor contábil no modelo do custo | Comentário sobre as faixas indicativas |
| 77 | Patrimônio cultural não reconhecido por falta de mensuração confiável: divulgar (a) as dificuldades na obtenção de mensuração confiável e (b) a relevância dos itens para os objetivos da entidade | Nota explicativa, parte dos itens não reconhecidos |
| 78 | Gastos subsequentes reconhecidos com itens não reconhecidos seguem as divulgações dos itens 69 a 76 e 79 a 84 | Nota explicativa |
| 79 a 84 | Divulgações de mensuração pelo valor corrente (técnicas, dados observáveis ou não, sensibilidade) | Aplicáveis só se a classe for mensurada pelo valor corrente; item 83 se o valor corrente for divulgado |
| 87(a) | Na aplicação inicial, a entidade pode mensurar o patrimônio cultural pelo custo atribuído quando não houver informação confiável sobre o custo | Tratamento de transição dos valores do cadastro patrimonial |

### NBC TSP 38, Mensuração

| Item | Conteúdo (síntese fiel) | Uso no modelo |
|---|---|---|
| 6 | Definições: custo histórico, valor corrente operacional (valor que a entidade pagaria pelo potencial de serviço remanescente), valor justo (preço de saída em transação ordenada), custo atribuído (substituto do preço de transação), abordagens de mercado, custo e renda, dados de entrada observáveis e não observáveis, níveis 1, 2 e 3 | Vocabulário de bases, técnicas e dados de entrada |
| 7, 10 e 12(b) | Mensuração inicial pelo preço de transação, salvo quando não observável ou sem informação relevante, como em ativos doados ou transferidos sem custo; nesses casos usa-se custo atribuído, determinado por base de valor corrente | Doações e transferências |
| 17 e 18 | Após a mensuração inicial, escolha de política entre custo histórico e valor corrente, considerando as características do item | Modelo subsequente |
| 23 a 25 | Valor corrente operacional: pode ser obtido indiretamente, ajustando o preço de ativo semelhante aos aspectos únicos do ativo; é preço de entrada, inclui os custos necessários, reflete o uso atual e é específico da entidade | Ajustes dos comparáveis; preço de entrada com prêmio do comprador e custos |
| 29 a 31 | Valor justo: medida de saída, baseada no mercado, na perspectiva dos participantes do mercado | Distinção em relação à base adotada |
| 32 | Considerar características do ativo: condição, uso, localização e restrições à venda ou ao uso | Fatores de comparabilidade |
| 36 a 39 | Usar técnicas apropriadas com dados suficientes; técnicas não são bases; abordagens de mercado, custo e renda; com várias técnicas, avaliar a razoabilidade da faixa | Escolha de técnica por categoria |
| 42 a 45 | Abordagem de mercado (preços de transações de itens idênticos ou comparáveis); de custo (custo de reposição de ativo substituto de utilidade comparável, ajustado por obsolescência); de renda (fluxos futuros descontados) | Mercado para obras com artista identificado; custo para mobiliário; renda não aplicável |
| 54 e 55 | Divulgar base, técnicas e dados de entrada, segundo a norma específica | Nota explicativa |
