from collections import namedtuple
from collections import deque
from functools import  reduce
import random as random
import time
import numpy as np
import math as math

mem_field = namedtuple('mem_field', ['turn_num', 'prev_node_coord'])
node = namedtuple('node', ['coord', 'turn_num', 'prev_node_coord'])
coord = namedtuple('coord', ['x', 'y'])
challenger = namedtuple('challenger', ['turn_num', 'middle_coord', 'finish_coord'])


class EndOfGame(Exception):
    pass


class Coord(coord):
    def __new__(cls, x, y):
        return super().__new__(cls, x, y)

    def __add__(self, other):
        return Coord(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Coord(self.x - other.x, self.y - other.y)


class MemField:
    def __init__(self, field_size, start):
        self.start = start
        empty_field = mem_field(None, start)
        self.field = np.array([[empty_field for j in range(field_size)] for i in range(field_size)], dtype=mem_field)

    def set_field(self, current_node):
        position = self.start + current_node.coord
        self.field[position.x, position.y] = mem_field(current_node.turn_num, current_node.prev_node_coord)

    def get_field(self, cell_coord):
        position = self.start + cell_coord
        return mem_field(*self.field[position.x, position.y])


class Game:
    turns = (Coord(1, 2), Coord(2, 1), Coord(-1, 2), Coord(-2, 1), Coord(1, -2), Coord(2, -1), Coord(-2, -1), Coord(-1, -2))

    def time_it(func):

        def timed(*args, **kw):
            ts = time.time()
            func(*args, **kw)
            te = time.time()
            print(te - ts, 'seconds')

        return timed

    def end_of_game_decorator(func):
        def decorated_func(self, current_node):
            """TODO: clear oll this if-else gargage"""
            current_field = self.mem_field.get_field(current_node.coord)
            if current_field.turn_num is None:
                self.mem_field.set_field(current_node)
                if current_node.coord == self.finish:
                    self.node_query.clear()
                    self.challenger = challenger(current_node.turn_num, current_node.coord, current_node.coord)
                    raise EndOfGame
                else:
                    func(self, current_node)

        return decorated_func

    def mem_decorator(func):
        def decorated_func(self, current_node):
            """TODO: clear oll this if-else gargage"""
            relative_finish = self.finish - current_node.coord
            current_field = self.mem_field.get_field(current_node.coord)
            if current_field.turn_num is None:
                self.mem_field.set_field(current_node)
                if math.fabs(relative_finish.x) < self.size / 2 and math.fabs(relative_finish.y) < size / 2:
                    field = self.mem_field.get_field(relative_finish)
                    if field.turn_num:
                        self.challenger = challenger(current_node.turn_num + field.turn_num, current_node.coord, relative_finish)
                        raise EndOfGame
                    else:
                        func(self, current_node)
                else:
                    func(self, current_node)

        return decorated_func

    def __init__(self, size, finish):
        self.size = size
        self.finish = finish
        self.start = Coord(math.floor(self.size / 2), math.floor(self.size / 2))
        self.mem_field = MemField(self.size, self.start)
        start_field = node(Coord(0, 0), 0, None)
        self.node_query = deque((start_field,))
        self.turn_counter = 0
        self.challenger = challenger(size, Coord(0, 0), Coord(0, 0))
        self.node_counter = 0

    @time_it
    def start_calculation(self):
        try:
            while len(self.node_query):
                next_node = self.node_query.popleft()
                self.fast_next_turn(next_node)
        except EndOfGame:
            self.recover_horse_way()
            print(self.challenger, 'challenger')
            print(self.node_counter, 'node_counter')
            print(next_node.turn_num, 'turn deep')

    @time_it
    def start_slow_calculation(self):
        try:
            while len(self.node_query):
                next_node = self.node_query.popleft()
                self.slow_next_turn(next_node)
        except EndOfGame:
            print(self.challenger, 'challenger')
            print(self.node_counter, 'node_counter')
            print(next_node.turn_num, 'turn deep')

    def next_turn(self, current_node):
        self.node_counter += 1
        next_nodes = list(filter(
            lambda map_node: math.fabs(map_node.coord.x) < self.start.x and math.fabs(map_node.coord.y) < self.start.y,
                map(
                    lambda turn: node(turn + current_node.coord, current_node.turn_num + 1, current_node.coord), Game.turns)
                )
            )
        self.node_query.extend(next_nodes)

    @mem_decorator
    def fast_next_turn(self, current_node):
        self.next_turn(current_node)

    @end_of_game_decorator
    def slow_next_turn(self, current_node):
        self.next_turn(current_node)

    def recover_node(self, way_coord):
        """TODO: fix turn history generator"""
        loop_flag = True
        while loop_flag:
            prev_node = self.mem_field.get_field(way_coord)
            prev_coord = prev_node.prev_node_coord
            yield way_coord - prev_coord
            if prev_coord == Coord(0, 0):
                loop_flag = False
            way_coord = prev_coord
        return

    def recover_horse_way(self):
        deq = deque()
        before_node = list(self.recover_node(self.challenger.middle_coord))
        deq.extend(reversed(before_node))
        # print(list(reduce(lambda x, y: x + y, deq)))
        # print(self.finish - self.challenger.middle_coord)
        after_node = list(self.recover_node(self.challenger.finish_coord))
        deq.extend(reversed(after_node))
        # print(list(reduce(lambda x, y: x + y, deq)))
        # print(self.start - self.finish)
        print(list(map(lambda item: 'x: {0}, y: {1}'.format(item.x, item.y), deq)))



size = 500
start = Coord(0, 0)
finish = Coord(random.randint(math.floor(size * 8 / 9), size) - math.floor(size / 2), random.randint(math.floor(size * 8 / 9), size) - math.floor(size / 2))
finish = Coord(8, 16)
print(size, 'size')
print(start, 'start')
print(finish, 'finish')
game_fast = Game(size, finish)
game_fast.start_calculation()

game_slow = Game(size, finish)
game_slow.start_slow_calculation()


