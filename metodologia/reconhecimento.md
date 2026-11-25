# Etapa II: Reconhecimento contábil

Pergunta orientadora (Regras, item 8): quais registros apresentam evidências suficientes para o reconhecimento contábil como ativos da UnB?

Fundamentação conferida em 24/11/2026 no texto publicado da NBC TSP Estrutura Conceitual (R1) e da NBC TSP 37, Ativo Imobilizado, ambas com vigência a partir de 1º/01/2027 e aplicadas antecipadamente, como pedem as Regras (item 19.2). Itens e fontes em `metodologia/fundamentacao_normativa.md`.

## Teste em duas etapas

**1. Definição de ativo** (Estrutura Conceitual (R1), item 5.6): recurso controlado no presente pela entidade como resultado de evento passado.

| Componente | Evidência usada | Fundamento | Coluna em `dados/reconhecimento.csv` |
|---|---|---|---|
| Recurso com potencial de serviços | Função museológica do acervo; o patrimônio cultural é exemplo de ativo com potencial de serviços | EC, itens 5.6A, 5.8 e 5.9 | `recurso_potencial_servicos` |
| Controle: propriedade legal | Ingresso por doação ou transferência, com data, ou tombamento confirmado no relatório de bens da UnB | EC, item 5.12(a) | `controle_propriedade_legal` |
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
| Obra de arte ou de arte contemporânea com definição atendida, sem mensuração própria (versão 2) | Pendente de verificação | Provável bem já reconhecido no cadastro patrimonial, sem vínculo obra a obra: concluir após o vínculo (NBC TSP 37, itens 6 e 7) | Registro pendente de vínculo (Regras, item 10(g)) |
| Bem do cadastro com tombamento, ingresso documentado e valor atribuído na incorporação | Reconhecimento sustentado pelas evidências | Custo atribuído na incorporação (NBC TSP 37, item 12; NBC TSP 38, item 10) | NBC TSP 37, item 69 |
| Bem do cadastro com valor de base desconhecida | Pendente de verificação | Confirmar a base ou mensurar pelo custo atribuído na aplicação inicial (NBC TSP 37, item 87(a)) | Valor registrado com ressalva |
| Bem do cadastro tombado por R$ 0,01 | Não reconhecimento fundamentado | Custo simbólico não é custo atribuído (NBC TSP 37, item 13): item 7 | NBC TSP 37, item 77 |
| Bem de terceiro sob guarda | Não reconhecimento fundamentado | Sem controle (EC, itens 5.11 e 5.12) | Restrição patrimonial (Regras, item 10(i)) |

## O funil

Cada registro recebe, na coluna `funil` de `dados/reconhecimento.csv`, a etapa em que sai do fluxo: (I) registro de evento, que não é bem; (II) definição de ativo não confirmada; (II) definição atendida, à espera do vínculo com bem já reconhecido no cadastro; (III) definição atendida sem mensuração confiável, divulgada em nota pelo item 77; (IV) reconhecido no balanço. O site mostra dois funis lado a lado, um para o acervo digital e outro para o cadastro patrimonial, porque as duas fontes não têm chave comum e não podem ser somadas.

### Fundamento normativo de cada passo do funil

Cada saída do funil tem uma norma que a justifica. A mesma tabela aparece no site, abaixo dos funis.

| Etapa | Fonte | Quem sai ou fica retido | Norma que fundamenta |
|---|---|---|---|
| I Identificar | Acervo digital | 699 registros de evento saem: não são bens | Ativo é recurso controlado pela entidade como resultado de evento passado (Estrutura Conceitual (R1), item 5.6). O registro de exposição ou evento não identifica um recurso individualizado nem é bem cultural de caráter museológico (Resolução Normativa Ibram nº 6/2021, art. 6º, I). |
| I Identificar | Cadastro patrimonial | Nenhum sai; 27 recentes não têm registro no acervo digital | Os bens recentes não têm o número de registro museológico, primeiro elemento do inventário (Resolução Normativa Ibram nº 6/2021, art. 7º, § 1º, I). |
| II Reconhecer | Acervo digital | 976 ficam pendentes: falta evidência de existência ou de controle | O controle é avaliado por indicadores (propriedade legal, acesso, meios de uso e direito ao potencial de serviços), e o recurso deve resultar de evento passado (Estrutura Conceitual (R1), itens 5.11 a 5.13). A presença no portal não basta para presumir o controle da UnB (Regras, item 8). |
| II Reconhecer | Cadastro patrimonial | 10 bens de terceiros saem (R$ 173.015,00) | Bem de terceiro sob guarda não é controlado pela UnB (Estrutura Conceitual (R1), itens 5.11 e 5.12) e é divulgado como restrição patrimonial (Regras, item 10(i)). |
| III Mensurar | Acervo digital | 316 aguardam o vínculo com bens já reconhecidos no cadastro; 206 etnográficos sem mensuração possível | Só se reconhece o item que pode ser mensurado com confiabilidade (NBC TSP 37, item 6(b)); o patrimônio cultural que satisfaz a definição de ativo sem mensuração confiável não é reconhecido e é divulgado (item 7). Objetos de comunidades tradicionais não são presumidos mercadoria (Regras, item 4.3), e a falta de evidência não é substituída por estimativa (item 9.4). |
| III Mensurar | Cadastro patrimonial | 455 com base do valor a confirmar; 303 com R$ 0,01 | O valor de R$ 0,01 é custo simbólico, que não é custo atribuído (NBC TSP 37, item 13); sem mensuração confiável, aplica-se o item 7. Valor registrado de base desconhecida não demonstra mensuração confiável (item 6(b)) e deve ser confirmado ou substituído pelo custo atribuído na aplicação inicial (item 87(a)). |
| IV Evidenciar | Acervo digital | 206 vão para a nota explicativa; 1.292 ficam listados como pendentes | Os itens não reconhecidos são divulgados com as dificuldades de mensuração e a sua relevância (NBC TSP 37, item 77); os registros pendentes constam da evidenciação (Regras, item 10(g)). |
| IV Evidenciar | Cadastro patrimonial | 258 no balanço (R$ 1.859.185,00); 303 vão para a nota explicativa; 455 com ressalva | Reconhecidos: NBC TSP 37, item 69, e NBC TSP 38, itens 54 e 55. Não reconhecidos: NBC TSP 37, item 77. Valores em revisão: ressalva, com o ajuste da aplicação inicial em resultados acumulados (NBC TSP 37, item 87(b); Regras, item 10(h)). |

Textos publicados conferidos em 24/11/2026 (`metodologia/fundamentacao_normativa.md`). A Estrutura Conceitual (R1), a NBC TSP 37 e a NBC TSP 38 vigoram a partir de 1º/01/2027 e são aplicadas antecipadamente (Regras, item 19.2).

## Resultado no acervo digital (24/11/2026, versão 2)

| Grupo | Sustentado | Não reconhecimento fundamentado | Pendente |
|---|---:|---:|---:|
| Arte | 0 | 0 | 476 |
| Arte contemporânea | 0 | 0 | 162 |
| Etnográfica | 0 | 206 | 654 |
| Registro de evento (não é bem) | 0 | 699 | 0 |
| **Total** | **0** | **905** | **1.292** |

Satisfazem a definição de ativo 522 registros. Desses, 316 (161 de arte e 155 da Triangular) provavelmente correspondem a bens já reconhecidos no cadastro e aguardam o vínculo obra a obra; 206 etnográficos (139 da Galvão e 67 da Inicial) seguem o item 7 da NBC TSP 37. Outros 976 não permitem concluir se satisfazem a definição: 766 têm ingresso documentado mas localização não confirmada, 137 estão localizados sem forma ou data de ingresso e 73 carecem das duas informações.

Mudanças em relação à versão 1 (24/11/2026), conforme o Parecer de Reconhecimento dos Ativos da CAL v1 (código anterior em `codigos/versoes_anteriores/reconhecimento_v1.py`):

1. As 316 obras de arte e de arte contemporânea com definição atendida passaram de "Não reconhecimento fundamentado" (item 7) para "Pendente de verificação": concluir que não se reconhecem contrariaria o cadastro, que provavelmente já as reconhece (Triangular: Lista da CAL; Arte: doações de pessoas físicas e do Banco Central).
2. Os 10 registros "Emprestado" da Coleção Galvão passaram a satisfazer a definição de ativo: o catálogo de 2025 informa 17 peças emprestadas ao Museu das Bandeiras (GO) e ao Museu do Descobrimento (Porto Seguro), e o empréstimo de saída é indicador de acesso (EC, item 5.12(b)) (ENTIDADES e peles, 2025).
3. A propriedade legal da Coleção Galvão passou a se apoiar na trajetória documentada: coleção formada na UnB, depositada no Centro Nacional de Referência Cultural em 1977 e devolvida em 2002 por termo de rescisão do acordo de guarda (PINTO, 2019, p. 44 e 49). A "Transferência" do portal é o fim da guarda, não uma aquisição. Ressalva: o trabalho registra cessão à Fundação Nacional Pró-Memória e pedido de reintegração (PINTO, 2019, p. 46-47); a titularidade deve ser confirmada no termo de 2002.
4. Coleção Chocó: sob a responsabilidade da CAL desde 1989, sem documento de ingresso (ENTIDADES e peles, 2025); segue pendente. Coleção Inicial: doada no FLAAC de 1987, enquanto o portal registra 1993 em 262 registros, inconsistência a conferir. Coleção CNRC: de propriedade do IPHAN, sob cessão de uso (PINTO, 2019, p. 49 e 54); fora do portal e do ativo da UnB.

## Resultado no cadastro patrimonial (24/11/2026)

`codigos/reconhecimento_cadastro.py` aplica o teste aos 1.026 bens do relatório de bens da UnB nas localidades da CAL e aos bens recentes (`dados/reconhecimento_cadastro_resumo.csv`; a versão bem a bem fica fora do repositório público):

| Camada | Bens | Valor registrado | Classe |
|---|---:|---:|---|
| A1. Doações de 2024 a 2026, com termo ou processo SEI e valor individual | 27 | R$ 113.800,00 | Reconhecimento sustentado pelas evidências |
| A2. Lista da CAL: obras próprias doadas em 2019 e 2020, por ato de ingresso | 231 | R$ 1.745.385,00 | Reconhecimento sustentado pelas evidências |
| A3. Outros bens com valor registrado, migrados do SIPAT sem data de ingresso | 455 | R$ 338.429,60 | Pendente de verificação (base do valor) |
| B. Bens tombados por R$ 0,01 (custo simbólico) | 303 | R$ 3,03 | Não reconhecimento fundamentado (itens 7 e 13) |
| D. Bens de terceiros | 10 | R$ 173.015,00 | Não reconhecimento fundamentado (sem controle) |
| **Total** | **1.026** | **R$ 2.370.632,63** | |

Memória de cálculo: 27 + 231 = 258 bens com reconhecimento sustentado; R$ 113.800,00 + R$ 1.745.385,00 = R$ 1.859.185,00. Valores oficialmente registrados pela UnB, não estimados pela equipe (Regras, item 10). Ressalvas: a base de cada valor (avaliação ou declaração do doador) está nos processos e atos de ingresso, não examinados; no ato 217, 80 obras têm o mesmo valor de R$ 5.000,00, o que sugere valor convencionado, a confirmar.

## Conciliação com o cadastro patrimonial

O cadastro patrimonial da UnB (Lista da CAL, termo 209/2021) registra 242 obras de arte na localidade da CAL: 232 próprias, com valor registrado de R$ 1.765.385,00, e 10 marcadas como bem de terceiro (R$ 173.015,00). Os bens de terceiro não atendem ao critério de controle (EC, item 5.11). A denominação de todos os itens é genérica ("OBRA DE ARTE") e nenhum número de tombamento ou de registro do SIPAT aparece no portal. Se um registro do portal corresponder a um tombamento, o bem já está reconhecido pela UnB, e o valor registrado pode ser tratado como custo atribuído na aplicação inicial da NBC TSP 37 (item 87(a)); a conciliação item a item é, por isso, investigação indicada em todos os registros do Acervo. Arquivos: `codigos/cadastro_patrimonial.py` e `dados/conciliacao_patrimonial.csv` (agregados). A versão item a item, sem dados pessoais (`dados/cadastro_patrimonial_cal.csv`), fica fora do repositório público até a equipe confirmar a autorização de divulgação (Regras, item 12).

## Vínculo com o relatório de bens da UnB

O relatório de bens da UnB com todas as obras de arte (código de material 5244000000001), fornecido pela professora da disciplina em 24/11/2026, permitiu vincular 27 registros do portal a 33 tombamentos, porque o número de registro desses registros é o próprio tombamento ou o registro do SIPAT; outros 249 têm vínculo provável por procedência (`codigos/cadastro_unb_relatorio.py`, `resultados/conciliacao_cadastro_unb.md`). O tombamento confirmado é evidência de propriedade legal (EC, item 5.12(a)) e passou a atender ao critério de controle; o vínculo provável não identifica o tombamento individual e não é usado como evidência de controle. Quase todos os bens vinculados estão registrados por R$ 0,01, valor simbólico que não constitui custo atribuído (NBC TSP 37, itens 12 e 13).

## Efeito da ausência de chave comum entre o portal e o cadastro

O acervo digital não registra o número de tombamento, e a Lista da CAL não registra título, autoria ou número do portal (`metodologia/identificacao.md`). Isso afeta o teste de reconhecimento em três pontos:

1. **Controle e existência.** O cadastro patrimonial é a principal evidência de propriedade legal (EC, item 5.12(a)) e de localização. Sem chave comum, o registro do portal não pode usá-la, e as Regras vedam presumir o controle pela presença no portal (item 8). Só os 27 registros com tombamento confirmado no relatório de bens ganharam essa evidência; boa parte dos 976 pendentes decorre dessa lacuna.
2. **Mensuração confiável (NBC TSP 37, item 6(b)).** A Lista da CAL traz valores registrados no ingresso por doação, com ato de ingresso: R$ 1.765.385,00 para 232 obras próprias. Com o vínculo obra a obra, o valor seria evidência de custo atribuído (NBC TSP 37, itens 11 a 13; NBC TSP 38, itens 7, 10 e 12(b)). Sem ele, o critério 6(b) não é atendido no registro, e os bens que satisfazem a definição de ativo seguem o item 7: não reconhecimento e divulgação pelo item 77. É o caso de 155 das 162 obras da subcoleção Triangular, a provável contrapartida da lista.
3. **Unidade de reconhecimento e dupla contagem.** As obras da lista já constam do cadastro da UnB com valor. Reconhecer registros do portal com valoração própria poderia contar o mesmo objeto duas vezes ou omitir obras que não estão no portal. Por isso os valores oficiais não são somados às estimativas acadêmicas (Regras, item 10).

A situação é reversível: o item 7 da NBC TSP 37 manda reconhecer o bem a partir da data em que o custo ou o valor corrente estiver disponível, e o item 87(a) admite o custo atribuído na aplicação inicial. Com os atos de doação, até 155 registros da Triangular podem passar a "Reconhecimento sustentado pelas evidências", com o valor já registrado na camada A2 do cadastro.

## Vínculo pelos atos de incorporação publicados (25/11/2026)

Os atos de doação estão públicos. A Instrução DAF nº 001/2018 da UnB, em vigor nas doações de 2019 e 2020, determina que o termo de doação traga especificação, quantidade e valores dos bens (art. 4º, parágrafo único) e que obras de arte passem por comissão de avaliação especial, com critérios objetivos de valoração (art. 19, V). A doação termina com um ato que incorpora o bem ao patrimônio (art. 21), cujo extrato é publicado no Boletim de Atos Oficiais (art. 11). Cada ato traz o tombamento, o valor e o doador de cada bem, na consulta pública de publicações do SEI da UnB.

Procedimento:

1. `codigos/atos_bao.py` baixa os atos encontrados pela busca "obra de arte doação" com publicação de 2018 a 2021 (96 publicações: 95 atos e a própria Instrução). A busca "incorporação doados" no mesmo período (143 publicações, quase todas de outros bens) acrescentou 2 atos com obras de arte. A coleta faz pausa de 1 s entre requisições (Regras, item 17.12) e grava `dados/atos_incorporacao_bao.csv` sem CPF, CNPJ, passaporte ou RG. As páginas originais ficam num cache fora do repositório.
2. `codigos/vinculo_bao.py` liga os registros do portal aos atos pelo nome do doador (procedência no portal) e pela ordem das datas: a doação no portal ocorre até 540 dias antes da publicação do ato, ou no mesmo ano ou no anterior quando o portal só informa o ano. O resultado está em `dados/vinculo_bao.csv`, um registro por linha, com o endereço de cada ato.

Resultado: 97 atos, 253 bens, R$ 1.836.095,00 (os 95 atos da primeira busca somam 246 bens e R$ 1.756.595,00). Dos 162 registros da Triangular, 145 têm vínculo:

| Tipo de vínculo | Registros | Doadores | O que se sabe | Valor |
|---|---|---|---|---|
| Um a um | 53 | 53 | Tombamento e valor da obra | R$ 721.700,00 |
| Valor único | 20 | 9 | Valor individual; tombamento entre os do mesmo doador | R$ 175.900,00 |
| Grupo | 45 | 16 | Só o total do doador | R$ 307.085,00 |
| Quantidade diferente | 27 | 4 | Pendente: o portal tem mais obras do doador do que os atos | R$ 45.600,00 (15 bens) |

Somam 73 os registros com valor individual (R$ 897.600,00). Outros 17 registros da Triangular não têm ato publicado no período: Lenora de Barros (6), Raquel Nava (4), Danielle Fonseca do Nascimento (3) e mais 4. Na direção contrária, 15 doadores dos atos não têm obra no portal: 120 bens, R$ 585.810,00, dos quais 90 do ato 217/2020 (herdeiros de Fayga Ostrower).

Os atos de 2019 e 2020 especificam só "OBRA DE ARTE", sem título. Por isso o vínculo se apoia em doador, data e quantidade e recebe o grau "forte", abaixo de "confirmado", que este projeto reserva ao vínculo por identificador. Seis vínculos foram conferidos no texto do ato (doador, tombamento e valor): dois um a um, os dois registrados à mão por grafia diferente e dois feitos pelo nome mais curto do doador.

Ressalvas:

- O total dos 95 atos da primeira busca é próximo do da camada A2 do cadastro (R$ 1.745.385,00 para 231 obras). A coincidência das obras depende de conferir os tombamentos dos atos na Lista da CAL.
- 10 registros dependem de grafia diferente do nome do doador, duas delas registradas no script (Claudio Felipe de Oliveira Creti e Cláudio Cretti; Luiz Renato Pera e Renato Pera). Cabe confirmar no termo de doação.
- 10 registros têm valores abaixo de R$ 200,00. A equipe precisa decidir se são simbólicos, como o R$ 0,01 (NBC TSP 37, item 13).
- O parecer da comissão de avaliação fica no processo do SEI e não foi examinado. A base de cada valor continua a confirmar.
- 22 das obras reconhecidas são videoarte, fotografia digital ou performance, já marcadas na classificação contábil para confirmar se o bem é tangível (NBC TSP 37, item 5).

Aplicação no funil (25/11/2026): os 73 registros com valor individual (um a um e valor único) recebem em `dados/mensuracao.csv` a situação "Custo atribuído registrado no ato de incorporação" (R$ 897.600,00), que `codigos/reconhecimento.py` aceita como mensuração confiável (NBC TSP 37, itens 6(b), 12, 13 e 87(a)). Os 71 que atendem à definição de ativo passam a "Reconhecimento sustentado pelas evidências" (R$ 862.600,00); os outros 2 (IDs 13984 e 19319) têm valor, mas a definição de ativo segue pendente. O ato 217/2020 (90 obras, R$ 481.100,00) e a distribuição dos atos por número de obras coincidem com a Lista da CAL, o que torna o vínculo fortemente compatível com a camada A2; a prova final é a conferência dos tombamentos. Esses valores já estão no total do cadastro: não são somados de novo nem entram no valor agregado estimado, reservado às mensurações da equipe (Regras, itens 10 e 15). Os 45 registros com vínculo por grupo recebem a situação "Custo atribuído registrado no ato de incorporação, por grupo" (16 doadores, R$ 307.085,00). Cada tombamento do doador tem valor próprio no cadastro, mas o ato não diz qual tombamento é qual obra; o valor individual não é rateado (Regras, item 9.4). O site mostra o total do grupo. Os 40 desses que atendem à definição de ativo também passam a reconhecidos: são 111 no total. Os 27 com quantidade diferente continuam pendentes.

## Reprodução

`python3 codigos/reconhecimento.py` e `python3 codigos/reconhecimento_cadastro.py` (este exige os arquivos locais do cadastro). O primeiro lê `dados/inventario.csv`, `dados/metadados_completos.csv` e `dados/mensuracao.csv`; gera `dados/reconhecimento.csv` e `dados/reconhecimento_resumo.csv`). O vínculo pelos atos publicados: `python3 codigos/atos_bao.py` (acessa a rede) e `python3 codigos/vinculo_bao.py`.

## Referências

ENTIDADES e peles: desvendando máscaras dos povos originários: exposição do acervo da Casa da Cultura da América Latina. Curadoria de Gustavo Hamilton Menezes. Brasília, DF: Ed. dos Autores, 2025. E-book (PDF). ISBN 978-65-01-60206-6. Disponível em: https://bdce.unb.br/wp-content/uploads/tainacan-items/18648/42894/af_entidades-e-peles_28x21cm_30jul25_isbn.pdf. Acesso em: 24 nov. 2026.

PINTO, Tamine Alana Oliveira. **Classificação museológica e coleções etnográficas**: trajetória da Coleção Galvão da Casa da Cultura da América Latina da Universidade de Brasília. Orientador: Clovis Carvalho Britto. 2019. 85 f. Trabalho de Conclusão de Curso (Graduação em Museologia), Faculdade de Ciência da Informação, Universidade de Brasília, Brasília, 2019. Disponível em: https://bdm.unb.br/bitstream/10483/23735/1/2019_TamineAlanaOliveiraPinto_tcc.pdf. Acesso em: 24 nov. 2026.
