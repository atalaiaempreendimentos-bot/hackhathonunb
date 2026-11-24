# Etapa IV: Evidenciação contábil

Pergunta orientadora (Regras, item 10): como apresentar as informações patrimoniais e contábeis dos bens culturais da CAL de forma transparente e útil à gestão pública?

## Modelo proposto

A evidenciação combina três peças, todas geradas por `codigos/evidenciacao.py` a partir das etapas anteriores:

1. **Minuta de nota explicativa** (`resultados/nota_explicativa/minuta_nota_explicativa.md`), com os dez conteúdos do item 10 (a a j) e notas de rodapé que remetem à metodologia e aos arquivos de cada etapa.
2. **Quadro demonstrativo consolidado** (`resultados/demonstrativos/quadro_consolidado.csv`), por grupo: registros analisados, situação quanto à definição de ativo, classe de reconhecimento, situação de mensuração, valor fundamentado e soma das faixas indicativas por moeda.
3. **Indicadores obrigatórios do item 15** (`resultados/indicadores/indicadores_item15.csv`) e valor agregado por base de mensuração e categoria (`resultados/demonstrativos/valor_agregado_por_base.csv`).

## Separação entre resultado acadêmico e registro oficial

Conforme o item 10, os valores acadêmicos ficam separados do valor registrado pela contabilidade da UnB. A nota apresenta, em parágrafo próprio, o cadastro patrimonial (232 obras próprias, R$ 1.765.385,00) como informação de comparação, sem somá-lo às estimativas da equipe, e registra que a falta de vínculo entre tombamento e registro do portal impede a conciliação item a item.

## Informações não financeiras

Caracterização das coleções, completude cadastral, situação física (Localizado, Não localizado, Emprestado), restrições culturais das coleções etnográficas, direitos sobre as fotografias e limitações da coleta.

## Valores agregados

O valor agregado soma apenas mensurações fundamentadas (níveis A e B), por base e categoria, e não é apresentado como valor total do patrimônio cultural da CAL (item 15). As faixas indicativas (nível C) são somadas por moeda, sem conversão, e identificadas como não equivalentes a valor justo.

## Reprodução

`python3 codigos/evidenciacao.py`, depois de `reconhecimento.py` e `validacao_casos.py`, ou o fluxo completo com `python3 codigos/executar_pipeline.py`.
