import argparse
import math
from environment import CarMazeEnv

from queue import PriorityQueue


class State:
    def __init__(self, x, y, d=0, v=0, remain_fuel=-1, cur_cost=0, disToG=0, par=None, mode=1):
        self.x = x
        self.y = y
        self.d = d
        self.v = v
        self.remain_fuel = remain_fuel
        self.cur_cost = cur_cost
        self.disToG = disToG
        self.par = par
        self.mode = mode    #1:ucs  2:greedy - manhattan   3:greedy - more remaining fuel   4:less steps    5:A*
        if par is None:
            self.posCollectedFuel = set()
            self.steps = 0
        else:
            self.posCollectedFuel = par.posCollectedFuel.copy()
            self.steps = par.steps + 1

    def display(self):
        print(self.x, self.y, self.d, self.v, self.remain_fuel, self.posCollectedFuel)

    def displayxy(self):
        print(self.x, self.y, self.d, self.v, self.remain_fuel)

    def __lt__(self, other):
        if other is None:
            return False
        if self.mode == 1:  #ucs
            return self.cur_cost < other.cur_cost
        elif self.mode == 2:    #greedy - manhattan
            return self.disToG < other.disToG
        elif self.mode == 3:    #greedy - more remaining fuel
            return self.remain_fuel > other.remain_fuel
        elif self.mode == 4:    #less steps
            return self.steps < other.steps
        else:   #A*
            return self.disToG + self.cur_cost + other.remain_fuel/9 < other.disToG + other.cur_cost + self.remain_fuel/9

    def __eq__(self, other):
        if other is None:
            return False
        return self.remain_fuel == other.remain_fuel and self.x == other.x and self.y == other.y and self.d == other.d and self.v == other.v

    def xydv(self):
        return (self.x, self.y, self.d, self.v)


def equal(O, G):
    x, y = G
    if O.x == x and O.y == y and O.v == 0:
        return True
    return False


def checkInPriority(tmp, c):
    if tmp is None:
        return False
    return tmp in c.queue


def getPath(O):
    O.display()
    if O.par is not None:
        getPath(O.par)
    else:
        return


def creatPath(S):
    path = dict()
    while S.par is not None:
        path[S.xydv()] = S.par.xydv()
        S = S.par
    path[S.xydv()] = None
    return path


class Solver:
    def __init__(self, env: CarMazeEnv, mode=1) -> None:
        self.Open = PriorityQueue()
        self.Closed = PriorityQueue()
        self.env = env
        self.mode = mode

    def step_fn(self, act, s):
        par_cost = s.cur_cost
        remain_fuel_par = s.remain_fuel
        x, y, d, v, cost = act(s.x, s.y, s.d, s.v)

        if x < 0 or y < 0:  # Invalid action
            return None

        tmp = State(x, y, d, v, remain_fuel_par - cost, cost + par_cost, self.manhattan(x, y), s, self.mode)

        if v == 0 and (x % 5 == 0 or y % 5 == 0) and not ((x, y) in tmp.posCollectedFuel): #check and collect fuel
            tmp.remain_fuel += 10
            tmp.posCollectedFuel.add((x, y))

        ok1 = checkInPriority(tmp, self.Open)
        ok2 = checkInPriority(tmp, self.Closed)

        if tmp.remain_fuel > 0 and not ok1 and not ok2:
            self.Open.put(tmp)

    def manhattan(self, x, y):
        x_, y_ = self.env.goal
        return abs(x-x_) + abs(y-y_)

    def solve(self):
        x0, y0 = self.env.start
        s = State(x=x0, y=y0, remain_fuel=10)
        self.Open.put(s)

        while True:
            if (self.Open.empty()):
                print('Not found')
                return -1, None
            s = self.Open.get()
            self.Closed.put(s)
            # print('duyet: ')
            # s.display()
            # print('Open:')
            # for st in self.Open.queue:
            #     st.displayxy()
            # print('-------------')
            if equal(s, self.env.goal):
                print('Done')
                print('Cost:', s.cur_cost, ', Remaining fuel:', s.remain_fuel)
                # getPath(s)
                self.path = creatPath(s)
                return s.cur_cost, (s.xydv())
            v = s.v
            if v == 0:
                self.step_fn(self.env.turn_left, s)
                self.step_fn(self.env.turn_right, s)
                self.step_fn(self.env.speed_up, s)
            else:
                self.step_fn(self.env.no_action, s)
                self.step_fn(self.env.slow_down, s)
                if v < self.env.vmax:
                    self.step_fn(self.env.speed_up, s)
