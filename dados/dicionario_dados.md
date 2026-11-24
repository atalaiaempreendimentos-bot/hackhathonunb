# Dicionário de dados: Acervo Digital da CAL/UnB

Gerado automaticamente por `extrair_acervo_cal.py` v1.1.2 em 2026-11-23 19:12. Fonte: https://www.acervocal.unb.br.

## inventario.csv (base padronizada)

| Coluna | Descrição |
|---|---|
| `id_registro` | Identificador interno do item no Tainacan (preservado do portal). |
| `colecao_id` | Identificador da coleção no Tainacan. |
| `colecao` | Nome da coleção no portal. |
| `subcolecao` | Conjunto ou subcoleção informado nos metadados (ex.: Coleção Galvão, Chocó). |
| `grupo_sugerido` | Triagem automática: Arte, Arte contemporânea, Etnográfica ou A classificar. Sujeita a revisão. |
| `criterio_grupo` | Termo que motivou a triagem do grupo (rastreabilidade da regra). |
| `flag_possivel_contemporanea` | 'sim' quando técnica, categoria ou suporte indicam obra contemporânea (vídeo, instalação, arte postal etc.). |
| `categoria` | Categoria, tipologia ou classificação do bem. |
| `titulo` | Título ou denominação. |
| `autoria_origem` | Artista, autor ou grupo de origem (inclui etnia ou povo, nas coleções etnográficas). |
| `ano_periodo` | Ano, data ou período de produção, como consta no portal. |
| `ano_inicial_extraido` | Primeiro ano com quatro dígitos encontrado em ano_periodo (apoio a filtros; não substitui o dado original). |
| `tecnica` | Técnica. |
| `materiais` | Materiais ou suporte. |
| `dimensoes` | Dimensões, como constam no portal. |
| `tiragem` | Tiragem, edição ou numeração de exemplar (gravuras, fotografias, múltiplos). |
| `proveniencia` | Proveniência, procedência ou local de origem. |
| `forma_aquisicao` | Forma de aquisição ou incorporação (compra, doação, transferência etc.). |
| `localizacao` | Localização atual do bem. |
| `estado_conservacao` | Estado de conservação. |
| `numero_patrimonio` | Número de patrimônio ou de tombo. |
| `outros_identificadores` | Outros números de registro, inventário ou código. |
| `direitos_restricoes` | Direitos, licenças ou restrições de acesso e divulgação. |
| `descricao` | Descrição histórica ou cultural (descrição do item somada a campos descritivos). |
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
| `chave_duplicidade` | Chave normalizada título+autoria+dimensões usada na detecção. |

As variáveis padronizadas são preenchidas pelo de-para em `mapeamento_campos.csv`. Quando mais de um campo original alimenta a mesma variável, os valores são unidos por ` | `. Campos vazios significam que o dado não consta no portal; nada é inferido ou inventado.

## Campos originais por coleção

### Mobiliário moderno da UnB (id 26193)

| Campo original | Slug | Tipo | Variável padronizada |
|---|---|---|---|
| Denominação | `titulo-4` | Core_Title | titulo |
| Código patrimonial | `codigo-patrimonial` | Numeric | numero_patrimonio |
| Autoria | `autoria` | Taxonomy | autoria_origem |
| Data de produção | `data-de-producao-2` | Text | ano_periodo |
| Material e técnica | `material-e-tecnica-2` | Taxonomy | tecnica+materiais |
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
| Grupo indígena | `grupo-indigena` | Taxonomy | (não mapeado) |
| Autoria | `autor` | Taxonomy | autoria_origem |
| Título | `titulo` | Text | titulo |
| Local de produção | `local-de-producao` | Taxonomy | proveniencia |
| Data de produção | `data-de-producao` | Text | ano_periodo |
| Material/Técnica/Suporte | `material-tecnica` | Taxonomy | tecnica+materiais |
| Dimensões | `dimensoes` | Text | dimensoes |
| Marcas/Inscrições | `marcas-inscricoes` | Textarea | descricao |
| Tiragem | `tiragem` | Text | tiragem |
| Com imagem? | `com-imagem` | Selectbox | (não mapeado) |
| Forma de aquisição | `forma-de-aquisicao` | Selectbox | forma_aquisicao |
| Data de aquisição | `data-de-aquisicao` | Text | forma_aquisicao |
| Procedência | `procedencia` | Taxonomy | proveniencia |
| Situação | `situacao` | Selectbox | (não mapeado) |
| Estado de conservação | `estado-de-conservacao` | Selectbox | estado_conservacao |
| Condições de reprodução | `condicoes-de-reproducao` | Text | direitos_restricoes |
| Exposições | `exposicoes` | Textarea | (não mapeado) |
| Fontes bibliográficas | `fontes-bibliograficas` | Textarea | (não mapeado) |
| Description | `description-3` | Core_Description | descricao |

## Demais arquivos

- `inventario_bruto_longo.csv`: todos os metadados de todos os itens, um valor por linha.
- `por_colecao/`: uma planilha por coleção, com os campos originais.
- `colecoes.csv`: itens declarados, total da API e itens recuperados por coleção.
- `diagnostico_qualidade.csv`: percentual de preenchimento por variável e coleção.
- `duplicidades.csv`: possíveis duplicidades e critério.
- `indicadores.csv`: indicadores da etapa de identificação.
- `brutos/`: respostas originais da API (JSON), com URL e data de consulta.
- `log_extracao.json`: parâmetros, requisições, avisos, erros e limitações.
