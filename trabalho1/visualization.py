import mesa.visualization
from model import Sujeira, Obstaculo, ModeloApirador
from agents import BaseVacuumAgent  # Para checar isinstance

def agent_portrayal(agent):
    """Função para desenhar os agentes no grid."""
    portrayal = {"Shape": "circle", "Filled": True, "r": 0.5}
    
    if isinstance(agent, BaseVacuumAgent):
        portrayal["Color"] = "blue"
        portrayal["Layer"] = 2  # Acima de sujeiras
        portrayal["r"] = 0.8
    elif isinstance(agent, Sujeira):
        if agent.dirt_type == 'Poeira':
            portrayal["Color"] = "lightgray"
        elif agent.dirt_type == 'Liquido':
            portrayal["Color"] = "lightblue"
        elif agent.dirt_type == 'Detritos':
            portrayal["Color"] = "brown"
        portrayal["Layer"] = 1
        portrayal["r"] = 0.4
    elif isinstance(agent, Obstaculo):
        portrayal["Color"] = "black"
        portrayal["Layer"] = 0
        portrayal["Shape"] = "rect"
        portrayal["w"] = 1
        portrayal["h"] = 1
    else:
        portrayal = None  # Célula vazia
    
    return portrayal

def launch_server(agent_class):
    """Lança o servidor de visualização para um agente específico."""
    grid = mesa.visualization.CanvasGrid(agent_portrayal, 5, 5, 500, 500)
    server = mesa.visualization.ModularServer(
        ModeloApirador,
        [grid],
        "Robô Aspirador Inteligente",
        {"agent_class": agent_class}
    )
    server.port = 8521  # Porta padrão
    server.launch()