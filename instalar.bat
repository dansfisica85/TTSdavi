@echo off
REM Script de Instalação do Clonador de Voz
REM =========================================

echo.
echo ================================================
echo    Instalador do Clonador de Voz TTS Davi
echo ================================================
echo.

REM Verificar se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python nao encontrado! Por favor instale Python 3.9-3.12
    pause
    exit /b 1
)

echo [OK] Python encontrado
python --version

echo.
echo Instalando dependencias... (isso pode demorar alguns minutos)
echo.

REM Instalar dependências principais
pip install coqpit coqui-tts-trainer

REM Instalar dependências do TTS
pip install pysbd inflect anyascii mutagen flask umap-learn matplotlib
pip install jieba pypinyin hangul_romanize jamo nltk g2pkk
pip install bangla bnnumerizer bnunicodenormalizer
pip install einops encodec unidecode num2words gruut

REM Instalar dependências para interface e áudio
pip install gradio faster-whisper torchaudio librosa soundfile

echo.
echo ================================================
echo    Instalacao concluida!
echo ================================================
echo.
echo Para executar o clonador de voz:
echo    python clonar_voz.py
echo.
echo Para mais informacoes, leia o README_CLONADOR.md
echo.

pause
