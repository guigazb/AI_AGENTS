import copy
import random
import time
from environment import VacuumEnvironment
from agents import (
    SimpleReactiveAgent,
    ModelBasedAgent,
    GoalBasedAgent,
    UtilityBasedAgent,
    BDIAgent
)

def run_simulation(agent_class, agent_name, env, visualize=False, max_same_state=4):
    agent = agent_class(copy.deepcopy(env))  # Agente usa cópia
    steps = 0
    if visualize:
        print("Grid Inicial:")
        agent.env.print_grid(agent_name)  # Usa agent.env
    prev_sig = None
    same_sig_count = 0
    while agent.energy > 0 and not agent.stopped:
        agent.step()
        steps += 1
        try:
            sig = agent.state_signature()
        except Exception:

            sig = (agent.pos, agent.energy, agent.points_collected)

        if sig == prev_sig:
            same_sig_count += 1
        else:
            prev_sig = sig
            same_sig_count = 0
        if same_sig_count >= max_same_state:
            print(f"Estado inalterado, encerrando")
            agent.stop()
            break


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

def compare_agents(visualize=False, seed=50):
    agent_types = {
        'Reativo Simples': SimpleReactiveAgent,
        'Baseado em modelo': ModelBasedAgent,
        'Baseado em objetivos': GoalBasedAgent,
        'Baseado em utilidade': UtilityBasedAgent,
        'BDI': BDIAgent
    }
    base_env = VacuumEnvironment(seed)
    results = {}
    for name, cls in agent_types.items():
        results[name] = run_simulation(cls, name, base_env, visualize=visualize)
    print("Comparação de Desempenho:")
    for name, res in results.items():
        print(f"\n{name}:")
        print(f"  Pontos coletados: {res['points']}")
        print(f"  Energia restante: {res['energy_left']}")
        print(f"  Passos totais: {res['steps']}")
        print(f"  Células limpas: {res['cleaned_cells']}/25")

if __name__ == "__main__":
    compare_agents(visualize=True)  # Mude para False para execução rápida sem visualização