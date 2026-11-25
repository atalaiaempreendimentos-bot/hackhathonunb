# Dicionário de dados: Acervo Digital da CAL/UnB

Gerado automaticamente por `extrair_acervo_cal.py` v1.3.0 em 2026-11-23 19:12. Fonte: https://www.acervocal.unb.br.

## inventario.csv (base padronizada)

| Coluna | Descrição |
|---|---|
| `id_registro` | Identificador interno do item no Tainacan (preservado do portal). |
| `colecao_id` | Identificador da coleção no Tainacan. |
| `colecao` | Nome da coleção no portal. |
| `subcolecao` | Conjunto ou subcoleção informado nos metadados (ex.: Coleção Galvão, Chocó). |
| `grupo_sugerido` | Triagem automática: Arte, Arte contemporânea, Etnográfica, Registro de evento (não é bem) ou A classificar. Sujeita a revisão. |
| `criterio_grupo` | Termo que motivou a triagem do grupo (rastreabilidade da regra). |
| `flag_possivel_contemporanea` | 'sim' quando técnica, categoria ou suporte indicam obra contemporânea (vídeo, instalação, arte postal etc.). |
| `categoria` | Categoria, tipologia ou classificação do bem, como consta no portal (nos bens, o portal não tem esse campo; na Memória Institucional, é o tipo do evento). |
| `classificacao_tesauro` | Classificação proposta pela equipe para a categoria do bem: termo e código do Tesauro de Objetos do Patrimônio Cultural nos Museus Brasileiros (FERREZ, 2016), pela denominação, com o vocabulário revisável dados/vocabulario_tesauro.csv; vazio quando não há termo correspondente. Fora da completude. |
| `categoria_tesauro` | Categoria de primeiro nível do Tesauro correspondente à classificação proposta (por exemplo, 06 Objetos de atividades artísticas). Fora da completude. |
| `verificacao_classificacao` | Se o termo foi localizado literalmente no Tesauro ou é equivalência a confirmar. |
| `titulo` | Título ou denominação. |
| `autoria_origem` | Artista, autor ou grupo de origem; nas coleções etnográficas, o grupo indígena informado no portal (inclusive "Não identificado"). |
| `ano_periodo` | Ano, data ou período de produção, como consta no portal. |
| `ano_inicial_extraido` | Primeiro ano com quatro dígitos encontrado em ano_periodo (apoio a filtros; não substitui o dado original). |
| `material_tecnica` | Material, técnica e suporte como constam no portal, em campo único (INBCM, inciso X). |
| `tecnica` | Técnica, separada de material_tecnica: a parte antes de "sobre" ou o termo de técnica; quando a separação não é possível, repete o valor original (ver criterio_tecnica). |
| `materiais` | Materiais ou suporte, separados de material_tecnica: a parte depois de "sobre" ou o termo de material; quando a separação não é possível, repete o valor original (ver criterio_tecnica). |
| `criterio_tecnica` | Como técnica e materiais foram separados: padrão "técnica sobre suporte", termo de técnica, termo de material, ou não separável. |
| `dimensoes` | Dimensões, como constam no portal. |
| `tiragem` | Tiragem, edição ou numeração de exemplar (gravuras, fotografias, múltiplos). |
| `proveniencia` | Proveniência ou procedência (de quem ou de onde o bem veio para o acervo). |
| `local_producao` | Local de produção, indicação geográfica de onde o bem foi feito (INBCM, inciso XII). |
| `forma_aquisicao` | Forma de aquisição ou incorporação (compra, doação, transferência etc.). |
| `data_aquisicao` | Data de aquisição ou incorporação, como consta no portal. |
| `data_aquisicao_padronizada` | Data de aquisição em forma padronizada: AAAA-MM-DD, AAAA-MM ou AAAA, quando legível. |
| `precisao_data_aquisicao` | Precisão da data padronizada: dia, mês, ano, ano incerto ("(?)" no portal) ou ilegível. |
| `localizacao` | Localização atual do bem. |
| `situacao` | Situação do bem no portal: localizado, não localizado ou emprestado (INBCM, inciso III). |
| `estado_conservacao` | Estado de conservação. |
| `numero_patrimonio` | Número de patrimônio ou de tombo. |
| `outros_identificadores` | Outros números de registro, inventário ou código. |
| `direitos_restricoes` | Direitos, licenças ou restrições de acesso e divulgação. |
| `descricao` | Descrição histórica ou cultural: descrição do item somada a campos descritivos (marcas e inscrições, exposições, fontes bibliográficas). |
| `url_registro` | Endereço eletrônico do registro no portal. |
| `fonte` | Fonte do dado. |
| `data_consulta` | Data e hora da consulta (UTC-3). |
| `data_criacao_registro` | Data de criação do registro no Tainacan. |
| `data_modificacao_registro` | Data da última modificação do registro no Tainacan. |
| `tipo_documento` | Tipo do documento principal do item no Tainacan (imagem, url, texto, vazio). |
| `url_documento` | Endereço do documento principal quando ele é um link externo (tipo url). |
| `url_foto` | Endereço da foto original do item no portal (arquivo em tamanho integral). |
| `url_foto_grande` | Endereço da versão da foto com até 1024 px, gerada pelo portal. |
| `arquivo_foto` | Caminho da foto baixada, relativo à pasta dados: imagens/<colecao_id>/<id_registro>_<titulo>.<ext> (preenchido com --baixar-imagens). |
| `campos_principais_preenchidos` | Quantidade de variáveis principais preenchidas (ver completude). |
| `completude_pct` | Percentual de preenchimento das variáveis principais. |
| `possivel_duplicata` | Indica possível duplicidade e o critério usado. |
| `chave_duplicidade` | Chave normalizada título+autoria individual+dimensões usada na triagem inicial de duplicidades (o grupo de origem não entra na chave); a verificação refinada está em verificacao_duplicidades.csv. |

Completude cadastral: média, por registro, do preenchimento das 13 variáveis principais (categoria, titulo, autoria_origem, ano_periodo, tecnica, materiais, dimensoes, proveniencia, forma_aquisicao, localizacao, estado_conservacao, numero_patrimonio, descricao). Mede só o que consta no portal; as colunas propostas pela equipe (classificacao_tesauro, categoria_tesauro) ficam fora do cálculo.

As variáveis padronizadas são preenchidas pelo de-para em `mapeamento_campos.csv`. Quando mais de um campo original alimenta a mesma variável, os valores são unidos por ` | `. Campos vazios significam que o dado não consta no portal; nada é inferido ou inventado.

## Campos originais por coleção

### Mobiliário moderno da UnB (id 26193)

| Campo original | Slug | Tipo | Variável padronizada |
|---|---|---|---|
| Denominação | `titulo-4` | Core_Title | titulo |
| Código patrimonial | `codigo-patrimonial` | Numeric | numero_patrimonio |
| Autoria | `autoria` | Taxonomy | autoria_origem |
| Data de produção | `data-de-producao-2` | Text | ano_periodo |
| Material e técnica | `material-e-tecnica-2` | Taxonomy | material_tecnica |
| Assinatura/marca/fabricante | `assinatura-marca-fabricante` | Text | autoria_origem |
| Dimensões | `dimensoes-2` | Text | dimensoes |
| Descrição | `descricao-3` | Core_Description | descricao |
| Localização | `localizacao-3` | Text | localizacao |
| Unidade da UnB | `unidade-da-unb` | GeoCoordinate | (não mapeado) |
| Estado de conservação | `material-e-tecnica` | Selectbox | estado_conservacao |
| Descrição do estado de conservação | `descricao-do-estado-de-conservacao-2` | Textarea | estado_conservacao |
| Observações | `observacoes-4` | Textarea | descricao |
| Data de catalogação | `data-de-catalogacao` | Date | (não mapeado) |
| Responsável pela catalogação | `responsavel-pela-catalogacao` | Text | (não mapeado) |

### Memória Institucional (id 3146)

| Campo original | Slug | Tipo | Variável padronizada |
|---|---|---|---|
| Nome do evento | `title-4` | Core_Title | (não mapeado) |
| Com imagem? | `com-imagem-2` | Selectbox | (não mapeado) |
| Tipo do evento | `tipo-do-evento` | Taxonomy | categoria |
| Evento relacionado | `evento-relacionado-2` | Taxonomy | (não mapeado) |
| Ano | `ano` | Numeric | ano_periodo |
| Início | `inicio` | Text | (não mapeado) |
| Término | `termino` | Text | (não mapeado) |
| Descrição do evento | `descricao-do-evento` | Textarea | descricao |
| Diretor | `diretor` | Taxonomy | (não mapeado) |
| Responsável | `responsavel` | Taxonomy | (não mapeado) |
| Equipe | `equipe` | Text | (não mapeado) |
| Artista | `artista` | Taxonomy | autoria_origem |
| Local | `local` | Taxonomy | (não mapeado) |
| Documento relacionado | `numeros-do-documento` | Text | outros_identificadores |
| Observações | `observacoes-3` | Textarea | descricao |

### Acervo (id 1565)

| Campo original | Slug | Tipo | Variável padronizada |
|---|---|---|---|
| Denominação | `title-3` | Core_Title | titulo |
| Número de Registro | `numero-de-registro` | Text | outros_identificadores |
| Coleção | `colecao` | Taxonomy | subcolecao |
| Grupo indígena | `grupo-indigena` | Taxonomy | autoria_origem |
| Autoria | `autor` | Taxonomy | autoria_origem |
| Título | `titulo` | Text | titulo |
| Local de produção | `local-de-producao` | Taxonomy | local_producao |
| Data de produção | `data-de-producao` | Text | ano_periodo |
| Material/Técnica/Suporte | `material-tecnica` | Taxonomy | material_tecnica |
| Dimensões | `dimensoes` | Text | dimensoes |
| Marcas/Inscrições | `marcas-inscricoes` | Textarea | descricao |
| Tiragem | `tiragem` | Text | tiragem |
| Com imagem? | `com-imagem` | Selectbox | (não mapeado) |
| Forma de aquisição | `forma-de-aquisicao` | Selectbox | forma_aquisicao |
| Data de aquisição | `data-de-aquisicao` | Text | data_aquisicao |
| Procedência | `procedencia` | Taxonomy | proveniencia |
| Situação | `situacao` | Selectbox | situacao |
| Estado de conservação | `estado-de-conservacao` | Selectbox | estado_conservacao |
| Condições de reprodução | `condicoes-de-reproducao` | Text | direitos_restricoes |
| Exposições | `exposicoes` | Textarea | descricao |
| Fontes bibliográficas | `fontes-bibliograficas` | Textarea | descricao |
| Description | `description-3` | Core_Description | descricao |

## Arquivos derivados

Gerados pelos demais scripts de `codigos/` a partir desta base (`codigos/executar_pipeline.py`).

### identificacao_inbcm.csv (identificacao_inbcm.py)

| Coluna | Descrição |
|---|---|
| `id_registro, colecao, grupo_sugerido` | Identificação do bem, como no inventário (só bens; registros de evento ficam fora). |
| `numero_registro` | Número de registro museológico (INBCM, inciso I). |
| `outros_numeros_portal / outros_numeros_proposto` | Número patrimonial informado no portal / tombamento confirmado no relatório de bens da UnB, proposto pela equipe (inciso II). |
| `situacao_portal / situacao_conforme_rn` | Situação no portal e se está entre as opções da norma (inciso III). |
| `denominacao` | Nome do objeto (inciso IV). |
| `classificacao_termo, classificacao_codigo, classificacao_hierarquia, classificacao_verificacao` | Classificação proposta pelo Tesauro de Objetos (inciso VII; FERREZ, 2016) e sua verificação. |
| `obrigatorios_preenchidos / obrigatorios_ausentes / facultativos_preenchidos` | Elementos do art. 7º, § 1º, da Resolução Normativa Ibram nº 6/2021 presentes e ausentes. |

### denominacoes.csv (identificacao_inbcm.py)

| Coluna | Descrição |
|---|---|
| `denominacao / variantes` | Denominação do acervo digital (forma mais frequente) e variações só de acento ou caixa. |
| `registros / grupos` | Bens com a denominação e sua distribuição por grupo. |
| `classificacao_*` | Classificação proposta pelo Tesauro, como em identificacao_inbcm.csv. |

### vocabulario_tesauro.csv (revisão manual)

| Coluna | Descrição |
|---|---|
| `chave / correspondencia` | Denominação normalizada e tipo de correspondência (exata ou pela primeira palavra). |
| `termo_tesauro, codigo, hierarquia` | Termo, código e categoria no Tesauro de Objetos (FERREZ, 2016). |
| `verificacao / fonte` | Se o termo foi localizado literalmente ou é equivalência a confirmar; fonte. |

### inconsistencias.csv (verificar_inconsistencias.py)

| Coluna | Descrição |
|---|---|
| `id_registro, colecao, grupo_sugerido, titulo, url_registro` | Identificação do bem. |
| `tipo / campo / valor` | Tipo de inconsistência, campo do portal e valor encontrado. |
| `o_que_conferir` | O que verificar na CAL; nada é corrigido automaticamente. |

### verificacao_duplicidades.csv (verificar_duplicidades.py)

| Coluna | Descrição |
|---|---|
| `grupo / criterio / classificacao` | Grupo de registros comparados, critério e resultado (provável duplicidade, a conferir, registros distintos). |
| `demais colunas` | Dados do registro usados na comparação e observação. |

### valores_cadastro_unb.csv (cadastro_unb_relatorio.py)

| Coluna | Descrição |
|---|---|
| `id_registro / numero_registro_portal / procedencia_portal` | Registro do Acervo e dados do portal usados no vínculo. |
| `tombamentos / origem_sipat / localidade / status_cadastro` | Dados do relatório de bens da UnB, quando há vínculo. |
| `valor_registrado / valor_exibicao` | Valor registrado no cadastro (informação oficial, não mensuração). |
| `criterio_vinculo / confianca / observacao` | Critério (identificador ou procedência), grau (confirmado, provável, sem vínculo) e ressalvas. |

### bens_recentes_cadastro.csv (cadastro_unb_relatorio.py)

| Coluna | Descrição |
|---|---|
| `tombamento, data_tombamento, termo, localidade, status, estado, valor_registrado` | Dados do relatório de bens da UnB, sem nomes ou matrículas. |
| `titulo, serie, data_producao, material_tecnica, dimensoes, denominacao_inbcm` | Elementos lidos da denominação do cadastro, sem completar o que não está escrito. |
| `grupo_sugerido, criterio_grupo, indicio_contemporanea, registro_acervo_digital` | Triagem do subgrupo e verificação de registro no acervo digital. |

### reconhecimento.csv e mensuracao.csv (reconhecimento.py e mensuracao.py)

| Coluna | Descrição |
|---|---|
| `todas` | Etapas II e III; colunas descritas em metodologia/reconhecimento.md e metodologia/mensuracao.md. |

## Demais arquivos

- `inventario_bruto_longo.csv`: todos os metadados de todos os itens, um valor por linha.
- `por_colecao/`: uma planilha por coleção, com os campos originais.
- `colecoes.csv`: itens declarados, total da API e itens recuperados por coleção.
- `diagnostico_qualidade.csv`: percentual de preenchimento por variável e coleção.
- `duplicidades.csv`: possíveis duplicidades e critério.
- `indicadores.csv`: indicadores da etapa de identificação.
- `brutos/`: respostas originais da API (JSON), com URL e data de consulta.
- `log_extracao.json`: parâmetros, requisições, avisos, erros e limitações.
