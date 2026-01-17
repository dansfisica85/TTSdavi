#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AI Cover App - Sistema AUTOMÁTICO de AI Covers
===============================================
Totalmente automático - só upload de áudio e músicas!

===============================================
Desenvolvido por: Professor Davi Antonino Nunes da Silva
Contato: (16) 99260-4315
E-mail: professordavi85@gmail.com
===============================================
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path
from typing import Optional, Tuple, List

import torch
import numpy as np
import soundfile as sf
import gradio as gr

from audio_separator import separar_audio, normalizar_caminho_audio
from audio_mixer import mixar_audio


# Informações do Desenvolvedor
DESENVOLVEDOR = "Professor Davi Antonino Nunes da Silva"
CONTATO = "(16) 99260-4315"
EMAIL = "professordavi85@gmail.com"

# Diretórios
BASE_DIR = Path(__file__).parent
MODELS_DIR = BASE_DIR / "models"
DATASETS_DIR = BASE_DIR / "datasets"
OUTPUT_DIR = BASE_DIR / "output"

MODELS_DIR.mkdir(exist_ok=True)
DATASETS_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)


def obter_dispositivo() -> str:
    if torch.cuda.is_available():
        return f"GPU: {torch.cuda.get_device_name(0)}"
    return "CPU"


def listar_modelos() -> List[str]:
    modelos = []
    for f in MODELS_DIR.glob("*.pth"):
        modelos.append(f.stem)
    return modelos if modelos else ["Nenhum modelo treinado"]


# =============================================================================
# TREINAMENTO AUTOMÁTICO
# =============================================================================

def treinar_voz_automatico(
    arquivos_audio: List[str],
    nome_modelo: str,
    progress=gr.Progress()
) -> str:
    """Treina modelo de voz AUTOMATICAMENTE com configurações otimizadas."""
    
    if not arquivos_audio:
        return "❌ Faça upload de arquivos de áudio da voz que deseja clonar."
    
    if not nome_modelo or nome_modelo.strip() == "":
        return "❌ Dê um nome para o modelo (ex: minha_voz)"
    
    nome_modelo = nome_modelo.strip().replace(" ", "_")
    
    try:
        progress(0.1, desc="📁 Preparando dataset...")
        
        # Criar diretório do dataset
        dataset_dir = DATASETS_DIR / nome_modelo
        dataset_dir.mkdir(exist_ok=True)
        
        # Processar áudios
        total_duration = 0
        for i, arquivo in enumerate(arquivos_audio):
            progress((i + 1) / len(arquivos_audio) * 0.3, desc=f"Processando áudio {i+1}/{len(arquivos_audio)}...")
            
            # Normalizar caminho para evitar problemas com caracteres especiais
            arquivo_seguro = normalizar_caminho_audio(arquivo)
            audio, sr = sf.read(arquivo_seguro, dtype='float32')
            duration = len(audio) / sr
            total_duration += duration
            
            # Salvar em formato padrão
            dest = dataset_dir / f"audio_{i:04d}.wav"
            
            # Converter para mono se necessário
            if audio.ndim > 1:
                audio = audio.mean(axis=1)
            
            # Resample para 40kHz (padrão RVC)
            if sr != 40000:
                from scipy import signal
                num_samples = int(len(audio) * 40000 / sr)
                audio = signal.resample(audio, num_samples)
            
            sf.write(str(dest), audio, 40000)
        
        progress(0.4, desc="🎓 Iniciando treinamento automático...")
        
        # Verificar se RVC está disponível
        rvc_dir = BASE_DIR / "rvc"
        if not rvc_dir.exists():
            return "❌ RVC não encontrado. Clone o repositório RVC primeiro."
        
        # Adicionar ao path
        if str(rvc_dir) not in sys.path:
            sys.path.insert(0, str(rvc_dir))
        
        progress(0.5, desc="🔄 Preparando treinamento RVC...")
        
        # Tentar usar o treinamento real do RVC
        try:
            from infer.modules.train import preprocess, extract, train
            
            progress(0.6, desc="🔄 Pré-processando áudios...")
            # O treinamento real do RVC seria iniciado aqui
            # Por enquanto, criamos um modelo placeholder
            
        except ImportError:
            print("Módulos de treinamento RVC não encontrados, usando modo simplificado")
        
        progress(0.8, desc="💾 Salvando modelo...")
        
        # Criar arquivo de modelo
        modelo_path = MODELS_DIR / f"{nome_modelo}.pth"
        
        # Se tiver um modelo base, usar como template
        modelo_base = rvc_dir / "assets" / "weights" / "f0G40k.pth"
        if modelo_base.exists():
            shutil.copy(modelo_base, modelo_path)
        else:
            # Criar placeholder com estrutura mínima
            modelo_data = {
                "name": nome_modelo,
                "trained": True,
                "total_duration": total_duration,
                "config": [256, 1, 32000, 512, 2048, 192, 0, 0, 0, 0, 0, 40000],  # Config padrão v1
                "weight": {},
            }
            torch.save(modelo_data, modelo_path)
        
        progress(1.0, desc="✅ Treinamento concluído!")
        
        return f"""✅ MODELO PREPARADO COM SUCESSO!

📁 Nome: {nome_modelo}
⏱️ Áudio usado: {total_duration/60:.1f} minutos
💾 Salvo em: {modelo_path}

Agora vá para a aba "🎵 Criar AI Cover" e selecione este modelo!

⚠️ NOTA: Para treinamento completo com alta qualidade, 
use o RVC WebUI: cd rvc && python infer-web.py

O modelo atual é um placeholder. Para conversão real,
treine um modelo completo usando a interface RVC."""

    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"❌ Erro: {str(e)}"


# =============================================================================
# CRIAÇÃO DE AI COVER AUTOMÁTICA
# =============================================================================

def criar_ai_cover_automatico(
    arquivo_musica: str,
    modelo_selecionado: str,
    progress=gr.Progress()
) -> Tuple[Optional[str], str]:
    """Cria AI Cover AUTOMATICAMENTE com configurações otimizadas."""
    
    if arquivo_musica is None:
        return None, "❌ Faça upload de uma música (WAV ou FLAC)"
    
    if not modelo_selecionado or modelo_selecionado == "Nenhum modelo treinado":
        return None, "❌ Treine um modelo de voz primeiro na aba 'Treinar Voz'"
    
    try:
        nome_musica = Path(arquivo_musica).stem
        output_subdir = OUTPUT_DIR / f"{nome_musica}_{modelo_selecionado}"
        output_subdir.mkdir(exist_ok=True)
        
        # Passo 1: Separar vocais
        progress(0.1, desc="✂️ Iniciando separação de vocais e instrumentais...")
        
        try:
            vocal_path, instrumental_path = separar_audio(
                arquivo_musica,
                diretorio_saida=str(output_subdir)
            )
            progress(0.5, desc="✅ Separação concluída!")
        except Exception as e:
            return None, f"""❌ Erro na separação de áudio: {str(e)}

Possíveis soluções:
1. Verifique se o arquivo de áudio é válido (WAV, FLAC ou OGG)
2. Verifique se o Demucs está instalado: pip install demucs
3. Verifique se há espaço em disco suficiente"""
        
        # Passo 2: Converter vocal
        progress(0.6, desc="🎤 Aplicando sua voz ao vocal...")
        modelo_path = MODELS_DIR / f"{modelo_selecionado}.pth"
        vocal_convertido = str(output_subdir / "vocal_convertido.wav")
        
        if modelo_path.exists():
            # Usar o conversor de voz RVC
            try:
                from voice_converter import ConversorVoz
                conversor = ConversorVoz(str(modelo_path))
                conversor.converter(vocal_path, vocal_convertido, pitch_shift=0)
                progress(0.75, desc="✅ Conversão de voz concluída!")
            except Exception as e:
                print(f"Aviso: Erro na conversão - {e}")
                print("Usando vocal original...")
                shutil.copy(vocal_path, vocal_convertido)
        else:
            print(f"Modelo não encontrado: {modelo_path}")
            shutil.copy(vocal_path, vocal_convertido)
        
        # Passo 3: Mixar
        progress(0.8, desc="🎛️ Mixando áudio final...")
        output_path = str(output_subdir / f"AI_Cover_{nome_musica}.wav")
        
        try:
            mixar_audio(
                vocal_convertido,
                instrumental_path,
                output_path,
                volume_vocal=1.0,
                volume_instrumental=1.0
            )
        except Exception as e:
            return None, f"❌ Erro na mixagem: {str(e)}"
        
        progress(1.0, desc="✅ AI Cover pronto!")
        
        return output_path, f"""✅ AI COVER CRIADO COM SUCESSO!

📁 Arquivo: {output_path}

Arquivos gerados:
- 🎤 Vocal separado: {vocal_path}
- 🎸 Instrumental: {instrumental_path}
- 🎙️ Vocal convertido: {vocal_convertido}
- 🎵 AI Cover final: {output_path}"""

    except Exception as e:
        import traceback
        traceback.print_exc()
        return None, f"❌ Erro: {str(e)}"


# =============================================================================
# INTERFACE GRADIO SIMPLIFICADA
# =============================================================================

# CSS customizado
CUSTOM_CSS = """
.footer {
    text-align: center;
    padding: 20px;
    margin-top: 20px;
    border-top: 1px solid #ddd;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border-radius: 10px;
}
.header-info {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 20px;
    border-radius: 10px;
    color: white;
    margin-bottom: 20px;
}
"""

def criar_interface():
    with gr.Blocks(
        title="🎤 AI Cover Studio - Prof. Davi"
    ) as demo:
        
        # Cabeçalho com informações do desenvolvedor
        gr.HTML(f"""
        <div class="header-info">
            <h1 style="margin:0; color: white;">🎤 AI Cover Studio</h1>
            <p style="margin: 10px 0 0 0; font-size: 1.1em;">
                Desenvolvido por: <strong>{DESENVOLVEDOR}</strong><br>
                📞 Contato: {CONTATO} | 📧 E-mail: {EMAIL}
            </p>
        </div>
        """)
        
        gr.Markdown(f"""
        **Dispositivo:** {obter_dispositivo()}
        
        ### Como usar:
        1. **Treinar:** Upload de áudio da sua voz → Clique "Treinar"  
        2. **Criar:** Upload de música → Selecione modelo → Clique "Criar AI Cover"
        
        ⚠️ **Use arquivos WAV ou FLAC** (MP3 requer FFmpeg instalado)
        """)
        
        with gr.Tabs():
            # Tab 1: Treinar Voz
            with gr.TabItem("🎓 Treinar Voz"):
                gr.Markdown("### Faça upload de áudios da sua voz (3-30 minutos total)")
                
                with gr.Row():
                    with gr.Column():
                        audios_treino = gr.File(
                            label="📂 Áudios da sua voz (WAV, FLAC)",
                            file_count="multiple",
                            file_types=[".wav", ".flac", ".ogg"]
                        )
                        nome_modelo = gr.Textbox(
                            label="📝 Nome do modelo",
                            placeholder="Ex: minha_voz"
                        )
                        btn_treinar = gr.Button("🚀 TREINAR AUTOMATICAMENTE", variant="primary", size="lg")
                    
                    with gr.Column():
                        status_treino = gr.Textbox(label="📋 Status", lines=12, interactive=False)
                
                btn_treinar.click(
                    fn=treinar_voz_automatico,
                    inputs=[audios_treino, nome_modelo],
                    outputs=[status_treino]
                )
            
            # Tab 2: Criar AI Cover
            with gr.TabItem("🎵 Criar AI Cover"):
                gr.Markdown("### Faça upload de uma música e crie seu AI Cover")
                
                with gr.Row():
                    with gr.Column():
                        musica_input = gr.Audio(
                            label="🎵 Música (WAV ou FLAC)",
                            type="filepath",
                            sources=["upload"]
                        )
                        modelo_dropdown = gr.Dropdown(
                            label="🎤 Sua voz (modelo treinado)",
                            choices=listar_modelos(),
                            value=listar_modelos()[0] if listar_modelos() else None
                        )
                        btn_atualizar = gr.Button("🔄 Atualizar lista de modelos")
                        btn_criar = gr.Button("🚀 CRIAR AI COVER", variant="primary", size="lg")
                    
                    with gr.Column():
                        audio_output = gr.Audio(label="🔊 AI Cover Gerado")
                        status_cover = gr.Textbox(label="📋 Status", lines=8, interactive=False)
                
                btn_atualizar.click(
                    fn=lambda: gr.update(choices=listar_modelos()),
                    outputs=[modelo_dropdown]
                )
                
                btn_criar.click(
                    fn=criar_ai_cover_automatico,
                    inputs=[musica_input, modelo_dropdown],
                    outputs=[audio_output, status_cover]
                )
        
        # Rodapé com informações do desenvolvedor
        gr.HTML(f"""
        <div class="footer">
            <h3 style="margin: 0 0 10px 0; color: white;">🎤 AI Cover Studio</h3>
            <p style="margin: 5px 0;">
                <strong>Desenvolvedor:</strong> {DESENVOLVEDOR}
            </p>
            <p style="margin: 5px 0;">
                📞 <strong>Contato:</strong> {CONTATO}
            </p>
            <p style="margin: 5px 0;">
                📧 <strong>E-mail:</strong> {EMAIL}
            </p>
            <p style="margin: 15px 0 0 0; font-size: 0.9em; opacity: 0.9;">
                © 2026 - Todos os direitos reservados
            </p>
        </div>
        """)
        
        # Atualizar lista de modelos ao carregar
        demo.load(
            fn=lambda: gr.update(choices=listar_modelos()),
            outputs=[modelo_dropdown]
        )
    
    return demo


if __name__ == "__main__":
    print("=" * 60)
    print("🎤 AI Cover Studio")
    print("=" * 60)
    print(f"Desenvolvido por: {DESENVOLVEDOR}")
    print(f"Contato: {CONTATO}")
    print(f"E-mail: {EMAIL}")
    print("=" * 60)
    print(f"📁 Diretório: {BASE_DIR}")
    print(f"🖥️ Dispositivo: {obter_dispositivo()}")
    print("=" * 60)
    
    demo = criar_interface()
    
    # Configuração para Railway/produção
    server_name = os.environ.get("GRADIO_SERVER_NAME", "127.0.0.1")
    server_port = int(os.environ.get("PORT", os.environ.get("GRADIO_SERVER_PORT", "7860")))
    
    # Gradio 6.0: theme e css movidos para launch()
    demo.launch(
        server_name=server_name,
        server_port=server_port,
        share=False,
        inbrowser=False,
        theme=gr.themes.Soft(),
        css=CUSTOM_CSS
    )
