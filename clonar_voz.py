#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Clonador de Voz - Script Simplificado
=====================================
Este script permite clonar uma voz usando o modelo XTTS da Coqui TTS.

Uso:
    python clonar_voz.py --audio_referencia "caminho/para/audio.wav" --texto "Olá, mundo!" --saida "output.wav"

Ou execute sem argumentos para usar a interface interativa.
"""

import argparse
import os
import sys
import tempfile
from pathlib import Path

import torch
import torchaudio


def verificar_dependencias():
    """Verifica se todas as dependências estão instaladas."""
    dependencias_faltando = []
    
    try:
        from TTS.api import TTS
    except ImportError:
        dependencias_faltando.append("TTS")
    
    try:
        import gradio as gr
    except ImportError:
        dependencias_faltando.append("gradio")
    
    if dependencias_faltando:
        print(f"❌ Dependências faltando: {', '.join(dependencias_faltando)}")
        print("Instale com: pip install TTS gradio")
        return False
    
    return True


def obter_dispositivo():
    """Retorna o dispositivo disponível (CUDA ou CPU)."""
    if torch.cuda.is_available():
        print(f"🚀 Usando GPU: {torch.cuda.get_device_name(0)}")
        return "cuda"
    else:
        print("💻 Usando CPU (pode ser mais lento)")
        return "cpu"


def carregar_modelo(device="cpu"):
    """Carrega o modelo XTTS v2."""
    from TTS.api import TTS
    
    print("📥 Carregando modelo XTTS v2...")
    print("   (Isso pode demorar na primeira execução, pois o modelo será baixado)")
    
    # Usa o modelo multilíngue XTTS v2
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
    tts.to(device)
    
    print("✅ Modelo carregado com sucesso!")
    return tts


def clonar_voz(tts, audio_referencia: str, texto: str, idioma: str = "pt", arquivo_saida: str = "output.wav"):
    """
    Clona a voz do áudio de referência e gera fala com o texto fornecido.
    
    Args:
        tts: Instância do modelo TTS
        audio_referencia: Caminho para o arquivo de áudio da voz a ser clonada
        texto: Texto a ser falado com a voz clonada
        idioma: Código do idioma (pt, en, es, fr, de, it, etc.)
        arquivo_saida: Caminho para salvar o áudio gerado
    
    Returns:
        str: Caminho do arquivo de áudio gerado
    """
    if not os.path.exists(audio_referencia):
        raise FileNotFoundError(f"Arquivo de áudio de referência não encontrado: {audio_referencia}")
    
    print(f"🎙️ Clonando voz de: {audio_referencia}")
    print(f"📝 Texto: {texto}")
    print(f"🌍 Idioma: {idioma}")
    
    # Gera o áudio com a voz clonada
    tts.tts_to_file(
        text=texto,
        speaker_wav=audio_referencia,
        language=idioma,
        file_path=arquivo_saida
    )
    
    print(f"✅ Áudio gerado: {arquivo_saida}")
    return arquivo_saida


def interface_gradio():
    """Cria uma interface web com Gradio para clonagem de voz."""
    import gradio as gr
    
    device = obter_dispositivo()
    tts = None
    
    def carregar_modelo_gradio():
        nonlocal tts
        if tts is None:
            tts = carregar_modelo(device)
        return "✅ Modelo carregado!"
    
    def processar_clonagem(audio_referencia, texto, idioma):
        nonlocal tts
        
        if tts is None:
            tts = carregar_modelo(device)
        
        if audio_referencia is None:
            return None, "❌ Por favor, forneça um áudio de referência."
        
        if not texto or texto.strip() == "":
            return None, "❌ Por favor, forneça um texto para sintetizar."
        
        try:
            # Cria arquivo temporário para saída
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as fp:
                arquivo_saida = fp.name
            
            clonar_voz(tts, audio_referencia, texto, idioma, arquivo_saida)
            return arquivo_saida, "✅ Áudio gerado com sucesso!"
        
        except Exception as e:
            return None, f"❌ Erro: {str(e)}"
    
    # Interface Gradio
    with gr.Blocks(title="🎙️ Clonador de Voz", theme=gr.themes.Soft()) as demo:
        gr.Markdown("""
        # 🎙️ Clonador de Voz com XTTS v2
        
        Este aplicativo permite clonar qualquer voz a partir de um pequeno áudio de referência.
        
        ## Como usar:
        1. Faça upload de um áudio de referência (3-10 segundos de fala clara)
        2. Digite o texto que deseja que seja falado
        3. Selecione o idioma
        4. Clique em "Gerar Áudio"
        """)
        
        with gr.Row():
            with gr.Column():
                audio_input = gr.Audio(
                    label="🎵 Áudio de Referência",
                    type="filepath",
                    sources=["upload", "microphone"]
                )
                
                texto_input = gr.Textbox(
                    label="📝 Texto para Sintetizar",
                    placeholder="Digite o texto que você quer que seja falado...",
                    lines=3
                )
                
                idioma_input = gr.Dropdown(
                    label="🌍 Idioma",
                    choices=[
                        ("Português", "pt"),
                        ("Inglês", "en"),
                        ("Espanhol", "es"),
                        ("Francês", "fr"),
                        ("Alemão", "de"),
                        ("Italiano", "it"),
                        ("Russo", "ru"),
                        ("Japonês", "ja"),
                        ("Coreano", "ko"),
                        ("Chinês", "zh-cn"),
                    ],
                    value="pt"
                )
                
                btn_gerar = gr.Button("🚀 Gerar Áudio", variant="primary")
            
            with gr.Column():
                audio_output = gr.Audio(label="🔊 Áudio Gerado")
                status_output = gr.Textbox(label="📋 Status", interactive=False)
        
        btn_gerar.click(
            fn=processar_clonagem,
            inputs=[audio_input, texto_input, idioma_input],
            outputs=[audio_output, status_output]
        )
        
        gr.Markdown("""
        ---
        ## 💡 Dicas:
        - Use um áudio de referência com **3-10 segundos** de fala clara
        - Evite ruídos de fundo no áudio de referência
        - O modelo funciona melhor com frases mais curtas
        - Na primeira execução, o modelo será baixado (~2GB)
        
        ## 🌍 Idiomas Suportados:
        Português, Inglês, Espanhol, Francês, Alemão, Italiano, Polonês, Turco, Russo, 
        Holandês, Tcheco, Árabe, Chinês, Húngaro, Coreano, Japonês
        """)
    
    return demo


def main():
    parser = argparse.ArgumentParser(
        description="Clonador de Voz usando XTTS v2",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  # Modo interface web:
  python clonar_voz.py
  
  # Modo linha de comando:
  python clonar_voz.py --audio_referencia voz.wav --texto "Olá, mundo!" --saida output.wav
  
  # Com idioma específico:
  python clonar_voz.py --audio_referencia voz.wav --texto "Hello world!" --idioma en --saida output.wav
        """
    )
    
    parser.add_argument("--audio_referencia", "-a", type=str, 
                        help="Caminho para o áudio de referência da voz a clonar")
    parser.add_argument("--texto", "-t", type=str, 
                        help="Texto a ser sintetizado com a voz clonada")
    parser.add_argument("--idioma", "-i", type=str, default="pt",
                        help="Código do idioma (pt, en, es, fr, de, it, etc.). Padrão: pt")
    parser.add_argument("--saida", "-o", type=str, default="output.wav",
                        help="Caminho para o arquivo de saída. Padrão: output.wav")
    parser.add_argument("--web", "-w", action="store_true",
                        help="Iniciar interface web Gradio")
    parser.add_argument("--porta", "-p", type=int, default=7860,
                        help="Porta para a interface web. Padrão: 7860")
    
    args = parser.parse_args()
    
    if not verificar_dependencias():
        sys.exit(1)
    
    # Se nenhum argumento for fornecido ou --web, inicia interface Gradio
    if args.web or (args.audio_referencia is None and args.texto is None):
        print("🌐 Iniciando interface web...")
        demo = interface_gradio()
        demo.launch(
            server_port=args.porta,
            share=False,
            inbrowser=True
        )
    else:
        # Modo linha de comando
        if not args.audio_referencia:
            print("❌ Erro: --audio_referencia é obrigatório no modo linha de comando")
            sys.exit(1)
        if not args.texto:
            print("❌ Erro: --texto é obrigatório no modo linha de comando")
            sys.exit(1)
        
        device = obter_dispositivo()
        tts = carregar_modelo(device)
        clonar_voz(tts, args.audio_referencia, args.texto, args.idioma, args.saida)
        print("🎉 Pronto!")


if __name__ == "__main__":
    main()
