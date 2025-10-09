import random
from collections import deque
from .goal_based_agent import GoalBasedAgent
from environment import ACTIONS, DIRT_TYPES

acoes_possiveis = {k: v for k, v in ACTIONS.items() if k not in ('ASPIRAR', 'PARAR')}


class UtilityBasedAgent(GoalBasedAgent):


    def _calculate_utility(self, path, dirt_type):
        move_cost = len(path) - 1 if path else 0
        vacuum_cost = 2
        total_cost = move_cost + vacuum_cost
        reward = DIRT_TYPES.get(dirt_type, 0)
        if total_cost == 0 or total_cost > self.energy:
            return -1
        return reward / total_cost

    def _find_path_to_nearest_unvisited(self):
        start = self.pos
        q = deque([(start, [start])])
        visited_bfs = {start}

        while q:
            (x, y), path = q.popleft()

            for dx, dy in acoes_possiveis.values():
                nx, ny = x + dx, y + dy

                if (nx, ny) not in self.known_map:
                    if 0 <= nx < len(self.env.grid) and 0 <= ny < len(self.env.grid[0]):
                        return path + [(nx, ny)]

                if (0 <= nx < len(self.env.grid) and 0 <= ny < len(self.env.grid[0])) and (nx, ny) not in visited_bfs:
                    if not self.known_map.get((nx, ny), {}).get('obstacle'):
                        visited_bfs.add((nx, ny))
                        q.append(((nx, ny), path + [(nx, ny)]))
        return None

    def step(self):
        if self.energy <= 0 or self.stopped:
            return

        self._perceive_and_update()

        cx, cy = self.pos
        if self.env.grid[cx][cy].get('dirt'):
            self.vacuum()
            self.current_plan = []
            return

        if self.current_plan:
            target = self.current_plan[-1]
            if target in self.known_map and not self.known_map[target].get('dirt'):
                self.current_plan = []

        if not self.current_plan:
            dirt_pos = self._known_dirt_positions()
            best_target = None;
            best_path = None;
            max_utility = -1
            for d_pos in dirt_pos:
                path = self._bfs(self.pos, d_pos)
                if not path: continue
                utility = self._calculate_utility(path, self.known_map[d_pos]['dirt'])
                if utility > max_utility:
                    max_utility = utility;
                    best_path = path;
                    best_target = d_pos

            if best_path:
                self.current_plan = best_path
            else:
                exploration_path = self._find_path_to_nearest_unvisited()
                if exploration_path:
                    self.current_plan = exploration_path
                else:
                    self.stop()
                    return

        if self.current_plan and len(self.current_plan) >= 2:
            next_pos = self.current_plan[1]
            action = self._pos_to_action(self.pos, next_pos)
            if action:
                if not self.move(action):
                    self.known_map.setdefault(next_pos, {})['obstacle'] = True
                    self.current_plan = []
                else:
                    self.current_plan.pop(0)
            else:
                self.current_plan = []

    def __repr__(self):
        return f"<UtilityBasedAgent pos={self.pos} energy={self.energy} points={self.points_collected}>"