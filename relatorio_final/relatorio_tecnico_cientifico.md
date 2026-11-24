# Relatório técnico-científico (minuta v1, 23/11/2026)

**Quanto vale o patrimônio cultural da UnB? Identificação, reconhecimento, mensuração e evidenciação dos ativos culturais do Acervo Digital da CAL/UnB**

Hackathon CULTIVA UnB 2026. PPGCont/UnB, Valoração de Ativos Culturais e Ambientais (318710), 2026/2. Profa. Fátima de Souza Freire e Prof. Jorge Madeira Nogueira. Equipe: Hugo Rodrigues Gomes, Yang Alfredo Florentino e Lucas [sobrenome a completar].

> Minuta gerada a partir dos resultados do repositório. Os trechos marcados com [a completar] dependem de leitura das fontes indicadas e de decisão da equipe. Resultados acadêmicos; não constituem registro contábil oficial da UnB (Regras, item 17.13).

## i. Introdução e problema de pesquisa

As universidades públicas guardam bens de valor histórico, artístico e cultural cujo reconhecimento e mensuração contábil enfrentam ausência de preços de mercado, singularidade dos objetos e documentação patrimonial incompleta (PPGCONT/UnB, 2026). O problema proposto é: como identificar, reconhecer, mensurar e evidenciar os ativos culturais da CAL/UnB de maneira sistemática, fundamentada, transparente e reproduzível, utilizando as NBC TSP convergentes às IPSAS e ferramentas computacionais?

## ii. Objetivos

Objetivo geral: desenvolver uma solução científica, contábil e tecnológica que processe todos os registros públicos do Acervo Digital da CAL nas quatro etapas contábeis, com rastreabilidade e possibilidade de aplicação a outros acervos Tainacan. Objetivos específicos: os do item 3.2 das Regras (a a k).

## iii. Fundamentação normativa e científica

Normas indicadas nas Regras (item 19.2): NBC TSP Estrutura Conceitual (R1); NBC TSP 37, Ativo Imobilizado; NBC TSP 38, Mensuração; IPSAS 45 e IPSAS 46; MCASP e PCASP. [a completar: citação dos parágrafos aplicáveis, conferidos no texto das normas.]

Base documental obrigatória (item 19.1): relatório de valoração de ativos culturais da UnB (UNIVERSIDADE DE BRASÍLIA, 2024); Oliveira, Freire e Costa, sobre valoração de ativos culturais nas universidades federais; Lima et al. (2024), sobre extração automatizada de informações de ativos culturais. [a completar: síntese das contribuições, após leitura.]

## iv. Metodologia

Fluxo automatizado em Python (biblioteca padrão), executado por `codigos/executar_pipeline.py`:

1. **Identificação** (`extrair_acervo_cal.py`): API REST do Tainacan; padronização das 16 variáveis do item 7; dicionário de dados; diagnóstico de completude e de duplicidades. Detalhes em `metodologia/identificacao.md`.
2. **Reconhecimento** (`reconhecimento.py`): matriz com os oito critérios do item 8 aplicada a cada registro; classes "Reconhecimento sustentado", "Não reconhecimento fundamentado" e "Pendente de verificação". Detalhes em `metodologia/reconhecimento.md`.
3. **Mensuração** (`mensuracao.py`, `comparaveis.py`): escolha da base (custo histórico, valor justo, valor operacional corrente) separada da técnica (mercado, custo); níveis de evidência A a D; faixas e medianas a partir de comparáveis com fonte; registros sem evidência classificados conforme o item 9.4. Detalhes em `metodologia/mensuracao.md`.
4. **Validação** (`validacao_casos.py`): nove casos (item 6.3).
5. **Evidenciação** (`evidenciacao.py`): minuta de nota explicativa, quadro consolidado e indicadores do item 15. Detalhes em `metodologia/evidenciacao.md`.
6. **Conciliação patrimonial** (`cadastro_patrimonial.py`): leitura da Lista da CAL (cadastro patrimonial da UnB), sem dados pessoais.

## v. Caracterização dos dados

Consulta em 23/11/2026, 19h12: 2.197 registros em três coleções (Acervo 1.497; Memória Institucional 699; Mobiliário moderno da UnB 1), cobertura de 100,0% do universo digital identificável, completude cadastral média de 32,9% e 427 possíveis duplicidades. Grupos: Arte 479, Arte contemporânea 162, Etnográfica 859 (Inicial 349, Galvão 347, Chocó 163) e A classificar 697. A Coleção CNRC não consta do portal. Cadastro patrimonial: 243 bens na localidade da CAL, dos quais 242 obras de arte (232 próprias, R$ 1.765.385,00; 10 de terceiros, R$ 173.015,00).

## vi. Resultados

| Indicador (item 15) | Resultado |
|---|---|
| Registros identificados | 2.197 |
| Registros recuperados | 2.197 |
| Cobertura | 100,0% |
| Completude cadastral | 32,9% |
| Registros duplicados (possíveis) | 427 |
| Reconhecimento sustentado | 0 |
| Reconhecimento pendente | 1.303 |
| Mensuração fundamentada | 0 |
| Mensuração pendente | 639 (inclui 15 com faixa indicativa) |
| Valor agregado estimado | R$ 0,00 |
| Rastreabilidade | 100,0% |
| Validação | 9 casos |

Não reconhecimento fundamentado: 894 registros (699 da Memória Institucional e 195 bens etnográficos com definição de ativo atendida, mas sem mensuração monetária confiável). Faixas indicativas: 15 obras (14 serigrafias de Cícero Dias, USD 600 a 2.040 cada; uma serigrafia de Tarsila do Amaral, USD 300 a 600).

## vii. Discussão

[a completar pela equipe] Pontos a discutir: (1) a diferença entre o universo digital (1.497 registros do Acervo) e o cadastro patrimonial (242 obras de arte), sem chave comum, que reproduz a divergência entre registros patrimoniais e bens localizados apontada no relatório de 2024 (PPGCONT/UnB, 2026, item 2); (2) a escassez de transações comparáveis para arte brasileira em suporte de papel; (3) o tratamento das coleções etnográficas sem presunção de mercadoria (item 4.3); (4) a decisão de não reconhecer sem mensuração confiável, que privilegia a qualidade sobre a quantidade de registros monetizados (item 16).

## viii. Limitações

Certificado TLS do portal vencido em 23/11/2026; triagem automática de grupos; poucos comparáveis e em dólar, sem conversão; portal sem dimensões e tiragem de muitas obras; ausência da Coleção CNRC; cadastro patrimonial sem vínculo com o portal; validação apenas documental (sem exame físico na CAL); regras de decisão propostas pela equipe e ainda não confrontadas com os parágrafos das normas.

## ix. Conclusões

[a completar pela equipe]

## x. Referências

BRASIL. Lei nº 9.610, de 19 de fevereiro de 1998. Altera, atualiza e consolida a legislação sobre direitos autorais e dá outras providências. Brasília, DF, 1998.

PPGCONT/UnB. Programa de Pós-Graduação em Ciências Contábeis. **Hackathon CULTIVA UnB 2026**: quanto vale o patrimônio cultural da Universidade de Brasília? Regras do Hackathon. Brasília: FACE/UnB, 2026.

UNIVERSIDADE DE BRASÍLIA. Casa da Cultura da América Latina. **Acervo Digital da CAL**. Brasília, [2026]. Disponível em: https://www.acervocal.unb.br/. Acesso em: 23 nov. 2026.

UNIVERSIDADE DE BRASÍLIA. **Relatório Final**: Valoração de Ativos Culturais da UnB. Edital nº 01/2023. Brasília, 2024. [obra indicada nas Regras; conferir antes de citar o conteúdo]

[a completar: NBC TSP, IPSAS, MCASP, PCASP e os estudos de Oliveira, Freire e Costa e de Lima et al. (2024), com os dados de publicação conferidos nas próprias fontes.]
