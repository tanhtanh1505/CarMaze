from environment import CarMazeEnv
from queue import Queue
from functools import partial


class Solver:
    def __init__(self, env: CarMazeEnv) -> None:
        self.env = env
        self.found = None

    def act_and_add_state(self, act, prev_state, cur_cost, is_ucf=False):
        x, y, d, v, step_cost = act(*prev_state)
        if cur_cost == -1:
            prev_state = None  # Init state
        if x < 0 or y < 0:  # Invalid action
            return None

        cur_cost += 1
        s = (x, y, d, v)

        # Fast stop

        if self.env.goal == (x, y) and v == 0:
             self.path[s] = prev_state
             self.found = cur_cost, s
             return None
        if s in self.seen:
            return None

            # Sure min path to s
        p = self.path.get(s, None)
        if p is not None:
            return None
        self.path[s] = prev_state
        return x, y, d, v, cur_cost

    def explore(self, s, cost, is_ucf):
        if s in self.seen:
            return -1, None
        self.seen.add(s)

        if self.found is not None:  # Fast stop
            return self.found

        step_fn = self.step_bfs
        # Action
        v = s[-1]
        if v == 0:
            step_fn(self.env.turn_left, s, cost)
            step_fn(self.env.turn_right, s, cost)
            step_fn(self.env.speed_up, s, cost)
        else:
            step_fn(self.env.no_action, s, cost)
            step_fn(self.env.slow_down, s, cost)
            if v < self.env.vmax:
                step_fn(self.env.speed_up, s, cost)
        return -1, None

    def step_bfs(self, act, s, total_cost):
        ret = self.act_and_add_state(act, s, total_cost, is_ucf=False)
        if ret is None:
            return  # Already explored or invalid action
        x, y, d, v, cur_cost = ret
        new_s = (x, y, d, v)
        self.Q.put(partial(self.explore, new_s, cur_cost, False))

    def solve_bfs(self):
        self.Q = Queue()
        self.seen = set()
        self.path = dict()
        # self.mins = dict()
        x0, y0 = self.env.start
        self.step_bfs(self.env.no_action, (x0, y0, 0, 0), -1)
        ans = -1
        last_state = None
        while ans == -1 and not self.Q.empty():
            ans, last_state = self.Q.get()()

        return ans, last_state

