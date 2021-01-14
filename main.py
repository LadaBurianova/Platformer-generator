import pygame
from os.path import join, isfile
from sys import exit
import csv

W = 800  # width of window
H = 600  # height of window
FPS = 20


def load_image(folder, name):
    """  Loading image.  """
    full_path = join(folder, name)
    if not isfile(full_path):
        print(f"Файл '{full_path}' не найден")
        exit()
    return pygame.image.load(full_path)


class Field:
    """There are 2 modes of __init__.
    1) Loading a map from file. This is default mode.
       Variable opened_map_file is None in this mode. The map will be loaded from the file lv_filename.
    2) Creating new map. Variable opened_map_file is not None. Use self.save_level function to save the map.  """

    def __init__(self, opened_map_file=None):
        self.opened_f = opened_map_file
        if self.opened_f is not None:
            self.matrix = []
            self.load_level()
        else:
            self.matrix = [[Cell('1', i, j) for i in range(110)] for j in range(9)] + \
                          [[Cell('7', i, 110)] for i in range(110)]

    def load_level(self):
        reader = csv.reader(self.opened_f, delimiter=';', quotechar='"')
        y = 0
        for line in reader:
            self.matrix.append([Cell(line[i], i, y) if line[i] != '1' else '1' for i in range(len(line))])
            y += 1
        self.opened_f.close()

    def save_level(self, f_name):
        with open(f_name, 'w', encoding='utf-8') as f_w:
            writer = csv.writer(f_w, delimiter=';', quotechar='"')
            for line in self.matrix:
                writer.writerow(line)


class Cell(pygame.sprite.Sprite):
    EXP = '.png'

    def __init__(self, n, pos_x, pos_y):
        self.n = n
        if n == '7':
            super().__init__(yellow_cells_sprites, cells_sprites, all_sprites)
        else:
            super().__init__(cells_sprites, all_sprites)
        self.image = load_image('cells', n + Cell.EXP)
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect().move(60 * pos_x, 60 * pos_y)


class Border(pygame.sprite.Sprite):
    def __init__(self, x1, y1, x2, y2):
        super().__init__(all_sprites)
        if x1 == x2:
            self.add(vertical_borders)
            self.image = pygame.Surface([1, y2 - y1])
            self.rect = pygame.Rect(x1, y1, 1, y2 - y1)
        else:
            self.add(horizontal_borders)
            self.image = pygame.Surface([x2 - x1, 1])
            self.rect = pygame.Rect(x1, y1, x2 - x1, 1)


class Camera:
    def __init__(self):
        self.dx = 0

    def apply(self, obj):
        obj.rect.x += self.dx

    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - W // 2)


class Person(pygame.sprite.Sprite):
    EXP = '.png'  # expansion

    def __init__(self, pos_x, pos_y):
        super().__init__(person_sprites, all_sprites)
        self.image = load_image('person', 'pre-person.png')  # TODO: change pre-person.png to n + Cell.EXP

        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = pos_x
        self.rect.y = pos_y
        self.field = field
        self.vx = 0
        self.vy = 0
        self.g = 10
        self.falling = True
        self.t_falling = 0

    def update(self):
        if pygame.sprite.spritecollideany(self, horizontal_borders):
            self.vy = -self.vy
        if pygame.sprite.spritecollideany(self, vertical_borders):
            self.vx = -self.vx

        if pygame.sprite.spritecollideany(self, green_cells_sprites):
            print('you_win')

        elif pygame.sprite.spritecollideany(self, yellow_cells_sprites):
            end('gameover_v0.png')
            start_screen()

        elif pygame.sprite.spritecollideany(self, cells_sprites):
            if self.t_falling:
                self.vy = 0
                self.vx = 0
                self.t_falling = 0

        else:
            self.vy += self.g * self.t_falling
            self.t_falling += 0.01
        self.rect = self.rect.move(self.vx, self.vy)


def start_screen():
    pass


def end(img):
    image = pygame.image.load(img)
    screen.fill((0, 0, 0))
    screen.blit(image, (0, 0))
    pygame.display.flip()
    run = True
    while run:
        screen.fill((0, 0, 0))
        screen.blit(image, (0, 0))
        pygame.display.flip()
        for ev in pygame.event.get():
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_TAB:
                run = False
            if ev.type == pygame.QUIT:
                pygame.quit()
                exit()


def loaded_level():
    run = True
    clock = pygame.time.Clock()
    while run:
        clock.tick(FPS)
        for ev in pygame.event.get():
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_TAB:
                    break
                pressed = pygame.key.get_pressed()
                if pressed[pygame.K_d] and pygame.sprite.spritecollideany(person, cells_sprites):
                    person.vx += 5

                if pressed[pygame.K_a] and pygame.sprite.spritecollideany(person, cells_sprites):
                    person.vx -= 5

                if pressed[pygame.K_SPACE]:
                    person.vy -= 10
                    person.t_falling = 0

        screen.fill((0, 0, 0))
        all_sprites.update()
        camera.update(person)
        for sprite in all_sprites:
            camera.apply(sprite)
        cells_sprites.draw(screen)
        person_sprites.draw(screen)
        pygame.display.flip()


all_sprites = pygame.sprite.Group()
cells_sprites = pygame.sprite.Group()
yellow_cells_sprites = pygame.sprite.Group()
green_cells_sprites = pygame.sprite.Group()
person_sprites = pygame.sprite.Group()
horizontal_borders = pygame.sprite.Group()
vertical_borders = pygame.sprite.Group()
horizontal_borders.add(Border(-1, -1, 6601, -1))
horizontal_borders.add(Border(-1, H + 1, 6601, H + 1))
vertical_borders.add(Border(-1, -1, -1, H + 1))
vertical_borders.add(Border(6601, -1, 6601, H + 1))

pygame.init()
screen = pygame.display.set_mode((W, H))
screen.fill((50, 10, 200))

input_box = pygame.Rect(100, 100, 150, 32)
font = pygame.font.Font(None, 32)
text = ''
color_inactive = pygame.Color('lightskyblue3')
color_active = pygame.Color('dodgerblue2')
color = color_inactive
active = False

run = True
clock = pygame.time.Clock()

while run:
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            run = False
        if ev.type == pygame.MOUSEBUTTONDOWN:
            if input_box.collidepoint(ev.pos):
                active = not active
            else:
                active = False
            color = color_active if active else color_inactive
        if ev.type == pygame.KEYDOWN:
            if active:
                if ev.key == pygame.K_RETURN:
                    try:
                        with open(text, 'r', encoding='utf-8') as f:
                            camera = Camera()
                            field = Field(f)
                            person = Person(0, 50)
                            person.add(person_sprites)
                            loaded_level()
                    except FileNotFoundError:
                        text = ''
                elif ev.key == pygame.K_BACKSPACE:
                    text = text[:-1]
                else:
                    text += ev.unicode
    screen.fill((30, 30, 30))
    txt_surface = font.render(text, True, color)
    input_box.w = max(200, txt_surface.get_width() + 10)
    screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
    pygame.draw.rect(screen, color, input_box, 2)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
