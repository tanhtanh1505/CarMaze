from bisect import bisect_left, bisect_right
from math import sqrt
from PIL import Image, ImageDraw


class CarMazeEnv:
    directions = ('N', 'E', 'S', 'W')

    def is_inside(self, x, y):
        return (0 <= x) and (x < self.N) and (0 <= y) and (y < self.N)

    def _line2ints(self, line):
        return [int(n) for n in line.split()]

    def _is_hozirontal_wall(self, wall):
        if not (wall[1] == wall[3] or wall[0] == wall[2]):
            raise ValueError
        return wall[0] == wall[2]

    def read_map(self, input_file):
        with open(input_file, 'r') as f:
            lines = [self._line2ints(line) for line in f.readlines()]
            (self.N, self.n_walls, self.vmax, fuel_cost) = lines[0]
            # xs, ys, xg, yg = lines[1]
            xs, ys, xg, yg = lines[1]

            # Map image
            if self.N < 10:
                self.image = Image.new('RGB', (300, 300), color='white')
                self.scale_factor = 300 / (self.N)
            else:
                self.image = Image.new('RGB', (600, 600), color='white')
                self.scale_factor = 600 / (self.N)
            draw = ImageDraw.Draw(self.image)

            self.start = (xs, ys)
            self.goal = (xg, yg)
            self.fuel_cost = fuel_cost
            self.v_walls = []
            self.h_walls = []
            self.walls_x = []
            for i in range(self.N):
                draw.line([(i * self.scale_factor, 0),
                           (i * self.scale_factor, self.N * self.scale_factor)],
                          fill="black", width=0)
                draw.line([(0, i * self.scale_factor), (self.N * self.scale_factor, i * self.scale_factor)],
                          fill="black", width=0)
                if i % 5 == 0:
                    draw.line([(0.5, (i + 0.5) * self.scale_factor),
                               ((self.N + 0.5) * self.scale_factor, (i + 0.5) * self.scale_factor)],
                              fill="green", width=4)
                    draw.line([((i + 0.5) * self.scale_factor, 0.5),
                               ((i + 0.5) * self.scale_factor, (self.N + 0.5) * self.scale_factor)],
                              fill="green", width=4)

            for wall in lines[2: 2 + self.n_walls]:
                x0, y0, x1, y1 = wall
                self.walls_x.append(wall)
                try:
                    if self._is_hozirontal_wall(wall):
                        self.h_walls.append(tuple([*sorted((x0, x1)), max(y0, y1)]))
                    else:
                        self.v_walls.append(tuple([*sorted((y0, y1)), max(x0, x1)]))
                    # Draw wall to map image
                    if x0 == x1:
                        draw.line([(x0 * self.scale_factor, max(y0, y1) * self.scale_factor),
                                   ((x1 + 1) * self.scale_factor, max(y0, y1) * self.scale_factor)],
                                  fill="black", width=4)
                    if y0 == y1:
                        draw.line([(max(x0, x1) * self.scale_factor, y0 * self.scale_factor),
                                   (max(x0, x1) * self.scale_factor, (y1 + 1) * self.scale_factor)],
                                  fill="black", width=4)
                except ValueError:
                    print('Error wall:', wall)

            self.v_walls = sorted(self.v_walls, key=lambda x: x[-1])
            self.h_walls = sorted(self.h_walls, key=lambda x: x[-1])

    # Check colision
    def _is_collided(self, walls, fix, s, e):
        """
        s < e
        """
        tmp = [p[-1] for p in walls]
        s_ind = bisect_left(tmp, s)  # any bisect is fine
        if s < e:
            end_ind = bisect_right(tmp, e)  # bound == case
        else:
            end_ind = bisect_left(tmp, e)  # bound == case
        s_ind, end_ind = sorted((s_ind, end_ind))
        for w in walls[s_ind:end_ind + 1]:
            if w[0] <= fix <= w[1]:
                return True
        return False

    def isColl(self, x1, y1, x2, y2):
        for w in self.walls_x:
            if x1 == x2:  # ver
                if w[0] != w[2]:
                    continue
                if (w[0] == x1) and ((y1 > w[1] + 0.5 > y2) or (y2 > w[1] + 0.5 > y1)):
                    return True
            if y1 == y2:  # hor
                if w[1] != w[3]:
                    continue
                if (w[1] == y1) and ((x1 > w[0] + 0.5 > x2) or (x2 > w[0] + 0.5 > x1)):
                    return True

        return False

    # Chỉ kiểm tra các tường ngang dọc tuỳ theo hướng di chuyển
    def _next_position(self, x, y, d, v):
        """
        :param x0:
        :param y0:
        :param d: moving direction, ['N', 'S', 'E', 'W']
        :param v: speed
        :param list_of_walls: list of walls has to check collision
        :return:
            x1, y1:
            if invalid move (collision) return -1, -1
        """
        if v == 0:
            return x, y

        if d % 2 == 0:  # verical direction
            v = (d - 1) * v
            # if self.is_inside(x, y + v) and not self._is_collided(self.h_walls, x, y, y + v):
            #     return x, y + v
            if self.is_inside(x, y + v) and not self.isColl(x, y, x, y + v):
                return x, y + v
        else:  # hozi direction
            v = (2 - d) * v
            # if self.is_inside(x + v, y) and not self.isColl(x, y, x+v, y):
            #     return x + v, y
            if self.is_inside(x + v, y) and not self.isColl(x, y, x + v, y):
                return x + v, y
        return -1, -1

    # Actions
    # Trả về vị trí, d, v tương ứng với action
    # return x, y, d, v, cost of action
    def turn_left(self, x, y, d, v):
        d += 3
        d %= 4
        x, y = self._next_position(x, y, d, v)
        return x, y, d, v, self.fuel_cost + int(sqrt(v))

    def turn_right(self, x, y, d, v):
        d += 1
        d %= 4
        x, y = self._next_position(x, y, d, v)
        return x, y, d, v, self.fuel_cost + int(sqrt(v))

    def speed_up(self, x, y, d, v):
        v = min(v + 1, self.vmax)
        x, y = self._next_position(x, y, d, v)
        return x, y, d, v, self.fuel_cost + int(sqrt(v))

    def slow_down(self, x, y, d, v):
        v = max(v - 1, 0)
        x, y = self._next_position(x, y, d, v)
        return x, y, d, v, self.fuel_cost + int(sqrt(v))

    def no_action(self, x, y, d, v):
        x, y = self._next_position(x, y, d, v)
        return x, y, d, v, self.fuel_cost + int(sqrt(v))


if __name__ == "__main__":
    print('Car maze environment')

    carmaze = CarMazeEnv()
    carmaze.read_map('car.in')
    ## Q1. Run test here
