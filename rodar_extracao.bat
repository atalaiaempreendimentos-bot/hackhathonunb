@echo off
rem Hackathon CULTIVA UnB 2026: coleta do Acervo Digital da CAL/UnB (Windows: dois cliques)
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (
  py -3 codigos\extrair_acervo_cal.py --saida dados --sem-verificar-ssl %*
) else (
  python codigos\extrair_acervo_cal.py --saida dados --sem-verificar-ssl %*
)
echo.
echo Arquivos em: %cd%\dados
pause
