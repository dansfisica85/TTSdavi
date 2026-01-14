#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Mixer de Áudio - Combina vocais convertidos com instrumental
=============================================================
"""

import os
from pathlib import Path
from typing import Optional

import numpy as np
import torch
import torchaudio
import torchaudio.transforms as T


def carregar_audio(caminho: str, sample_rate: int = 44100) -> torch.Tensor:
    """Carrega e resampla áudio para sample rate específico."""
    waveform, sr = torchaudio.load(caminho)
    
    if sr != sample_rate:
        resampler = T.Resample(sr, sample_rate)
        waveform = resampler(waveform)
    
    return waveform


def normalizar_audio(audio: torch.Tensor, target_db: float = -3.0) -> torch.Tensor:
    """Normaliza áudio para um nível de dB específico."""
    rms = torch.sqrt(torch.mean(audio ** 2))
    if rms > 0:
        target_rms = 10 ** (target_db / 20)
        audio = audio * (target_rms / rms)
    return audio


def ajustar_duracao(audio: torch.Tensor, duracao_alvo: int) -> torch.Tensor:
    """Ajusta a duração do áudio (corta ou preenche com zeros)."""
    if audio.shape[-1] > duracao_alvo:
        return audio[..., :duracao_alvo]
    elif audio.shape[-1] < duracao_alvo:
        padding = duracao_alvo - audio.shape[-1]
        return torch.nn.functional.pad(audio, (0, padding))
    return audio


def mixar_audio(
    vocal_path: str,
    instrumental_path: str,
    output_path: str,
    volume_vocal: float = 1.0,
    volume_instrumental: float = 1.0,
    sample_rate: int = 44100
) -> str:
    """
    Combina vocal e instrumental em um único arquivo.
    
    Args:
        vocal_path: Caminho para o arquivo de vocal
        instrumental_path: Caminho para o arquivo instrumental
        output_path: Caminho para salvar o mix final
        volume_vocal: Multiplicador de volume para o vocal (0.0 - 2.0)
        volume_instrumental: Multiplicador de volume para o instrumental
        sample_rate: Sample rate de saída
    
    Returns:
        str: Caminho do arquivo mixado
    """
    print(f"🎛️ Mixando áudios...")
    print(f"   Vocal: {vocal_path}")
    print(f"   Instrumental: {instrumental_path}")
    
    # Carregar áudios
    vocal = carregar_audio(vocal_path, sample_rate)
    instrumental = carregar_audio(instrumental_path, sample_rate)
    
    # Garantir que ambos são stereo ou mono
    if vocal.shape[0] == 1 and instrumental.shape[0] == 2:
        vocal = vocal.repeat(2, 1)
    elif vocal.shape[0] == 2 and instrumental.shape[0] == 1:
        instrumental = instrumental.repeat(2, 1)
    
    # Ajustar durações
    max_len = max(vocal.shape[-1], instrumental.shape[-1])
    vocal = ajustar_duracao(vocal, max_len)
    instrumental = ajustar_duracao(instrumental, max_len)
    
    # Aplicar volumes
    vocal = vocal * volume_vocal
    instrumental = instrumental * volume_instrumental
    
    # Mixar
    mix = vocal + instrumental
    
    # Normalizar para evitar clipping
    max_val = torch.max(torch.abs(mix))
    if max_val > 1.0:
        mix = mix / max_val * 0.95
    
    # Criar diretório de saída se necessário
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    
    # Salvar
    torchaudio.save(output_path, mix, sample_rate)
    
    print(f"✅ Mix salvo: {output_path}")
    return output_path


def exportar_mp3(wav_path: str, mp3_path: Optional[str] = None, bitrate: str = "320k") -> str:
    """
    Converte WAV para MP3 usando FFmpeg.
    
    Args:
        wav_path: Caminho para o arquivo WAV
        mp3_path: Caminho para salvar o MP3 (se None, usa mesmo nome)
        bitrate: Bitrate do MP3
    
    Returns:
        str: Caminho do arquivo MP3
    """
    import subprocess
    
    if mp3_path is None:
        mp3_path = str(Path(wav_path).with_suffix(".mp3"))
    
    cmd = [
        "ffmpeg", "-y",
        "-i", wav_path,
        "-b:a", bitrate,
        "-q:a", "0",
        mp3_path
    ]
    
    print(f"🎵 Exportando MP3: {mp3_path}")
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Aviso: FFmpeg pode não estar instalado. Salvando apenas WAV.")
        return wav_path
    
    print(f"✅ MP3 exportado: {mp3_path}")
    return mp3_path


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 4:
        print("Uso: python audio_mixer.py <vocal.wav> <instrumental.wav> <output.wav>")
        sys.exit(1)
    
    mixar_audio(sys.argv[1], sys.argv[2], sys.argv[3])
