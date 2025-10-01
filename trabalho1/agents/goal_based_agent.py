import random
from .base_vacuum_agent import BaseVacuumAgent
from model import Acoes

class GoalBasedAgent(BaseVacuumAgent):
    """Agente Baseado em Objetivos: tem objetivo de limpar tudo, planeja caminho para sujeiras."""
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.goals = []  # Lista de posições com sujeira conhecidas

    def step(self):
        