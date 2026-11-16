@echo off
rem Atualiza o cartao "Construindo com IA" do perfil do GitHub (agendado toda segunda 10h).
rem So conta sessoes por dia; nada de nomes de projeto ou conteudo sai do PC.
cd /d "%~dp0"
git pull -q
python scripts\build_ai_activity.py >> atualizar-ia.log 2>&1
git add assets\ai-dark.svg assets\ai-light.svg
git diff --cached --quiet || (git commit -q -m "Atualiza cartao de atividade com IA" && git push -q)
echo %date% %time% ok >> atualizar-ia.log
