"""
Mock do pacote trainer para permitir inferência sem o pacote real.
Este módulo é usado quando o pacote trainer não está instalado (ex: Python 3.12+)
"""

class TrainerConfig:
    """Mock da configuração do Trainer"""
    def __init__(self, *args, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

class TrainerModel:
    """Mock do modelo base do Trainer"""
    pass

class Trainer:
    """Mock do Trainer"""
    def __init__(self, *args, **kwargs):
        raise NotImplementedError("Trainer não disponível. Use Python 3.11 ou anterior para treinamento.")

class TrainerArgs:
    """Mock dos argumentos do Trainer"""
    def __init__(self, *args, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

def get_last_checkpoint(*args, **kwargs):
    """Mock da função get_last_checkpoint"""
    return None

# Submodule torch mock
class _TorchMock:
    """Mock para trainer.torch"""
    @staticmethod
    def NoamLR(*args, **kwargs):
        pass
    
    class KeepAverage:
        pass

torch = _TorchMock()
