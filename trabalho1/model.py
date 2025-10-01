import random
import mesa

# Tipos de sujeira e pontos
Tipo_sujeira = {
    'Poeira': 1,
    'Liquido': 2,
    'Detritos': 3
}

# Ações possíveis
Acoes = {
    'N': (-1, 0),  # Norte
    'S': (1, 0),   # Sul
    'L': (0, 1),   # Leste
    'O': (0, -1),  # Oeste
    'ASPIRAR': None,
    'PARAR': None
}

class Sujeira(mesa.Agent):
    """Agente passivo representando sujeira."""
    def __init__(self, unique_id, model, dirt_type):
        super().__init__(unique_id, model)
        self.dirt_type = dirt_type
        self.points = Tipo_sujeira[dirt_type]

class Obstaculo(mesa.Agent):
    """Agente passivo representando obstáculo."""
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

class ModeloApirador(mesa.Model):
    """Modelo do ambiente."""
    def __init__(self, agent_class, seed=42):
        self.random = random.Random(seed)  # Para reproducibilidade
        super().__init__(seed=seed)
        self.grid = mesa.space.MultiGrid(5, 5, torus=False)
        self.schedule = mesa.time.RandomActivation(self)

        # Gerar obstáculos (ex: 3 aleatórios)
        obstacle_positions = []
        for _ in range(3):
            while True:
                x, y = self.random.randrange(5), self.random.randrange(5)
                if (x, y) not in obstacle_positions:
                    obs = Obstaculo(self.next_id(), self)
                    self.grid.position_agent(obs, (x, y))
                    obstacle_positions.append((x, y))
                    break

        # Gerar sujeiras (prob 0.6 por célula, mas não em obstáculos)
        for x in range(5):
            for y in range(5):
                if (x, y) not in obstacle_positions and self.random.random() < 0.6:
                    dirt_type = self.random.choice(list(Tipo_sujeira.keys()))
                    dirt = Sujeira(self.next_id(), self, dirt_type)
                    self.grid.position_agent(dirt, (x, y))

        # Colocar agente em posição aleatória sem obstáculo
        while True:
            x, y = self.random.randrange(5), self.random.randrange(5)
            if (x, y) not in obstacle_positions:
                self.agent = agent_class(self.next_id(), self)
                self.grid.position_agent(self.agent, (x, y))
                self.schedule.add(self.agent)
                break

    def step(self):
        if self.agent.energy > 0 and not self.agent.stopped:
            self.schedule.step()

    def run_simulation(self):
        steps = 0
        while self.agent.energy > 0 and not self.agent.stopped:
            self.step()
            steps += 1
        dirt_agents = [a for a in self.schedule.agents if isinstance(a, Sujeira)]
        return {
            'points': self.agent.points_collected,
            'energy_left': self.agent.energy,
            'steps': steps,
            'cleaned_cells': 25 - len(dirt_agents)
        }