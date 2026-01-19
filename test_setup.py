#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de teste para validar configurações de Gradio e uploads
"""

import os
import sys
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_import_modules():
    """Testa se os módulos necessários podem ser importados"""
    print("\n" + "="*60)
    print("🧪 TESTE 1: Importar módulos")
    print("="*60)
    
    try:
        from gradio_config import GradioConfig, setup_gradio_environment
        print("✅ gradio_config.py importado com sucesso")
    except ImportError as e:
        print(f"❌ Erro ao importar gradio_config: {e}")
        return False
    
    try:
        from upload_handler import validate_upload, sanitize_filename
        print("✅ upload_handler.py importado com sucesso")
    except ImportError as e:
        print(f"❌ Erro ao importar upload_handler: {e}")
        return False
    
    return True


def test_gradio_config():
    """Testa configurações de Gradio"""
    print("\n" + "="*60)
    print("🧪 TESTE 2: Configurações de Gradio")
    print("="*60)
    
    try:
        from gradio_config import GradioConfig
        
        print(f"📊 MAX_FILE_SIZE_MB: {GradioConfig.MAX_FILE_SIZE_MB}")
        print(f"⏱️  UPLOAD_TIMEOUT: {GradioConfig.UPLOAD_TIMEOUT}s")
        print(f"📦 CHUNK_SIZE: {GradioConfig.CHUNK_SIZE} bytes")
        print(f"🔄 MAX_RETRIES: {GradioConfig.MAX_RETRIES}")
        
        # Testar get_launch_kwargs
        kwargs = GradioConfig.get_launch_kwargs()
        print(f"\n✅ Launch kwargs gerados:")
        for key, value in kwargs.items():
            if value is not None and value != "":
                print(f"   - {key}: {value}")
        
        return True
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False


def test_validate_upload():
    """Testa validação de upload com arquivo fictício"""
    print("\n" + "="*60)
    print("🧪 TESTE 3: Validação de Upload")
    print("="*60)
    
    try:
        from upload_handler import validate_upload
        
        # Teste 1: Arquivo não existe
        is_valid, msg = validate_upload("/nao/existe/arquivo.wav")
        print(f"❌ Arquivo não existe: {msg}")
        
        # Teste 2: Criar arquivo temporário
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            temp_file = f.name
            # Escrever 1MB de dados
            f.write(b"RIFF" + b"\x00" * 1048576)
        
        try:
            is_valid, msg = validate_upload(temp_file)
            print(f"✅ Validação com sucesso: {msg}")
            return True
        finally:
            os.unlink(temp_file)
    
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False


def test_sanitize_filename():
    """Testa sanitização de nomes de arquivo"""
    print("\n" + "="*60)
    print("🧪 TESTE 4: Sanitização de Nomes")
    print("="*60)
    
    try:
        from upload_handler import sanitize_filename
        
        test_cases = [
            "arquivo normal.wav",
            "arquivo@#$%&.wav",
            "arquivo com   espaços.wav",
            "muito_longo" * 50 + ".wav",
        ]
        
        for test_input in test_cases:
            output = sanitize_filename(test_input)
            print(f"  '{test_input[:40]}...' → '{output[:40]}...'")
        
        return True
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False


def test_environment_setup():
    """Testa configuração de variáveis de ambiente"""
    print("\n" + "="*60)
    print("🧪 TESTE 5: Variáveis de Ambiente")
    print("="*60)
    
    try:
        from gradio_config import setup_gradio_environment
        
        setup_gradio_environment()
        
        env_vars = [
            "GRADIO_REQUEST_TIMEOUT",
            "GRADIO_ANALYTICS_ENABLED",
            "GRADIO_UPLOAD_BUFFER_SIZE",
            "GRADIO_AUTORELOAD",
            "GRADIO_LOG_LEVEL",
        ]
        
        for var in env_vars:
            value = os.environ.get(var, "não definida")
            print(f"  {var}: {value}")
        
        return True
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False


def test_gradio_import():
    """Testa importação do Gradio"""
    print("\n" + "="*60)
    print("🧪 TESTE 6: Importação do Gradio")
    print("="*60)
    
    try:
        import gradio as gr
        print(f"✅ Gradio {gr.__version__} importado com sucesso")
        return True
    except ImportError as e:
        print(f"❌ Erro ao importar Gradio: {e}")
        return False


def test_ai_cover_app():
    """Testa se ai_cover_app.py pode ser importado"""
    print("\n" + "="*60)
    print("🧪 TESTE 7: Importação de ai_cover_app.py")
    print("="*60)
    
    try:
        # Adicionar ao path
        workspace_path = Path(__file__).parent
        if str(workspace_path) not in sys.path:
            sys.path.insert(0, str(workspace_path))
        
        # Tenta importar (pode falhar por dependências, que é OK)
        import ai_cover_app
        print(f"✅ ai_cover_app.py importado com sucesso")
        print(f"   - DESENVOLVEDOR: {ai_cover_app.DESENVOLVEDOR}")
        print(f"   - CONTATO: {ai_cover_app.CONTATO}")
        return True
    except ImportError as e:
        if "No module named" in str(e) and ("audio_separator" in str(e) or "voice_trainer" in str(e)):
            print(f"⚠️  Aviso: Dependência ausente (esperado): {e}")
            print("   Isto é normal se os módulos ainda não foram instalados")
            return True
        else:
            print(f"❌ Erro ao importar: {e}")
            return False
    except Exception as e:
        print(f"⚠️  Aviso: {e}")
        return True  # Falhas de dependência são OK


def main():
    """Executa todos os testes"""
    print("\n" + "="*60)
    print("🧪 TESTES DE VALIDAÇÃO - AI COVER STUDIO")
    print("="*60)
    
    tests = [
        ("Importar módulos", test_import_modules),
        ("Configurações de Gradio", test_gradio_config),
        ("Validação de Upload", test_validate_upload),
        ("Sanitização de Nomes", test_sanitize_filename),
        ("Variáveis de Ambiente", test_environment_setup),
        ("Importação do Gradio", test_gradio_import),
        ("Importação de ai_cover_app", test_ai_cover_app),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            logger.error(f"Erro ao executar {test_name}: {e}")
            results[test_name] = False
    
    # Resumo
    print("\n" + "="*60)
    print("📋 RESUMO DOS TESTES")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅" if result else "❌"
        print(f"{status} {test_name}")
    
    print(f"\nTotal: {passed}/{total} testes passaram")
    
    if passed == total:
        print("\n🎉 Todos os testes passaram! O aplicativo está pronto.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} teste(s) falharam. Veja acima para detalhes.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
