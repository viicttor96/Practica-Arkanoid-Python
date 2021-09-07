from os import path
from sprites import Wall, Brick
from pygame import Vector2
from random import random
from settings import *


class Map:
    def __init__(self):
        self.map_data = []
        self.counter = 0

    def load_map_from_file(self, stage_num):
        root_folder = path.dirname(__file__)
        self.map_data = []
        filename = f'stage{stage_num}.txt'
        with open(path.join(root_folder, "stages", filename), 'r') as file:
            for line in file:
                self.map_data.append(line)

    def create_sprites_from_data(self, game, stage_num):
        for row, tiles in enumerate(self.map_data):
            for col, tile in enumerate(tiles):
                pixel_x = (col * TILE_SIZE) + TILE_SIZE
                pixel_y = (row * TILE_SIZE) + TILE_SIZE/2
                if tile == '1':
                    Wall(game, col, row, stage_num)
                if tile == 'B':
                    if random() <= 0.93:       #probabilidad del 93% de que el ladrillo sea normal
                        self.counter += 1
                        Brick(game, pixel_x, pixel_y, False)
                    else:
                        self.counter += 1
                        Brick(game, pixel_x, pixel_y, True)
                    