import random
from .base_vacuum_agent import BaseVacuumAgent
from environment import ACTIONS

class ModelBasedAgent(BaseVacuumAgent):
    def __init__(self, env):
        super().__init__(env)
        self.world_model = {}  # pos: {'dirt': bool, 'obstacle': bool, 'visited': bool}

    def _pos_key(self, pos):
        return tuple(pos)

    def _update_model_with_perception(self, perception):
        for dir_name, info in perception.items():
            if dir_name == 'position':
                continue
            if dir_name == 'center':
                x, y = perception['position']
            else:
                dx, dy = ACTIONS[dir_name]
                px, py = perception['position']
                x, y = px + dx, py + dy
            key = (x, y)
            
            if not (0 <= x < len(self.env.grid) and 0 <= y < len(self.env.grid[0])):
                continue
            self.world_model[key] = {
                'dirt': info['dirt'],
                'obstacle': info['obstacle'],
                'visited': (dir_name == 'center') or self.world_model.get(key, {}).get('visited', False)
            }

    def _known_dirty_positions(self):
        return [pos for pos, v in self.world_model.items() if v.get('dirt')]

    def _neighbors(self, pos):
        x, y = pos
        for dir_name, (dx, dy) in ACTIONS.items():
            if dir_name in ['ASPIRAR', 'PARAR']:
                continue
            nx, ny = x + dx, y + dy
            if 0 <= nx < len(self.env.grid) and 0 <= ny < len(self.env.grid[0]):
                known = self.world_model.get((nx, ny))
                if known and known.get('obstacle'):
                    continue
                yield (nx, ny)

    def _bfs_path(self, start, goal):
        from collections import deque
        q = deque([start])
        parent = {start: None}
        while q:
            cur = q.popleft()
            if cur == goal:
                path = []
                p = cur
                while p is not None:
                    path.append(p)
                    p = parent[p]
                path.reverse()
                return path
            for nb in self._neighbors(cur):
                if nb not in parent:
                    parent[nb] = cur
                    q.append(nb)
        return []

    def step(self):
        if self.energy <= 0 or self.stopped:
            return

        perc = self.perceive()
        self.pos = perc['position']
        self._update_model_with_perception(perc)
        # marca o grid atual como visitado
        self.world_model[self._pos_key(self.pos)]['visited'] = True

        # se tem sujeira ele aspira
        if perc['center']['dirt']:
            success = self.vacuum()
            if not success:
                self.stop()
            return

        # procura as sujeiras que o agente sabe que existe
        dirty_positions = self._known_dirty_positions()
        if dirty_positions:
            best_path = None
            for dpos in dirty_positions:
                path = self._bfs_path(self.pos, dpos)
                if path:
                    if best_path is None or len(path) < len(best_path):
                        best_path = path
            if best_path and len(best_path) >= 2:
                next_pos = best_path[1]
                for dir_name, (dx, dy) in ACTIONS.items():
                    if dir_name in ['ASPIRAR', 'PARAR']:
                        continue
                    nx, ny = self.pos[0] + dx, self.pos[1] + dy
                    if (nx, ny) == next_pos:
                        self.move(dir_name)
                        return
            else:
                for dpos in dirty_positions:
                    if not self._bfs_path(self.pos, dpos):
                        self.world_model[dpos]['dirt'] = False

        possible_moves = []
        unvisited_moves = []
        for dir_name, (dx, dy) in ACTIONS.items():
            if dir_name in ['ASPIRAR', 'PARAR']:
                continue
            nx, ny = self.pos[0] + dx, self.pos[1] + dy
            if not (0 <= nx < len(self.env.grid) and 0 <= ny < len(self.env.grid[0])):
                continue
            known = self.world_model.get((nx, ny))
            if known and known.get('obstacle'):
                continue
            possible_moves.append(dir_name)
            if not known or not known.get('visited'):
                unvisited_moves.append(dir_name)

        if unvisited_moves:
            self.move(random.choice(unvisited_moves))
        elif possible_moves:
            self.move(random.choice(possible_moves))
        else:
            self.stop()