
from PIL import Image, ImageDraw
import time
import sys
from environment import CarMazeEnv
from solver import Solver
import argparse
import os


def trace_back(solver, x, y, d, v, image):
    path = [(x, y, d, v)]
    draw = ImageDraw.Draw(image)
    scale_factor = solver.env.scale_factor
    prev_state = solver.path[path[-1]]
    while prev_state != None:
        path.append(prev_state)
        draw.line([((x+0.5) * scale_factor, (y+0.5) * scale_factor),
                    ((prev_state[0] + 0.5) * scale_factor, (prev_state[1] + 0.5) * scale_factor)], 
                    fill='red', width=4)
        x, y, d, v = prev_state
        prev_state = solver.path[prev_state]
    return path

def write_output(output_file, path, cost):
    f = open(output_file, "w")
    if cost == -1 or path is None:
        f.write('-1 -1')
        f.close()
        return
    f.write('%i %i\n' % (len(path) - 1, cost))
    for i in reversed(range(0, len(path) - 1)):
        action = ''
        (x0, y0, d0, v0) = path[i + 1]
        (x1, y1, d1, v1) = path[i]
        if d0 == d1:
            if v0 == v1:
                action = 'O'
            elif v0 < v1:
                action = '+'
            else: 
                action = '-'
        elif (d0 > d1 and not (d0 == 3 and d1 == 0)) or (d0 == 0 and d1 == 3):
            action = 'L'
        else:
            action ='R'
        f.write('%s' % action)
    f.close()
    

#%%
if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('--input_file', type=str, default='car.in',
                        help='Input file')
    parser.add_argument('--output_file', type=str, default='car.out',
                        help='Output file')
    parser.add_argument('--method', type=int, default=1,
                        help='The searching algorithm')

    args = parser.parse_args()
    method = args.method
    inputmap = args.input_file
    output_file = args.output_file

    env = CarMazeEnv()
    env.read_map(inputmap)
    env.image.show()

    solver = Solver(env, method)
    print("solving ...")
    start = time.time()
    ans, last_state = solver.solve()
    if last_state is not None:
        # print('Cost', ans, 'Done in', time.time() - start)
        # print('Tracing...')
        path = trace_back(solver, *last_state, env.image)
        print('Num steps:', len(path) - 1)
        print('Found path:')
        for s in reversed(path):
            print('->',s)
        print('Showing map and path')
        write_output(output_file, path, ans)
        env.image.show()
    else:
        print("Not Found")
        write_output(output_file, None, ans)

# %%
