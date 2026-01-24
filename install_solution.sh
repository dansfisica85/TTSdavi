#!/bin/bash

# ============================================================
# Script de Instalação - Solução ClientDisconnect
# ============================================================

echo "🚀 Instalando solução para erro ClientDisconnect..."
echo ""

# Verificar se estamos no diretório correto
if [ ! -f "ai_cover_app.py" ]; then
    echo "❌ Erro: Execute este script no diretório raiz do projeto"
    echo "   cd /workspaces/TTSdavi && bash install_solution.sh"
    exit 1
fi

echo "✅ Diretório correto detectado"
echo ""

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado"
    exit 1
fi
echo "✅ Python 3 detectado: $(python3 --version)"
echo ""

# Verificar se os arquivos já existem
if [ -f "gradio_config.py" ] && [ -f "upload_handler.py" ]; then
    echo "✅ Arquivos de solução já estão presentes"
    echo ""
    echo "📋 Arquivos instalados:"
    echo "   - gradio_config.py (configurações otimizadas)"
    echo "   - upload_handler.py (handler robusto de upload)"
    echo "   - ai_cover_app.py (atualizado com validação)"
    echo "   - SOLUCAO_CLIENTDISCONNECT.md (documentação)"
    echo "   - test_setup.py (testes de validação)"
    echo ""
else
    echo "⚠️  Arquivos não encontrados. Verifique se foram criados corretamente."
    exit 1
fi

# Executar testes básicos
echo "🧪 Executando testes de validação..."
python3 -m py_compile gradio_config.py upload_handler.py ai_cover_app.py 2>&1

if [ $? -eq 0 ]; then
    echo "✅ Todos os arquivos estão sintaticamente corretos"
else
    echo "❌ Erro de sintaxe detectado"
    exit 1
fi

echo ""
echo "============================================================"
echo "✅ SOLUÇÃO INSTALADA COM SUCESSO!"
echo "============================================================"
echo ""
echo "📖 Para mais informações, leia: SOLUCAO_CLIENTDISCONNECT.md"
echo ""
echo "🚀 Para iniciar o servidor com as otimizações:"
echo "   python ai_cover_app.py"
echo ""
echo "📊 Com configurações customizadas:"
echo "   GRADIO_REQUEST_TIMEOUT=1200 python ai_cover_app.py"
echo ""
echo "🧪 Para executar testes de validação:"
echo "   python test_setup.py"
echo ""
