# 🎙️ Clonador de Voz - TTS Davi

Um sistema de clonagem de voz usando o modelo **XTTS v2** da Coqui TTS.

## 📋 Funcionalidades

- ✅ **Clonagem de voz** a partir de um pequeno áudio de referência (3-10 segundos)
- ✅ **Suporte a 16 idiomas** incluindo Português Brasileiro
- ✅ **Interface Web** amigável com Gradio
- ✅ **Modo linha de comando** para automação
- ✅ **Suporte a GPU** (CUDA) para processamento mais rápido

## 🚀 Como Usar

### Instalação

1. Certifique-se de ter Python 3.9-3.12 instalado
2. Instale as dependências:

```bash
cd TTSdavi-1
pip install -e .
pip install gradio faster-whisper
```

### Executar

#### Interface Web (Recomendado)

```bash
python clonar_voz.py
```

Isso abrirá uma interface web no navegador onde você pode:
1. Fazer upload de um áudio de referência
2. Digitar o texto desejado
3. Selecionar o idioma
4. Gerar o áudio clonado

#### Linha de Comando

```bash
# Exemplo básico (português)
python clonar_voz.py --audio_referencia minha_voz.wav --texto "Olá, eu sou uma voz clonada!" --saida output.wav

# Com idioma específico (inglês)
python clonar_voz.py -a voice.wav -t "Hello, this is a cloned voice!" -i en -o output_en.wav
```

## 🌍 Idiomas Suportados

| Código | Idioma |
|--------|--------|
| `pt` | Português |
| `en` | Inglês |
| `es` | Espanhol |
| `fr` | Francês |
| `de` | Alemão |
| `it` | Italiano |
| `pl` | Polonês |
| `tr` | Turco |
| `ru` | Russo |
| `nl` | Holandês |
| `cs` | Tcheco |
| `ar` | Árabe |
| `zh-cn` | Chinês |
| `hu` | Húngaro |
| `ko` | Coreano |
| `ja` | Japonês |

## 💡 Dicas para Melhores Resultados

1. **Qualidade do áudio de referência**: Use um áudio limpo, sem ruídos de fundo
2. **Duração ideal**: 3-10 segundos de fala contínua
3. **Fala clara**: O áudio de referência deve ter pronúncia clara
4. **Formato**: WAV, MP3 ou FLAC são aceitos
5. **Primeira execução**: O modelo (~2GB) será baixado automaticamente

## 🛠️ Requisitos do Sistema

- **Python**: 3.9 - 3.12
- **RAM**: Mínimo 8GB (recomendado 16GB)
- **GPU**: Opcional, mas recomendado para melhor performance
  - NVIDIA com CUDA (RTX 2060 ou superior recomendado)
- **Armazenamento**: ~5GB para modelos

## 📁 Estrutura do Projeto

```
TTSdavi-1/
├── clonar_voz.py          # Script principal de clonagem de voz
├── TTS/
│   ├── api.py             # API do TTS
│   ├── demos/
│   │   └── xtts_ft_demo/  # Demo de fine-tuning XTTS
│   └── tts/               # Modelos e utilitários
├── requirements.txt       # Dependências
└── README_CLONADOR.md     # Este arquivo
```

## 🔧 Solução de Problemas

### Erro: "CUDA out of memory"
- Reduza o tamanho do texto
- Use CPU ao invés de GPU (mais lento)

### Erro: "Model not found"
- Na primeira execução, aguarde o download do modelo (~2GB)
- Verifique sua conexão com a internet

### Áudio de saída com qualidade baixa
- Use um áudio de referência de melhor qualidade
- Aumente a duração do áudio de referência (5-10 segundos)

## 📝 Licença

Este projeto é baseado no Coqui TTS e utiliza a licença MPL 2.0.

## 🙏 Créditos

- [Coqui TTS](https://github.com/coqui-ai/TTS) - Biblioteca base
- [XTTS](https://huggingface.co/coqui/XTTS-v2) - Modelo de clonagem de voz
