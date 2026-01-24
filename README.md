# 🎤 AI Cover Studio

<div align="center">

![AI Cover Studio](https://img.shields.io/badge/AI%20Cover-Studio-purple?style=for-the-badge&logo=music&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.9+-blue?style=for-the-badge&logo=python&logoColor=white)
![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-red?style=for-the-badge&logo=pytorch&logoColor=white)
![Gradio](https://img.shields.io/badge/Gradio-4.0+-orange?style=for-the-badge&logo=gradio&logoColor=white)

**Sistema Completo de AI Covers - Transforme qualquer música com vozes clonadas por IA**

[🚀 Demo Online](https://ttsdavi-production.up.railway.app) | [📖 Documentação](#-arquitetura-do-sistema) | [🛠️ Instalação](#-instalação)

</div>

---

## 👨‍🏫 Desenvolvedor

| | |
|---|---|
| **Nome** | Professor Davi Antonino Nunes da Silva |
| **Contato** | (16) 99260-4315 |
| **E-mail** | <professordavi85@gmail.com> |

---

## 📋 Índice

- [O que é o AI Cover Studio?](#-o-que-é-o-ai-cover-studio)
- [Funcionalidades](#-funcionalidades)
- [Arquitetura do Sistema](#-arquitetura-do-sistema)
- [Fluxo de Processamento Completo](#-fluxo-de-processamento-completo)
- [Estrutura de Arquivos](#-estrutura-de-arquivos)
- [Instalação](#-instalação)
- [Como Usar](#-como-usar)
- [Módulos em Detalhe](#-módulos-em-detalhe)
- [Deploy](#-deploy)
- [Requisitos do Sistema](#-requisitos-do-sistema)
- [Solução de Problemas](#-solução-de-problemas)
- [Licença](#-licença)

---

## 🎵 O que é o AI Cover Studio?

O **AI Cover Studio** é um sistema completo e automatizado para criação de **AI Covers** - versões de músicas onde a voz original é substituída por uma voz clonada usando Inteligência Artificial.

### O que são AI Covers?

AI Covers são recriações de músicas onde:

1. A voz original do cantor é **removida** da música
2. Uma nova voz (clonada por IA) **canta** a mesma melodia
3. A voz clonada é **mixada** de volta com os instrumentos originais

Isso permite, por exemplo, ouvir como seria se um artista diferente cantasse determinada música.

---

## ✨ Funcionalidades

### 🎙️ Clonagem de Voz

- Clone qualquer voz a partir de **3-10 segundos** de áudio
- Suporte a **16 idiomas** incluindo Português Brasileiro
- Modelo XTTS v2 da Coqui TTS

### 🎵 Separação de Áudio

- Separa **vocais** e **instrumentais** de qualquer música
- Usa tecnologia **Demucs** (Meta AI)
- Alta qualidade de separação

### 🔄 Conversão de Voz (RVC)

- Converte vocais usando modelos **RVC** (Retrieval-based Voice Conversion)
- Treinamento de modelos personalizados
- Preserva entonação e emoção

### 🎛️ Mixagem Automática

- Combina vocal convertido com instrumental
- Ajuste automático de volume
- Normalização profissional

### 🌐 Interface Web

- Interface **Gradio** intuitiva
- 100% automatizado - apenas upload e download
- Funciona no navegador

---

## 🏗️ Arquitetura do Sistema

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           AI COVER STUDIO                                    │
│                                                                              │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐  │
│  │   ENTRADA   │───▶│  SEPARAÇÃO  │───▶│  CONVERSÃO  │───▶│   MIXAGEM   │  │
│  │   (Upload)  │    │   (Demucs)  │    │    (RVC)    │    │   (Final)   │  │
│  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘  │
│        │                   │                  │                  │          │
│        ▼                   ▼                  ▼                  ▼          │
│   ┌─────────┐        ┌──────────┐       ┌──────────┐       ┌──────────┐    │
│   │ Música  │        │  Vocal   │       │  Vocal   │       │  Música  │    │
│   │Original │        │   +      │       │Convertido│       │ AI Cover │    │
│   │  .mp3   │        │Instrumen-│       │  .wav    │       │  .wav    │    │
│   └─────────┘        │tal .wav  │       └──────────┘       └──────────┘    │
│                      └──────────┘                                          │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Componentes Principais

| Componente | Arquivo | Função |
|------------|---------|--------|
| **Interface Principal** | `ai_cover_app.py` | Orquestra todo o sistema, interface Gradio |
| **Separador de Áudio** | `audio_separator.py` | Separa vocais e instrumentais |
| **Conversor de Voz** | `voice_converter.py` | Aplica modelo RVC aos vocais |
| **Mixer de Áudio** | `audio_mixer.py` | Combina vocal + instrumental |
| **Clonador de Voz** | `clonar_voz.py` | Clona voz usando XTTS v2 |

---

## 🔄 Fluxo de Processamento Completo

### Visão Geral do Pipeline

```
USUÁRIO                          SISTEMA                              RESULTADO
   │                                │                                     │
   │  1. Upload da música          │                                     │
   │  ─────────────────────────────▶                                     │
   │                                │                                     │
   │  2. Upload/seleção do modelo  │                                     │
   │  ─────────────────────────────▶                                     │
   │                                │                                     │
   │                           ┌────┴────┐                               │
   │                           │SEPARAÇÃO│                               │
   │                           └────┬────┘                               │
   │                                │                                     │
   │                           ┌────┴────┐                               │
   │                           │CONVERSÃO│                               │
   │                           └────┬────┘                               │
   │                                │                                     │
   │                           ┌────┴────┐                               │
   │                           │ MIXAGEM │                               │
   │                           └────┬────┘                               │
   │                                │                                     │
   │  3. Download do AI Cover      │                                     │
   │  ◀─────────────────────────────                                     │
   │                                                                      │
```

---

### ETAPA 1: Upload e Validação

**Arquivo:** `ai_cover_app.py` → função `criar_ai_cover()`

```python
# O usuário faz upload de:
# - Arquivo de música (MP3, WAV, FLAC)
# - Seleção do modelo de voz treinado

def criar_ai_cover(arquivo_musica, modelo_selecionado, volume_vocal, volume_instrumental):
    # 1.1 Validação do arquivo
    if not arquivo_musica:
        return None, "❌ Faça upload de uma música"
    
    # 1.2 Verificação do modelo
    modelo_path = MODELS_DIR / f"{modelo_selecionado}.pth"
    if not modelo_path.exists():
        return None, "❌ Modelo não encontrado"
```

**O que acontece:**

1. Gradio recebe o arquivo via interface web
2. Arquivo é salvo temporariamente no servidor
3. Sistema valida formato e tamanho
4. Modelo selecionado é localizado em `models/`

---

### ETAPA 2: Separação de Áudio (Demucs)

**Arquivo:** `audio_separator.py` → função `separar_audio()`

```python
def separar_audio(arquivo_entrada, diretorio_saida, modelo="htdemucs"):
    """
    Separa a música em stems usando Demucs.
    
    Entrada: música completa (vocal + instrumental)
    Saída: vocal.wav + instrumental.wav (no_vocals.wav)
    """
    
    # 2.1 Carregar modelo Demucs
    from demucs.pretrained import get_model
    from demucs.apply import apply_model
    
    model = get_model(modelo)  # htdemucs é o modelo padrão
    model.to(device)
    
    # 2.2 Carregar áudio
    audio, sr = carregar_audio(arquivo_entrada, sr_alvo=44100)
    
    # 2.3 Aplicar separação
    # Demucs separa em 4 stems: drums, bass, other, vocals
    stems = apply_model(model, audio)
    
    # 2.4 Extrair vocal e criar instrumental
    vocal = stems['vocals']
    instrumental = stems['drums'] + stems['bass'] + stems['other']
    
    # 2.5 Salvar arquivos
    salvar_audio(vocal, f"{diretorio_saida}/vocals.wav")
    salvar_audio(instrumental, f"{diretorio_saida}/no_vocals.wav")
    
    return vocal_path, instrumental_path
```

**Detalhes Técnicos:**

| Parâmetro | Valor | Descrição |
|-----------|-------|-----------|
| **Modelo** | htdemucs | Modelo híbrido (transformers + U-Net) |
| **Sample Rate** | 44100 Hz | Taxa de amostragem padrão |
| **Canais** | Stereo | Preserva canais L/R |
| **Stems** | 4 | drums, bass, other, vocals |

**Fluxo interno do Demucs:**

```
┌──────────────┐
│ Música Input │
│   (stereo)   │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   Encoder    │  ◀── Espectrograma + Waveform
│  (Híbrido)   │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Transformer  │  ◀── Atenção temporal
│   Layers     │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   Decoder    │
│   (4 stems)  │
└──────┬───────┘
       │
       ├───▶ 🥁 Drums
       ├───▶ 🎸 Bass  
       ├───▶ 🎹 Other (piano, guitarra, etc)
       └───▶ 🎤 Vocals ◀── Este é extraído
```

---

### ETAPA 3: Conversão de Voz (RVC)

**Arquivo:** `voice_converter.py` → classe `ConversorVoz`

```python
class ConversorVoz:
    def __init__(self, modelo_path, index_path=None):
        """
        Inicializa conversor com modelo RVC treinado.
        
        modelo_path: arquivo .pth com pesos do modelo
        index_path: arquivo .index para retrieval (opcional)
        """
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self._carregar_modelo()
    
    def converter(self, audio_entrada, f0_metodo="rmvpe", f0_up_key=0):
        """
        Converte voz do áudio de entrada para voz do modelo.
        
        Parâmetros:
        - f0_metodo: método de extração de pitch (rmvpe é mais preciso)
        - f0_up_key: ajuste de tom (-12 a +12 semitons)
        """
        
        # 3.1 Carregar áudio de entrada (vocal separado)
        audio, sr = carregar_audio_sf(audio_entrada, sr_alvo=16000)
        
        # 3.2 Extrair características F0 (pitch)
        f0 = self._extrair_f0(audio, metodo=f0_metodo)
        
        # 3.3 Ajustar tom se necessário
        if f0_up_key != 0:
            f0 = f0 * (2 ** (f0_up_key / 12))
        
        # 3.4 Extrair embeddings de voz
        embeddings = self._extrair_embeddings(audio)
        
        # 3.5 Converter usando modelo RVC
        audio_convertido = self.modelo(embeddings, f0)
        
        # 3.6 Pós-processamento
        audio_final = self._pos_processar(audio_convertido)
        
        return audio_final
```

**Pipeline de Conversão RVC:**

```
┌─────────────────┐
│  Vocal Original │
│   (separado)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Extração de F0  │  ◀── Pitch (frequência fundamental)
│    (RMVPE)      │      Preserva melodia e entonação
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Extração de     │  ◀── Características da fala
│  Embeddings     │      (conteúdo fonético)
│   (HuBERT)      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Modelo RVC     │  ◀── Modelo treinado com voz alvo
│  (Generator)    │      Transforma timbre
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Vocoder        │  ◀── Reconstrói forma de onda
│  (HiFi-GAN)     │      Alta qualidade de áudio
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Vocal Convertido│
│  (nova voz)     │
└─────────────────┘
```

**Parâmetros importantes:**

| Parâmetro | Descrição | Valor típico |
|-----------|-----------|--------------|
| **f0_up_key** | Ajuste de tom (semitons) | 0 (mesmo tom) |
| **f0_metodo** | Método de extração F0 | rmvpe (mais preciso) |
| **index_rate** | Peso do índice de retrieval | 0.75 |
| **filter_radius** | Suavização do pitch | 3 |
| **resample_sr** | Sample rate interno | 40000 Hz |

---

### ETAPA 4: Mixagem Final

**Arquivo:** `audio_mixer.py` → função `mixar_audio()`

```python
def mixar_audio(vocal_path, instrumental_path, output_path, 
                volume_vocal=1.0, volume_instrumental=1.0):
    """
    Combina vocal convertido com instrumental original.
    
    Processo:
    1. Carregar ambos os áudios
    2. Sincronizar durações
    3. Aplicar volumes
    4. Mixar e normalizar
    5. Exportar arquivo final
    """
    
    # 4.1 Carregar áudios
    vocal = carregar_audio(vocal_path, sample_rate=44100)
    instrumental = carregar_audio(instrumental_path, sample_rate=44100)
    
    # 4.2 Garantir mesmo número de canais
    if vocal.shape[1] == 1 and instrumental.shape[1] == 2:
        vocal = np.repeat(vocal, 2, axis=1)  # Mono → Stereo
    
    # 4.3 Sincronizar durações
    max_len = max(vocal.shape[0], instrumental.shape[0])
    vocal = ajustar_duracao(vocal, max_len)
    instrumental = ajustar_duracao(instrumental, max_len)
    
    # 4.4 Aplicar volumes
    vocal = vocal * volume_vocal
    instrumental = instrumental * volume_instrumental
    
    # 4.5 Mixar
    mix = vocal + instrumental
    
    # 4.6 Normalizar para evitar clipping
    mix = normalizar_audio(mix, target_db=-3.0)
    
    # 4.7 Salvar
    sf.write(output_path, mix, 44100)
    
    return output_path
```

**Diagrama de Mixagem:**

```
┌──────────────────┐     ┌──────────────────┐
│ Vocal Convertido │     │   Instrumental   │
│    (RVC out)     │     │  (Demucs out)    │
└────────┬─────────┘     └────────┬─────────┘
         │                        │
         ▼                        ▼
   ┌───────────┐           ┌───────────┐
   │  Volume   │           │  Volume   │
   │   ×1.0    │           │   ×1.0    │
   └─────┬─────┘           └─────┬─────┘
         │                        │
         └──────────┬─────────────┘
                    │
                    ▼
            ┌───────────────┐
            │   MIXAGEM     │
            │  vocal + inst │
            └───────┬───────┘
                    │
                    ▼
            ┌───────────────┐
            │ NORMALIZAÇÃO  │
            │  -3dB target  │
            └───────┬───────┘
                    │
                    ▼
            ┌───────────────┐
            │  AI COVER     │
            │   FINAL.wav   │
            └───────────────┘
```

---

### ETAPA 5: Entrega ao Usuário

**Arquivo:** `ai_cover_app.py` → interface Gradio

```python
# Após todo processamento:
return caminho_audio_final, "✅ AI Cover criado com sucesso!"

# O Gradio exibe:
# - Player de áudio para preview
# - Botão de download
# - Mensagem de status
```

---

## 📁 Estrutura de Arquivos

```
TTSdavi/
│
├── 📄 ai_cover_app.py          # 🎯 PRINCIPAL - Interface Gradio
├── 📄 audio_separator.py       # 🎵 Separação vocal/instrumental (Demucs)
├── 📄 voice_converter.py       # 🔄 Conversão de voz (RVC)
├── 📄 audio_mixer.py           # 🎛️ Mixagem de áudio
├── 📄 clonar_voz.py           # 🎤 Clonagem de voz (XTTS)
│
├── 📁 models/                  # Modelos RVC treinados (.pth)
├── 📁 datasets/                # Datasets para treinamento
├── 📁 output/                  # Arquivos de saída
│
├── 📁 TTS/                     # Biblioteca Coqui TTS
├── 📁 rvc/                     # Módulos RVC
│
├── 📁 api/                     # API para Vercel
│   └── 📄 index.py
│
├── 📄 Dockerfile               # Build para Railway
├── 📄 railway.json             # Configuração Railway
├── 📄 nixpacks.toml            # Build alternativo
├── 📄 vercel.json              # Configuração Vercel
│
├── 📄 requirements.txt         # Dependências completas
├── 📄 requirements-railway.txt # Dependências Railway (leve)
├── 📄 pyproject.toml           # Metadados do projeto
│
└── 📄 LICENSE.txt              # Licença MPL 2.0
```

---

## 🛠️ Instalação

### Pré-requisitos

- Python 3.9 - 3.12
- 8GB RAM mínimo (16GB recomendado)
- GPU NVIDIA com CUDA (opcional, mas recomendado)
- FFmpeg instalado no sistema

### Instalação Local

```bash
# 1. Clonar repositório
git clone https://github.com/dansfisica85/TTSdavi.git
cd TTSdavi

# 2. Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou: venv\Scripts\activate  # Windows

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Executar
python ai_cover_app.py
```

### Instalação com Docker

```bash
# Build
docker build -t ai-cover-studio .

# Executar
docker run -p 7860:7860 ai-cover-studio
```

---

## 🎮 Como Usar

### Interface Web (Recomendado)

1. Acesse <https://ttsdavi-production.up.railway.app> ou execute localmente
2. **Aba "Treinar Voz"**: Faça upload de áudios para criar um modelo de voz
3. **Aba "Criar AI Cover"**:
   - Upload da música
   - Selecione o modelo de voz
   - Ajuste volumes
   - Clique em "Criar AI Cover"
4. Baixe o resultado

### Modo Programático

```python
from audio_separator import separar_audio
from voice_converter import ConversorVoz
from audio_mixer import mixar_audio

# 1. Separar música
vocal, instrumental = separar_audio("musica.mp3", "output/")

# 2. Converter voz
conversor = ConversorVoz("models/minha_voz.pth")
vocal_convertido = conversor.converter(vocal)

# 3. Mixar
resultado = mixar_audio(vocal_convertido, instrumental, "ai_cover.wav")
```

---

## 📦 Módulos em Detalhe

### `ai_cover_app.py` - Interface Principal

| Função | Descrição |
|--------|-----------|
| `criar_interface()` | Cria interface Gradio completa |
| `treinar_voz_automatico()` | Pipeline de treinamento RVC |
| `criar_ai_cover()` | Pipeline completo de AI Cover |
| `listar_modelos()` | Lista modelos disponíveis |
| `obter_dispositivo()` | Detecta GPU/CPU |

### `audio_separator.py` - Separação de Áudio

| Função | Descrição |
|--------|-----------|
| `separar_audio()` | Função principal de separação |
| `carregar_audio()` | Carrega arquivo com soundfile |
| `salvar_audio()` | Salva tensor como WAV |
| `resample_audio()` | Altera sample rate |

### `voice_converter.py` - Conversão RVC

| Classe/Função | Descrição |
|---------------|-----------|
| `ConversorVoz` | Classe principal do conversor |
| `converter()` | Converte áudio com modelo |
| `_extrair_f0()` | Extrai pitch do áudio |
| `_carregar_modelo()` | Carrega pesos .pth |

### `audio_mixer.py` - Mixagem

| Função | Descrição |
|--------|-----------|
| `mixar_audio()` | Combina vocal + instrumental |
| `normalizar_audio()` | Normaliza para -3dB |
| `ajustar_duracao()` | Sincroniza durações |
| `carregar_audio()` | Carrega com resample |

### `clonar_voz.py` - Clonagem XTTS

| Função | Descrição |
|--------|-----------|
| `clonar_voz()` | Clona voz de referência |
| `carregar_modelo()` | Carrega XTTS v2 |
| `interface_gradio()` | Interface standalone |

---

## 🚀 Deploy

### Railway (Aplicação Completa)

```bash
# URL de produção
https://ttsdavi-production.up.railway.app
```

**Configuração:** `railway.json` + `Dockerfile`

### Vercel (Página Vitrine)

```bash
# URL
https://tts-davi.vercel.app
```

**Configuração:** `vercel.json` + `api/index.py`

---

## 💻 Requisitos do Sistema

### Mínimo

| Componente | Requisito |
|------------|-----------|
| **CPU** | 4 cores |
| **RAM** | 8 GB |
| **Disco** | 10 GB |
| **Python** | 3.9+ |

### Recomendado

| Componente | Requisito |
|------------|-----------|
| **CPU** | 8+ cores |
| **RAM** | 16 GB |
| **GPU** | NVIDIA RTX 2060+ (6GB VRAM) |
| **Disco** | 20 GB SSD |
| **Python** | 3.10 |

---

## 🔧 Solução de Problemas

### Erro: "CUDA out of memory"

```bash
# Use CPU
export CUDA_VISIBLE_DEVICES=""
python ai_cover_app.py
```

### Erro: "Model not found"

- Verifique se o modelo está em `models/`
- Extensão deve ser `.pth`

### Áudio com qualidade baixa

- Use áudio de referência mais longo (5-10s)
- Áudio de referência deve ser limpo (sem música de fundo)
- Ajuste os volumes na mixagem

### Separação de vocais imperfeita

- Alguns instrumentos podem vazar para o vocal
- Músicas muito complexas podem ter resultados variados
- Considere usar modelo `htdemucs_ft` para melhor qualidade

---

## 📄 Licença

Este projeto está licenciado sob a **Mozilla Public License 2.0** (MPL 2.0).

Baseado em:

- [Coqui TTS](https://github.com/coqui-ai/TTS) - Síntese de voz
- [Demucs](https://github.com/facebookresearch/demucs) - Separação de áudio
- [RVC](https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI) - Conversão de voz

---

<div align="center">

**Desenvolvido com ❤️ por Professor Davi Antonino Nunes da Silva**

📞 (16) 99260-4315 | 📧 <professordavi85@gmail.com>

</div>
