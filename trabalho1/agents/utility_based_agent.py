from .base_vacuum_agent import BaseVacuumAgent
from environment import DIRT_TYPES

class UtilityBasedAgent(BaseVacuumAgent):
    """Agente Baseado em Utilidade: maximiza pontos / custo."""
    def step(self):
        if self.energy <= 0 or self.stopped:
            return
        perc = self.perceive()
        options = []
        if perc['center']['dirt']:
            dirt_points = sum(DIRT_TYPES[t] for t in perc['center']['dirt_type'])
            utility = dirt_points / 2.0
            options.append(('ASPIRAR', utility))
        for d in ['N', 'S', 'L', 'O']:
            if not perc[d]['obstacle']:
                move_utility = 0
                if perc[d]['dirt']:
                    move_utility += sum(DIRT_TYPES[t] for t in perc[d]['dirt_type']) / 3.0
                else:
                    move_utility = 0.1
                options.append((d, move_utility))
        if not options:
            self.stop()
            return
        best_action, _ = max(options, key=lambda x: x[1])
        if best_action == 'ASPIRAR':
            self.vacuum()
        else:
            self.move(best_action)