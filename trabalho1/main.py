import copy
import random
import time
from environment import VacuumEnvironment
# from agents import (
#    SimpleReactiveAgent,
#    ModelBasedAgent,
#    GoalBasedAgent,
#    UtilityBasedAgent,
#    BDIAgent
#)
from agents import (
    SimpleReactiveAgent
)

def run_simulation(agent_class, agent_name, seed=42, visualize=False):
    env_original = VacuumEnvironment(seed)  # Renomeei para clareza
    agent = agent_class(copy.deepcopy(env_original))  # Agente usa cópia
    steps = 0
    if visualize:
        print("Grid Inicial:")
        agent.env.print_grid(agent_name)  # Usa agent.env
    while agent.energy > 0 and not agent.stopped:
        agent.step()
        steps += 1
        if visualize:
            time.sleep(0.5)  # Delay para ver passos
            print(f"Passo {steps}: Agente {agent_name}, Energia {agent.energy}, Pontos {agent.points_collected}")
            agent.env.print_grid(agent_name)  # Usa agent.env
    return {
        'points': agent.points_collected,
        'energy_left': agent.energy,
        'steps': steps,
        'cleaned_cells': agent.env.get_cleaned_cells()  # Usa agent.env
    }

def compare_agents(visualize=False):
    #agent_types = {
    #    'Reativo Simples': SimpleReactiveAgent,
    #    'Baseado em Modelo': ModelBasedAgent,
    #    'Baseado em Objetivos': GoalBasedAgent,
    #    'Baseado em Utilidade': UtilityBasedAgent,
    #    'BDI': BDIAgent
    #}
    agent_types = {
        'Reativo Simples': SimpleReactiveAgent
    }
    results = {}
    for name, cls in agent_types.items():
        results[name] = run_simulation(cls, name, seed= random.randint(0, 1000), visualize=visualize)
    print("Comparação de Desempenho:")
    for name, res in results.items():
        print(f"\n{name}:")
        print(f"  Pontos coletados: {res['points']}")
        print(f"  Energia restante: {res['energy_left']}")
        print(f"  Passos totais: {res['steps']}")
        print(f"  Células limpas: {res['cleaned_cells']}/25")

if __name__ == "__main__":
    compare_agents(visualize=True)  # Mude para False para execução rápida sem visualização