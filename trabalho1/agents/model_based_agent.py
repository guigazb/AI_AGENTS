import random
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

    def _count_unknown_neighbors(self, pos):
        x, y = pos
        cnt = 0
        max_x, max_y = len(self.env.grid), len(self.env.grid[0])
        for dx, dy in acoes_possiveis.values():
            nx, ny = x + dx, y + dy
            if not (0 <= nx < max_x and 0 <= ny < max_y):
                continue
            if (nx, ny) not in self.world_model:
                cnt += 1
        return cnt

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

        cx, cy = self.pos

        if self.env.grid[cx][cy].get('dirt'):
            self.vacuum()
            return

        possible = []
        unvisited = []
        max_x, max_y = len(self.env.grid), len(self.env.grid[0])
        for name, (dx, dy) in acoes_possiveis.items():
            nx, ny = cx + dx, cy + dy
            if not (0 <= nx < max_x and 0 <= ny < max_y):
                continue
            known = self.world_model.get((nx, ny))
            if known and known.get('obstacle'):
                continue
            possible.append((name, (nx, ny)))
            if not known or not known.get('visited'):
                unvisited.append((name, (nx, ny)))

        if unvisited:
            act, target = random.choice(unvisited)
            moved = self.move(act)
            if not moved:
                self.world_model.setdefault(target, {'dirt': None, 'obstacle': True, 'visited': False})['obstacle'] = True
            else:
                self.world_model.setdefault(self.pos, {'dirt': None, 'obstacle': False, 'visited': True})['visited'] = True
            return

        if possible:
            best = None; best_score = -1
            for act, targ in possible:
                score = self._count_unknown_neighbors(targ)
                if score > best_score or (score == best_score and random.random() < 0.5):
                    best_score = score
                    best = (act, targ)
            act, target = best
            moved = self.move(act)
            if not moved:
                self.world_model.setdefault(target, {'dirt': None, 'obstacle': True, 'visited': False})['obstacle'] = True
            else:
                self.world_model.setdefault(self.pos, {'dirt': None, 'obstacle': False, 'visited': True})['visited'] = True
            return

        if self.env.grid[cx][cy].get('dirt'):
            self.vacuum()
            return
        self.stop()

    def __repr__(self):
        return f"<ModelBasedAgent pos={self.pos} energy={self.energy} points={self.points_collected}>"
