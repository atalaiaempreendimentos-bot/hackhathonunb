# Etapa I: Identificação e organização dos dados

Pergunta orientadora (Regras, item 7): quais bens culturais estão documentados no Acervo CAL e qual é a qualidade das informações disponíveis?

## Estratégia de recuperação

- Fonte: API REST pública do Tainacan, `https://www.acervocal.unb.br/wp-json/tainacan/v2/`, rotas `/collections` e `/collection/{id}/items` (96 itens por página, ordenados por ID).
- Procedimento: `codigos/extrair_acervo_cal.py`, com intervalo de 1 s entre requisições (Regras, item 17.12). Alternativa: `codigos/coletar_no_navegador.js` seguido de `--importar`.
- Data da consulta: 23/11/2026, 19h12 (horário de Brasília), registrada em cada resposta bruta (`dados/brutos/`) e em `dados/log_extracao.json`.
- Identificadores originais preservados: `id_registro` (ID do Tainacan), `url_registro`, número de registro da CAL (CAL.xxxx, CE.xxx) e código patrimonial, quando existem.
- Limitação de acesso: em 23/11/2026 o portal apresentava certificado TLS vencido; a coleta dispensou a verificação do certificado por decisão da equipe (dados públicos, somente leitura).

## Universo e cobertura

| Coleção do portal | Registros declarados | Recuperados |
|---|---:|---:|
| Acervo (subcoleções Arte, Triangular, Inicial, Galvão e Chocó) | 1.497 | 1.497 |
| Memória Institucional (eventos e atividades) | 699 | 699 |
| Mobiliário moderno da UnB | 1 | 1 |
| **Total** | **2.197** | **2.197** |

Cobertura: 100,0% do universo digital identificável. A Coleção CNRC, listada no item 4.3 das Regras, não aparece em nenhum registro público do portal; a ausência é registrada como limitação. A cobertura digital não equivale ao patrimônio físico da CAL (item 4.4): o cadastro patrimonial da UnB lista 242 obras de arte na localidade da CAL, e nenhum dos seus números de tombamento aparece no portal (`dados/conciliacao_patrimonial.csv`).

## Triagem por grupo (Regras, itens 4.1 a 4.3)

A triagem é uma árvore de decisão em três níveis (`triagem_grupo()` e `triagem_residual()` em `codigos/extrair_acervo_cal.py`, versão 1.2.0). Cada registro recebe o grupo e o critério aplicado (coluna `criterio_grupo`), o que permite a revisão registro a registro.

1. **Natureza do registro.** Antes de atribuir grupo, separa-se o que é bem do que é registro de atividade. Registros com metadados de evento (nome e tipo do evento) e sem técnica, materiais, dimensões ou número de patrimônio descrevem exposições, sessões de cinema, palestras e cursos da CAL, e não um objeto. Recebem o grupo "Registro de evento (não é bem)", fora dos três conjuntos do item 4 das Regras, e não satisfazem a definição de ativo (Estrutura Conceitual (R1), item 5.6).
2. **Grupo do bem**, nesta ordem:
   - subcoleções Inicial, Galvão, Chocó e CNRC: Etnográfica (Regras, item 4.3);
   - subcoleção Triangular: Arte contemporânea (registros CE.xxx, com fotografia, impressão digital, objetos e videoperformance; item 4.2);
   - subcoleção Arte: Arte (item 4.1);
   - coleção de mobiliário ou design: Arte, como objeto artístico de autoria identificada (item 4.1, "outros objetos artísticos");
   - demais registros: termos de categoria e técnica.
3. **Resíduo.** Registro sem subcoleção e sem termo indicativo recebe a subcoleção provável quando o seu número de registro está numa sequência que pertence a uma única subcoleção: os três números anteriores e os três posteriores, a até dez posições, todos da mesma subcoleção. O critério é marcado como "provável". O que não passar por nenhum nível fica "A classificar", com o motivo, para investigação complementar (Regras, seção 6, item 8). O valor `False`, que o Tainacan devolve quando a taxonomia não foi preenchida, é tratado como subcoleção não informada.

Resultado em 24/11/2026: Arte 476 (475 do Acervo e a Cadeira UnB, de Sérgio Rodrigues, 1962, da coleção Mobiliário moderno da UnB), Arte contemporânea 162, Etnográfica 860 (Inicial 349 e mais o ID 25320, Galvão 347, Chocó 163), Registro de evento (não é bem) 699 (toda a Memória Institucional) e A classificar 0.

Mudanças em relação à versão 1.1.3 (697 registros "A classificar"):

| Registros | Antes | Agora | Fundamento |
|---|---|---|---|
| 695 da Memória Institucional | A classificar | Registro de evento (não é bem) | 699 de 699 têm "Nome do evento"; nenhum tem técnica, materiais, dimensões ou número de patrimônio |
| 4 da Memória Institucional (IDs 3704, 3715, 3757 e 3815) | Arte, pelo termo "artes visuais" da categoria do evento | Registro de evento (não é bem) | São festivais, feiras e mostras, não obras; a regra por palavra-chave os confundia com bens |
| ID 26277, Cadeira UnB | A classificar | Arte | Mobiliário de design com autoria e data (Sérgio Rodrigues, 1962), item 4.1 das Regras |
| ID 25320, São João Batista (cerâmica, Goiás) | A classificar ("Coleção = False") | Etnográfica (provável) | Número de registro 0913212 na sequência 0913207 a 0913215, toda da subcoleção Inicial; no relatório de bens da UnB, o tombamento 913212 tem origem PNDA, a mesma procedência dos 23 registros da Inicial com procedência PNDA |

Os registros de evento não entram na contagem de bens, mas não são descartados: guardam o histórico de exposições da CAL (nome do evento, datas, local e, em 244 registros, os artistas expostos), que pode servir de evidência complementar sobre o uso das obras.

## Qualidade cadastral

Completude média das 13 variáveis principais (`dados/diagnostico_qualidade.csv`): 32,9% no total; Arte 45,9%; Arte contemporânea 66,3%; Etnográfica 24,7%; Registro de evento 26,6% (as variáveis principais descrevem objetos e, em geral, não se aplicam a eventos). Campos mais ausentes no total: localização (0,0%), número de patrimônio (0,0%), estado de conservação (7,0%), dimensões (11,8%) e categoria (13,9%). O campo "Situação" do portal (Localizado, Não localizado, Emprestado) informa a existência física, mas não o local de guarda. A triagem inicial do extrator (título, autoria e dimensões, mesmo vazias) apontou 427 registros (`dados/duplicidades.csv`), mas essa chave agrupa homônimos. Em 24/11/2026, `codigos/verificar_duplicidades.py` refinou a verificação:

| Critério | Grupos | Registros | Classificação |
|---|---:|---:|---|
| ID, URL, número de registro da CAL ou código patrimonial repetido | 0 | 0 | Nenhuma duplicidade de identificador |
| Memória Institucional: mesmo evento, datas, artista e local, descrição quase igual | 2 | 4 | Provável duplicidade (IDs 3963 e 3966; 4395 e 4409) |
| Memória Institucional: mesmo evento e datas, artista ou local diferentes | 3 | 6 | Registros distintos do mesmo evento |
| Acervo: mesma imagem com números de registro diferentes | 7 | 15 | A conferir (foto de conjunto ou cópia) |
| Acervo: mesma descrição (título, autoria, técnica, dimensões, tiragem) com números diferentes | 10 | 30 | A conferir (série ou catalogação repetida) |
| Acervo: mesmo título e autoria com números diferentes | 156 | 1.032 | Homônimos: objetos distintos |

Indicador do item 15 (registros possivelmente duplicados): 48, sendo 4 em provável duplicidade e 44 a conferir (um registro aparece nos dois critérios do Acervo). Lista em `dados/verificacao_duplicidades.csv`; relatório em `resultados/verificacao_duplicidades.md`.

## Padrão de referência: INBCM (Resolução Normativa Ibram nº 6/2021)

A identificação adota como referência os elementos de descrição do Inventário Nacional dos Bens Culturais Musealizados (INBCM), regulamentado pela Resolução Normativa Ibram nº 6, de 31 de agosto de 2021, em vigor desde 1º/10/2021 (INSTITUTO BRASILEIRO DE MUSEUS, 2021). O art. 7º, § 1º, define 15 elementos para o bem cultural de caráter museológico, 9 obrigatórios e 6 facultativos; o art. 6º, I, define esse bem como o bem material que, incorporado ao museu, perdeu as funções originais e ganhou outros valores simbólicos, artísticos, históricos ou culturais. Por essa definição, os registros de evento da Memória Institucional não são bens e ficam fora da contagem. O art. 5º estabelece que o INBCM não substitui os outros instrumentos de documentação do museu; aqui ele serve de régua para a qualidade da identificação.

Dois elementos resolvem as limitações apontadas abaixo: o inciso II, "outros números", informação facultativa de numerações anteriores, "tais como números antigos e números patrimoniais", e o inciso VII, "classificação", segundo o "Thesaurus" para Acervos Museológicos ou outros vocabulários controlados. O acervo digital da CAL não tem nenhum dos dois na coleção Acervo. A equipe propõe: (a) como outros números, o tombamento confirmado no relatório de bens da UnB (27 registros); (b) como classificação, o Tesauro de Objetos do Patrimônio Cultural nos Museus Brasileiros (FERREZ, 2016), sucessor do Thesaurus de 1987, aplicado pela denominação do portal com o vocabulário revisável `dados/vocabulario_tesauro.csv`. O vocabulário registra, para cada denominação, o termo e o código do Tesauro e se o termo foi localizado literalmente ou é equivalência a confirmar (Cesto, para Cesta; Gravura, de que só se localizou a subclasse 6.3). A classificação segue a função original do objeto, regra do próprio Tesauro.

Resultado nos 1.498 bens (`codigos/identificacao_inbcm.py`, `dados/identificacao_inbcm.csv`, `resultados/identificacao_inbcm.md`):

| Inciso | Elemento | Obrigatório | Campo do portal | Bens com o elemento |
|---|---|---|---|---:|
| I | Número de registro | sim | Número de Registro | 99,9% |
| II | Outros números | não | Código patrimonial (só no Mobiliário) | 0,1% (proposta: 1,8%) |
| III | Situação | sim | Situação | 46,6% |
| IV | Denominação | sim | Denominação | 100,0% |
| V | Título | não | Título | 11,9% |
| VI | Autor | sim | Autoria ou Grupo indígena | 81,2% |
| VII | Classificação | não | não existe | 0,0% (proposta: 62,6%) |
| VIII | Resumo descritivo | sim | Descrição | 0,1% |
| IX | Dimensões | sim | Dimensões | 17,4% |
| X | Material/técnica | sim | Material/Técnica/Suporte | 44,0% |
| XI | Estado de conservação | sim | Estado de conservação | 10,2% |
| XII | Local de produção | não | Local de produção | 41,4% |
| XIII | Data de produção | não | Data de produção | 11,5% |
| XIV | Condições de reprodução | sim | Condições de reprodução | 82,8% |
| XV | Mídias relacionadas | não | imagem do item | 83,2% |

Nenhum bem tem os 9 elementos obrigatórios. Dez registros têm a situação "Emprestado", fora das opções da norma (localizado, não localizado, excluído). A denominação é texto livre, com 293 formas distintas e variações da mesma palavra ("boneca" e "bonecas"); no Tainacan, campos como Autoria e Procedência já são taxonomias, e a classificação poderia sê-lo também. A classificação proposta alcança 938 bens: 675 na categoria 06, objetos de atividades artísticas; 98 na 13, equipamentos de caça e de guerra; 97 na 15, recipientes; 26 na 04; 24 na 03; 15 na 08; 3 na 02. Os demais 560 ficam "a classificar" (bordado, bastão, videoarte, xale, máscara e outros), porque o termo não foi localizado no Tesauro ou depende da função original, como a máscara, que pode ser acessório de traje (3.6.1) ou objeto ritual (9.2).

### Subgrupo da triagem: bens recentes do cadastro patrimonial

No relatório de bens da UnB, 27 bens têm denominação que descreve a obra (título, série, ano, material e técnica), em vez de "OBRA DE ARTE". Foram tombados de 13/11/2024 a 17/09/2026, somam R$ 113.800,00 e nenhum tem registro no acervo digital: não há número de registro museológico (inciso I), e o tombamento seria o inciso II. Formam um subgrupo da triagem, fora do acervo digital, no grupo Arte pela classe patrimonial: o código de material 5244000000001 tem o prefixo da natureza de despesa 4.4.90.52.44, obras de arte e peças para exposição (UNIVERSIDADE FEDERAL DE GOIÁS, 2019). Desses, 15 têm indício de obra contemporânea (uma instalação e 14 obras produzidas de 2010 a 2025), a confirmar. A denominação foi lida pelos elementos do INBCM que ela traz (título, data de produção, material/técnica, dimensões), sem completar o que não está escrito (`codigos/cadastro_unb_relatorio.py`, `dados/bens_recentes_cadastro.csv`). A mudança na forma de registrar a denominação, a partir de 2024, mostra que o cadastro patrimonial já pode carregar os dados que permitem a conciliação com o acervo digital.

Referências:

FERREZ, Helena Dodd. **Tesauro de Objetos do Patrimônio Cultural nos Museus Brasileiros**. [S. l.], 2016. Disponível em: https://cultura.rs.gov.br/upload/arquivos/carga20190600/17110012-tesauro-de-objetos-do-patrimonio-cultural-dos-museus-brasileiros.pdf. Acesso em: 24 nov. 2026.

INSTITUTO BRASILEIRO DE MUSEUS. Resolução Normativa Ibram nº 6, de 31 de agosto de 2021. Normatiza o Inventário Nacional dos Bens Culturais Musealizados. **Diário Oficial da União**: seção 1, Brasília, DF, 2 set. 2021. Disponível em: https://www.gov.br/museus/pt-br/assuntos/legislacao-e-normas/outros-instrumentos-normativos/resolucao-normativa-ibram-no-6-de-31-de-agosto-de-2021. Acesso em: 24 nov. 2026.

UNIVERSIDADE FEDERAL DE GOIÁS. **Código de natureza de despesa**: tabela de itens e subitens. Atualizada em 30 jan. 2019. Disponível em: https://files.cercomp.ufg.br/weby/up/355/o/C%C3%B3digo_de_natureza_de_despesa_-_Tabela_de_itens_e_subitens_ATUALIZADA_30-01-2019-38-45_(1).pdf. Acesso em: 24 nov. 2026.

## Correlação entre o acervo digital e o cadastro patrimonial

O Tainacan é um software livre, gratuito e de código aberto, desenvolvido como plugin para WordPress pela Universidade de Brasília, com apoio da UFG, do IBICT e do Ibram, para a gestão e a publicação de acervos digitais (TAINACAN, 2026). O Acervo Digital da CAL é uma instância desse software (UNIVERSIDADE DE BRASÍLIA, 2026), na qual a própria instituição define coleções, metadados e taxonomias. Nesse acervo, o identificador das obras é o número de registro museológico (CAL.xxxx e, na subcoleção Triangular, CE.xxx); o número de tombamento do sistema patrimonial da UnB não é informado, salvo na coleção Mobiliário moderno, que possui o metadado "Código patrimonial". A Lista da CAL, relação dos bens patrimoniais da UnB localizados na CAL, identifica cada obra apenas pelo tombamento, pela denominação genérica "obra de arte", pelo ato de ingresso e pelo valor. Os 243 tombamentos da lista foram procurados em todos os metadados dos 2.197 registros do portal, sem coincidência. Não há, portanto, chave comum que permita a conciliação obra a obra. A limitação decorre da forma de catalogação, e não do software, que admite metadados definidos pela instituição.

| Fonte | Conteúdo | Identificador disponível | Título, autoria e técnica | Valor |
|---|---|---|---|---|
| Acervo Digital da CAL (Tainacan) | 2.197 registros | Número de registro museológico (CAL.xxxx, CE.xxx); numérico em 41 registros | Sim | Não |
| Lista da CAL (cadastro patrimonial, sala 107) | 243 bens, 242 obras de arte | Tombamento, igual ao registro do SIPAT; ato de ingresso | Não ("OBRA DE ARTE") | Sim |
| Relatório de bens da UnB (obras de arte) | 1.127 bens | Tombamento, registro do SIPAT e origem | Não | Sim |

Resultado da conciliação (`codigos/cadastro_patrimonial.py`, `codigos/cadastro_unb_relatorio.py`):

| Par de fontes | Vínculos |
|---|---|
| Acervo Digital e Lista da CAL | Nenhum tombamento coincide (`dados/conciliacao_patrimonial.csv`) |
| Acervo Digital e relatório de bens | 27 registros confirmados por identificador (33 tombamentos); 249 prováveis por procedência; 1.221 sem vínculo (`resultados/conciliacao_cadastro_unb.md`) |
| Lista da CAL e relatório de bens | 241 dos 243 bens coincidem, com os mesmos valores |

Indícios de grupo, que não substituem o vínculo obra a obra: as 242 obras da Lista da CAL têm origem PESFIS (doação de pessoa física) e ingressaram por 87 atos da DGM ou do Decanato de Administração, de 2019 e 2020; no portal, os únicos registros com aquisição a partir de 2016 são 155 doações da subcoleção Triangular, de 86 doadores. O registro de evento 15117 descreve a exposição "Triangular: arte deste século", na Casa Niemeyer, a partir de 06/12/2019, como mostra das aquisições recentes incorporadas ao acervo da CAL. A lista, porém, tem mais obras que a subcoleção: o maior ato de ingresso reúne 90 obras (80 de R$ 5.000,00), sem doação equivalente no portal, onde nenhuma doação passa de 14 obras. A tentativa de parear obra a obra pela ordem dos atos e das doações não superou o resultado de ordenações aleatórias e foi descartada.

Encaminhamento: (1) solicitar à CAL ou à DGM os atos de doação, que nomeiam doador e obras, para vincular cada tombamento a um registro do portal; (2) incluir nas coleções da CAL no Tainacan o metadado "Número de tombamento", como já existe na coleção Mobiliário moderno, e registrar o ato de ingresso. A divergência entre registros patrimoniais e bens localizados é um dos problemas que motivam o desafio (Regras, item 2), e o metadado tornaria a conciliação automática para novos registros (item 11). O efeito sobre o reconhecimento está em `metodologia/reconhecimento.md`.

Referências:

TAINACAN. **Tainacan**: uma plataforma de repositórios flexível e poderosa para WordPress. [S. l.], 2026. Disponível em: https://tainacan.org/. Acesso em: 24 nov. 2026.

UNIVERSIDADE DE BRASÍLIA. Casa da Cultura da América Latina. **Acervo Digital da CAL**. Brasília, 2026. Disponível em: https://www.acervocal.unb.br/. Acesso em: 23 nov. 2026.

## Produtos

`dados/inventario.csv` (base padronizada), `dados/metadados_completos.csv` (todos os campos), `dados/dicionario_dados.md`, `dados/diagnostico_qualidade.csv`, `dados/duplicidades.csv`, `dados/indicadores.csv`, `dados/colecoes.csv`, `dados/log_extracao.json`.
