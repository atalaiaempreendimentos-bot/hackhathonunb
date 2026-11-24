"""
Hackathon CULTIVA UnB 2026: coleta completa do Acervo Digital da CAL/UnB pelo VS Code.

Como usar no Visual Studio Code:
  1. Arquivo > Abrir Pasta... e escolha a pasta cultiva-unb-trio.
  2. Abra este arquivo (rodar_no_vscode.py).
  3. Clique no botão de executar (triângulo no canto superior direito, "Run Python File"),
     ou abra Terminal > Novo Terminal e digite:  python3 rodar_no_vscode.py

O que acontece:
  - Coleta todas as coleções e todos os metadados (reaproveita o cache em dados/brutos, se existir).
  - Liga cada item à sua foto pelos links (url_foto, url_foto_grande).
  - Gera dados/metadados_completos.csv (todos os metadados + links das fotos) e dados/galeria.html.

As fotos NÃO são baixadas: o portal informa que as fotografias do acervo não podem ser baixadas
e/ou reproduzidas sem autorização (Lei nº 9.610/1998). Com autorização da CAL, acrescente à lista
"--baixar-imagens", "--autorizacao", "referência da autorização".
Para refazer a coleta do zero (ignorar o cache), acrescente "--atualizar" à lista.
"""
import os
import runpy
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
os.chdir(AQUI)

sys.argv = [
    "extrair_acervo_cal.py",
    "--saida", "dados",
    "--sem-verificar-ssl",          # certificado do portal vencido em 23/11/2026 (ver README)
]

runpy.run_path(os.path.join(AQUI, "codigos", "extrair_acervo_cal.py"), run_name="__main__")
