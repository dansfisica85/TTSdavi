#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Configurações otimizadas para Gradio
Resolve problemas de ClientDisconnect e uploads instáveis
"""

import os
from pathlib import Path


# =============================================================================
# CONFIGURAÇÕES DE UPLOAD
# =============================================================================

class GradioConfig:
    """Configurações otimizadas para Gradio com melhor tratamento de uploads"""
    
    # Tamanho máximo de upload em MB
    MAX_FILE_SIZE_MB = int(os.environ.get("MAX_FILE_SIZE_MB", "500"))
    
    # Timeout para uploads (em segundos)
    UPLOAD_TIMEOUT = int(os.environ.get("UPLOAD_TIMEOUT", "600"))
    
    # Chunk size para upload (em bytes)
    CHUNK_SIZE = int(os.environ.get("CHUNK_SIZE", "1048576"))  # 1MB
    
    # Retry count para uploads falhados
    MAX_RETRIES = int(os.environ.get("MAX_RETRIES", "3"))
    
    # Temporary directory for uploads
    TEMP_DIR = Path(os.environ.get("TEMP_DIR", "/tmp/gradio_uploads"))
    
    # Keep uploaded files after processing
    KEEP_TEMP_FILES = os.environ.get("KEEP_TEMP_FILES", "false").lower() == "true"
    
    @staticmethod
    def get_launch_kwargs():
        """Retorna argumentos otimizados para gr.demo.launch()"""
        return {
            # Básico
            "server_name": os.environ.get("GRADIO_SERVER_NAME", "0.0.0.0"),
            "server_port": int(os.environ.get("PORT", os.environ.get("GRADIO_SERVER_PORT", "7860"))),
            
            # Upload e Request
            "max_file_size": f"{GradioConfig.MAX_FILE_SIZE_MB}mb",
            
            # Timeouts
            "max_size": GradioConfig.MAX_FILE_SIZE_MB * 1024 * 1024,  # bytes
            
            # Interface
            "show_error": True,
            "inbrowser": False,
            
            # Produção (Railway/Vercel)
            "share": os.environ.get("GRADIO_SHARE", "true").lower() == "true",
            
            # Performance
            "quiet": False,
            
            # SSL (se necessário)
            "ssl_certfile": os.environ.get("SSL_CERTFILE"),
            "ssl_keyfile": os.environ.get("SSL_KEYFILE"),
            "ssl_verify": os.environ.get("SSL_VERIFY", "true").lower() == "true",
            
            # Proxy
            "root_path": os.environ.get("GRADIO_ROOT_PATH", ""),
            
            # Analytics (desabilitar em produção)
            "analytics_enabled": False,
        }
    
    @staticmethod
    def get_gradio_environment_vars():
        """Define variáveis de ambiente para otimizar Gradio"""
        return {
            # Aumentar timeout de request
            "GRADIO_REQUEST_TIMEOUT": os.environ.get("GRADIO_REQUEST_TIMEOUT", "600"),
            
            # Desabilitar analytics (economiza banda)
            "GRADIO_ANALYTICS_ENABLED": "False",
            
            # Aumentar buffer de upload
            "GRADIO_UPLOAD_BUFFER_SIZE": os.environ.get("GRADIO_UPLOAD_BUFFER_SIZE", "10485760"),  # 10MB
            
            # Desabilitar auto-reload em produção
            "GRADIO_AUTORELOAD": "False",
            
            # Logging
            "GRADIO_LOG_LEVEL": os.environ.get("GRADIO_LOG_LEVEL", "INFO"),
        }


def setup_gradio_environment():
    """Configura variáveis de ambiente para otimizar Gradio"""
    env_vars = GradioConfig.get_gradio_environment_vars()
    for key, value in env_vars.items():
        if value is not None:
            os.environ[key] = str(value)
    
    # Criar diretório temporário
    GradioConfig.TEMP_DIR.mkdir(parents=True, exist_ok=True)


# Aplicar configurações ao importar
setup_gradio_environment()
