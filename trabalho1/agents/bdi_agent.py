import random
from collections import deque
from .base_vacuum_agent import BaseVacuumAgent
from environment import ACTIONS, DIRT_TYPES

acoes_possiveis = {k: v for k, v in ACTIONS.items() if k not in ('ASPIRAR', 'PARAR')}


class BDIAgent(BaseVacuumAgent):

    def __init__(self, env, perception_radius=1):
        super().__init__(env)
        self.perception_radius = perception_radius
        self.beliefs_known_map = {}
        self.intention_plan = []
        self.intention_target = None
        self.desire_priority = {'Detritos': 3, 'Liquido': 2, 'Poeira': 1}

        self.ASPIRAR_COST = 2
        self._perceive_and_update()

    def _perceive_and_update(self):
        px, py = self.pos
        r = self.perception_radius
        for dx in range(-r, r + 1):
            for dy in range(-r, r + 1):
                nx, ny = px + dx, py + dy
                if not (0 <= nx < len(self.env.grid) and 0 <= ny < len(self.env.grid[0])):
                    continue
                cell = self.env.grid[nx][ny]
                is_visited = self.beliefs_known_map.get((nx, ny), {}).get('visited', False)
                self.beliefs_known_map[(nx, ny)] = {
                    'dirt': cell.get('dirt'),
                    'obstacle': bool(cell.get('obstacle')),
                    'visited': is_visited
                }
        self.beliefs_known_map.setdefault(self.pos, {})['visited'] = True

    def _get_known_dirt_positions(self):
        return [pos for pos, info in self.beliefs_known_map.items() if info.get('dirt')]

    def _bfs(self, start, goal):
        if start == goal: return [start]
        q = deque([start])
        parent = {start: None}
        while q:
            pos = q.popleft()
            if pos == goal:
                path = []
                while pos is not None: path.append(pos); pos = parent[pos]
                path.reverse()
                return path
            x, y = pos
            for dx, dy in acoes_possiveis.values():
                next_pos = (x + dx, y + dy)
                if next_pos in parent: continue
                known_cell = self.beliefs_known_map.get(next_pos)
                if not known_cell or known_cell.get('obstacle'): continue
                parent[next_pos] = pos
                q.append(next_pos)
        return None

    def _find_path_to_nearest_unvisited(self):
        start = self.pos;
        q = deque([(start, [start])]);
        visited_bfs = {start}
        while q:
            (x, y), path = q.popleft()
            for dx, dy in acoes_possiveis.values():
                nx, ny = x + dx, y + dy
                if (nx, ny) not in self.beliefs_known_map:
                    if 0 <= nx < len(self.env.grid) and 0 <= ny < len(self.env.grid[0]): return path + [(nx, ny)]
                if (0 <= nx < len(self.env.grid) and 0 <= ny < len(self.env.grid[0])) and (nx, ny) not in visited_bfs:
                    if not self.beliefs_known_map.get((nx, ny), {}).get('obstacle'):
                        visited_bfs.add((nx, ny));
                        q.append(((nx, ny), path + [(nx, ny)]))
        return None

    def _pos_to_action(self, a, b):
        dx, dy = b[0] - a[0], b[1] - a[1]
        for name, (adx, ady) in acoes_possiveis.items():
            if (dx, dy) == (adx, ady): return name
        return None

    def _deliberate_on_desires(self):
        known_dirts = self._get_known_dirt_positions()
        best_option = {"path": None, "priority": -1, "cost": float('inf'), "target": None}
        for pos in known_dirts:
            path = self._bfs(self.pos, pos)
            if not path: continue
            move_cost = len(path) - 1;
            total_cost = move_cost + self.ASPIRAR_COST
            if total_cost > self.energy: continue
            dirt_type = self.beliefs_known_map[pos].get('dirt');
            priority = self.desire_priority.get(dirt_type, 0)
            if priority > best_option["priority"]:
                best_option.update({"path": path, "priority": priority, "cost": total_cost, "target": pos})
            elif priority == best_option["priority"] and total_cost < best_option["cost"]:
                best_option.update({"path": path, "cost": total_cost, "target": pos})
        return best_option["target"], best_option["path"]

    def step(self):
        if self.energy <= 0 or self.stopped: return

        self._perceive_and_update()
        if self.env.grid[self.pos[0]][self.pos[1]].get('dirt'):
            self.vacuum()
            self.intention_plan = [];
            self.intention_target = None
            return

        best_target, best_path = self._deliberate_on_desires()

        if not self.intention_plan or self.intention_target != best_target:
            self.intention_target = best_target
            self.intention_plan = best_path

        if not self.intention_plan:
            path = self._find_path_to_nearest_unvisited()
            if path:
                self.intention_plan = path
                self.intention_target = path[-1]
            else:
                self.stop()
                return

        if self.intention_plan and len(self.intention_plan) >= 2:
            next_pos = self.intention_plan[1]
            action = self._pos_to_action(self.pos, next_pos)
            if action:
                if not self.move(action):
                    self.beliefs_known_map.setdefault(next_pos, {})['obstacle'] = True
                    self.intention_plan = [];
                    self.intention_target = None
                else:
                    self.intention_plan.pop(0)
            else:
                self.intention_plan = [];
                self.intention_target = None

    def __repr__(self):
        return f"<BDIAgent pos={self.pos} energy={self.energy} points={self.points_collected}>"