import random
from .base_vacuum_agent import BaseVacuumAgent
from model import Acoes  # Para usar em update_model

class ModelBasedAgent(BaseVacuumAgent):
    """Agente Baseado em Modelo: mantém um modelo interno do mundo (visitados e conhecidos)."""
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.world_model = {}  # Dict de posições: {'dirt': bool, 'obstacle': bool, 'visited': bool}

    def update_model(self, perc):
        

    def step(self):
        