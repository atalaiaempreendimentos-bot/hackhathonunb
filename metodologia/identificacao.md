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

## Produtos

`dados/inventario.csv` (base padronizada), `dados/metadados_completos.csv` (todos os campos), `dados/dicionario_dados.md`, `dados/diagnostico_qualidade.csv`, `dados/duplicidades.csv`, `dados/indicadores.csv`, `dados/colecoes.csv`, `dados/log_extracao.json`.
