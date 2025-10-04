import random
from environment import ACTIONS, DIRT_TYPES

class BaseVacuumAgent:
    """Classe base para todos os agentes aspiradores."""
    def __init__(self, env):
        self.env = env
        self.energy = 30
        self.points_collected = 0
        self.stopped = False
        self.pos = env.agent_pos

    def perceive(self):
        """Percepção: célula atual + 4 vizinhas + posição."""
        x, y = self.pos
        perception = {'position': (x, y)}
        directions = [('center', (0, 0))]
        for dir_name, (dx, dy) in ACTIONS.items():
            if dir_name in ['ASPIRAR', 'PARAR']:
                continue
            directions.append((dir_name, (dx, dy)))

        for dir_name, (dx, dy) in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < 5 and 0 <= ny < 5:
                cell = self.env.grid[nx][ny]
                has_dirt = cell['dirt'] is not None
                has_obstacle = cell['obstacle']
                dirt_type = [cell['dirt']] if has_dirt else []
                perception[dir_name] = {
                    'dirt': has_dirt,
                    'obstacle': has_obstacle,
                    'dirt_type': dirt_type
                }
            else:
                perception[dir_name] = {'dirt': False, 'obstacle': True, 'dirt_type': []}
        return perception

    def move(self, direction):
        """Mover para uma direção, se possível."""
        dx, dy = ACTIONS[direction]
        nx, ny = self.pos[0] + dx, self.pos[1] + dy
        if 0 <= nx < 5 and 0 <= ny < 5 and not self.env.grid[nx][ny]['obstacle']:
            self.env.grid[self.pos[0]][self.pos[1]]['agent'] = False
            self.pos = (nx, ny)
            self.env.grid[nx][ny]['agent'] = True
            self.energy -= 1

    def vacuum(self):
        """Aspirar a célula atual."""
        cell = self.env.grid[self.pos[0]][self.pos[1]]
        if cell['dirt']:
            self.points_collected += DIRT_TYPES[cell['dirt']]
            cell['dirt'] = None
            self.energy -= 2

    def stop(self):
        """Parar a execução."""
        self.stopped = True

    def step(self):
        """Método a ser sobrescrito pelos subtipos."""
        raise NotImplementedError