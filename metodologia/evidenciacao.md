# Etapa IV: Evidenciação contábil

Pergunta orientadora (Regras, item 10): como apresentar as informações patrimoniais e contábeis dos bens culturais da CAL de forma transparente e útil à gestão pública?

Fundamentação conferida em 24/11/2026 no texto publicado da NBC TSP 37 (itens 69, 76, 77, 78 e 79 a 84) e da NBC TSP 38 (itens 54 e 55). Itens e fontes em `metodologia/fundamentacao_normativa.md`.

## Requisitos normativos e onde são atendidos

| Requisito | Conteúdo | Onde está |
|---|---|---|
| NBC TSP 37, item 77 | Para patrimônio cultural não reconhecido por falta de mensuração confiável: (a) dificuldades na obtenção da mensuração e (b) relevância dos itens para os objetivos da entidade | Minuta, seção 4, por classe (arte, arte contemporânea, etnográfica) |
| NBC TSP 37, item 69 | Por classe reconhecida: critérios de mensuração, métodos de depreciação, vidas úteis, valor contábil bruto e depreciação acumulada, conciliação do período | Minuta, seção 3, com o que a Lista da CAL permite informar e as lacunas |
| NBC TSP 37, item 76(d) | Encoraja divulgar o valor corrente materialmente diferente do valor contábil no modelo do custo | Minuta, seção 6 (não aplicável sem vínculo entre portal e cadastro) |
| NBC TSP 37, item 78 | Gastos subsequentes reconhecidos com itens não reconhecidos | Minuta, seção 4 (nenhum identificado) |
| NBC TSP 37, itens 79 a 84 | Divulgações de mensuração pelo valor corrente | Não aplicáveis: o modelo proposto para a classe é o do custo histórico |
| NBC TSP 38, itens 54 e 55 | Base de mensuração, técnicas e dados de entrada | Minuta, seções 2 e 6 |
| Regras, item 10, a) a j) | Dez conteúdos mínimos | Indicados entre colchetes em cada seção da minuta |

## Produtos (`codigos/evidenciacao.py`)

1. **Minuta de nota explicativa** (`resultados/nota_explicativa/minuta_nota_explicativa.md`): caracterização, política contábil proposta, acervos registrados no cadastro (item 69), itens não reconhecidos (item 77), pendências, mensuração e incerteza, restrições e limitações, com notas de rodapé metodológicas.
2. **Quadro demonstrativo consolidado** (`resultados/demonstrativos/quadro_consolidado.csv`), por grupo: registros, definição de ativo, classe de reconhecimento, situação de mensuração, valor fundamentado e soma das faixas indicativas por moeda.
3. **Indicadores do item 15** (`resultados/indicadores/indicadores_item15.csv`) e valor agregado por base de mensuração e categoria (`resultados/demonstrativos/valor_agregado_por_base.csv`).

## Separação entre resultado acadêmico e registro oficial

Conforme o item 10 das Regras, os valores acadêmicos ficam separados do valor registrado pela UnB. A minuta apresenta o cadastro patrimonial (232 obras próprias, R$ 1.765.385,00) em seção própria, segundo o item 69 da NBC TSP 37, sem somá-lo às estimativas da equipe, e registra que a falta de vínculo entre tombamento e registro do portal impede a conciliação item a item.

## Valores agregados

O valor agregado soma apenas mensurações fundamentadas (níveis A e B), por base e categoria, e não é apresentado como valor total do patrimônio cultural da CAL (item 15). As faixas indicativas (nível C) são somadas por moeda, sem conversão, identificadas como mensuração não confiável (Estrutura Conceitual (R1), item 6.8) e separadas em dados observáveis e não observáveis (NBC TSP 38, item 6).

## Reprodução

`python3 codigos/evidenciacao.py`, depois de `reconhecimento.py` e `validacao_casos.py`, ou o fluxo completo com `python3 codigos/executar_pipeline.py`.
