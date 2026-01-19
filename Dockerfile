# Dockerfile leve para Railway - AI Cover Studio
# Build version: 2026-01-19
FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV GRADIO_SERVER_NAME=0.0.0.0
ENV PORT=8080

WORKDIR /app

# Instalar apenas ffmpeg
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Copiar apenas requirements
COPY requirements-railway.txt .

# Instalar dependências Python
RUN pip install -r requirements-railway.txt

# Copiar apenas os arquivos necessários da aplicação
COPY ai_cover_app.py .
COPY audio_separator.py .
COPY audio_mixer.py .
COPY voice_converter.py .
COPY voice_trainer.py .
COPY clonar_voz.py .

# Criar diretórios
RUN mkdir -p models datasets output

EXPOSE 8080

CMD ["python", "ai_cover_app.py"]
