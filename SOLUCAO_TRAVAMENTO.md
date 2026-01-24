# 🎵 SOLUÇÃO: Progresso Travado em 10% na Separação de Áudio

Se o progresso fica em 10% ao tentar separar vocais e instrumentais, aqui estão as soluções:

## ✅ O QUE FOI CORRIGIDO

Atualizamos o `audio_separator.py` para:
- ✓ Mostrar **progresso contínuo** durante o processamento (não mais travado em 10%)
- ✓ Tratar **erro de falta de memória** com fallback automático
- ✓ Melhorar **mensagens de erro** com dicas úteis

## 🔧 COMO USAR

### 1. Atualizar a aplicação
```bash
cd /workspaces/TTSdavi
git pull origin dev  # ou seu branch
```

### 2. Verificar o ambiente
```bash
python diagnostico_separacao.py
```

Isso vai verificar:
- ✓ Dependências instaladas
- ✓ Memória disponível
- ✓ GPU (se disponível)
- ✓ Carregamento do modelo Demucs
- ✓ Processamento básico

## 🆘 SE AINDA ASSIM NÃO FUNCIONAR

### Problema 1: Travamento em "Carregando modelo"
**Solução:**
```bash
# Baixe o modelo manualmente
python -c "from demucs.pretrained import get_model; get_model('htdemucs')"
```

### Problema 2: Erro de "out of memory"
**Solução - Opção A (use CPU em vez de GPU):**
```bash
export CUDA_VISIBLE_DEVICES=""
# Agora execute a app (vai ser mais lento, mas vai funcionar)
```

**Solução - Opção B (use áudio mais curto):**
- Tente com um áudio < 30 segundos
- O Demucs consome bastante memória em áudios longos

### Problema 3: Velocidade muito lenta
**Solução:**
```bash
# Verifique se GPU está sendo usada
nvidia-smi  # se tiver GPU

# Se usar muita RAM/VRAM, reduza o tamanho do áudio
```

## 📊 SOLUÇÕES RÁPIDAS

| Problema | Solução |
|----------|---------|
| Travado em 10% | ✓ Já corrigido - agora mostra progresso contínuo |
| "Out of memory" | Use CPU: `export CUDA_VISIBLE_DEVICES=""` |
| Muito lento | Use áudio mais curto (< 30 seg) |
| Modelo não baixa | Execute: `python -c "from demucs.pretrained import get_model; get_model('htdemucs')"` |
| Arquivo inválido | Use WAV, FLAC ou OGG (não MP3) |

## 🚀 OTIMIZAÇÕES APLICADAS

### No `audio_separator.py`:
```python
def separar_audio(
    arquivo_entrada: str,
    diretorio_saida: Optional[str] = None,
    modelo: str = "htdemucs",
    progress_callback=None,  # ← NOVO: callback de progresso
) -> Tuple[str, str]:
    # Agora atualiza progresso em cada etapa:
    # 15% - Carregando modelo
    # 25% - Carregando áudio
    # 35% - Processando separação
    # 65% - Finalizando
    # 75% - Salvando arquivos
    # 95% - Concluindo
```

### No `ai_cover_app.py`:
```python
# Novo callback que mapeia progresso de 0.1 a 0.5
def progress_sep_callback(pct, msg):
    mapped_pct = 0.1 + (pct * 0.4)
    progress(mapped_pct, desc=f"✂️ {msg}")

vocal_path, instrumental_path = separar_audio(
    arquivo_musica,
    diretorio_saida=str(output_subdir),
    progress_callback=progress_sep_callback  # ← NOVO
)
```

## 📝 PRÓXIMOS PASSOS

1. Execute o diagnóstico: `python diagnostico_separacao.py`
2. Leia as recomendações
3. Tente novamente com a app
4. Se ainda falhar, compartilhe a saída do diagnóstico

---

**Desenvolvido por:** Professor Davi Antonino Nunes da Silva  
**Contato:** (16) 99260-4315 | professordavi85@gmail.com
