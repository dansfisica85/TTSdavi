#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
FastAPI entrypoint for Vercel deployment
Simple API endpoint for serverless deployment
"""

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

# Create the FastAPI app
app = FastAPI(title="AI Cover Studio")

# Informações do Desenvolvedor
DESENVOLVEDOR = "Professor Davi Antonino Nunes da Silva"
CONTATO = "(16) 99260-4315"
EMAIL = "professordavi85@gmail.com"

@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AI Cover Studio</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                color: white;
            }
            .container {
                text-align: center;
                padding: 40px;
                background: rgba(255,255,255,0.1);
                border-radius: 20px;
                backdrop-filter: blur(10px);
                max-width: 600px;
                margin: 20px;
            }
            h1 {
                font-size: 2.5em;
                margin-bottom: 10px;
                background: linear-gradient(90deg, #e94560, #ff6b6b);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }
            .subtitle { color: #aaa; margin-bottom: 30px; }
            .feature {
                background: rgba(233, 69, 96, 0.2);
                padding: 15px 25px;
                border-radius: 10px;
                margin: 10px 0;
                border-left: 4px solid #e94560;
            }
            .developer {
                margin-top: 30px;
                padding-top: 20px;
                border-top: 1px solid rgba(255,255,255,0.2);
                font-size: 0.9em;
                color: #888;
            }
            .status {
                display: inline-block;
                background: #4caf50;
                color: white;
                padding: 5px 15px;
                border-radius: 20px;
                font-size: 0.8em;
                margin-top: 20px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎤 AI Cover Studio</h1>
            <p class="subtitle">Sistema de Clonagem e Conversão de Voz com IA</p>
            
            <div class="feature">🎵 Separação de Vocais e Instrumentais</div>
            <div class="feature">🗣️ Clonagem de Voz com IA</div>
            <div class="feature">🎧 Mixagem Automática de Áudio</div>
            
            <span class="status">✓ API Online</span>
            
            <div class="developer">
                <p><strong>Desenvolvido por:</strong> Professor Davi Antonino Nunes da Silva</p>
                <p>📞 (16) 99260-4315 | 📧 professordavi85@gmail.com</p>
            </div>
        </div>
    </body>
    </html>
    """

@app.get("/api/status")
async def status():
    return {
        "status": "online",
        "app": "AI Cover Studio",
        "version": "1.0.0",
        "developer": DESENVOLVEDOR,
        "contact": CONTATO,
        "email": EMAIL,
        "message": "API funcionando! Para funcionalidades completas de ML, use o Docker localmente."
    }

@app.get("/api/info")
async def info():
    return {
        "name": "AI Cover Studio",
        "description": "Sistema de AI Covers - Clonagem e Conversão de Voz",
        "features": [
            "Separação de vocais e instrumentais",
            "Clonagem de voz com IA", 
            "Mixagem automática de áudio"
        ],
        "note": "Esta é uma versão demo. Para treinar modelos e processar áudio, execute localmente com Docker."
    }
