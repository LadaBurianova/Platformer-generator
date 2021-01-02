import pygame
from os.path import join, isfile
from sys import exit


def load(folder, name):
    full_path = join(folder, name)
    if not isfile(full_path):
        print(f"Файл '{full_path}' не найден")
        exit()
    return pygame.image.load(full_path)


class Field:
    def __init__(self, matrix=None):
        if matrix is None:
            self.matrix = [[Cell(1) for _ in range(110)] for __ in range(9)] + [[Cell(7)] for _ in range(110)]


class Person:
    EXP = '.png'

    def __init__(self, n):
        super().__init__(self, person_sprites, all_sprites)
        self.img = load('person', n + Cell.EXP)


class Cell(pygame.Sprite.sprite):
    EXP = '.png'

    def __init__(self, n):
        super().__init__(self, cells_sprites, all_sprites)
        self.img = load('cells', n + Cell.EXP)


all_sprites = pygame.sprite.Group()
cells_sprites = pygame.sprite.Group()
person_sprites = pygame.sprite.Group()
