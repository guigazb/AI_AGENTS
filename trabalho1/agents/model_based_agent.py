import random
from .base_vacuum_agent import BaseVacuumAgent
from environment import ACTIONS

class ModelBasedAgent(BaseVacuumAgent):
    """Agente Baseado em Modelo: mantém um modelo interno do mundo."""
    def __init__(self, env):
        super().__init__(env)
        self.world_model = {}  # pos: {'dirt': bool, 'obstacle': bool, 'visited': bool}
