import random
import copy
import time

# Tipos de sujeira e pontos
DIRT_TYPES = {
    'Poeira': 1,
    'Liquido': 2,
    'Detritos': 3
}

# Ações possíveis
ACTIONS = {
    'N': (-1, 0),  # Norte
    'S': (1, 0),   # Sul
    'L': (0, 1),   # Leste
    'O': (0, -1),  # Oeste
    'ASPIRAR': (0, 0),
    'PARAR': (0, 0)
}

class VacuumEnvironment:
    """Simula o ambiente 5x5."""
    def __init__(self, seed=42):
        random.seed(seed)
        self.grid = [[{'dirt': None, 'obstacle': False, 'agent': False} for _ in range(5)] for _ in range(5)]
        self.obstacle_positions = set()

        # Gerar 3 obstáculos
        while len(self.obstacle_positions) < 3:
            x, y = random.randrange(5), random.randrange(5)
            self.obstacle_positions.add((x, y))
        for x, y in self.obstacle_positions:
            self.grid[x][y]['obstacle'] = True

        # Gerar sujeiras (prob 0.6, não em obstáculos)
        self.total_dirt_cells = 0
        for x in range(5):
            for y in range(5):
                if (x, y) not in self.obstacle_positions and random.random() < 0.6:
                    dirt_type = random.choice(list(DIRT_TYPES.keys()))
                    self.grid[x][y]['dirt'] = dirt_type
                    self.total_dirt_cells += 1

        # Posição inicial do agente (não em obstáculo)
        while True:
            x, y = random.randrange(5), random.randrange(5)
            if (x, y) not in self.obstacle_positions:
                self.grid[x][y]['agent'] = True
                self.agent_pos = (x, y)
                break

    def get_cleaned_cells(self):
        cleaned = 0
        for x in range(5):
            for y in range(5):
                if self.grid[x][y]['dirt'] is None and not self.grid[x][y]['obstacle']:
                    cleaned += 1
        return cleaned

    def print_grid(self, agent_name):
        """Visualização simples no console com nome do agente."""
        symbols = {'Poeira': 'P', 'Liquido': 'L', 'Detritos': 'D'}
        print(f"Estado do Agente: {agent_name}")
        for row in self.grid:
            print(' '.join([
                'A' if cell['agent'] else symbols[cell['dirt']] if cell['dirt'] else 'X' if cell['obstacle'] else '.'
                for cell in row
            ]))
        print()