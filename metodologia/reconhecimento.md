# Etapa II: Reconhecimento contábil

Pergunta orientadora (Regras, item 8): quais registros apresentam evidências suficientes para o reconhecimento contábil como ativos da UnB?

Fundamentação conferida em 24/11/2026 no texto publicado da NBC TSP Estrutura Conceitual (R1) e da NBC TSP 37, Ativo Imobilizado, ambas com vigência a partir de 1º/01/2027 e aplicadas antecipadamente, como pedem as Regras (item 19.2). Itens e fontes em `metodologia/fundamentacao_normativa.md`.

## Teste em duas etapas

**1. Definição de ativo** (Estrutura Conceitual (R1), item 5.6): recurso controlado no presente pela entidade como resultado de evento passado.

| Componente | Evidência usada | Fundamento | Coluna em `dados/reconhecimento.csv` |
|---|---|---|---|
| Recurso com potencial de serviços | Função museológica do acervo; o patrimônio cultural é exemplo de ativo com potencial de serviços | EC, itens 5.6A, 5.8 e 5.9 | `recurso_potencial_servicos` |
| Controle: propriedade legal | Ingresso por doação ou transferência, com data | EC, item 5.12(a) | `controle_propriedade_legal` |
| Controle: acesso | Situação "Localizado"; "Não localizado" e "Emprestado" ficam a verificar | EC, item 5.12(b) | `controle_acesso` |
| Controle: meios que assegurem o uso | Guarda, documentação e exposição pela CAL | EC, item 5.12(c) | `controle_meios_uso` |
| Evento passado | Doação ou transferência (transação sem contraprestação) | EC, item 5.13 | `evento_passado` |

Os indicadores de controle não são conclusivos isoladamente (EC, item 5.12); a presença no portal não basta (Regras, item 8). A definição é considerada atendida com acesso confirmado e ingresso documentado com data.

**2. Critérios de reconhecimento** (NBC TSP 37, item 6; EC, item 6.2): (a) provável potencial de serviços; (b) mensuração confiável. A mensuração é confiável com evidência de nível A ou B (Etapa III); a faixa indicativa de nível C tem incerteza elevada demais (EC, itens 6.7 e 6.8).

Classificação contábil: ativo imobilizado tangível (NBC TSP 37, item 5), classe "acervos do patrimônio cultural" (item 34(l)). Unidade de reconhecimento: o registro individual do catálogo (item 8). Obras em suporte digital ou de performance recebem alerta para confirmar a tangibilidade.

## Regras de decisão

| Situação | Classe (Regras, item 8) | Enquadramento normativo | Divulgação |
|---|---|---|---|
| Registro de evento (Memória Institucional) | Não reconhecimento fundamentado | Não satisfaz a definição de ativo (EC, item 5.6) | Nenhuma como ativo |
| Definição atendida e mensuração de nível A ou B | Reconhecimento sustentado pelas evidências | Reconhecer (NBC TSP 37, item 6), mensuração inicial pelo custo atribuído (itens 12 e 13) | NBC TSP 37, item 69; NBC TSP 38, itens 54 e 55 |
| Definição atendida sem mensuração confiável | Não reconhecimento fundamentado | Não reconhecer: falha o item 6(b) (NBC TSP 37, item 7); reconhecer quando houver custo ou valor corrente confiável | NBC TSP 37, item 77: dificuldades de mensuração e relevância dos itens |
| Existência ou controle sem evidência suficiente | Pendente de verificação | Definição de ativo não confirmada (EC, itens 5.11 a 5.13) | Registro pendente (Regras, item 10(g)) |

## Resultado (24/11/2026)

| Grupo | Sustentado | Não reconhecimento fundamentado | Pendente |
|---|---:|---:|---:|
| Arte | 0 | 165 (161 pelo item 7 e 4 eventos) | 314 |
| Arte contemporânea | 0 | 155 | 7 |
| Etnográfica | 0 | 195 | 664 |
| A classificar | 0 | 695 (eventos) | 2 |
| **Total** | **0** | **1.210** | **987** |

Satisfazem a definição de ativo 511 registros (161 de arte, 155 de arte contemporânea e 195 etnográficos); todos ficam fora do balanço pelo item 7 da NBC TSP 37, porque nenhum tem, até aqui, três transações comparáveis realizadas (nível B). Dos 987 pendentes, 751 têm ingresso documentado mas localização não confirmada, 138 estão localizados sem forma ou data de ingresso e 98 carecem das duas informações.

Mudança em relação à versão de 23/11/2026: as 316 obras de arte e de arte contemporânea que satisfazem a definição de ativo passaram de "Pendente de verificação" para "Não reconhecimento fundamentado", porque o item 7 da NBC TSP 37 dá o tratamento exato desse caso (não reconhecer, divulgar pelo item 77 e reconhecer quando houver mensuração confiável).

## Conciliação com o cadastro patrimonial

O cadastro patrimonial da UnB (Lista da CAL, termo 209/2021) registra 242 obras de arte na localidade da CAL: 232 próprias, com valor registrado de R$ 1.765.385,00, e 10 marcadas como bem de terceiro (R$ 173.015,00). Os bens de terceiro não atendem ao critério de controle (EC, item 5.11). A denominação de todos os itens é genérica ("OBRA DE ARTE") e nenhum número de tombamento ou de registro do SIPAT aparece no portal. Se um registro do portal corresponder a um tombamento, o bem já está reconhecido pela UnB, e o valor registrado pode ser tratado como custo atribuído na aplicação inicial da NBC TSP 37 (item 87(a)); a conciliação item a item é, por isso, investigação indicada em todos os registros do Acervo. Arquivos: `codigos/cadastro_patrimonial.py` e `dados/conciliacao_patrimonial.csv` (agregados). A versão item a item, sem dados pessoais (`dados/cadastro_patrimonial_cal.csv`), fica fora do repositório público até a equipe confirmar a autorização de divulgação (Regras, item 12).

## Reprodução

`python3 codigos/reconhecimento.py` (lê `dados/inventario.csv`, `dados/metadados_completos.csv` e `dados/mensuracao.csv`; gera `dados/reconhecimento.csv` e `dados/reconhecimento_resumo.csv`).
