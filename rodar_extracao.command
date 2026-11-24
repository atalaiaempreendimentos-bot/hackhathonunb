#!/bin/bash
# Hackathon CULTIVA UnB 2026: coleta do Acervo Digital da CAL/UnB
# macOS: dê dois cliques neste arquivo. Ou, no Terminal: bash rodar_extracao.command
cd "$(dirname "$0")" || exit 1
echo "Pasta do projeto: $(pwd)"
if ! command -v python3 >/dev/null 2>&1; then
  echo ""
  echo "Python 3 não encontrado neste Mac."
  echo "Instale rodando no Terminal:  xcode-select --install"
  echo "ou baixe em https://www.python.org/downloads/ e rode este arquivo de novo."
  read -r -p "Tecle Enter para fechar..." _
  exit 1
fi
python3 --version
echo ""
python3 codigos/extrair_acervo_cal.py --saida dados --sem-verificar-ssl "$@"
status=$?
echo ""
if [ $status -eq 0 ]; then
  echo "Pronto. Arquivos gerados em: $(pwd)/dados"
  command -v open >/dev/null 2>&1 && open dados
else
  echo "A coleta terminou com erro (código $status). Veja dados/log_extracao.json."
fi
read -r -p "Tecle Enter para fechar..." _
