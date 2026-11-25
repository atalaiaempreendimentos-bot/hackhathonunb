# Inconsistências cadastrais dos bens do acervo digital

Regras, item 7(g). Script: `codigos/verificar_inconsistencias.py`; registro a registro em `dados/inconsistencias.csv`. Ausências ficam no diagnóstico de completude e duplicidades na verificação própria; aqui entram valores presentes, mas incoerentes, fora do padrão da coleção ou fora das opções do INBCM. Nada foi corrigido.

| Tipo | Registros | Exemplo |
|---|---:|---|
| Data de aquisição sem forma de aquisição | 166 | ID 3544: 1993 |
| Denominação com variante de grafia | 73 | ID 2662: boneca |
| Dimensões sem unidade de medida | 71 | ID 25696: 42 x 32 |
| Número de registro fora do padrão da subcoleção | 40 | ID 26143: 0130809 |
| Situação fora das opções do INBCM | 10 | ID 1805: Emprestado |
| Data de aquisição incerta | 6 | ID 2848: 1995 (?) |
| "Com imagem?" divergente da imagem publicada | 3 | ID 20691: Não |
| Número de registro ausente | 1 | ID 26277:  |
| Subcoleção não informada | 1 | ID 25320: False |
| Data de produção sem ano legível | 1 | ID 20301: de castigo |
| Data de aquisição ilegível | 1 | ID 13145: Fernanda Cristina Pereira Lima Siqueira Maravilha |
| Registros com ao menos uma inconsistência | 340 |  |

## Heterogeneidade de formatos

Data de aquisição, pela precisão da forma padronizada (`data_aquisicao_padronizada`): ano (893); dia (525); não informada (70); ano incerto (6); mês (3); ilegível (1).

Data de produção, por formato (9 = dígitos): `9` (142); `9-9` (16); `9/9` (8); `9/9/9` (5); `a a` (1).

Dimensões, por formato (9 = número, a = palavra ou letra): `9 x 9 a` (116); `9 a x 9 a` (36); `9 x 9 x 9 a` (30); `a: 9'9''` (24); `9 a` (12); `9 x 9` (9); `9 x 9 x 9` (6); `a: 9'` (6).
