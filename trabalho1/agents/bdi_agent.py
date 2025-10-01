from .base_vacuum_agent import BaseVacuumAgent
from model import Acoes, Tipo_sujeira

class BDIAgent(BaseVacuumAgent):
    """Agente BDI: Crenças (modelo), Desejos (priorizar alta pontuação), Intenções (plano curto)."""
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.beliefs = {}  # pos -> info
        self.desires = []  # (pos, points)
        self.intentions = []  # lista de ações

    def update_beliefs(self, perc):
        

    def select_desire(self):
        
    def plan_intention(self, target):
        

    def step(self):
       