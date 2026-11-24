# Relatório técnico-científico (minuta v1, 23/11/2026)

**Quanto vale o patrimônio cultural da UnB? Identificação, reconhecimento, mensuração e evidenciação dos ativos culturais do Acervo Digital da CAL/UnB**

Hackathon CULTIVA UnB 2026. PPGCont/UnB, Valoração de Ativos Culturais e Ambientais (318710), 2026/2. Profa. Fátima de Souza Freire e Prof. Jorge Madeira Nogueira. Equipe: Hugo Rodrigues Gomes, Yang Alfredo Florentino e Lucas Moura Nutels.

> Minuta gerada a partir dos resultados do repositório. Os trechos marcados com [a completar] dependem de leitura das fontes indicadas e de decisão da equipe. Resultados acadêmicos; não constituem registro contábil oficial da UnB (Regras, item 17.13).

## i. Introdução e problema de pesquisa

As universidades públicas guardam bens de valor histórico, artístico e cultural cujo reconhecimento e mensuração contábil enfrentam ausência de preços de mercado, singularidade dos objetos e documentação patrimonial incompleta (PPGCONT/UnB, 2026). O problema proposto é: como identificar, reconhecer, mensurar e evidenciar os ativos culturais da CAL/UnB de maneira sistemática, fundamentada, transparente e reproduzível, utilizando as NBC TSP convergentes às IPSAS e ferramentas computacionais?

## ii. Objetivos

Objetivo geral: desenvolver uma solução científica, contábil e tecnológica que processe todos os registros públicos do Acervo Digital da CAL nas quatro etapas contábeis, com rastreabilidade e possibilidade de aplicação a outros acervos Tainacan. Objetivos específicos: os do item 3.2 das Regras (a a k).

## iii. Fundamentação normativa e científica

Normas indicadas nas Regras (item 19.2) e conferidas no texto publicado em 24/11/2026 (CONSELHO FEDERAL DE CONTABILIDADE, 2026a, 2026b, 2026c): NBC TSP Estrutura Conceitual (R1), definição de ativo (itens 5.6 a 5.13) e reconhecimento (itens 6.2, 6.7 e 6.8); NBC TSP 37, Ativo Imobilizado, convergente à IPSAS 45 (itens 5 a 8, 11 a 13, 24 a 27, 34(l), 52 a 56, 69, 77, 78 e 87(a)); NBC TSP 38, Mensuração, convergente à IPSAS 46 (itens 6, 7, 10, 12, 17 a 25, 29 a 45, 54 e 55). As três vigoram a partir de 1º/01/2027. Síntese de cada item e uso no modelo em `metodologia/fundamentacao_normativa.md`. MCASP e PCASP: [a completar].

Base documental obrigatória (item 19.1): relatório de valoração de ativos culturais da UnB (UNIVERSIDADE DE BRASÍLIA, 2024); Oliveira, Freire e Costa, sobre valoração de ativos culturais nas universidades federais; Lima et al. (2024), sobre extração automatizada de informações de ativos culturais. [a completar: síntese das contribuições, após leitura.]

## iv. Metodologia

Fluxo automatizado em Python (biblioteca padrão), executado por `codigos/executar_pipeline.py`:

1. **Identificação** (`extrair_acervo_cal.py`): API REST do Tainacan; padronização das 16 variáveis do item 7; dicionário de dados; diagnóstico de completude e de duplicidades. Detalhes em `metodologia/identificacao.md`.
2. **Reconhecimento** (`reconhecimento.py`): definição de ativo pela Estrutura Conceitual (R1) e critérios dos itens 6 e 7 da NBC TSP 37, aplicados a cada registro; classes "Reconhecimento sustentado", "Não reconhecimento fundamentado" e "Pendente de verificação". Detalhes em `metodologia/reconhecimento.md`.
3. **Mensuração** (`mensuracao.py`, `comparaveis.py`): doações e transferências mensuradas pelo custo atribuído, determinado pelo valor corrente operacional (NBC TSP 37, itens 12 e 27; NBC TSP 38, itens 10 e 23 a 25); abordagem de mercado com comparáveis ajustados (NBC TSP 38, itens 24, 32 e 42); níveis de evidência A a D, em que só A e B são mensuração confiável (NBC TSP 37, item 6(b)); registros sem evidência classificados conforme o item 9.4 das Regras. Detalhes em `metodologia/mensuracao.md`.
4. **Validação** (`validacao_casos.py`): nove casos (item 6.3).
5. **Evidenciação** (`evidenciacao.py`): minuta de nota explicativa, quadro consolidado e indicadores do item 15. Detalhes em `metodologia/evidenciacao.md`.
6. **Conciliação patrimonial** (`cadastro_patrimonial.py`): leitura da Lista da CAL (cadastro patrimonial da UnB), sem dados pessoais.

## v. Caracterização dos dados

Consulta em 23/11/2026, 19h12: 2.197 registros em três coleções (Acervo 1.497; Memória Institucional 699; Mobiliário moderno da UnB 1), cobertura de 100,0% do universo digital identificável, completude cadastral média de 32,9% e nenhum identificador repetido; 4 registros em provável duplicidade (Memória Institucional) e 44 a conferir no Acervo. Grupos (árvore de decisão do extrator 1.2.0, 24/11/2026): Arte 476 (inclui a Cadeira UnB, design autoral), Arte contemporânea 162, Etnográfica 860 (Inicial 349 e o ID 25320, provável; Galvão 347; Chocó 163) e Registro de evento (não é bem) 699, que é toda a Memória Institucional; nenhum registro "A classificar". A Coleção CNRC não consta do portal. Pelo padrão do INBCM (Resolução Normativa Ibram nº 6/2021, art. 7º, § 1º), nenhum bem tem os 9 elementos obrigatórios; faltam no portal os incisos II (outros números) e VII (classificação), e a classificação proposta pelo Tesauro de Objetos (FERREZ, 2016) alcança 938 bens. No cadastro patrimonial há 27 bens recentes, com denominação descritiva e sem registro no acervo digital (R$ 113.800,00). Cadastro patrimonial: 243 bens na localidade da CAL, dos quais 242 obras de arte (232 próprias, R$ 1.765.385,00; 10 de terceiros, R$ 173.015,00).

## vi. Resultados

| Indicador (item 15) | Resultado |
|---|---|
| Registros identificados | 2.197 |
| Registros recuperados | 2.197 |
| Cobertura | 100,0% |
| Completude cadastral | 32,9% |
| Registros duplicados (possíveis) | 48 (4 prováveis e 44 a conferir) |
| Reconhecimento sustentado | 0 |
| Reconhecimento pendente | 986 |
| Mensuração fundamentada | 0 |
| Mensuração pendente | 638 (inclui 15 com faixa indicativa) |
| Valor agregado estimado | R$ 0,00 |
| Rastreabilidade | 100,0% |
| Validação | 9 casos |

Não reconhecimento fundamentado: 1.211 registros: 699 eventos da Memória Institucional, que não satisfazem a definição de ativo (Estrutura Conceitual (R1), item 5.6), e 512 bens que satisfazem a definição, mas não têm mensuração confiável (161 de arte, 155 de arte contemporânea e 196 etnográficos), tratados pelo item 7 da NBC TSP 37: não reconhecidos e divulgados conforme o item 77. Faixas indicativas: 15 obras (14 serigrafias de Cícero Dias, USD 600 a 2.040 cada; uma serigrafia de Tarsila do Amaral, USD 300 a 600).

## vii. Discussão

[a completar pela equipe] Pontos a discutir: (1) a diferença entre o universo digital (1.497 registros do Acervo) e o cadastro patrimonial (242 obras de arte), sem chave comum, que reproduz a divergência entre registros patrimoniais e bens localizados apontada no relatório de 2024 (PPGCONT/UnB, 2026, item 2); (2) a escassez de transações comparáveis para arte brasileira em suporte de papel; (3) o tratamento das coleções etnográficas sem presunção de mercadoria (item 4.3); (4) a decisão de não reconhecer sem mensuração confiável, que privilegia a qualidade sobre a quantidade de registros monetizados (item 16).

## viii. Limitações

Certificado TLS do portal vencido em 23/11/2026; triagem de grupos automática, sujeita a revisão (um registro classificado como provável pela sequência do número de registro); poucos comparáveis e em dólar, sem conversão; portal sem dimensões e tiragem de muitas obras; ausência da Coleção CNRC; cadastro patrimonial sem vínculo com o portal; validação apenas documental (sem exame físico na CAL); regras de decisão propostas pela equipe e ainda não confrontadas com os parágrafos das normas.

## ix. Conclusões

[a completar pela equipe]

## x. Referências

BRASIL. Lei nº 9.610, de 19 de fevereiro de 1998. Altera, atualiza e consolida a legislação sobre direitos autorais e dá outras providências. Brasília, DF, 1998.

CONSELHO FEDERAL DE CONTABILIDADE. **NBC TSP 37, de 11 de dezembro de 2025**. Aprova a NBC TSP 37: Ativo Imobilizado. Diário Oficial da União, Brasília, DF, 17 mar. 2026a. Disponível em: https://www.legisweb.com.br/legislacao/?id=492508. Acesso em: 24 nov. 2026.

CONSELHO FEDERAL DE CONTABILIDADE. **NBC TSP 38, de 9 de abril de 2026**. Aprova a NBC TSP 38: Mensuração. Diário Oficial da União, Brasília, DF, 17 abr. 2026b. Disponível em: https://www.legisweb.com.br/legislacao/?id=494368. Acesso em: 24 nov. 2026.

CONSELHO FEDERAL DE CONTABILIDADE. **NBC TSP Estrutura Conceitual (R1), de 13 de novembro de 2025**. Estrutura Conceitual para Elaboração e Divulgação de Informação Contábil de Propósito Geral pelas Entidades do Setor Público. Diário Oficial da União: seção 1, Brasília, DF, p. 199-209, 7 abr. 2026c. Disponível em: https://legismap.com.br/leis-e-normas/norma-brasileira-de-contabilidade-nbc-tsp-estrutura-conceitual-r1-de-13-11-2025. Acesso em: 24 nov. 2026.

PPGCONT/UnB. Programa de Pós-Graduação em Ciências Contábeis. **Hackathon CULTIVA UnB 2026**: quanto vale o patrimônio cultural da Universidade de Brasília? Regras do Hackathon. Brasília: FACE/UnB, 2026.

UNIVERSIDADE DE BRASÍLIA. Casa da Cultura da América Latina. **Acervo Digital da CAL**. Brasília, [2026]. Disponível em: https://www.acervocal.unb.br/. Acesso em: 23 nov. 2026.

UNIVERSIDADE DE BRASÍLIA. **Relatório Final**: Valoração de Ativos Culturais da UnB. Edital nº 01/2023. Brasília, 2024. [obra indicada nas Regras; conferir antes de citar o conteúdo]

[a completar: IPSAS, MCASP, PCASP e os estudos de Oliveira, Freire e Costa e de Lima et al. (2024), com os dados de publicação conferidos nas próprias fontes.]

