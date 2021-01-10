import pygame
from os.path import join, isfile
from sys import exit
import csv


def load_image(folder, name):
    full_path = join(folder, name)
    if not isfile(full_path):
        print(f"Файл '{full_path}' не найден")
        exit()
    return pygame.image.load(full_path)


class Field:
    """There are 2 modes of __init__.
    1) if mode == 'load' the map will be loaded from lv_filename. It's default mode.
    2) if mode != 'load' the new map will be created. Use self.save_level function to save the map.  """

    def __init__(self, map_filename, mode='load'):
        self.f = map_filename
        if mode == 'load':
            self.matrix = []
            self.load_level()
        else:
            self.matrix = [[Cell('1') for _ in range(110)] for __ in range(9)] + [[Cell('7')] for _ in range(110)]

    def load_level(self):
        with open(self.f, 'r', encoding='utf-8') as f_r:
            reader = csv.reader(f_r, delimiter=';', quotechar='"')
            for line in reader:
                self.matrix.append([Cell(i) for i in line])

    def save_level(self):
        with open(self.f, 'w', encoding='utf-8') as f_w:
            writer = csv.writer(f_w, delimiter=';', quotechar='"')
            for line in self.matrix:
                writer.writerow(line)


class Person:
    EXP = '.png'

    def __init__(self, n):
        super().__init__(self, person_sprites, all_sprites)
        self.img = load_image('person', n + Cell.EXP)


class Cell(pygame.Sprite.sprite):
    EXP = '.png'

    def __init__(self, n):
        super().__init__(self, cells_sprites, all_sprites)
        self.img = load_image('cells', n + Cell.EXP)


all_sprites = pygame.sprite.Group()
cells_sprites = pygame.sprite.Group()
person_sprites = pygame.sprite.Group()
