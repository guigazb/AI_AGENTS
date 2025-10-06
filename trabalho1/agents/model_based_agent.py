import random
from collections import deque
from .base_vacuum_agent import BaseVacuumAgent
from environment import ACTIONS

acoes_possiveis = {k: v for k, v in ACTIONS.items() if k not in ('ASPIRAR', 'PARAR')}

class ModelBasedAgent(BaseVacuumAgent):
    def __init__(self, env):
        super().__init__(env)
        self.world_model = {}

    def _update_model(self, perc):
        if not perc:
            return
        px, py = perc.get('position', self.pos)
        center = perc.get('center', {})
        self.world_model.setdefault((px, py), {'dirt': None, 'obstacle': False, 'visited': True})
        self.world_model[(px, py)]['dirt'] = center.get('dirt')
        self.world_model[(px, py)]['obstacle'] = bool(center.get('obstacle', False))
        self.world_model[(px, py)]['visited'] = True
        for name, (dx, dy) in acoes_possiveis.items():
            nx, ny = px + dx, py + dy
            if 0 <= nx < len(self.env.grid) and 0 <= ny < len(self.env.grid[0]):
                info = perc.get(name)
                if info is None:
                    c = self.env.grid[nx][ny]
                    info = {'dirt': c.get('dirt'), 'obstacle': c.get('obstacle', False)}
                entry = self.world_model.setdefault((nx, ny), {'dirt': None, 'obstacle': False, 'visited': False})
                entry['dirt'] = info.get('dirt')
                entry['obstacle'] = bool(info.get('obstacle', False))

    def _bfs(self, start, goal):
        sx, sy = start; gx, gy = goal
        max_x, max_y = len(self.env.grid), len(self.env.grid[0])
        q = deque([start])
        parent = {start: None}
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
                nx, ny = x + dx, y + dy
                if not (0 <= nx < max_x and 0 <= ny < max_y):
                    continue
                if (nx, ny) in parent:
                    continue
                known = self.world_model.get((nx, ny))
                if known and known.get('obstacle'):
                    continue
                parent[(nx, ny)] = (x, y)
                q.append((nx, ny))
        return None

    def _pos_to_action(self, from_pos, to_pos):
        fx, fy = from_pos; tx, ty = to_pos
        dx, dy = tx - fx, ty - fy
        for name, (adx, ady) in acoes_possiveis.items():
            if (dx, dy) == (adx, ady):
                return name
        return None

    def _known_dirt(self):
        return [pos for pos, v in self.world_model.items() if v.get('dirt')]

    def step(self):
        if self.energy <= 0 or self.stopped:
            return

        try:
            perc = self.perceive()
        except Exception:
            perc = None

        if perc and 'position' in perc:
            self.pos = perc['position']
        self._update_model(perc)

        cell = self.env.grid[self.pos[0]][self.pos[1]]
        if cell.get('dirt'):
            self.vacuum()
            return
        dirt_positions = self._known_dirt()
        if dirt_positions:
            best_path = None
            for d in dirt_positions:
                path = self._bfs(self.pos, d)
                if path and (best_path is None or len(path) < len(best_path)):
                    best_path = path
            if best_path and len(best_path) >= 2:
                next_pos = best_path[1]
                act = self._pos_to_action(self.pos, next_pos)
                if act:
                    moved = self.move(act)
                    if not moved:
                        entry = self.world_model.setdefault(next_pos, {'dirt': None, 'obstacle': True, 'visited': False})
                        entry['obstacle'] = True
                    return
        possible = []
        unvisited = []
        max_x, max_y = len(self.env.grid), len(self.env.grid[0])
        for name, (dx, dy) in acoes_possiveis.items():
            nx, ny = self.pos[0] + dx, self.pos[1] + dy
            if not (0 <= nx < max_x and 0 <= ny < max_y):
                continue
            known = self.world_model.get((nx, ny))
            if known and known.get('obstacle'):
                continue
            possible.append(name)
            if not known or not known.get('visited'):
                unvisited.append(name)

        if unvisited:
            choice = random.choice(unvisited)
            moved = self.move(choice)
            if not moved:
                nx, ny = self.pos[0] + acoes_possiveis[choice][0], self.pos[1] + acoes_possiveis[choice][1]
                self.world_model.setdefault((nx, ny), {'dirt': None, 'obstacle': True, 'visited': False})['obstacle'] = True
            return

        if possible:
            choice = random.choice(possible)
            moved = self.move(choice)
            if not moved:
                nx, ny = self.pos[0] + acoes_possiveis[choice][0], self.pos[1] + acoes_possiveis[choice][1]
                self.world_model.setdefault((nx, ny), {'dirt': None, 'obstacle': True, 'visited': False})['obstacle'] = True
            return
        self.stop()

    def __repr__(self):
        return f"<ModelBasedAgent pos={self.pos} energy={self.energy} points={self.points_collected}>"
