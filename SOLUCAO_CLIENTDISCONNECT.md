# Solução: Erro de ClientDisconnect no Gradio

## 🔍 Problema Identificado

O aplicativo estava recebendo erros `starlette.requests.ClientDisconnect` durante uploads de arquivos:

```
ERROR: Exception in ASGI application
starlette.requests.ClientDisconnect
  File "/usr/local/lib/python3.10/site-packages/gradio/routes.py", line 1169, in upload_file
    form = await multipart_parser.parse()
```

### Causas Raiz

1. **Timeout de Upload**: Arquivos grandes levavam muito tempo para fazer upload
2. **Desconexão de Proxy**: Railway/produção usa proxy reverso com timeouts padrão
3. **Falta de Validação**: Uploads inválidos causavam crashes
4. **Configuração Subótima**: Gradio não estava configurado para produção
5. **Sem Tratamento de Erro**: Desconexões não eram capturadas graciosamente

---

## ✅ Soluções Implementadas

### 1. **Arquivo: `gradio_config.py`** 
Configurações otimizadas para Gradio em produção:

```python
# Aumentar timeout de request
GRADIO_REQUEST_TIMEOUT = 600 segundos

# Buffer de upload aumentado
GRADIO_UPLOAD_BUFFER_SIZE = 10485760 bytes (10MB)

# Tamanho máximo de arquivo
MAX_FILE_SIZE_MB = 500

# Chunk size para upload
CHUNK_SIZE = 1048576 bytes (1MB)
```

**Variáveis de Ambiente Suportadas:**
- `GRADIO_REQUEST_TIMEOUT`: Timeout em segundos (padrão: 600)
- `MAX_FILE_SIZE_MB`: Tamanho máximo em MB (padrão: 500)
- `UPLOAD_TIMEOUT`: Timeout específico para uploads (padrão: 600)
- `CHUNK_SIZE`: Tamanho do chunk em bytes (padrão: 1MB)
- `GRADIO_SHARE`: Habilitar share link (padrão: true)

### 2. **Arquivo: `upload_handler.py`**
Handlers robusto para upload com:

✅ **Retry automático** para uploads falhados  
✅ **Validação de arquivo** (tipo, tamanho)  
✅ **Timeout com fallback**  
✅ **Tratamento de desconexão** gracioso  
✅ **Limpeza automática** de arquivos temporários  

**Funções principais:**

```python
# Validar arquivo antes do upload
is_valid, message = validate_upload(
    file_path="/caminho/arquivo.wav",
    allowed_extensions=(".wav", ".mp3", ".flac", ".ogg"),
    max_size_mb=500
)

# Sanitizar nomes de arquivo
safe_name = sanitize_filename(user_input)

# Limpar arquivos temporários
cleanup_temp_files(Path("/tmp/uploads"), max_age_hours=24)
```

### 3. **Integração no `ai_cover_app.py`**

Foram adicionadas:

✅ **Validação de upload** antes de processar  
✅ **Logging aprimorado** para debug  
✅ **Tratamento de erro** melhorado  
✅ **Configuração otimizada** de Gradio  

```python
# Novo código adicionado
from gradio_config import GradioConfig, setup_gradio_environment
from upload_handler import validate_upload

# Validação automática
is_valid, message = validate_upload(arquivo_musica)
if not is_valid:
    return None, message
```

---

## 🚀 Como Usar

### Instalação

1. Os novos arquivos já foram criados:
   - `/workspaces/TTSdavi/gradio_config.py`
   - `/workspaces/TTSdavi/upload_handler.py`

2. O `ai_cover_app.py` foi atualizado automaticamente.

### Executar o Aplicativo

```bash
# Com configuração automática
python ai_cover_app.py

# Com variáveis de ambiente customizadas
GRADIO_REQUEST_TIMEOUT=900 \
MAX_FILE_SIZE_MB=1000 \
GRADIO_SHARE=true \
python ai_cover_app.py
```

### Variáveis de Ambiente Úteis

```bash
# Aumentar timeout para uploads muito grandes
export GRADIO_REQUEST_TIMEOUT=1200

# Limitar tamanho de arquivo
export MAX_FILE_SIZE_MB=300

# Para desenvolvimento (desabilitar share)
export GRADIO_SHARE=false

# Aumentar verbosidade do log
export GRADIO_LOG_LEVEL=DEBUG
```

---

## 📊 Melhorias de Performance

| Aspecto | Antes | Depois |
|--------|-------|--------|
| Timeout de Request | Default (30s) | Configurável (600s+) |
| Tamanho Máximo | Não definido | 500MB configurável |
| Validação | Nenhuma | Antes do processamento |
| Tratamento de Erro | Crash | Gracioso com retry |
| Buffer de Upload | Pequeno | 10MB |
| Logging | Básico | Detalhado |

---

## 🔧 Troubleshooting

### Erro: "Arquivo muito grande"

**Solução:**
```bash
export MAX_FILE_SIZE_MB=1000
python ai_cover_app.py
```

### Erro: "Timeout na esperação de upload"

**Solução:**
```bash
export GRADIO_REQUEST_TIMEOUT=1200  # 20 minutos
python ai_cover_app.py
```

### Erro: "ClientDisconnect" continua

**Solução:**
1. Verificar conexão de rede
2. Tentar arquivo menor
3. Verificar logs:
```bash
GRADIO_LOG_LEVEL=DEBUG python ai_cover_app.py
```

### Erro: "Porta 7860 já em uso"

**Solução:**
```bash
export PORT=8080
python ai_cover_app.py
```

---

## 📝 Logging

O aplicativo agora registra detalhes úteis:

```
2026-01-19 10:58:00 - INFO - 🌐 Iniciando servidor em 0.0.0.0:8080
2026-01-19 10:59:00 - INFO - ✓ Upload bem-sucedido: audio.wav
2026-01-19 11:00:00 - WARNING - ⚠️ Cliente desconectou
2026-01-19 11:01:00 - ERROR - ❌ Falha final após 3 tentativas
```

Visualizar logs:
```bash
python ai_cover_app.py 2>&1 | tee server.log
```

---

## 🛡️ Segurança

As validações adicionadas protegem contra:

- ✅ Upload de arquivos malformados
- ✅ Arquivos muito grandes (DDoS)
- ✅ Nomes de arquivo maliciosos
- ✅ Path traversal
- ✅ Consumo infinito de memória

---

## 📦 Dependências

Nenhuma dependência nova foi adicionada. O código usa apenas:

- `pathlib` (built-in)
- `os` (built-in)
- `asyncio` (built-in)
- `logging` (built-in)
- `gradio` (já instalado)

---

## 🎯 Próximas Melhorias Sugeridas

1. **Resumable Uploads**: Permitir retomar uploads interrompidos
2. **Métricas**: Coletar dados de uploads bem-sucedidos/falhados
3. **Rate Limiting**: Limitar upload por IP/usuário
4. **Compressão**: Aceitar arquivos comprimidos
5. **Preview**: Mostrar preview antes do processamento

---

## 📞 Suporte

Para problemas:

1. Verificar logs: `GRADIO_LOG_LEVEL=DEBUG python ai_cover_app.py`
2. Validar arquivo: `ffprobe audio.wav`
3. Testar conexão: `curl -I https://seu-app.railway.app`
4. Abrir issue no GitHub

---

**Atualizado:** 2026-01-19  
**Versão:** 2.0 (com tratamento robusto de upload)
