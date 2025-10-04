import random
from .base_vacuum_agent import BaseVacuumAgent
from environment import ACTIONS

class GoalBasedAgent(BaseVacuumAgent):
    """Agente Baseado em Objetivos: planeja para sujeiras conhecidas."""
    def __init__(self, env):
        super().__init__(env)
        self.goals = []  # Lista de posições com sujeira
