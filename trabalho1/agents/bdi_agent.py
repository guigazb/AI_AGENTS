import random
from .base_vacuum_agent import BaseVacuumAgent
from environment import ACTIONS, DIRT_TYPES

class BDIAgent(BaseVacuumAgent):
    """Agente BDI: Crenças, Desejos, Intenções."""
    def __init__(self, env):
        super().__init__(env)
        self.beliefs = {}  # pos -> info
        self.desires = []  # (pos, points)
        self.intentions = []  # lista de ações
