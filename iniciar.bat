@echo off
rem Abre a tela do assistente em http://localhost:8501 (mensagens sem acento: o console pode nao exibi-los).
cd /d "%~dp0"
python -c "import streamlit, pypdf, openai, dotenv" >nul 2>&1 || python -m pip install -r requirements.txt || (pause & exit /b 1)
if not exist ".env" echo [AVISO] Copie .env.example para .env e preencha a GEMINI_API_KEY.
python -m streamlit run app.py || pause
