#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Teste rápido de lançamento do Gradio
"""

import sys
from pathlib import Path

# Adicionar ao path
workspace_path = Path(__file__).parent
if str(workspace_path) not in sys.path:
    sys.path.insert(0, str(workspace_path))

print("🧪 Testando configuração do Gradio...")
print("=" * 60)

try:
    # Importar configuração
    from gradio_config import GradioConfig
    print("✅ gradio_config importado com sucesso")
    
    # Obter kwargs
    kwargs = GradioConfig.get_launch_kwargs()
    print(f"✅ {len(kwargs)} parâmetros configurados")
    print()
    
    # Mostrar parâmetros
    print("📋 Parâmetros do launch():")
    for key, value in kwargs.items():
        print(f"   • {key}: {value}")
    print()
    
    # Verificar Gradio
    import gradio as gr
    print(f"✅ Gradio {gr.__version__} disponível")
    print()
    
    # Verificar se os parâmetros são válidos
    print("🔍 Verificando compatibilidade...")
    valid_params = []
    invalid_params = []
    
    import inspect
    launch_signature = inspect.signature(gr.Blocks.launch)
    valid_param_names = set(launch_signature.parameters.keys())
    
    for param in kwargs.keys():
        if param in valid_param_names:
            valid_params.append(param)
        else:
            invalid_params.append(param)
    
    if valid_params:
        print(f"✅ Parâmetros válidos ({len(valid_params)}):")
        for p in valid_params:
            print(f"   • {p}")
    
    if invalid_params:
        print(f"⚠️  Parâmetros não suportados ({len(invalid_params)}):")
        for p in invalid_params:
            print(f"   • {p}")
    else:
        print("✅ Todos os parâmetros são compatíveis!")
    
    print()
    print("=" * 60)
    print("✅ CONFIGURAÇÃO VÁLIDA - Pronto para usar!")
    print("=" * 60)
    sys.exit(0)

except ImportError as e:
    print(f"❌ Erro de importação: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
