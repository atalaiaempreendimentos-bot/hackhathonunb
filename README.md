# CULTIVA UnB 2026: Quanto vale o patrimônio cultural da UnB?

Solução da equipe para o Hackathon CULTIVA UnB 2026 (PPGCont/UnB, disciplina Valoração de Ativos Culturais e Ambientais, código 318710; Profa. Fátima de Souza Freire e Prof. Jorge Madeira Nogueira).

Objeto: identificação, reconhecimento, mensuração e evidenciação dos ativos culturais do Acervo Digital da Casa da Cultura da América Latina (CAL/UnB), em https://www.acervocal.unb.br/ (plataforma Tainacan).

## Integrantes

- Hugo Rodrigues Gomes
- Yang Alfredo Florentino
- Lucas (completar sobrenome)

## Estrutura

```
cultiva-unb-trio/
├── README.md
├── rodar_extracao.command          coleta com dois cliques (macOS)
├── rodar_extracao.bat              coleta com dois cliques (Windows)
├── rodar_no_vscode.py              coleta completa pelo botão executar do VS Code
├── baixar_acervo_1565.py           busca da coleção 1565 (páginas 1 a 16) com todos os metadados
├── baixar_acervo_1565_com_fotos.py a mesma busca, com download das fotos (uso autorizado)
├── acervo_1565/                    saída da busca da coleção 1565 (fotos não incluídas no repositório)
├── codigos/
│   ├── extrair_acervo_cal.py      extrator (API REST do Tainacan), sem dependências externas
│   ├── versoes_anteriores/        versões anteriores do extrator
│   └── coletar_no_navegador.js    coleta alternativa pelo Console do navegador
├── dados/                          saída do extrator (ver dicionario_dados.md após rodar)
├── metodologia/
│   ├── identificacao.md
│   ├── reconhecimento.md
│   ├── mensuracao.md
│   └── evidenciacao.md
├── resultados/                     indicadores, demonstrativos, nota explicativa
├── relatorio_final/
└── apresentacao/
```

## Etapa I: como reproduzir a extração

Requisito: Python 3.8 ou superior. Nada mais precisa ser instalado. Se o pacote `openpyxl` estiver presente, o script também gera `dados/CULTIVA_acervo_CAL.xlsx`.

### Opção A: terminal

```bash
cd cultiva-unb-trio
python3 codigos/extrair_acervo_cal.py --saida dados
```

Em 23/11/2026 o portal apresentou certificado TLS vencido (o navegador exibe o aviso "Sua conexão não é particular"). Nessa situação o Python recusa a conexão e o script explica o erro. Se a equipe decidir aceitar o risco, por se tratar de dados públicos e de consulta somente leitura:

```bash
python3 codigos/extrair_acervo_cal.py --saida dados --sem-verificar-ssl
```

A opção fica registrada em `dados/log_extracao.json` e deve constar das limitações.

### Opção B: navegador

1. Abrir https://www.acervocal.unb.br/ no Chrome.
2. Abrir o Console (Cmd+Option+J no Mac; Ctrl+Shift+J no Windows). Se o Chrome pedir, digitar `allow pasting`.
3. Colar todo o conteúdo de `codigos/coletar_no_navegador.js` e teclar Enter.
4. O navegador baixa `acervo_cal_bruto_AAAAMMDD_HHMM.json`.
5. Rodar: `python3 codigos/extrair_acervo_cal.py --saida dados --importar caminho/do/acervo_cal_bruto_....json`

As duas opções produzem as mesmas tabelas.

### Arquivos gerados em `dados/`

| Arquivo | Conteúdo |
|---|---|
| `inventario.csv` | Base padronizada com as variáveis do item 7 das Regras (identificador, coleção, categoria, título, autoria ou grupo de origem, ano, técnica, materiais, dimensões, proveniência, forma de aquisição, localização, estado de conservação, nº de patrimônio, descrição, fonte e URL), mais triagem de grupo, completude e duplicidade |
| `inventario_excel.csv` | A mesma base com separador `;` (Excel em português) |
| `inventario_bruto_longo.csv` | Todos os metadados de todos os itens, um valor por linha, sem perda de informação |
| `por_colecao/*.csv` | Uma planilha por coleção, com os campos originais do portal |
| `colecoes.csv` | Itens declarados, total informado pela API e itens recuperados, por coleção |
| `metadados_colecoes.csv` | Definição dos campos de cada coleção |
| `mapeamento_campos.csv` | De-para campo original para variável padronizada, com a regra aplicada |
| `diagnostico_qualidade.csv` | Percentual de preenchimento de cada variável, por coleção e por grupo |
| `duplicidades.csv` | Possíveis duplicidades (mesmo ID, mesmo nº de patrimônio, mesmo título+autoria+dimensões) |
| `indicadores.csv` | Registros identificados, recuperados, cobertura, completude, duplicidades, rastreabilidade |
| `metadados_completos.csv` | Uma linha por item com todos os metadados de todas as coleções e os links e arquivos das fotos |
| `galeria.html` | Galeria para o navegador: foto e todos os metadados, com busca e filtros |
| `imagens/` | Fotos, somente com autorização da CAL registrada (`--autorizacao`) |
| `dicionario_dados.md` | Dicionário de dados gerado automaticamente |
| `log_extracao.json` | Data, parâmetros, requisições, avisos, erros e limitações |
| `brutos/` | Respostas originais da API (JSON) com URL e data de consulta |

### Pelo VS Code

- Coleta da coleção 1565 com todos os metadados: abra `baixar_acervo_1565.py` e clique em executar (Run Python File), ou, no terminal do VS Code, `python3 baixar_acervo_1565.py`. Resultado em `acervo_1565/`.
- Coleta de todas as coleções com o pacote completo de tabelas: `python3 rodar_no_vscode.py`, ou Terminal > Run Task > CULTIVA.

Cada obra fica ligada à sua foto pelos links (`url_foto_original`/`url_foto`, `url_foto_1024px`/`url_foto_grande`) e pela galeria (`galeria_acervo_1565.html`, `dados/galeria.html`), que exibe a foto do portal ao lado de todos os metadados.

### Direitos das imagens

No campo "Condições de reprodução", o portal informa para 1.237 das 1.245 obras com foto da coleção 1565: "Direitos Reservados. As fotografias do acervo não podem ser baixadas e/ou reproduzidas", com remissão à Lei nº 9.610/1998. As Regras exigem respeitar direitos autorais e restrições de uso (item 17.11) e vedam publicar imagens restritas sem autorização (item 12). Por isso os scripts não baixam as fotos. Com autorização por escrito da CAL/UnB, registre-a em `AUTORIZACAO_CAL` (`baixar_acervo_1565.py`) ou use `--baixar-imagens --autorizacao "referência"` no extrator; a autorização fica registrada no log. As fotos nunca vão para o GitHub (`.gitignore`).

### Revisão do de-para

O de-para inicial usa palavras-chave nos nomes dos campos e, quando existir, o mapeamento Dublin Core do Tainacan. Para corrigir: editar a coluna `variavel_padronizada` de `dados/mapeamento_campos.csv` (várias variáveis podem ser unidas com `+`, ou a célula pode ficar vazia) e rodar, sem acessar a rede:

```bash
python3 codigos/extrair_acervo_cal.py --saida dados --offline --mapa dados/mapeamento_campos.csv
```

### Cuidados

- Coleta com pausa de 1 s entre requisições, novas tentativas com espera crescente e cache local (Regras, item 17.12).
- Imagens e documentos não são baixados; apenas seus endereços são registrados (Regras, item 12, sobre restrições de divulgação).
- `grupo_sugerido` e `flag_possivel_contemporanea` são triagens automáticas por palavra-chave e precisam de revisão da equipe.
- Cobertura do acervo digital não equivale à cobertura do patrimônio físico da CAL (Regras, item 4.4).
- O mesmo script funciona em outros portais Tainacan (`--base https://...`), o que atende à demonstração de aplicação a outros acervos públicos (Regras, item 5, passo 12).

## Fontes

- UNIVERSIDADE DE BRASÍLIA. Casa da Cultura da América Latina. Acervo Digital da CAL. Disponível em: https://www.acervocal.unb.br/. Data de acesso: registrada em `dados/log_extracao.json`.
- Regras do Hackathon CULTIVA UnB 2026 (PPGCont/UnB, 2026).

## Registro de uso de inteligência artificial

| Data | Ferramenta | Uso | Verificação pela equipe |
|---|---|---|---|
| 23/11/2026 | Claude (Anthropic) | Rascunho do extrator, do trecho para navegador, deste README e do roteiro de trabalho | Código testado contra API simulada no formato do Tainacan |
| 23/11/2026 | Claude (Anthropic) | Versões 1.1.x do extrator (links das fotos, metadados completos, galeria), scripts `baixar_acervo_1565*.py`, tarefas do VS Code e diagnóstico das obras sem foto | Coletas executadas pela equipe em 23/11/2026: 2.197 registros em 3 coleções; 1.497 obras e 1.245 fotos da coleção 1565, sem falhas |

## Limitações

Registradas até 23/11/2026 (completar ao longo do hackathon):

- O portal apresentou certificado TLS vencido em 23/11/2026; a coleta foi feita sem verificação do certificado, por decisão da equipe, e isso consta dos logs.
- A cobertura refere-se ao universo digital público: 2.197 registros em 3 coleções (Acervo, 1.497; Memória Institucional, 699; Mobiliário moderno da UnB, 1), todos recuperados. Isso não equivale ao patrimônio físico da CAL (Regras, item 4.4).
- Completude cadastral média de 32,9% nas 13 variáveis principais e 427 registros com possível duplicidade, ainda a conferir manualmente.
- A triagem automática de grupos deixou 1.046 registros como "A classificar".
- Na coleção 1565, 252 obras não têm foto no portal (181 da coleção Inicial, 39 da Galvão, 21 da Arte, 10 da Triangular e 1 sem coleção informada). Há inconsistências cadastrais: o ID 11924 (Videoarte, CE.008) consta "Com imagem? = Sim" sem foto; os IDs 1715 e 25973 têm o campo vazio; o ID 25320 tem "Coleção = False".
- O portal informa, para 1.237 das 1.245 obras com foto da coleção 1565, que as fotografias não podem ser baixadas e/ou reproduzidas (Lei nº 9.610/1998). As fotos foram baixadas para uso acadêmico interno com autorização declarada pela equipe em 23/11/2026 (registrar quem autorizou, meio e data) e não fazem parte deste repositório.
