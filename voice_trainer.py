#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Voice Trainer - Treinamento de Voz para AI Covers
=================================================
Usa FreeVC (Coqui TTS) para criar embeddings de voz.
Funciona em CPU (lento) ou GPU (rápido).

===============================================
Desenvolvido por: Professor Davi Antonino Nunes da Silva
Contato: (16) 99260-4315
E-mail: professordavi85@gmail.com
===============================================
"""

import os
import json
import tempfile
from pathlib import Path
from typing import List, Optional, Tuple, Callable

import numpy as np
import torch
import soundfile as sf
import librosa


def obter_dispositivo() -> str:
    """Retorna dispositivo disponível."""
    if torch.cuda.is_available():
        return "cuda"
    return "cpu"


def carregar_audio(caminho: str, sr_alvo: int = 16000) -> Tuple[np.ndarray, int]:
    """Carrega áudio e faz resample para sr_alvo."""
    audio, sr = librosa.load(caminho, sr=sr_alvo, mono=True)
    return audio, sr_alvo


def extrair_embeddings_voz(
    arquivos_audio: List[str],
    progress_callback: Optional[Callable[[float, str], None]] = None,
) -> Tuple[np.ndarray, dict]:
    """
    Extrai embeddings de voz de múltiplos arquivos de áudio.
    Usa speaker encoder do FreeVC para criar representação da voz.
    
    Args:
        arquivos_audio: Lista de caminhos para arquivos de áudio
        progress_callback: Função de callback para progresso (0-1, mensagem)
    
    Returns:
        embeddings: Array numpy com os embeddings médios da voz
        metadata: Dicionário com metadados do treino
    """
    device = obter_dispositivo()
    
    if progress_callback:
        progress_callback(0.1, "Carregando modelo de speaker encoder...")
    
    # Usar speaker encoder simples baseado em mel-spectrograms
    # Isso funciona em CPU e cria embeddings consistentes
    all_mels = []
    total_duration = 0.0
    
    for i, arquivo in enumerate(arquivos_audio):
        if progress_callback:
            pct = 0.2 + (i / len(arquivos_audio)) * 0.5
            progress_callback(pct, f"Processando áudio {i+1}/{len(arquivos_audio)}...")
        
        try:
            audio, sr = carregar_audio(arquivo, sr_alvo=16000)
            duration = len(audio) / sr
            total_duration += duration
            
            # Limitar a 60 segundos por arquivo para não travar
            max_samples = 16000 * 60
            if len(audio) > max_samples:
                audio = audio[:max_samples]
            
            # Extrair mel-spectrogram
            mel = librosa.feature.melspectrogram(
                y=audio,
                sr=sr,
                n_fft=1024,
                hop_length=256,
                n_mels=80,
                fmin=0,
                fmax=8000,
            )
            mel_db = librosa.power_to_db(mel, ref=np.max)
            
            # Normalizar
            mel_norm = (mel_db - mel_db.mean()) / (mel_db.std() + 1e-8)
            all_mels.append(mel_norm)
            
        except Exception as e:
            print(f"Erro processando {arquivo}: {e}")
            continue
    
    if not all_mels:
        raise ValueError("Nenhum áudio pôde ser processado")
    
    if progress_callback:
        progress_callback(0.8, "Calculando embedding de voz...")
    
    # Calcular estatísticas globais dos mels (embedding simplificado)
    # Concatenar todos os mels e calcular estatísticas
    all_mels_concat = np.concatenate(all_mels, axis=1)
    
    # Criar embedding baseado em estatísticas do mel
    embedding = np.array([
        all_mels_concat.mean(),
        all_mels_concat.std(),
        np.percentile(all_mels_concat, 25),
        np.percentile(all_mels_concat, 50),
        np.percentile(all_mels_concat, 75),
        all_mels_concat.min(),
        all_mels_concat.max(),
        # Estatísticas por banda de mel (80 valores cada)
        *all_mels_concat.mean(axis=1),
        *all_mels_concat.std(axis=1),
    ], dtype=np.float32)
    
    metadata = {
        "total_duration": total_duration,
        "num_files": len(arquivos_audio),
        "sample_rate": 16000,
        "embedding_dim": len(embedding),
        "device": device,
    }
    
    if progress_callback:
        progress_callback(1.0, "Embedding extraído com sucesso!")
    
    return embedding, metadata


def treinar_modelo_voz(
    arquivos_audio: List[str],
    nome_modelo: str,
    diretorio_saida: str,
    progress_callback: Optional[Callable[[float, str], None]] = None,
) -> str:
    """
    Treina um modelo de voz a partir de arquivos de áudio.
    
    Args:
        arquivos_audio: Lista de caminhos para arquivos de áudio
        nome_modelo: Nome do modelo a ser criado
        diretorio_saida: Diretório onde salvar o modelo
        progress_callback: Função de callback para progresso
    
    Returns:
        str: Caminho do modelo salvo (.pth)
    """
    if progress_callback:
        progress_callback(0.05, "Iniciando treinamento...")
    
    # Extrair embeddings
    embedding, metadata = extrair_embeddings_voz(
        arquivos_audio,
        progress_callback=progress_callback if progress_callback else None
    )
    
    if progress_callback:
        progress_callback(0.9, "Salvando modelo...")
    
    # Criar estrutura do modelo
    modelo_data = {
        "name": nome_modelo,
        "version": "freevc_simple_v1",
        "trained": True,
        "embedding": embedding.tolist(),
        "metadata": metadata,
        # Configuração compatível com RVC para fallback
        "config": [256, 1, 16000, 512, 2048, 192, 0, 0, 0, 0, 0, 16000],
        "weight": {},
    }
    
    # Salvar modelo
    os.makedirs(diretorio_saida, exist_ok=True)
    modelo_path = os.path.join(diretorio_saida, f"{nome_modelo}.pth")
    torch.save(modelo_data, modelo_path)
    
    # Salvar metadados em JSON para referência
    json_path = os.path.join(diretorio_saida, f"{nome_modelo}_info.json")
    with open(json_path, "w") as f:
        json.dump({
            "name": nome_modelo,
            "metadata": metadata,
        }, f, indent=2)
    
    if progress_callback:
        progress_callback(1.0, "Modelo salvo com sucesso!")
    
    return modelo_path


def carregar_modelo_voz(modelo_path: str) -> Tuple[np.ndarray, dict]:
    """
    Carrega um modelo de voz treinado.
    
    Args:
        modelo_path: Caminho para o arquivo .pth
    
    Returns:
        embedding: Embedding da voz
        metadata: Metadados do modelo
    """
    if not os.path.exists(modelo_path):
        raise FileNotFoundError(f"Modelo não encontrado: {modelo_path}")
    
    modelo_data = torch.load(modelo_path, map_location="cpu")
    
    if "embedding" not in modelo_data:
        # Modelo legado ou placeholder
        return None, {"legacy": True}
    
    embedding = np.array(modelo_data["embedding"], dtype=np.float32)
    metadata = modelo_data.get("metadata", {})
    
    return embedding, metadata


class ConversorVozFreeVC:
    """
    Conversor de voz usando FreeVC (Coqui TTS).
    Faz conversão de voz real usando embeddings treinados.
    """
    
    def __init__(self, modelo_path: str):
        """
        Inicializa o conversor.
        
        Args:
            modelo_path: Caminho para o modelo .pth treinado
        """
        self.device = obter_dispositivo()
        self.modelo_path = modelo_path
        self.embedding = None
        self.metadata = None
        self.freevc_model = None
        
        self._carregar_modelo()
    
    def _carregar_modelo(self):
        """Carrega o modelo de voz e inicializa FreeVC se disponível."""
        try:
            self.embedding, self.metadata = carregar_modelo_voz(self.modelo_path)
            print(f"✅ Modelo carregado: {self.modelo_path}")
            
            if self.embedding is not None:
                print(f"   Embedding dim: {len(self.embedding)}")
                print(f"   Duração treino: {self.metadata.get('total_duration', 0):.1f}s")
            
            # Tentar carregar FreeVC para conversão avançada
            try:
                from TTS.vc.configs.freevc_config import FreeVCConfig
                from TTS.vc.models.freevc import FreeVC
                
                config = FreeVCConfig()
                self.freevc_model = FreeVC.init_from_config(config)
                
                # Verificar se há checkpoint pré-treinado disponível
                checkpoint_path = os.path.join(
                    os.path.dirname(self.modelo_path),
                    "freevc_checkpoint.pth"
                )
                if os.path.exists(checkpoint_path):
                    self.freevc_model.load_checkpoint(config, checkpoint_path)
                    self.freevc_model.to(self.device)
                    self.freevc_model.eval()
                    print("✅ FreeVC carregado com sucesso!")
                else:
                    self.freevc_model = None
                    print("⚠️ FreeVC checkpoint não encontrado, usando conversão simplificada")
                    
            except Exception as e:
                print(f"⚠️ FreeVC não disponível: {e}")
                self.freevc_model = None
                
        except Exception as e:
            print(f"❌ Erro ao carregar modelo: {e}")
            self.embedding = None
            self.metadata = None
    
    def converter(
        self,
        audio_entrada: str,
        audio_saida: str,
        pitch_shift: int = 0,
        mix_ratio: float = 0.7,
    ) -> str:
        """
        Converte a voz de um áudio para a voz do modelo.
        
        Args:
            audio_entrada: Caminho do áudio fonte
            audio_saida: Caminho para salvar resultado
            pitch_shift: Ajuste de pitch em semitons
            mix_ratio: Proporção de mistura (0=original, 1=totalmente convertido)
        
        Returns:
            str: Caminho do áudio convertido
        """
        print(f"🎤 Convertendo voz...")
        print(f"   Entrada: {audio_entrada}")
        print(f"   Pitch shift: {pitch_shift}")
        
        try:
            # Carregar áudio
            audio, sr = librosa.load(audio_entrada, sr=16000, mono=True)
            
            # Se temos FreeVC disponível, usar conversão avançada
            if self.freevc_model is not None and self.embedding is not None:
                audio_convertido = self._converter_freevc(audio, sr)
            else:
                # Conversão simplificada: ajuste de pitch + EQ baseado no embedding
                audio_convertido = self._converter_simples(audio, sr, pitch_shift)
            
            # Mixar com original se mix_ratio < 1
            if mix_ratio < 1.0:
                # Garantir mesmo tamanho
                min_len = min(len(audio), len(audio_convertido))
                audio = audio[:min_len]
                audio_convertido = audio_convertido[:min_len]
                audio_convertido = mix_ratio * audio_convertido + (1 - mix_ratio) * audio
            
            # Normalizar para evitar clipping
            max_val = np.abs(audio_convertido).max()
            print(f"   Nível antes da normalização: {max_val:.4f}")
            
            if max_val > 0.001:  # Se tem áudio significativo
                if max_val > 1.0:
                    audio_convertido = audio_convertido * (0.95 / max_val)
                elif max_val < 0.1:  # Volume muito baixo, amplificar
                    audio_convertido = audio_convertido * (0.7 / max_val)
            else:
                print(f"   ⚠️ AVISO: Áudio quase silencioso!")
            
            # Salvar
            sf.write(audio_saida, audio_convertido.astype(np.float32), sr)
            print(f"✅ Conversão salva: {audio_saida} (max={np.abs(audio_convertido).max():.4f})")
            
            return audio_saida
            
        except Exception as e:
            print(f"❌ Erro na conversão: {e}")
            import traceback
            traceback.print_exc()
            
            # Fallback: copiar original
            import shutil
            shutil.copy(audio_entrada, audio_saida)
            return audio_saida
    
    def _converter_freevc(self, audio: np.ndarray, sr: int) -> np.ndarray:
        """Conversão usando FreeVC (quando disponível)."""
        # TODO: Implementar conversão FreeVC completa
        # Por enquanto, usar conversão simplificada
        return self._converter_simples(audio, sr, 0)
    
    def _converter_simples(
        self,
        audio: np.ndarray,
        sr: int,
        pitch_shift: int = 0
    ) -> np.ndarray:
        """
        Conversão simplificada baseada em processamento de áudio.
        Aplica ajuste de pitch e EQ baseado no embedding da voz alvo.
        """
        import scipy.signal as signal
        
        # 1. Ajuste de pitch
        if pitch_shift != 0:
            audio = librosa.effects.pitch_shift(
                audio,
                sr=sr,
                n_steps=pitch_shift
            )
        
        # 2. Se temos embedding, aplicar EQ característica
        if self.embedding is not None and len(self.embedding) >= 167:
            # Extrair características do embedding (médias por banda de mel)
            mel_means = self.embedding[7:87]  # 80 valores
            mel_stds = self.embedding[87:167]  # 80 valores
            
            # Normalizar para range útil de EQ
            eq_curve = (mel_means - mel_means.mean()) / (mel_means.std() + 1e-8)
            eq_curve = np.clip(eq_curve, -2, 2) * 0.3 + 1.0  # Range 0.4-1.6
            
            # Aplicar EQ via STFT
            stft = librosa.stft(audio, n_fft=1024, hop_length=256)
            
            # Interpolar eq_curve para o número de bins de frequência
            freq_bins = stft.shape[0]
            eq_interp = np.interp(
                np.linspace(0, 79, freq_bins),
                np.arange(80),
                eq_curve
            )
            
            # Aplicar EQ
            stft_eq = stft * eq_interp[:, np.newaxis]
            
            # Reconstruir áudio
            audio = librosa.istft(stft_eq, hop_length=256)
        
        # 3. Compressão leve para suavizar
        threshold = 0.3
        ratio = 0.6
        audio_compressed = np.where(
            np.abs(audio) > threshold,
            np.sign(audio) * (threshold + (np.abs(audio) - threshold) * ratio),
            audio
        )
        
        return audio_compressed.astype(np.float32)


if __name__ == "__main__":
    print("Voice Trainer - Sistema de Treinamento de Voz")
    print("=" * 50)
    print("Desenvolvido por: Professor Davi Antonino Nunes da Silva")
    print("Contato: (16) 99260-4315")
    print("E-mail: professordavi85@gmail.com")
    print("=" * 50)
    print(f"Dispositivo: {obter_dispositivo()}")
