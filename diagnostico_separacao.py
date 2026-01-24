#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Diagnóstico de Separação de Áudio - Troubleshooting
====================================================
Script para ajudar a diagnosticar problemas na separação de áudio.
"""

import os
import sys
import torch
import soundfile as sf
import numpy as np
from pathlib import Path

def verificar_ambiente():
    """Verifica ambiente e dependências."""
    print("=" * 60)
    print("🔍 DIAGNÓSTICO DO AMBIENTE")
    print("=" * 60)
    
    # Python
    print(f"✓ Python: {sys.version.split()[0]}")
    
    # PyTorch
    print(f"✓ PyTorch: {torch.__version__}")
    print(f"✓ CUDA disponível: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"  - GPU: {torch.cuda.get_device_name(0)}")
        print(f"  - Memória GPU: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
    
    # Importações críticas
    try:
        import demucs
        print(f"✓ Demucs: instalado")
    except ImportError:
        print(f"✗ Demucs: NÃO INSTALADO (instale com: pip install demucs)")
        return False
    
    try:
        import soundfile
        print(f"✓ Soundfile: instalado")
    except ImportError:
        print(f"✗ Soundfile: NÃO INSTALADO")
        return False
    
    try:
        import scipy
        print(f"✓ Scipy: instalado")
    except ImportError:
        print(f"✗ Scipy: NÃO INSTALADO")
        return False
    
    return True

def verificar_memoria():
    """Verifica uso de memória."""
    print("\n" + "=" * 60)
    print("💾 MEMÓRIA DISPONÍVEL")
    print("=" * 60)
    
    try:
        import psutil
        mem = psutil.virtual_memory()
        print(f"RAM total: {mem.total / 1e9:.1f} GB")
        print(f"RAM disponível: {mem.available / 1e9:.1f} GB")
        print(f"RAM em uso: {mem.percent}%")
        
        if torch.cuda.is_available():
            cuda_mem = torch.cuda.get_device_properties(0).total_memory
            print(f"VRAM GPU: {cuda_mem / 1e9:.1f} GB")
    except ImportError:
        print("psutil não instalado - não é possível verificar memória")

def testar_carregamento_modelo():
    """Testa carregamento do modelo Demucs."""
    print("\n" + "=" * 60)
    print("🤖 TESTE DE CARREGAMENTO DO MODELO")
    print("=" * 60)
    
    try:
        from demucs.pretrained import get_model
        
        print("Carregando modelo 'htdemucs' (pode demorar)...")
        model = get_model("htdemucs")
        device = "cuda" if torch.cuda.is_available() else "cpu"
        model.to(device)
        print(f"✓ Modelo carregado com sucesso em {device}")
        print(f"  - Fontes: {model.sources}")
        print(f"  - Sample rate: {model.samplerate}")
        
        return True
    except Exception as e:
        print(f"✗ Erro ao carregar modelo: {e}")
        print("\nDica: Tente executar novamente. O download do modelo pode estar")
        print("      sendo feito na primeira execução (pode levar minutos).")
        return False

def testar_audio_simples():
    """Testa processamento com áudio de teste simples."""
    print("\n" + "=" * 60)
    print("🎵 TESTE COM ÁUDIO SIMPLES")
    print("=" * 60)
    
    try:
        import tempfile
        from demucs.pretrained import get_model
        from demucs.apply import apply_model
        
        # Criar áudio teste (1 segundo de tom)
        sr = 44100
        duration = 1  # 1 segundo apenas
        t = np.arange(sr * duration) / sr
        # Tom simples em 440 Hz
        audio_test = 0.3 * np.sin(2 * np.pi * 440 * t)
        audio_stereo = np.stack([audio_test, audio_test])
        
        # Salvar arquivo teste
        test_file = tempfile.mktemp(suffix=".wav")
        sf.write(test_file, audio_stereo.T, sr)
        print(f"Arquivo de teste criado: {test_file}")
        
        # Carregar modelo
        print("Carregando modelo...")
        model = get_model("htdemucs")
        device = "cuda" if torch.cuda.is_available() else "cpu"
        model.to(device)
        
        # Processar
        print("Processando áudio de teste...")
        audio_tensor = torch.from_numpy(audio_stereo).unsqueeze(0).to(device)
        
        with torch.no_grad():
            sources = apply_model(model, audio_tensor, device=device)
        
        print(f"✓ Processamento bem-sucedido!")
        print(f"  - Shape da saída: {sources.shape}")
        
        # Limpar
        os.remove(test_file)
        
        return True
    except Exception as e:
        print(f"✗ Erro no teste: {e}")
        import traceback
        traceback.print_exc()
        return False

def verificar_cache():
    """Verifica arquivo de modelo em cache."""
    print("\n" + "=" * 60)
    print("📦 CACHE DE MODELOS")
    print("=" * 60)
    
    cache_paths = [
        Path.home() / ".cache" / "torch" / "hub" / "checkpoints",
        Path.home() / ".demucs",
    ]
    
    for cache_path in cache_paths:
        if cache_path.exists():
            files = list(cache_path.glob("*.th")) + list(cache_path.glob("*.pth"))
            if files:
                print(f"✓ Cache encontrado em: {cache_path}")
                for f in files:
                    size_mb = f.stat().st_size / 1e6
                    print(f"  - {f.name} ({size_mb:.1f} MB)")
            else:
                print(f"  {cache_path}: existe mas vazia")
        else:
            print(f"  {cache_path}: não existe ainda")

def main():
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║" + "  DIAGNÓSTICO DE SEPARAÇÃO DE ÁUDIO DEMUCS".center(58) + "║")
    print("║" + " " * 58 + "║")
    print("╚" + "=" * 58 + "╝")
    
    # Executar checks
    checks = [
        ("Verificar Ambiente", verificar_ambiente),
        ("Verificar Memória", verificar_memoria),
        ("Testar Carregamento do Modelo", testar_carregamento_modelo),
        ("Testar Processamento", testar_audio_simples),
        ("Verificar Cache", verificar_cache),
    ]
    
    results = {}
    for name, func in checks:
        try:
            result = func() if func != verificar_memoria else (verificar_memoria(), True)[1]
            results[name] = result
        except Exception as e:
            print(f"✗ Erro no check {name}: {e}")
            results[name] = False
    
    # Resumo
    print("\n" + "=" * 60)
    print("📋 RESUMO")
    print("=" * 60)
    
    all_ok = all(v for v in results.values() if v is not None)
    
    if all_ok or results.get("Verificar Ambiente", False):
        print("✓ Ambiente aparentemente OK")
        print("\n💡 Se ainda assim o progresso travar em 10%:")
        print("  1. Tente usar um áudio MAIS CURTO (< 30 segundos)")
        print("  2. Se usar GPU, verifique memória (nvidia-smi)")
        print("  3. Tente usar CPU: export CUDA_VISIBLE_DEVICES=\"\"")
        print("  4. Reinicie a aplicação e tente novamente")
    else:
        print("✗ Encontrados problemas na configuração")

if __name__ == "__main__":
    main()
