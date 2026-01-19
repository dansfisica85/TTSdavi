"""Mock do módulo trainer.torch"""

class NoamLR:
    """Mock para NoamLR scheduler"""
    def __init__(self, *args, **kwargs):
        pass
    
    def step(self, *args, **kwargs):
        pass
    
    def get_lr(self, *args, **kwargs):
        return [0.001]

class KeepAverage:
    """Mock para KeepAverage"""
    def __init__(self, *args, **kwargs):
        self.avg_value = 0.0
    
    def update(self, value):
        self.avg_value = value
    
    def value(self):
        return self.avg_value
