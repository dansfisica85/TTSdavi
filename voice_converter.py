#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Conversor de Voz RVC - Voice Conversion para AI Covers
=======================================================
Converte vocais usando modelos RVC treinados.
"""

import os
import sys
from pathlib import Path
from typing import Optional, Tuple

import numpy as np
import torch
import torchaudio

# Adicionar diretório RVC ao path
RVC_DIR = os.path.join(os.path.dirname(__file__), "rvc")
if RVC_DIR not in sys.path:
    sys.path.insert(0, RVC_DIR)


def obter_dispositivo() -> str:
    """Retorna dispositivo disponível."""
    if torch.cuda.is_available():
        return "cuda:0"
    return "cpu"


class ConversorVoz:
    """Classe para conversão de voz usando RVC."""
    
    def __init__(self, modelo_path: str, index_path: Optional[str] = None):
        """
        Inicializa o conversor com um modelo RVC.
        
        Args:
            modelo_path: Caminho para o arquivo .pth do modelo
            index_path: Caminho para o arquivo .index (opcional)
        """
        self.device = obter_dispositivo()
        self.modelo_path = modelo_path
        self.index_path = index_path
        self.modelo = None
        self.sample_rate = 40000  # RVC usa 40kHz internamente
        
        print(f"🎤 Inicializando conversor de voz...")
        print(f"   Modelo: {modelo_path}")
        print(f"   Dispositivo: {self.device}")
        
        self._carregar_modelo()
    
    def _carregar_modelo(self):
        """Carrega o modelo RVC."""
        try:
            from infer.lib.infer_pack.models import (
                SynthesizerTrnMs256NSFsid,
                SynthesizerTrnMs256NSFsid_nono,
                SynthesizerTrnMs768NSFsid,
                SynthesizerTrnMs768NSFsid_nono,
            )
            
            cpt = torch.load(self.modelo_path, map_location="cpu")
            
            tgt_sr = cpt["config"][-1]
            cpt["config"][-3] = cpt["weight"]["emb_g.weight"].shape[0]
            
            if_f0 = cpt.get("f0", 1)
            version = cpt.get("version", "v1")
            
            if version == "v1":
                if if_f0 == 1:
                    self.modelo = SynthesizerTrnMs256NSFsid(*cpt["config"], is_half=False)
                else:
                    self.modelo = SynthesizerTrnMs256NSFsid_nono(*cpt["config"])
            elif version == "v2":
                if if_f0 == 1:
                    self.modelo = SynthesizerTrnMs768NSFsid(*cpt["config"], is_half=False)
                else:
                    self.modelo = SynthesizerTrnMs768NSFsid_nono(*cpt["config"])
            
            del self.modelo.enc_q
            self.modelo.load_state_dict(cpt["weight"], strict=False)
            self.modelo.eval().to(self.device)
            
            self.tgt_sr = tgt_sr
            self.if_f0 = if_f0
            self.version = version
            
            print(f"✅ Modelo carregado! (v{version}, f0={if_f0})")
            
        except Exception as e:
            print(f"⚠️ Erro ao carregar modelo RVC: {e}")
            print("   Usando modo simplificado...")
            self.modelo = None
    
    def converter(
        self,
        audio_entrada: str,
        audio_saida: str,
        pitch_shift: int = 0,
        index_rate: float = 0.75,
    ) -> str:
        """
        Converte um áudio para a voz do modelo.
        
        Args:
            audio_entrada: Caminho do áudio de entrada
            audio_saida: Caminho para salvar o áudio convertido
            pitch_shift: Ajuste de pitch em semitons (-12 a +12)
            index_rate: Taxa de mistura do index (0.0 a 1.0)
        
        Returns:
            str: Caminho do áudio convertido
        """
        print(f"🔄 Convertendo voz...")
        print(f"   Entrada: {audio_entrada}")
        print(f"   Pitch shift: {pitch_shift}")
        
        # Carregar áudio
        audio, sr = torchaudio.load(audio_entrada)
        
        if self.modelo is None:
            # Modo fallback: apenas copia o áudio (para testes)
            print("⚠️ Modelo não carregado, salvando áudio original")
            torchaudio.save(audio_saida, audio, sr)
            return audio_saida
        
        # Conversão real usando RVC
        try:
            from infer.modules.vc.modules import VC
            
            vc = VC()
            vc.get_vc(self.modelo_path)
            
            # Realizar conversão
            result = vc.vc_single(
                0,  # speaker id
                audio_entrada,
                pitch_shift,
                None,  # f0 file
                "rmvpe",  # f0 method
                self.index_path or "",
                "",  # index path 2
                index_rate,
                3,  # filter radius
                0,  # resample sr
                0.25,  # rms mix rate
                0.33,  # protect
            )
            
            if result[0] is not None:
                torchaudio.save(audio_saida, torch.tensor(result[0]).unsqueeze(0), result[1])
                print(f"✅ Conversão concluída: {audio_saida}")
            else:
                print(f"❌ Erro na conversão: {result[1]}")
                torchaudio.save(audio_saida, audio, sr)
                
        except Exception as e:
            print(f"❌ Erro na conversão: {e}")
            # Fallback: salvar áudio original
            torchaudio.save(audio_saida, audio, sr)
        
        return audio_saida


def converter_voz_simples(
    audio_entrada: str,
    audio_saida: str,
    modelo_path: str,
    pitch_shift: int = 0,
) -> str:
    """
    Função simplificada para converter voz.
    
    Args:
        audio_entrada: Caminho do áudio de entrada
        audio_saida: Caminho para salvar  
        modelo_path: Caminho do modelo .pth
        pitch_shift: Ajuste de pitch
    
    Returns:
        str: Caminho do áudio convertido
    """
    conversor = ConversorVoz(modelo_path)
    return conversor.converter(audio_entrada, audio_saida, pitch_shift)


def listar_modelos(diretorio: str = "models") -> list:
    """Lista modelos RVC disponíveis em um diretório."""
    modelos = []
    
    if not os.path.exists(diretorio):
        return modelos
    
    for arquivo in os.listdir(diretorio):
        if arquivo.endswith(".pth"):
            modelos.append(os.path.join(diretorio, arquivo))
    
    return modelos


if __name__ == "__main__":
    print("Conversor de Voz RVC")
    print("=" * 40)
    print("\nModelos disponíveis:")
    
    modelos = listar_modelos("models")
    if modelos:
        for m in modelos:
            print(f"  - {m}")
    else:
        print("  Nenhum modelo encontrado em 'models/'")
        print("\n  Para treinar um modelo, use a interface web.")
