import mesa

class BaseVacuumAgent(mesa.Agent):
    """Classe base para todos os agentes aspiradores."""
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.energy = 30
        self.points_collected = 0
        self.stopped = False

    def perceive(self):
        """Percepção: célula atual + 4 vizinhas + posição."""
        from model import Acoes  # Importa de model.py
        x, y = self.pos
        perception = {'position': (x, y), 'center': {'dirt': False, 'obstacle': False, 'dirt_type': []}}
        directions = {'N': (-1, 0), 'S': (1, 0), 'L': (0, 1), 'O': (0, -1)}
        contents = self.model.grid.get_cell_list_contents((x, y))
        perception['center']['dirt'] = any(isinstance(a, Dirt) for a in contents)
        perception['center']['obstacle'] = any(isinstance(a, Obstacle) for a in contents)
        perception['center']['dirt_type'] = [a.dirt_type for a in contents if isinstance(a, Dirt)]
        
        for dir_name, (dx, dy) in directions.items():
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.model.grid.width and 0 <= ny < self.model.grid.height:
                contents = self.model.grid.get_cell_list_contents((nx, ny))
                has_dirt = any(isinstance(a, Dirt) for a in contents)
                has_obstacle = any(isinstance(a, Obstacle) for a in contents)
                perception[dir_name] = {
                    'dirt': has_dirt,
                    'obstacle': has_obstacle,
                    'dirt_type': [a.dirt_type for a in contents if isinstance(a, Dirt)]
                }
            else:
                perception[dir_name] = {'dirt': False, 'obstacle': True, 'dirt_type': []}  # Bordas como obstáculos
        return perception

    def move(self, direction):
        """Mover para uma direção, se possível."""
        from model import Acoes
        dx, dy = Acoes[direction]
        nx, ny = self.pos[0] + dx, self.pos[1] + dy
        contents = self.model.grid.get_cell_list_contents((nx, ny))
        if not any(isinstance(a, Obstacle) for a in contents):
            self.model.grid.move_agent(self, (nx, ny))
            self.energy -= 1

    def vacuum(self):
        """Aspirar a célula atual."""
        contents = self.model.grid.get_cell_list_contents(self.pos)
        for agent in contents[:]:
            if isinstance(agent, Dirt):
                self.points_collected += agent.points
                self.model.grid.remove_agent(agent)
                self.model.schedule.remove(agent)
        self.energy -= 2

    def stop(self):
        """Parar a execução."""
        self.stopped = True

    def step(self):
        """Método a ser sobrescrito pelos subtipos."""
        raise NotImplementedError