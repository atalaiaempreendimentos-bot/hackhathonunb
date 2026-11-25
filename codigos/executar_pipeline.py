#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Executa as cinco etapas do Hackathon CULTIVA UnB 2026, em ordem, a partir da raiz do repositório.

  python3 codigos/executar_pipeline.py                 # reprocessa os dados já baixados (offline)
  python3 codigos/executar_pipeline.py --atualizar     # baixa de novo o portal antes de reprocessar
  python3 codigos/executar_pipeline.py --cadastro Lista_da_CAL.numbers   # inclui o cadastro patrimonial

Etapas: I identificação (extrair_acervo_cal.py, verificar_duplicidades.py, identificacao_inbcm.py e verificar_inconsistencias.py) → II reconhecimento (reconhecimento.py e reconhecimento_cadastro.py) →
III mensuração (comparaveis.py, que chama mensuracao.py) → validação de casos (validacao_casos.py) →
IV evidenciação (evidenciacao.py). O cadastro patrimonial é opcional e nunca vai para o repositório na
forma original, pois contém dados pessoais.
Para outro acervo Tainacan: --base https://outro-acervo/wp-json/tainacan/v2 (ver README).
"""
import argparse
import os
import subprocess
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)


def rodar(script, *args):
    cmd = [sys.executable, os.path.join(AQUI, script)] + list(args)
    print("\n>>", " ".join(os.path.relpath(c, RAIZ) if c.startswith(RAIZ) else c for c in cmd[1:]))
    r = subprocess.run(cmd, cwd=RAIZ)
    if r.returncode != 0:
        sys.exit("Falhou: " + script)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--atualizar", action="store_true", help="baixar de novo os registros do portal")
    ap.add_argument("--base", help="endereço da API Tainacan de outro acervo")
    ap.add_argument("--sem-verificar-ssl", action="store_true", help="repassado ao extrator (fica registrado no log)")
    ap.add_argument("--cadastro", help="arquivo do cadastro patrimonial (.numbers ou .csv) para a conciliação")
    ap.add_argument("--relatorio-bens", help="relatório de bens da UnB (.xlsx, obras de arte) para o valor de cada registro")
    a = ap.parse_args()
    ext = ["--saida", "dados"] + (["--base", a.base] if a.base else []) + (["--sem-verificar-ssl"] if a.sem_verificar_ssl else [])
    rodar("extrair_acervo_cal.py", *(ext + ([] if a.atualizar else ["--offline"])))
    if a.cadastro:
        rodar("cadastro_patrimonial.py", a.cadastro)
    if a.relatorio_bens:
        rodar("cadastro_unb_relatorio.py", a.relatorio_bens)
    rodar("verificar_duplicidades.py")
    rodar("identificacao_inbcm.py")
    rodar("verificar_inconsistencias.py")
    rodar("comparaveis.py")
    rodar("reconhecimento.py")
    rodar("reconhecimento_cadastro.py")
    rodar("validacao_casos.py")
    rodar("evidenciacao.py")
    print("\nConcluído. Resultados em dados/ e resultados/.")


if __name__ == "__main__":
    main()
