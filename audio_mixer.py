#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Mixer de Áudio - Combina vocais convertidos com instrumental
=============================================================

Desenvolvido por: Professor Davi Antonino Nunes da Silva
Contato: (16) 99260-4315
E-mail: professordavi85@gmail.com
"""

import os
from pathlib import Path
from typing import Optional

import numpy as np
import soundfile as sf
from scipy import signal


def carregar_audio(caminho: str, sample_rate: int = 44100) -> np.ndarray:
    """Carrega e resampla áudio para sample rate específico."""
    waveform, sr = sf.read(caminho, dtype='float32')
    
    # Converter para (samples, channels) se necessário
    if waveform.ndim == 1:
        waveform = waveform[:, np.newaxis]  # Adicionar dimensão de canal
    
    # Resample se necessário
    if sr != sample_rate:
        num_samples = int(len(waveform) * sample_rate / sr)
        waveform_resampled = np.zeros((num_samples, waveform.shape[1]), dtype=np.float32)
        for ch in range(waveform.shape[1]):
            waveform_resampled[:, ch] = signal.resample(waveform[:, ch], num_samples)
        waveform = waveform_resampled
    
    return waveform


def normalizar_audio(audio: np.ndarray, target_db: float = -3.0) -> np.ndarray:
    """Normaliza áudio para um nível de dB específico."""
    rms = np.sqrt(np.mean(audio ** 2))
    if rms > 0:
        target_rms = 10 ** (target_db / 20)
        audio = audio * (target_rms / rms)
    return audio


def ajustar_duracao(audio: np.ndarray, duracao_alvo: int) -> np.ndarray:
    """Ajusta a duração do áudio (corta ou preenche com zeros)."""
    if audio.shape[0] > duracao_alvo:
        return audio[:duracao_alvo]
    elif audio.shape[0] < duracao_alvo:
        padding = duracao_alvo - audio.shape[0]
        if audio.ndim == 1:
            return np.pad(audio, (0, padding), mode='constant')
        else:
            return np.pad(audio, ((0, padding), (0, 0)), mode='constant')
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
    
    # Garantir que ambos têm o mesmo número de canais
    if vocal.shape[1] == 1 and instrumental.shape[1] == 2:
        vocal = np.repeat(vocal, 2, axis=1)
    elif vocal.shape[1] == 2 and instrumental.shape[1] == 1:
        instrumental = np.repeat(instrumental, 2, axis=1)
    
    # Ajustar durações
    max_len = max(vocal.shape[0], instrumental.shape[0])
    vocal = ajustar_duracao(vocal, max_len)
    instrumental = ajustar_duracao(instrumental, max_len)
    
    # Aplicar volumes
    vocal = vocal * volume_vocal
    instrumental = instrumental * volume_instrumental
    
    # Mixar
    mix = vocal + instrumental
    
    # Normalizar para evitar clipping e garantir volume audível
    max_val = np.max(np.abs(mix))
    print(f"   Nível máximo antes da normalização: {max_val:.4f}")
    
    if max_val > 0.001:  # Se tem áudio significativo
        if max_val > 1.0:
            mix = mix / max_val * 0.95
        elif max_val < 0.1:  # Volume muito baixo, normalizar
            print(f"   ⚠️ Volume baixo detectado, normalizando...")
            mix = mix / max_val * 0.7
    else:
        print(f"   ⚠️ AVISO: Mix praticamente silencioso!")
    
    # Criar diretório de saída se necessário
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    
    # Salvar
    sf.write(output_path, mix, sample_rate)
    
    # Verificar arquivo salvo
    file_size = os.path.getsize(output_path) if os.path.exists(output_path) else 0
    print(f"✅ Mix salvo: {output_path} ({file_size/1024:.1f} KB)")
    
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
    
    print("Mixer de Áudio")
    print("=" * 40)
    print("Desenvolvido por: Professor Davi Antonino Nunes da Silva")
    print("Contato: (16) 99260-4315")
    print("E-mail: professordavi85@gmail.com")
    print()
    
    if len(sys.argv) < 4:
        print("Uso: python audio_mixer.py <vocal.wav> <instrumental.wav> <output.wav>")
        sys.exit(1)
    
    mixar_audio(sys.argv[1], sys.argv[2], sys.argv[3])
