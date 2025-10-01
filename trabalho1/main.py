import sys
from model import ModeloApirador
from agents import (
    SimpleReactiveAgent,
    ModelBasedAgent,
    GoalBasedAgent,
    UtilityBasedAgent,
    BDIAgent
)
from visualization import launch_server

CLASSES_AGENTE = {
    'SimpleReactiveAgent': SimpleReactiveAgent,
    'ModelBasedAgent': ModelBasedAgent,
    'GoalBasedAgent': GoalBasedAgent,
    'UtilityBasedAgent': UtilityBasedAgent,
    'BDIAgent': BDIAgent
}

def Compare_agentes():
    Resultados = {}
    for name, cls in CLASSES_AGENTE.items():
        model = ModeloApirador(cls, seed=42)
        Resultados[name] = model.run_simulation()
    print("Comparação de Desempenho:")
    for name, res in Resultados.items():
        print(f"\n{name}:")
        print(f"  Pontos coletados: {res['points']}")
        print(f"  Energia restante: {res['energy_left']}")
        print(f"  Passos totais: {res['steps']}")
        print(f"  Células limpas: {res['cleaned_cells']}/25")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--compare":
            Compare_agentes()
        elif sys.argv[1] == "--visualize" and len(sys.argv) > 2:
            agent_name = sys.argv[2]
            if agent_name in CLASSES_AGENTE:
                launch_server(CLASSES_AGENTE[agent_name])
            else:
                print(f"Agente inválido. Opções: {list(CLASSES_AGENTE.keys())}")
        else:
            print("Uso: python main.py --compare | --visualize <NomeDoAgente>")
    else:
        print("Uso: python main.py --compare | --visualize <NomeDoAgente>")