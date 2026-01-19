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
import requests

# Workaround: gradio_client crashes on bool schemas (TypeError: 'bool' not iterable)
# Monkeypatch json_schema_to_python_type to ignore pure-boolean schemas
try:
    import gradio_client.utils as _gc_utils

    _orig_json_schema_to_python_type = _gc_utils._json_schema_to_python_type

    def _safe_json_schema_to_python_type(schema, defs=None):
        if isinstance(schema, bool):
            return "Any"
        return _orig_json_schema_to_python_type(schema, defs)

    def _safe_json_schema_to_python_type_public(schema):
        defs = schema.get("$defs") if isinstance(schema, dict) else None
        return _safe_json_schema_to_python_type(schema, defs)

    _gc_utils._json_schema_to_python_type = _safe_json_schema_to_python_type
    _gc_utils.json_schema_to_python_type = _safe_json_schema_to_python_type_public
except Exception as _patch_err:  # pragma: no cover
    print(f"[gradio-client patch] falhou ao aplicar workaround: {_patch_err}")

from audio_separator import separar_audio, normalizar_caminho_audio
from audio_mixer import mixar_audio
from voice_trainer import treinar_modelo_voz, ConversorVozFreeVC


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


def _download_file(url: str, destino: Path):
    """Faz download de um arquivo via HTTP para o caminho destino."""
    with requests.get(url, stream=True, timeout=60) as r:
        r.raise_for_status()
        destino.parent.mkdir(parents=True, exist_ok=True)
        with open(destino, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)


def baixar_modelo_rvc(
    url_modelo: str,
    nome_modelo: str,
    url_index: Optional[str] = "",
    progress=gr.Progress(),
) -> Tuple[str, gr.Dropdown]:
    """Baixa um modelo RVC pronto (.pth) e opcionalmente o index (.index)."""

    if not url_modelo or not nome_modelo:
        return "❌ Informe a URL do modelo (.pth) e um nome.", gr.update()

    nome_modelo = nome_modelo.strip().replace(" ", "_")
    destino_pth = MODELS_DIR / f"{nome_modelo}.pth"
    destino_index = MODELS_DIR / f"{nome_modelo}.index" if url_index else None

    try:
        progress(0.1, desc="🔽 Baixando modelo (.pth)...")
        _download_file(url_modelo, destino_pth)

        if url_index:
            progress(0.6, desc="🔽 Baixando index (.index)...")
            _download_file(url_index, destino_index)

        progress(1.0, desc="✅ Download concluído!")
        status = f"✅ Modelo salvo em: {destino_pth}\nIndex: {destino_index if url_index else '—'}"
        return status, gr.update(choices=listar_modelos(), value=nome_modelo)
    except Exception as e:
        return f"❌ Erro ao baixar: {e}", gr.update()


# =============================================================================
# TREINAMENTO AUTOMÁTICO DE VOZ
# =============================================================================

def treinar_voz_automatico(
    arquivos_audio: List[str],
    nome_modelo: str,
    progress=gr.Progress()
) -> Tuple[str, gr.Dropdown]:
    """Treina modelo de voz REAL com extração de embeddings."""
    
    if not arquivos_audio:
        return "❌ Faça upload de arquivos de áudio da voz que deseja clonar.", gr.update()
    
    if not nome_modelo or nome_modelo.strip() == "":
        return "❌ Dê um nome para o modelo (ex: minha_voz)", gr.update()
    
    nome_modelo = nome_modelo.strip().replace(" ", "_")
    
    try:
        # Criar diretório do dataset
        dataset_dir = DATASETS_DIR / nome_modelo
        dataset_dir.mkdir(exist_ok=True)
        
        # Copiar e processar áudios para o dataset
        progress(0.05, desc="📁 Preparando áudios...")
        arquivos_processados = []
        
        for i, arquivo in enumerate(arquivos_audio):
            pct = 0.05 + (i / len(arquivos_audio)) * 0.15
            progress(pct, desc=f"Copiando áudio {i+1}/{len(arquivos_audio)}...")
            
            try:
                arquivo_seguro = normalizar_caminho_audio(arquivo)
                
                # Carregar e salvar em formato padrão
                import librosa
                audio, sr = librosa.load(arquivo_seguro, sr=16000, mono=True)
                
                # Limitar a 3 minutos por arquivo
                max_samples = 16000 * 60 * 3
                if len(audio) > max_samples:
                    audio = audio[:max_samples]
                
                dest = dataset_dir / f"audio_{i:04d}.wav"
                sf.write(str(dest), audio, 16000)
                arquivos_processados.append(str(dest))
                
            except Exception as e:
                print(f"Erro processando áudio {i+1}: {e}")
                continue
        
        if not arquivos_processados:
            return "❌ Nenhum áudio pôde ser processado. Verifique os arquivos.", gr.update()
        
        # Treinar modelo usando voice_trainer
        def progress_callback(pct, msg):
            # Mapear 0-1 para 0.2-0.95
            mapped_pct = 0.2 + pct * 0.75
            progress(mapped_pct, desc=msg)
        
        modelo_path = treinar_modelo_voz(
            arquivos_audio=arquivos_processados,
            nome_modelo=nome_modelo,
            diretorio_saida=str(MODELS_DIR),
            progress_callback=progress_callback,
        )
        
        # Carregar info do modelo
        modelo_data = torch.load(modelo_path, map_location="cpu")
        metadata = modelo_data.get("metadata", {})
        total_duration = metadata.get("total_duration", 0)
        
        progress(1.0, desc="✅ Treinamento concluído!")
        
        return f"""✅ MODELO TREINADO COM SUCESSO!

📁 Nome: {nome_modelo}
⏱️ Áudio usado: {total_duration:.1f} segundos ({total_duration/60:.1f} minutos)
🎤 Arquivos processados: {len(arquivos_processados)}
💾 Salvo em: {modelo_path}

🎵 Agora vá para a aba "Criar AI Cover" e selecione este modelo!

✨ O modelo contém embeddings reais da sua voz.
A conversão aplicará as características vocais extraídas.""", gr.update(choices=listar_modelos(), value=nome_modelo)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"❌ Erro: {str(e)}", gr.update()


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
        
        # Passo 2: Converter vocal com o modelo treinado
        progress(0.6, desc="🎤 Aplicando sua voz ao vocal...")
        modelo_path = MODELS_DIR / f"{modelo_selecionado}.pth"
        vocal_convertido = str(output_subdir / "vocal_convertido.wav")
        
        if modelo_path.exists():
            # Usar o conversor de voz FreeVC (com embeddings reais)
            try:
                conversor = ConversorVozFreeVC(str(modelo_path))
                conversor.converter(
                    audio_entrada=vocal_path,
                    audio_saida=vocal_convertido,
                    pitch_shift=0,
                    mix_ratio=0.8  # 80% voz convertida, 20% original
                )
                progress(0.75, desc="✅ Conversão de voz concluída!")
            except Exception as e:
                print(f"Aviso: Erro na conversão FreeVC - {e}")
                # Fallback para conversor antigo
                try:
                    from voice_converter import ConversorVoz
                    conversor_old = ConversorVoz(str(modelo_path))
                    conversor_old.converter(vocal_path, vocal_convertido, pitch_shift=0)
                except Exception as e2:
                    print(f"Fallback também falhou: {e2}")
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
        title="🎤 AI Cover Studio - Prof. Davi",
        theme=gr.themes.Soft(),
        css=CUSTOM_CSS
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

            # Tab 3: Baixar modelo RVC pronto
            with gr.TabItem("📥 Baixar Modelo RVC"):
                gr.Markdown("""
                Cole uma URL direta para um modelo RVC (.pth) e opcionalmente um arquivo de index (.index).
                Exemplo: link direto do Hugging Face (botão "Download" → "Copy link").
                """)

                with gr.Row():
                    with gr.Column():
                        url_modelo = gr.Textbox(label="URL do modelo (.pth)")
                        url_index = gr.Textbox(label="URL do index (.index) (opcional)")
                        nome_modelo_dl = gr.Textbox(label="Nome para salvar (sem espaços)", placeholder="minha_voz_pronta")
                        btn_baixar = gr.Button("⬇️ Baixar e adicionar", variant="primary")
                    with gr.Column():
                        status_download = gr.Textbox(label="Status do download", lines=6, interactive=False)

                btn_baixar.click(
                    fn=baixar_modelo_rvc,
                    inputs=[url_modelo, nome_modelo_dl, url_index],
                    outputs=[status_download, modelo_dropdown]
                )
        
        # Conectar eventos que dependem de componentes de outras abas (após todas as abas serem criadas)
        btn_treinar.click(
            fn=treinar_voz_automatico,
            inputs=[audios_treino, nome_modelo],
            outputs=[status_treino, modelo_dropdown]
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
    # IMPORTANTE: usar 0.0.0.0 para aceitar conexões externas
    server_name = os.environ.get("GRADIO_SERVER_NAME", "0.0.0.0")
    server_port = int(os.environ.get("PORT", os.environ.get("GRADIO_SERVER_PORT", "7860")))
    
    print(f"🌐 Iniciando servidor em {server_name}:{server_port}")
    
    # Gradio: configuração para produção
    demo.launch(
        server_name=server_name,
        server_port=server_port,
        # Railway executa atrás de proxy; share=True evita erro de localhost inacessível
        share=True,
        inbrowser=False,
        show_error=True
    )
