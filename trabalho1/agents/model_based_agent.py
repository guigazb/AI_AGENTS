import random
from collections import deque
from .base_vacuum_agent import BaseVacuumAgent
from environment import ACTIONS

SPATIAL_ACTIONS = {k: v for k, v in ACTIONS.items() if k not in ('ASPIRAR', 'PARAR')}

class ModelBasedAgent(BaseVacuumAgent):
    def __init__(self, env):
        super().__init__(env)
        self.world_model = {}

    def _pos_key(self, pos):
        return tuple(pos)

    def _update_model_with_perception(self, perception):

        if not perception:
            return

        pos = perception.get('position')
        if pos is None:
            return

        px, py = pos
        for dir_name, info in perception.items():
            if dir_name == 'position':
                continue

            if dir_name == 'center':
                x, y = px, py
            else:
                if dir_name not in ACTIONS:
                    continue
                dx, dy = ACTIONS[dir_name]
                x, y = px + dx, py + dy

            if not (0 <= x < len(self.env.grid) and 0 <= y < len(self.env.grid[0])):
                continue

            key = (x, y)
            entry = self.world_model.setdefault(key, {
                'dirt': None,
                'obstacle': False,
                'visited': False,
                'unreachable': False
            })

            if isinstance(info, dict):
                entry['dirt'] = info.get('dirt')
                entry['obstacle'] = bool(info.get('obstacle'))
            if dir_name == 'center':
                entry['visited'] = True

    def _known_dirty_positions(self):
        return [pos for pos, v in self.world_model.items() if v.get('dirt')]

    def _neighbors(self, pos):
        x, y = pos
        max_x = len(self.env.grid)
        max_y = len(self.env.grid[0])
        for dx, dy in SPATIAL_ACTIONS.values():
            nx, ny = x + dx, y + dy
            if 0 <= nx < max_x and 0 <= ny < max_y:
                known = self.world_model.get((nx, ny))
                if known and known.get('obstacle'):
                    continue
                yield (nx, ny)

    def _bfs_actions(self, start, goal):
        sx, sy = start
        gx, gy = goal
        max_x = len(self.env.grid)
        max_y = len(self.env.grid[0])

        visited = set()
        parent = {} 
        q = deque()
        q.append((sx, sy))
        visited.add((sx, sy))

        while q:
            x, y = q.popleft()
            if (x, y) == (gx, gy):
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
                known = self.world_model.get((nx, ny))
                if known and known.get('obstacle'):
                    continue
                visited.add((nx, ny))
                parent[(nx, ny)] = (x, y, act_name)
                q.append((nx, ny))

        return None

    def step(self):
        if self.energy <= 0 or self.stopped:
            return

        perc = self.perceive()
        if perc and 'position' in perc:
            self.pos = perc['position']

        self._update_model_with_perception(perc)

        cur_key = self._pos_key(self.pos)
        self.world_model.setdefault(cur_key, {
            'dirt': None,
            'obstacle': False,
            'visited': True,
            'unreachable': False
        })
        self.world_model[cur_key]['visited'] = True

        center_info = perc.get('center') if perc else None
        has_dirt_here = bool(center_info.get('dirt')) if center_info else bool(self.world_model[cur_key].get('dirt'))
        if has_dirt_here:
            success = self.vacuum()
            if not success:
                return
            self._update_model_with_perception(self.perceive())
            return
        dirty_positions = self._known_dirty_positions()
        best_plan = None
        best_target = None
        for dpos in dirty_positions:
            plan = self._bfs_actions(self.pos, dpos)
            if plan:
                if best_plan is None or len(plan) < len(best_plan):
                    best_plan = plan
                    best_target = dpos

        if best_plan:
            next_action = best_plan[0]
            moved = self.move(next_action)
            if not moved:
                dx, dy = SPATIAL_ACTIONS[next_action]
                blocked_pos = (self.pos[0] + dx, self.pos[1] + dy)
                entry = self.world_model.setdefault(blocked_pos, {
                    'dirt': None,
                    'obstacle': True,
                    'visited': False,
                    'unreachable': False
                })
                entry['obstacle'] = True
            return

        possible_moves = []
        unvisited_moves = []
        max_x = len(self.env.grid)
        max_y = len(self.env.grid[0])
        for act_name, (dx, dy) in SPATIAL_ACTIONS.items():
            nx, ny = self.pos[0] + dx, self.pos[1] + dy
            if not (0 <= nx < max_x and 0 <= ny < max_y):
                continue
            known = self.world_model.get((nx, ny))
            if known and known.get('obstacle'):
                continue
            possible_moves.append(act_name)
            if not known or not known.get('visited'):
                unvisited_moves.append(act_name)

        if unvisited_moves:
            chosen = random.choice(unvisited_moves)
            moved = self.move(chosen)
            if not moved:
                dx, dy = SPATIAL_ACTIONS[chosen]
                blocked_pos = (self.pos[0] + dx, self.pos[1] + dy)
                self.world_model.setdefault(blocked_pos, {
                    'dirt': None, 'obstacle': True, 'visited': False, 'unreachable': False
                })['obstacle'] = True
            return
        elif possible_moves:
            chosen = random.choice(possible_moves)
            moved = self.move(chosen)
            if not moved:
                dx, dy = SPATIAL_ACTIONS[chosen]
                blocked_pos = (self.pos[0] + dx, self.pos[1] + dy)
                self.world_model.setdefault(blocked_pos, {
                    'dirt': None, 'obstacle': True, 'visited': False, 'unreachable': False
                })['obstacle'] = True
            return
        else:
            self.stop()
            return

    def __repr__(self):
        return f"<ModelBasedAgent pos={self.pos} energy={self.energy} points={self.points_collected}>"
