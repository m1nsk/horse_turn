from collections import namedtuple
from collections import deque
import random as random
import numpy as np
import math as math

mem_field = namedtuple('mem_field', ['turn_num', 'prev_node'])
node = namedtuple('node', ['coord', 'turn_num', 'prev_node'])
coord = namedtuple('coord', ['x', 'y'])
challenger = namedtuple('challenger', ['turn_num', 'node', 'finish_node'])


class Coord(coord):
    def __new__(cls, x, y):
        return super().__new__(cls, x, y)

    def __add__(self, other):
        return Coord(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Coord(self.x - other.x, self.y - other.y)


class MemField:
    def __init__(self, field_size, start):
        empty_field = mem_field(0, start)
        self.field = np.array([[empty_field for j in range(field_size)] for i in range(field_size)], dtype=mem_field)

    def set_field(self, node):
        self.field[node.coord.x, node.coord.y] = mem_field(node.turn_num, node.prev_node)

    def get_field(self, cell_coord):
        return mem_field(*self.field[cell_coord.x, cell_coord.y])


class NodeQuery:
    def __init__(self, initial):
        self.deque = deque(initial)

    def __len__(self):
        return self.deque.__len__()

    def add_nodes(self, nodes):
        self.deque.extend(nodes)

    def get_node(self):
        return self.deque.popleft()


class Game:
    def end_of_game_decorator(func):
        def decorated_func(self, current_node):
            if current_node.coord == self.finish:
                self.challenger = challenger(current_node.turn_num, current_node, current_node)

    def mem_decorator(func):
        def decorated_func(self, current_node):
            if current_node.turn_num * 2 < self.challenger.turn_num or not self.challenger.turn_num:
                relative_finish = self.finish - current_node.coord
                current_field = self.mem_field.get_field(current_node.coord)
                if not current_field.turn_num:
                    self.mem_field.set_field(current_node)
                    field = self.mem_field.get_field(relative_finish)
                    if field.turn_num and field.turn_num < self.challenger.turn_num:
                        finish_node = node(relative_finish, *field)
                        self.challenger = challenger(current_node.turn_num + field.turn_num, current_node, finish_node)
                    else:
                        func(self, current_node)

        return decorated_func

    def __init__(self, size, finish):
        self.size = size
        self.finish = finish
        self.start = Coord(math.floor(self.size / 2), math.floor(self.size / 2))
        self.mem_field = MemField(self.size, self.start)
        start_field = node(start, 0, None)
        self.node_query = NodeQuery((start_field,))
        self.turn_counter = 0
        self.challenger = challenger(size, start_field, start_field)

    def start_calculation(self):
        while len(self.node_query):
            node = self.node_query.get_node()
            self.next_turn(node)
        self.recover_horse_way()

    @mem_decorator
    def next_turn(self, current_node):
        turns = (Coord(1, 2), Coord(2, 1), Coord(-1, 2), Coord(-2, 1), Coord(1, -2), Coord(2, -1), Coord(-2, -1), Coord(-1, -2))

        if node.coord != finish:
            next_nodes = list(filter(
                lambda map_node: 0 <= map_node.coord.x < self.size and 0 <= map_node.coord.y < self.size, map(
                    lambda turn: node(turn + current_node.coord, current_node.turn_num + 1, current_node), turns)
                )
            )
            self.node_query.add_nodes(next_nodes)

    def recover_node(self, way_node):
        while way_node.prev_node.turn_num:
            prev_node = node(way_node.prev_node.coord, *self.mem_field.get_field(way_node.prev_node.coord))
            print(way_node, 'wn')
            print(prev_node, 'pw')
            print(way_node.coord - prev_node.coord, 'delta')
            yield way_node.coord - prev_node.coord
            way_node = prev_node
        return

    def recover_horse_way(self):
        deq = deque()
        before_node = list(self.recover_node(self.challenger.node))
        deq.extend(reversed(before_node))
        after_node = list(self.recover_node(self.challenger.finish_node))
        deq.extend(reversed(after_node))
        print(deq)



size = random.randint(0, 100)
start = Coord(math.floor(size / 2), math.floor(size / 2))
finish = Coord(random.randint(0, size), random.randint(0, size))
print(start, 'start')
print(finish, 'finish')
game = Game(size, finish)
game.start_calculation()
