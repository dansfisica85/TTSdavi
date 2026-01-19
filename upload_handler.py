#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Middleware Gradio para tratamento robusto de uploads
Resolve problemas de ClientDisconnect e melhor gerenciamento de memória
"""

import os
import asyncio
import logging
from pathlib import Path
from typing import Optional, Callable
from functools import wraps

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UploadHandler:
    """Handler robusto para uploads de arquivos com retry e tratamento de erro"""
    
    def __init__(
        self,
        max_retries: int = 3,
        timeout: int = 600,
        chunk_size: int = 1048576  # 1MB
    ):
        self.max_retries = max_retries
        self.timeout = timeout
        self.chunk_size = chunk_size
    
    async def handle_upload_with_retry(
        self,
        file_path: str,
        operation: Callable,
        *args,
        **kwargs
    ):
        """Executa operação com retry automático para falhas de upload"""
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Tentativa {attempt + 1}/{self.max_retries}: {file_path}")
                
                # Verificar se arquivo existe
                if not os.path.exists(file_path):
                    raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
                
                # Obter tamanho do arquivo
                file_size = os.path.getsize(file_path)
                logger.info(f"Tamanho do arquivo: {file_size / 1024 / 1024:.2f} MB")
                
                # Executar operação com timeout
                try:
                    result = await asyncio.wait_for(
                        self._async_operation(operation, file_path, *args, **kwargs),
                        timeout=self.timeout
                    )
                    logger.info(f"✓ Upload bem-sucedido: {file_path}")
                    return result
                
                except asyncio.TimeoutError:
                    logger.warning(f"⏱️ Timeout na tentativa {attempt + 1}")
                    if attempt == self.max_retries - 1:
                        raise TimeoutError(f"Upload expirou após {self.timeout}s")
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                    continue
                
                except Exception as e:
                    logger.error(f"❌ Erro na tentativa {attempt + 1}: {str(e)}")
                    if attempt == self.max_retries - 1:
                        raise
                    await asyncio.sleep(2 ** attempt)
                    continue
            
            except Exception as e:
                if attempt == self.max_retries - 1:
                    logger.error(f"❌ Falha final após {self.max_retries} tentativas: {str(e)}")
                    raise
        
        raise RuntimeError(f"Upload falhou após {self.max_retries} tentativas")
    
    @staticmethod
    async def _async_operation(operation: Callable, file_path: str, *args, **kwargs):
        """Executa operação de forma assíncrona"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, operation, file_path, *args, **kwargs)


class ClientDisconnectHandler:
    """Handler para problemas de desconexão de cliente"""
    
    @staticmethod
    def catch_client_disconnect(func):
        """Decorator para capturar e tratar ClientDisconnect graciosamente"""
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                if "ClientDisconnect" in str(type(e)) or "ClientDisconnect" in str(e):
                    logger.warning(f"⚠️ Cliente desconectou: {str(e)}")
                    return None  # Retorna None em vez de crashed
                raise
        
        return wrapper


def validate_upload(
    file_path: Optional[str],
    allowed_extensions: tuple = (".wav", ".mp3", ".flac", ".ogg"),
    max_size_mb: int = 500
) -> tuple[bool, str]:
    """
    Valida um arquivo de upload
    
    Returns:
        (is_valid, message)
    """
    if file_path is None:
        return False, "❌ Nenhum arquivo selecionado"
    
    file_path = Path(file_path)
    
    if not file_path.exists():
        return False, f"❌ Arquivo não encontrado: {file_path}"
    
    if file_path.suffix.lower() not in allowed_extensions:
        return False, f"❌ Formato não suportado: {file_path.suffix}\n✅ Suportados: {', '.join(allowed_extensions)}"
    
    file_size_mb = file_path.stat().st_size / 1024 / 1024
    if file_size_mb > max_size_mb:
        return False, f"❌ Arquivo muito grande: {file_size_mb:.1f}MB (máximo: {max_size_mb}MB)"
    
    return True, f"✅ Arquivo validado: {file_path.name} ({file_size_mb:.1f}MB)"


def sanitize_filename(filename: str) -> str:
    """Remove caracteres perigosos do nome do arquivo"""
    import re
    # Manter apenas caracteres seguros
    filename = re.sub(r'[^\w\s.-]', '', filename)
    filename = re.sub(r'\s+', '_', filename)
    return filename[:255]  # Limitar comprimento


def cleanup_temp_files(directory: Path, max_age_hours: int = 24):
    """Limpa arquivos temporários antigos"""
    import time
    
    if not directory.exists():
        return
    
    now = time.time()
    max_age_seconds = max_age_hours * 3600
    
    deleted_count = 0
    for file in directory.glob("*"):
        if os.path.isfile(file):
            file_age = now - os.path.getmtime(file)
            if file_age > max_age_seconds:
                try:
                    file.unlink()
                    deleted_count += 1
                except Exception as e:
                    logger.warning(f"Erro ao deletar {file}: {e}")
    
    if deleted_count > 0:
        logger.info(f"🧹 Limpeza: {deleted_count} arquivos antigos removidos")
