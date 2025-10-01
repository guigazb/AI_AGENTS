from .base_vacuum_agent import BaseVacuumAgent
from model import Tipo_sujeira

class UtilityBasedAgent(BaseVacuumAgent):
    """Agente Baseado em Utilidade: maximiza utilidade (pontos / custo de energia)."""
    def step(self):
        if self.energy <= 0 or self.stopped:
            return
        perc = self.perceive()
        # Calcula utilidade para cada ação possível
        options = []
        if perc['center']['dirt']:
            dirt_points = sum(Tipo_sujeira[t] for t in perc['center']['dirt_type'])
            utility = dirt_points / 2.0  # custo 2
            options.append(('ASPIRAR', utility))
        for d in ['N', 'S', 'L', 'O']:
            if d in perc and not perc[d]['obstacle']:
                move_utility = 0
                if perc[d]['dirt']:
                    move_utility += sum(Tipo_sujeira[t] for t in perc[d]['dirt_type']) / 3.0  # estimado: move(1) + vacuum(2)
                else:
                    move_utility = 0.1  # pequeno incentivo para explorar
                options.append((d, move_utility))
        if not options:
            self.stop()
            return
        # Escolhe ação com max utilidade
        best_action, _ = max(options, key=lambda x: x[1])
        if best_action == 'ASPIRAR':
            self.vacuum()
        else:
            self.move(best_action)