#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Separador de Áudio - Módulo de Separação de Vocais e Instrumentais
===================================================================
Usa Demucs (Meta AI) para separar stems de áudio.
Sem dependência de torchaudio ou FFmpeg.

===============================================
Desenvolvido por: Professor Davi Antonino Nunes da Silva
Contato: (16) 99260-4315
E-mail: professordavi85@gmail.com
===============================================
"""

import os
import tempfile
from pathlib import Path
from typing import Tuple, Optional

import torch
import soundfile as sf
import numpy as np
from scipy import signal


def obter_dispositivo() -> str:
    """Retorna o dispositivo disponível."""
    if torch.cuda.is_available():
        return "cuda"
    return "cpu"


def resample_audio(audio: np.ndarray, sr_original: int, sr_alvo: int) -> np.ndarray:
    """Resample usando scipy (sem torchaudio)."""
    if sr_original == sr_alvo:
        return audio
    
    # Calcular número de amostras no novo sample rate
    num_samples = int(len(audio) * sr_alvo / sr_original)
    
    # Usar scipy resample
    if audio.ndim == 1:
        return signal.resample(audio, num_samples)
    else:
        # Para multi-canal, resamplear cada canal
        resampled = np.zeros((audio.shape[0], num_samples), dtype=audio.dtype)
        for i in range(audio.shape[0]):
            resampled[i] = signal.resample(audio[i], num_samples)
        return resampled


def normalizar_caminho_audio(caminho: str) -> str:
    """
    Copia arquivo de áudio para um caminho temporário seguro se necessário.
    Resolve problemas com espaços e caracteres especiais no nome.
    """
    import shutil
    import re
    
    # Verificar se o caminho tem caracteres problemáticos
    nome_arquivo = os.path.basename(caminho)
    tem_problemas = bool(re.search(r'[\s\(\)\[\]\{\}\&\$\#\@\!\%\^]', nome_arquivo))
    
    if tem_problemas:
        # Criar caminho temporário seguro
        ext = Path(caminho).suffix
        temp_dir = tempfile.mkdtemp(prefix="audio_safe_")
        nome_seguro = f"audio_temp{ext}"
        caminho_seguro = os.path.join(temp_dir, nome_seguro)
        shutil.copy2(caminho, caminho_seguro)
        return caminho_seguro
    
    return caminho


def carregar_audio(caminho: str, sr_alvo: int = 44100) -> Tuple[torch.Tensor, int]:
    """
    Carrega arquivo de áudio usando soundfile.
    Suporta WAV, FLAC, OGG.
    """
    # Normalizar caminho para evitar problemas com caracteres especiais
    caminho_seguro = normalizar_caminho_audio(caminho)
    
    # Carregar com soundfile
    audio, sr = sf.read(caminho_seguro, dtype='float32')
    
    # Converter para (channels, samples)
    if audio.ndim == 1:
        audio = audio[np.newaxis, :]
    else:
        audio = audio.T
    
    # Resample se necessário
    if sr != sr_alvo:
        audio = resample_audio(audio, sr, sr_alvo)
        sr = sr_alvo
    
    return torch.from_numpy(audio.astype(np.float32)), sr


def salvar_audio(audio: torch.Tensor, caminho: str, sr: int = 44100):
    """Salva tensor de áudio como WAV."""
    audio_np = audio.cpu().numpy()
    if audio_np.ndim == 2:
        audio_np = audio_np.T  # (channels, samples) -> (samples, channels)
    sf.write(caminho, audio_np, sr)


def separar_audio(
    arquivo_entrada: str,
    diretorio_saida: Optional[str] = None,
    modelo: str = "htdemucs",
    progress_callback=None,
) -> Tuple[str, str]:
    """
    Separa vocais e instrumentais de um arquivo de áudio.
    TOTALMENTE AUTOMÁTICO - sem configurações.
    
    progress_callback: função(percentage, message) para atualizar progresso
    """
    from demucs.pretrained import get_model
    from demucs.apply import apply_model
    import gc
    
    if not os.path.exists(arquivo_entrada):
        raise FileNotFoundError(f"Arquivo não encontrado: {arquivo_entrada}")
    
    # Verificar extensão
    ext = Path(arquivo_entrada).suffix.lower()
    if ext not in ['.wav', '.flac', '.ogg']:
        raise ValueError(f"Use arquivo WAV, FLAC ou OGG. Arquivo atual: {ext}")
    
    # Diretório de saída
    if diretorio_saida is None:
        diretorio_saida = tempfile.mkdtemp(prefix="demucs_")
    os.makedirs(diretorio_saida, exist_ok=True)
    
    device = obter_dispositivo()
    print(f"🎵 Separando áudio ({device})...")
    
    # Limpar memória antes de começar
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    
    if progress_callback:
        progress_callback(0.10, "Carregando modelo de separação...")
    
    # Carregar modelo - usando modelo mais leve se não tiver GPU
    # htdemucs_ft é mais preciso mas mais pesado
    # htdemucs é o padrão
    modelo_usado = modelo
    print(f"📦 Carregando modelo: {modelo_usado}")
    
    model = get_model(modelo_usado)
    model.to(device)
    model.eval()
    
    if progress_callback:
        progress_callback(0.20, "Carregando arquivo de áudio...")
    
    # Carregar áudio
    wav, _ = carregar_audio(arquivo_entrada, model.samplerate)
    
    # Verificar duração do áudio
    duracao_segundos = wav.shape[1] / model.samplerate
    print(f"⏱️ Duração do áudio: {duracao_segundos:.1f} segundos")
    
    # Se o áudio for muito longo e não tiver GPU, processar em chunks
    MAX_DURACAO_CPU = 180  # 3 minutos max para CPU
    if device == "cpu" and duracao_segundos > MAX_DURACAO_CPU:
        print(f"⚠️ Áudio muito longo para CPU ({duracao_segundos:.0f}s). Limitando a {MAX_DURACAO_CPU}s")
        max_samples = int(MAX_DURACAO_CPU * model.samplerate)
        wav = wav[:, :max_samples]
        duracao_segundos = MAX_DURACAO_CPU
    
    # Garantir stereo
    if wav.shape[0] == 1:
        wav = wav.repeat(2, 1)
    elif wav.shape[0] > 2:
        wav = wav[:2]
    
    # Normalizar
    ref = wav.mean(0)
    wav_norm = (wav - ref.mean()) / (ref.std() + 1e-8)
    wav_norm = wav_norm.to(device).unsqueeze(0)
    
    if progress_callback:
        progress_callback(0.30, f"Processando separação ({duracao_segundos:.0f}s de áudio)...")
    
    print(f"🔄 Iniciando separação Demucs (isso pode levar alguns minutos em CPU)...")
    
    # Separar - com tratamento de erro melhorado e processamento em partes
    try:
        with torch.no_grad():
            # Limpar memória antes do processamento pesado
            gc.collect()
            
            # Aplicar modelo Demucs - DESABILITAR progress interno para evitar travamento
            # O progress interno do demucs pode causar problemas em alguns ambientes
            sources = apply_model(
                model, 
                wav_norm, 
                device=device, 
                progress=False,  # DESABILITADO para evitar travamento
                num_workers=0,   # Evitar multiprocessing que pode travar
            )
    except RuntimeError as e:
        if "out of memory" in str(e).lower():
            print("⚠️ Memória insuficiente. Tentando com redução de qualidade...")
            if progress_callback:
                progress_callback(0.35, "Retentando com memória reduzida...")
            
            # Limpar memória
            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            
            # Tentar novamente com áudio mais curto (metade)
            wav_norm_reduced = wav_norm[:, :, :wav_norm.shape[-1]//2]
            with torch.no_grad():
                sources = apply_model(
                    model, 
                    wav_norm_reduced, 
                    device=device, 
                    progress=False,
                    num_workers=0,
                )
        else:
            raise
    
    if progress_callback:
        progress_callback(0.70, "Finalizando separação...")
    
    sources = sources * (ref.std() + 1e-8) + ref.mean()
    sources = sources.squeeze(0).cpu()
    
    # Guardar informações do modelo antes de liberar memória
    source_names = model.sources
    samplerate = model.samplerate
    
    # Liberar memória do modelo DEPOIS de pegar as informações necessárias
    del model
    del wav_norm
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    
    if progress_callback:
        progress_callback(0.80, "Salvando arquivos...")
    
    # Salvar
    nome = Path(arquivo_entrada).stem
    vocal_path = os.path.join(diretorio_saida, f"{nome}_vocals.wav")
    instrumental_path = os.path.join(diretorio_saida, f"{nome}_instrumental.wav")
    
    vocal_idx = source_names.index("vocals")
    salvar_audio(sources[vocal_idx], vocal_path, samplerate)
    
    # Combinar instrumentais
    instrumental = None
    for i, name in enumerate(source_names):
        if name != "vocals":
            if instrumental is None:
                instrumental = sources[i].clone()
            else:
                instrumental = instrumental + sources[i]
    salvar_audio(instrumental, instrumental_path, samplerate)
    
    if progress_callback:
        progress_callback(0.95, "Finalizando...")
    
    print(f"✅ Separação concluída!")
    return vocal_path, instrumental_path


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Uso: python audio_separator.py <arquivo.wav>")
        sys.exit(1)
    separar_audio(sys.argv[1])
