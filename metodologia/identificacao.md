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

Regras aplicadas em ordem, em `triagem_grupo()`:

1. Subcoleções Inicial, Galvão, Chocó e CNRC: grupo Etnográfica (item 4.3).
2. Subcoleção Triangular: Arte contemporânea (registros CE.xxx, com fotografia, impressão digital, objetos e videoperformance).
3. Subcoleção Arte: Arte.
4. Demais registros: termos de categoria e técnica; sem termo indicativo, "A classificar".

Resultado: Arte 479 (475 do Acervo e 4 da Memória Institucional), Arte contemporânea 162, Etnográfica 859 (Inicial 349, Galvão 347, Chocó 163), A classificar 697. A triagem é automática e sujeita a revisão (`dados/inventario.csv`, coluna `criterio_grupo`).

## Qualidade cadastral

Completude média das 13 variáveis principais (`dados/diagnostico_qualidade.csv`): 32,9% no total; Arte 45,6%; Arte contemporânea 66,3%; Etnográfica 24,6%; A classificar 26,7%. Campos mais ausentes no total: localização (0,0%), número de patrimônio (0,0%), estado de conservação (7,0%), dimensões (11,8%) e categoria (13,9%). O campo "Situação" do portal (Localizado, Não localizado, Emprestado) informa a existência física, mas não o local de guarda. A triagem inicial do extrator (título, autoria e dimensões, mesmo vazias) apontou 427 registros (`dados/duplicidades.csv`), mas essa chave agrupa homônimos. Em 24/11/2026, `codigos/verificar_duplicidades.py` refinou a verificação:

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
