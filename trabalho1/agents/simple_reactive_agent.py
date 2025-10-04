import random
from .base_vacuum_agent import BaseVacuumAgent

class SimpleReactiveAgent(BaseVacuumAgent):
    """Agente Reativo Simples: reage apenas à percepção atual."""
    def step(self):
        if self.energy <= 0 or self.stopped:
            return
        perc = self.perceive()
        if perc['center']['dirt']:
            self.vacuum()
        else:
            dirty_dirs = [d for d, info in perc.items() if d in ['N', 'S', 'L', 'O'] and info['dirt']]
            if dirty_dirs:
                self.move(random.choice(dirty_dirs))
            else:
                possible_moves = [d for d, info in perc.items() if d in ['N', 'S', 'L', 'O'] and not info['obstacle']]
                if possible_moves:
                    self.move(random.choice(possible_moves))
                else:
                    self.stop()