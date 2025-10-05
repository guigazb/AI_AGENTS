# agents/goal_based_agent.py
from collections import deque
from .base_vacuum_agent import BaseVacuumAgent
from environment import ACTIONS, DIRT_TYPES

# Ações espaciais (exclui ASPIRAR e PARAR)
SPATIAL_ACTIONS = {k: v for k, v in ACTIONS.items() if k not in ('ASPIRAR', 'PARAR')}

class GoalBasedAgent(BaseVacuumAgent):

    def __init__(self, env, perception_radius=1):
        super().__init__(env)
        self.perception_radius = perception_radius

        self.known_map = {}
        self.current_plan = [] 
        self.current_target = None

        self._perceive_local()

    def _in_bounds(self, x, y):
        max_x = len(self.env.grid)
        max_y = len(self.env.grid[0])
        return 0 <= x < max_x and 0 <= y < max_y

    def _perceive_local(self):
        x0, y0 = self.pos
        r = self.perception_radius
        for dx in range(-r, r+1):
            for dy in range(-r, r+1):
                nx, ny = x0 + dx, y0 + dy
                if not self._in_bounds(nx, ny):
                    continue
                cell = self.env.grid[nx][ny]
                self.known_map[(nx, ny)] = {
                    'dirt': cell.get('dirt'),
                    'obstacle': bool(cell.get('obstacle')),
                    'visited': self.known_map.get((nx, ny), {}).get('visited', False)
                }
        # marca a posição do agente como visitada
        if (x0, y0) in self.known_map:
            self.known_map[(x0, y0)]['visited'] = True
        else:
            self.known_map[(x0, y0)] = {'dirt': self.env.grid[x0][y0].get('dirt'),
                                        'obstacle': bool(self.env.grid[x0][y0].get('obstacle')),
                                        'visited': True}

    def _known_dirt_positions(self):
        res = []
        for (x, y), info in self.known_map.items():
            if info.get('dirt'):
                res.append((x, y, info['dirt']))
        return res

    # metodo de decisão do melhor caminho
    def _bfs_shortest_path(self, start, goal):

        max_x = len(self.env.grid)
        max_y = len(self.env.grid[0])
        sx, sy = start
        gx, gy = goal

        visited = set()
        parent = {}
        q = deque()
        q.append((sx, sy))
        visited.add((sx, sy))

        while q:
            x, y = q.popleft()
            if (x, y) == (gx, gy):
                # reconstruir ações
                actions = []
                cur = (x, y)
                while cur != (sx, sy):
                    px, py, act = parent[cur]
                    actions.append(act)
                    cur = (px, py)
                actions.reverse()
                return actions

            for act_name, (dx, dy) in SPATIAL_ACTIONS.items():
                nx, ny = x + dx, y + dy
                if not (0 <= nx < max_x and 0 <= ny < max_y):
                    continue
                if (nx, ny) in visited:
                    continue
                if (nx, ny) in self.known_map and self.known_map[(nx, ny)].get('obstacle'):
                    continue
                visited.add((nx, ny))
                parent[(nx, ny)] = (x, y, act_name)
                q.append((nx, ny))
        return None

    def _choose_best_known_dirt(self):

        known_dirt = self._known_dirt_positions()
        if not known_dirt:
            return (None, None)

        best = None
        best_score = -1
        best_plan = None

        for gx, gy, dirt_type in known_dirt:
            plan = self._bfs_shortest_path(self.pos, (gx, gy))
            if plan is None:
                continue
            move_cost = len(plan)
            vacuum_cost = 2
            total_cost = move_cost + vacuum_cost
            if total_cost > self.energy:
                continue
            value = DIRT_TYPES[dirt_type]
            score = value / total_cost
            if score > best_score or (score == best_score and value > (DIRT_TYPES.get(best[2]) if best else -1)):
                best_score = score
                best = (gx, gy, dirt_type)
                best_plan = plan

        if best is None:
            return (None, None)
        return (best, best_plan)

    def _find_nearest_unseen(self):

        max_x = len(self.env.grid)
        max_y = len(self.env.grid[0])

        sx, sy = self.pos
        visited = set()
        parent = {}
        q = deque()
        q.append((sx, sy))
        visited.add((sx, sy))

        while q:
            x, y = q.popleft()
            for act_name, (dx, dy) in SPATIAL_ACTIONS.items():
                nx, ny = x + dx, y + dy
                if not (0 <= nx < max_x and 0 <= ny < max_y):
                    continue
                if (nx, ny) not in self.known_map:
                    actions = []
                    cur = (x, y)
                    while cur != (sx, sy):
                        px, py, act = parent[cur]
                        actions.append(act)
                        cur = (px, py)
                    actions.reverse()
                    return actions
                if (nx, ny) in visited:
                    continue
                if (nx, ny) in self.known_map and self.known_map[(nx, ny)].get('obstacle'):
                    continue
                visited.add((nx, ny))
                parent[(nx, ny)] = (x, y, act_name)
                q.append((nx, ny))
        return None

    def step(self):

        if self.energy <= 0:
            self.stop()
            return

        self._perceive_local()

        cell = self.env.grid[self.pos[0]][self.pos[1]]
        if cell.get('dirt'):
            aspirou = self.vacuum()
            if not aspirou:
                return
            self._perceive_local()
            self.current_plan = []
            self.current_target = None
            return

        if self.current_plan and self.current_target:
            tx, ty, ttype = self.current_target
            if (tx, ty) in self.known_map and not self.known_map[(tx, ty)].get('dirt'):
                self.current_plan = []
                self.current_target = None

        if not self.current_plan:
            target_info, plan = self._choose_best_known_dirt()
            if target_info is not None:
                self.current_target = target_info
                self.current_plan = plan
            else:
                plan = self._find_nearest_unseen()
                if plan:
                    if len(plan) <= self.energy:
                        self.current_target = None
                        self.current_plan = plan
                    else:
                        self.stop()
                        return
                else:
                    self.stop()
                    return

        if self.current_plan:
            est_remaining_cost = len(self.current_plan) + 2
            if self.energy < 1:
                self.stop()
                return

            next_action = self.current_plan.pop(0)
            moved = self.move(next_action)
            if not moved:
                self.current_plan = []
                self.current_target = None
                self._perceive_local()
                return


    def __repr__(self):
        return f"<GoalBasedAgent pos={self.pos} energy={self.energy} points={self.points_collected}>"
