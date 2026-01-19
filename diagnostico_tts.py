#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Diagnóstico do TTS - Verifica problemas de carregamento
"""

import os
import sys
import time

print("=" * 60)
print("🔍 DIAGNÓSTICO DO TTS - Identificando problemas")
print("=" * 60)

# 1. Verificar memória disponível
print("\n📊 1. Verificando recursos do sistema...")
try:
    import psutil
    mem = psutil.virtual_memory()
    print(f"   RAM Total: {mem.total / (1024**3):.2f} GB")
    print(f"   RAM Disponível: {mem.available / (1024**3):.2f} GB")
    print(f"   RAM Usada: {mem.percent}%")
    
    if mem.available < 4 * (1024**3):  # Menos de 4GB
        print("   ⚠️  AVISO: Pouca memória RAM disponível! XTTS precisa de ~4GB+")
except ImportError:
    print("   ⚠️  psutil não instalado, pulando verificação de memória")

# 2. Verificar GPU/CUDA
print("\n🎮 2. Verificando GPU/CUDA...")
try:
    import torch
    print(f"   PyTorch versão: {torch.__version__}")
    print(f"   CUDA disponível: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"   GPU: {torch.cuda.get_device_name(0)}")
        print(f"   Memória GPU: {torch.cuda.get_device_properties(0).total_memory / (1024**3):.2f} GB")
    else:
        print("   ℹ️  Usando CPU (mais lento)")
except Exception as e:
    print(f"   ❌ Erro verificando PyTorch: {e}")

# 3. Verificar diretório de cache do TTS
print("\n📁 3. Verificando cache do modelo TTS...")
cache_paths = [
    os.path.expanduser("~/.local/share/tts"),
    os.path.expanduser("~/tts"),
    "/tmp/tts",
]

model_dir = None
for path in cache_paths:
    if os.path.exists(path):
        print(f"   ✓ Cache encontrado: {path}")
        # Verificar se há modelos XTTS
        for item in os.listdir(path):
            if "xtts" in item.lower():
                full_path = os.path.join(path, item)
                size = sum(os.path.getsize(os.path.join(full_path, f)) for f in os.listdir(full_path) if os.path.isfile(os.path.join(full_path, f))) if os.path.isdir(full_path) else 0
                print(f"      → {item}: {size / (1024**2):.2f} MB")
                model_dir = full_path

if model_dir is None:
    print("   ℹ️  Nenhum cache de modelo XTTS encontrado")
    print("   ℹ️  O modelo será baixado na primeira execução (~2GB)")

# 4. Verificar conexão de internet (para download do modelo)
print("\n🌐 4. Verificando conexão de internet...")
try:
    import urllib.request
    start = time.time()
    urllib.request.urlopen("https://coqui.gateway.scarf.sh/", timeout=10)
    latency = (time.time() - start) * 1000
    print(f"   ✓ Conexão OK (latência: {latency:.0f}ms)")
except Exception as e:
    print(f"   ❌ Erro de conexão: {e}")
    print("   ⚠️  Sem conexão, não será possível baixar o modelo!")

# 5. Tentar carregar o TTS
print("\n🔧 5. Tentando carregar módulo TTS...")
try:
    start = time.time()
    from TTS.api import TTS
    load_time = time.time() - start
    print(f"   ✓ Módulo TTS importado ({load_time:.2f}s)")
except Exception as e:
    print(f"   ❌ Erro importando TTS: {e}")
    sys.exit(1)

# 6. Listar modelos disponíveis
print("\n📋 6. Modelos disponíveis...")
try:
    tts = TTS()
    models = [m for m in tts.models if "xtts" in m.lower()][:5]
    for m in models:
        print(f"   → {m}")
except Exception as e:
    print(f"   ❌ Erro listando modelos: {e}")

# 7. Tentar baixar/carregar o modelo XTTS (com timeout)
print("\n⏳ 7. Testando carregamento do modelo XTTS v2...")
print("   (Isso pode demorar alguns minutos na primeira execução)")
print("   Pressione Ctrl+C para cancelar se demorar muito")
print()

def progress_callback(step, total, message=""):
    pct = (step / max(total, 1)) * 100
    bar_len = 30
    filled = int(bar_len * step / max(total, 1))
    bar = "█" * filled + "░" * (bar_len - filled)
    print(f"\r   [{bar}] {pct:.1f}% {message}", end="", flush=True)

try:
    import signal
    
    class TimeoutError(Exception):
        pass
    
    def timeout_handler(signum, frame):
        raise TimeoutError("Timeout no carregamento!")
    
    # Configurar timeout de 5 minutos
    if hasattr(signal, 'SIGALRM'):
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(300)  # 5 minutos
    
    start = time.time()
    print("   Iniciando carregamento...")
    
    # Carregar modelo com progresso
    device = "cuda" if torch.cuda.is_available() else "cpu"
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
    tts.to(device)
    
    if hasattr(signal, 'SIGALRM'):
        signal.alarm(0)  # Cancelar timeout
    
    elapsed = time.time() - start
    print(f"\n   ✅ Modelo carregado com sucesso! ({elapsed:.1f}s)")
    
except KeyboardInterrupt:
    print("\n   ⚠️  Carregamento cancelado pelo usuário")
except TimeoutError as e:
    print(f"\n   ❌ {e}")
    print("   ⚠️  O carregamento está demorando muito!")
    print("   Possíveis causas:")
    print("      1. Conexão de internet lenta")
    print("      2. Servidor de download congestionado")
    print("      3. Pouca memória RAM")
except Exception as e:
    print(f"\n   ❌ Erro carregando modelo: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("✅ Diagnóstico concluído!")
print("=" * 60)
