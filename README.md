# Simple CarMaze environment

An example of CarMaze environment for uninformed/informed search examples.

## Overview

The car moves through a `CarMazeEnv` from a starting position
to a goal position.
The car has a direction of `NSEW` and a velocity `v` which is always `0<=v<=Vmax`.
There are 5 actions in total:
- `No Action`: the car makes no action
- `Increase Velocity or Decrease Velocity`: the velocity would increase/
or decrease a unit. The resulting velocity should be in the range.
- `Turn Left or Turn Right`: change the direction. The car can change
its direction only if its velocity is 0

After each action, the car would update its direction and velocity `v`.
And it would move along the headed direction with `v` squares.
The car is not allow to go into war or go outside the maze.
The cost of each action is `fuel_cost + int(sqrt(v))`.

The car stops when it hit the wall or go outside the maze.
All of other actions are valid.
For example, if make a Turn Left action when its velocity is not zero would equal a No Action

## Input format

There are `n_wall + 2 lines`

- First line: `N n_walls Vmax fuel_cost`
- `xs ys xg yg`: start position and end position
- list of `n_walls` with 4 integers: x1 y1 x2 y2, the wall
is between the square (x1, y1) and (x2, y2)

The maze has NxN square, which index from 0 to N-1.
The (0, 0) is in the upper left corner.
A square (x, y) has x is the column index, y is the row index.

## Questions

- Q1: Find the bugs in `environment.py`, which should follow
the above description of `CarMazeEnv`.
- Q2: Use the solver to find the bfs path, given the `car.in`, and draw the path.
Could you find the dfs path.
- Q3: Assume the car start with 10 fuels, print the map which the car can reach.
Describe the algorithms (pseudocode) and its complexity.

