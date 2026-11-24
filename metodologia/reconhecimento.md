# Etapa II: Reconhecimento contábil

Pergunta orientadora (Regras, item 8): quais registros apresentam evidências suficientes para o reconhecimento contábil como ativos da UnB?

Base normativa indicada nas Regras (item 19.2): NBC TSP Estrutura Conceitual (R1) e NBC TSP 37, Ativo Imobilizado, convergente à IPSAS 45 (Property, Plant, and Equipment); MCASP e PCASP como referências complementares. Os parágrafos aplicáveis devem ser conferidos no texto das normas antes da citação no relatório final.

## Critérios examinados em cada registro

| Critério (item 8) | Evidência usada | Coluna em `dados/reconhecimento.csv` |
|---|---|---|
| Existência do recurso | Campo "Situação" do portal: Localizado (atendido), Não localizado ou Emprestado (a verificar), vazio (indício, se houver fotografia) | `existencia` |
| Controle pela entidade | Forma de aquisição (doação ou transferência) com data de aquisição | `controle` |
| Potencial de serviços | Função museológica do acervo (guarda, pesquisa, exposição, ensino) | `potencial_servicos` |
| Benefícios econômicos | Não aplicável: finalidade cultural, sem geração de caixa | `beneficios_economicos` |
| Natureza e classificação | Grupo da Etapa I (Arte, Arte contemporânea, Etnográfica) | `natureza` |
| Condições para reconhecimento | Mensuração confiável (Etapa III): nível de evidência A ou B | `condicao_mensuracao` |
| Investigação adicional | Lista do que falta para concluir | `investigacao_necessaria` |

O controle não é presumido pela presença do bem no portal (item 8): sem forma e data de aquisição, o critério fica pendente.

## Regras de decisão (proposta da equipe)

1. Registro de evento ou atividade (coleção Memória Institucional): não identifica bem individualizado controlado; **Não reconhecimento fundamentado**.
2. Atende à definição de ativo quando há existência confirmada e controle documentado.
3. Definição atendida e mensuração com evidência A ou B: **Reconhecimento sustentado pelas evidências**.
4. Definição atendida, mas mensuração monetária inviável com as evidências disponíveis, em bens de comunidades tradicionais (item 4.3): **Não reconhecimento fundamentado**, com evidenciação qualitativa em nota explicativa.
5. Demais casos: **Pendente de verificação**, com a lista das informações faltantes.

## Resultado (23/11/2026)

| Grupo | Sustentado | Não reconhecimento fundamentado | Pendente |
|---|---:|---:|---:|
| Arte | 0 | 4 | 475 |
| Arte contemporânea | 0 | 0 | 162 |
| Etnográfica | 0 | 195 | 664 |
| A classificar | 0 | 695 | 2 |
| **Total** | **0** | **894** | **1.303** |

Atendem à definição de ativo 511 registros; 987 têm a definição pendente (sobretudo por localização atual não informada) e 699 não se aplicam (Memória Institucional). Nenhum registro chega a reconhecimento sustentado porque nenhuma obra tem, até aqui, três transações comparáveis realizadas (nível B).

## Conciliação com o cadastro patrimonial

O cadastro patrimonial da UnB (Lista da CAL, termo 209/2021) registra 242 obras de arte na localidade da CAL: 232 próprias, com valor registrado de R$ 1.765.385,00, e 10 marcadas como bem de terceiro (R$ 173.015,00). A denominação de todos os itens é genérica ("OBRA DE ARTE") e nenhum número de tombamento ou de registro do SIPAT aparece no portal, de modo que não é possível vincular os valores registrados às obras catalogadas. Os 10 bens de terceiro não atendem ao critério de controle. Arquivos: `codigos/cadastro_patrimonial.py` e `dados/conciliacao_patrimonial.csv` (agregados). A versão item a item, sem dados pessoais (`dados/cadastro_patrimonial_cal.csv`), fica fora do repositório público até a equipe confirmar a autorização de divulgação (Regras, item 12).

## Reprodução

`python3 codigos/reconhecimento.py` (lê `dados/inventario.csv`, `dados/metadados_completos.csv` e `dados/mensuracao.csv`; gera `dados/reconhecimento.csv` e `dados/reconhecimento_resumo.csv`).
