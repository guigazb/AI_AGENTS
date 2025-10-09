import random
from collections import deque
from .base_vacuum_agent import BaseVacuumAgent
from environment import ACTIONS, DIRT_TYPES

acoes_possiveis = {k: v for k, v in ACTIONS.items() if k not in ('ASPIRAR', 'PARAR')}

class GoalBasedAgent(BaseVacuumAgent):
    def __init__(self, env, perception_radius=1):
        super().__init__(env)
        self.perception_radius = perception_radius
        self.known_map = {}
        self.current_plan = []
        self._perceive_and_update()

    def _perceive(self):
        try:
            p = self.perceive()
            if isinstance(p, dict) and 'position' in p and 'center' in p:
                return p
        except Exception:
            pass
        x0, y0 = self.pos
        perc = {'position': (x0, y0), 'center': {'dirt': self.env.grid[x0][y0].get('dirt'),
                                                  'obstacle': bool(self.env.grid[x0][y0].get('obstacle'))}}
        for name, (dx, dy) in acoes_possiveis.items():
            nx, ny = x0 + dx, y0 + dy
            if 0 <= nx < len(self.env.grid) and 0 <= ny < len(self.env.grid[0]):
                c = self.env.grid[nx][ny]
                perc[name] = {'dirt': c.get('dirt'), 'obstacle': bool(c.get('obstacle'))}
            else:
                perc[name] = {'dirt': None, 'obstacle': True}
        return perc

    def _perceive_and_update(self):
        p = self._perceive()
        if not p:
            return
        px, py = p['position']
        r = self.perception_radius
        for dx in range(-r, r+1):
            for dy in range(-r, r+1):
                nx, ny = px+dx, py+dy
                if not (0 <= nx < len(self.env.grid) and 0 <= ny < len(self.env.grid[0])):
                    continue
                cell = self.env.grid[nx][ny]
                self.known_map[(nx, ny)] = {
                    'dirt': cell.get('dirt'),
                    'obstacle': bool(cell.get('obstacle')),
                    'visited': self.known_map.get((nx, ny), {}).get('visited', False)
                }
        self.known_map.setdefault((px, py), {'dirt': None, 'obstacle': False, 'visited': True})
        self.known_map[(px, py)]['visited'] = True
        self.pos = p.get('position', self.pos)

    def _bfs(self, start, goal):
        sx, sy = start; gx, gy = goal
        max_x, max_y = len(self.env.grid), len(self.env.grid[0])
        q = deque([start]); parent = {start: None}
        while q:
            x, y = q.popleft()
            if (x, y) == (gx, gy):
                path = []
                cur = (x, y)
                while cur is not None:
                    path.append(cur)
                    cur = parent[cur]
                path.reverse()
                return path
            for dx, dy in acoes_possiveis.values():
                nx, ny = x+dx, y+dy
                if not (0 <= nx < max_x and 0 <= ny < max_y):
                    continue
                if (nx, ny) in parent:
                    continue
                known = self.known_map.get((nx, ny))
                if known and known.get('obstacle'):
                    continue
                parent[(nx, ny)] = (x, y)
                q.append((nx, ny))
        return None

    def _pos_to_action(self, a, b):
        dx, dy = b[0]-a[0], b[1]-a[1]
        for name, (adx, ady) in acoes_possiveis.items():
            if (dx, dy) == (adx, ady):
                return name
        return None

    def _known_dirt_positions(self):
        return [pos for pos, info in self.known_map.items() if info.get('dirt')]

    def step(self):
        if self.energy <= 0 or self.stopped:
            return

        self._perceive_and_update()

        cx, cy = self.pos
        if self.env.grid[cx][cy].get('dirt'):
            self.vacuum()
            return

        if self.current_plan:
            target = self.current_plan[-1] if len(self.current_plan) else None
            if target and (target in self.known_map) and (not self.known_map[target].get('dirt')):
                self.current_plan = []

        if not self.current_plan:
            dirt_pos = self._known_dirt_positions()
            best = None; best_path = None
            for d in dirt_pos:
                path = self._bfs(self.pos, d)
                if not path:
                    continue
                if best_path is None or len(path) < len(best_path) or (len(path) == len(best_path) and DIRT_TYPES.get(self.known_map[d]['dirt'],0) > DIRT_TYPES.get(self.known_map.get(best,{}).get('dirt',None),0)):
                    best_path = path; best = d
            if best_path:
                self.current_plan = best_path
            else:
                possible=[]; unvisited=[]
                max_x, max_y = len(self.env.grid), len(self.env.grid[0])
                for name, (dx, dy) in acoes_possiveis.items():
                    nx, ny = cx+dx, cy+dy
                    if not (0 <= nx < max_x and 0 <= ny < max_y):
                        continue
                    known = self.known_map.get((nx, ny))
                    if known and known.get('obstacle'):
                        continue
                    possible.append((name,(nx,ny)))
                    if not known or not known.get('visited'):
                        unvisited.append((name,(nx,ny)))
                if unvisited:
                    choice = random.choice(unvisited)
                    act = choice[0]
                    moved = self.move(act)
                    if not moved:
                        self.known_map.setdefault(choice[1], {'dirt': None, 'obstacle': True, 'visited': False})['obstacle'] = True
                    return
                if possible:
                    choice = random.choice(possible)
                    act = choice[0]
                    moved = self.move(act)
                    if not moved:
                        self.known_map.setdefault(choice[1], {'dirt': None, 'obstacle': True, 'visited': False})['obstacle'] = True
                    return
                self.stop()
                return

        if self.current_plan and len(self.current_plan) >= 2:
            next_pos = self.current_plan[1]
            action = self._pos_to_action(self.pos, next_pos)
            if action:
                moved = self.move(action)
                if not moved:
                    self.known_map.setdefault(next_pos, {'dirt': None, 'obstacle': True, 'visited': False})['obstacle'] = True
                    self.current_plan = []
                else:
                    self.current_plan.pop(0)
            else:
                self.current_plan = []

    def __repr__(self):
        return f"<GoalBasedAgent pos={self.pos} energy={self.energy} points={self.points_collected}>"
