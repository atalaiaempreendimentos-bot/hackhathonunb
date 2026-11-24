# Minuta de nota explicativa: bens culturais sob guarda da Casa da Cultura da América Latina (CAL/UnB)

**Resultado acadêmico do Hackathon CULTIVA UnB 2026. Não constitui registro contábil oficial da Universidade de Brasília (Regras, item 17.13).**

## a) Caracterização das coleções

A CAL guarda coleções de arte, arte contemporânea e etnográficas. O acervo digital público reúne 2.197 registros em três coleções: Acervo (1.497 registros, com as subcoleções Arte, Triangular, Inicial, Galvão e Chocó), Memória Institucional (699) e Mobiliário moderno da UnB (1).[^1] A Coleção CNRC, listada no item 4.3 das Regras, não aparece em nenhum registro do portal.

## b) Quantidade de registros analisados

Foram analisados 2.197 registros, 100,0% do universo digital identificável, com completude cadastral média de 32,9%.[^1] A cobertura digital não equivale ao patrimônio físico da CAL (Regras, item 4.4).

## c) Critérios de reconhecimento

Cada registro foi examinado quanto a existência, controle, potencial de serviços, natureza e condições de reconhecimento, inclusive mensuração confiável.[^2] Resultado: 0 registros com reconhecimento sustentado, 894 com não reconhecimento fundamentado (dos quais 699 são registros de eventos e 195 são bens etnográficos sem mensuração monetária confiável) e 1.303 pendentes de verificação. 511 registros atendem à definição de ativo, com existência confirmada e controle documentado.

## d) Bases de mensuração

Na ausência de custo histórico (os ingressos registrados no portal são doações e transferências), a base proposta para obras de arte é o valor justo ou o valor operacional corrente, estimado pela abordagem de mercado com obras comparáveis.[^3] Para bens de comunidades tradicionais não se atribui valor monetário por padrão (Regras, item 4.3).

## e) Quantidade de ativos com mensuração fundamentada

0 registros. Há 15 obras com faixa indicativa (nível C de evidência), que não constitui valor justo.[^4]

## f) Montantes estimados

Valor agregado das mensurações fundamentadas: R$ 0,00. Faixas indicativas, somadas por moeda e sem conversão: USD 8.700 a 29.160.[^4] Esses montantes não representam o valor total do patrimônio cultural da CAL (Regras, item 15).

Para comparação, o cadastro patrimonial da UnB registra, na localidade da CAL, 242 obras de arte, das quais 232 próprias, com valor registrado de R$ 1.765.385,00, e 10 marcadas como bem de terceiro (R$ 173.015,00).[^5] Nenhum número de tombamento desse cadastro aparece no acervo digital, o que impede vincular os valores registrados às obras do portal.

## g) Registros pendentes de reconhecimento ou mensuração

1.303 registros pendentes de reconhecimento e 639 pendentes de mensuração. As pendências mais frequentes são a localização atual não informada no portal e a ausência de transações comparáveis.[^2][^3]

## h) Incerteza

As estimativas trazem intervalo (mínimo e máximo) e nível de evidência (A a D). Os comparáveis disponíveis são poucos, e o portal não informa dimensões nem tiragem das obras, o que impede os ajustes do item 9.2 das Regras.[^4]

## i) Restrições patrimoniais, culturais e documentais

Bens etnográficos sujeitos a restrições culturais e éticas (Regras, item 4.3); fotografias com direitos reservados (Lei nº 9.610/1998); 10 bens no cadastro marcados como de terceiros; 39 registros do portal com situação "Não localizado" e 10 "Emprestado".[^2][^5]

## j) Limitações dos resultados

Certificado TLS do portal vencido em 2026-11-23 19:12; coleta realizada sem verificação do certificado. Triagem de grupos automática e sujeita a revisão. Regras de reconhecimento e mensuração propostas pela equipe, a validar com a fundamentação normativa e com a CAL.[^1][^2][^3]

---

[^1]: Identificação: extração pela API pública do Tainacan em 2026-11-23 19:12 (`codigos/extrair_acervo_cal.py`); base padronizada em `dados/inventario.csv`, dicionário em `dados/dicionario_dados.md` e diagnóstico em `dados/diagnostico_qualidade.csv`.
[^2]: Reconhecimento: matriz aplicada a todos os registros (`codigos/reconhecimento.py`, `dados/reconhecimento.csv`). Atende à definição de ativo o registro com existência confirmada (situação "Localizado") e controle documentado (doação ou transferência com data); a presença no portal, sozinha, não basta (Regras, item 8). Reconhecimento sustentado exige ainda mensuração com evidência nível A ou B. Fundamento indicado nas Regras (item 19.2): NBC TSP Estrutura Conceitual (R1) e NBC TSP 37, Ativo Imobilizado (convergente à IPSAS 45); os parágrafos aplicáveis devem ser conferidos no texto das normas.
[^3]: Mensuração: base (custo histórico, valor justo ou valor operacional corrente; NBC TSP 38 / IPSAS 46) separada da técnica (abordagem de mercado ou de custo), conforme o item 9 das Regras (`codigos/mensuracao.py`, `metodologia/mensuracao.md`). Bens sem evidência suficiente recebem a classificação do item 9.4, sem valor arbitrário.
[^4]: Abordagem de mercado: comparáveis do mesmo artista e da mesma família de técnica, com fonte (`dados/comparaveis.csv`, `codigos/comparaveis.py`). Nível A: 3 ou mais transações e obra com dimensões e tiragem conhecidas; B: 3 ou mais transações; C: 1 ou 2 transações, ou só estimativas. Valor central: mediana das transações; intervalo: menor e maior valor. Moedas não convertidas sem taxa e fonte. Preço anunciado não é valor justo (Regras, item 9.2).
[^5]: Cadastro patrimonial: Lista da CAL fornecida pela equipe, com 243 bens tombados em 05/01/2021 (termo 209/2021), migrados do SIPAT; conciliação agregada em `dados/conciliacao_patrimonial.csv` (`codigos/cadastro_patrimonial.py`); a versão item a item, sem dados pessoais, fica fora do repositório público até a confirmação da autorização de divulgação (Regras, item 12).
