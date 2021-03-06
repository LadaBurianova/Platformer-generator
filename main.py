import pygame
import os
from sys import exit
import csv

W = 800  # width of window
H = 600  # height of window
FPS = 20

COLOR_INACTIVE = pygame.Color('lightskyblue3')
COLOR_ACTIVE = pygame.Color('dodgerblue2')
COLOR_BG1 = (50, 10, 200)
COLOR_BG2 = (0, 0, 0)


pygame.init()
INPUT_FONT = pygame.font.Font(None, 32)
COMMENT_FONT = pygame.font.Font(None, 40)


def load_image(folder, name):
    """  Loading image.  """
    full_path = os.path.join(folder, name)
    if not os.path.isfile(full_path):
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
                          [[Cell('7', i, 9) for i in range(110)]]
        self.place = None
        self.x = 0
        self.locked = False

    def load_level(self):
        reader = csv.reader(self.opened_f, delimiter=';', quotechar='"')
        y = 0
        for line in reader:
            self.matrix.append(
                [Cell(line[i], i, y) if line[i] != '1' else '1' for i in
                 range(len(line))])
            y += 1
        self.opened_f.close()

    def save_level(self, f_name):
        with open(f_name, 'w', newline='\n', encoding='utf-8') as f_w:
            writer = csv.writer(f_w, delimiter=';', quotechar='\n')
            for line in self.matrix:
                writer.writerow(line)

    def lock(self, pos):
        self.place = pos[0]
        for row in self.matrix:
            for cell in row:
                cell.lock(pos)
        self.locked = True

    def unlock(self):
        for row in self.matrix:
            for cell in row:
                cell.unlock()
        self.locked = False

    def move(self, pos):
        if self.locked:
            for row in self.matrix:
                for cell in row:
                    cell.move(pos)
            shift = pos[0] - self.place
            self.place = pos[0]
            self.x += shift

    def change(self, pos):
        cell = [(pos[0] - self.x) // 60, pos[1] // 60]
        if 0 <= cell[0] < 110 and 0 <= cell[1] < 11:
            self.matrix[cell[1]][cell[0]].switch()


class Cell(pygame.sprite.Sprite):
    EXP = '.png'

    def __init__(self, n, pos_x, pos_y):
        super().__init__(groups_dict[n], cells_sprites, all_sprites)
        self.image = load_image('cells', n + Cell.EXP)
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect().move(60 * pos_x, 60 * pos_y)
        self.shift = 0
        self.locked = False
        self.place = None
        self.all = ['1', '2', '3', '4', '7', '8']
        self.n = self.all.index(n)
        self.pos = [pos_x, pos_y]

    def __repr__(self):
        return str(self.all[self.n])

    def lock(self, pos):
        self.locked = True
        self.place = pos[0]

    def unlock(self):
        self.locked = False

    def move(self, pos):
        if self.locked:
            shift = pos[0] - self.place
            self.rect.x += shift
            self.place = pos[0]

    def switch(self):
        self.n = (self.n + 1) % 6
        self.image = load_image('cells', self.all[self.n] + Cell.EXP)
        self.mask = pygame.mask.from_surface(self.image)


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
        self.image = load_image('right', 'right0001.png')
        self.rect = self.image.get_rect()
        self.rect.x = pos_x
        self.rect.y = pos_y

        self.r_frames = self.load_frames('right')
        self.l_frames = self.load_frames('left')
        self.frames = self.r_frames
        self.cur = 0

        self.vx = 0
        self.vy = 0
        self.g = 10
        self.falling = True
        self.t_falling = 0

    @staticmethod
    def load_frames(directory):
        res = []
        files = os.listdir(os.path.join(os.getcwd(), directory))
        for file in files:
            res.append(load_image(directory, file))
        return res

    def check(self, spr, k):
        return spr.rect.collidepoint(self.rect.x + 40, self.rect.y + k) or \
               spr.rect.collidepoint(self.rect.x, self.rect.y + k)

    def update(self):
        if pygame.sprite.spritecollideany(self, horizontal_borders):
            if self.t_falling:
                self.rect.y = 0
            self.vy = -self.vy
        if pygame.sprite.spritecollideany(self, vertical_borders):
            self.vx = -self.vx

        spr2 = pygame.sprite.spritecollideany(self, full_cells_sprites)
        spr3 = pygame.sprite.spritecollideany(self, down_half_cells_sprites)
        spr4 = pygame.sprite.spritecollideany(self, top_half_cells_sprites)

        if pygame.sprite.spritecollideany(self, green_cells_sprites):
            end('finish_v0.png', False)
            return False

        if pygame.sprite.spritecollideany(self, yellow_cells_sprites):
            end('gameover_v0.png')
            return False

        elif pygame.sprite.spritecollideany(self, cells_sprites):
            k = 59
            if spr2 is not None:
                self.rect.y = self.rect.clip(spr2).y - 89
                if self.check(spr2, k):
                    self.vx = -self.vx

            elif spr4 is not None:
                self.rect.y = self.rect.clip(spr4).y - 89
                if self.check(spr4, k):
                    self.vx = -self.vx

            if spr3 is not None:
                if spr2 is None and spr4 is None:
                    self.rect.y = self.rect.clip(spr3).y - 89
                    self.rect = self.rect.move(0, 30)
                    if not self.t_falling and self.vy < 0:
                        self.rect.y -= 30
                elif self.check(spr3, k) and \
                        not spr3.rect.collidepoint(self.rect.x + 20, self.rect.y + 89):
                    self.vx = -self.vx

            if self.t_falling:
                self.vy = 0
                self.vx = 0
                self.t_falling = 0

        else:
            self.vy += self.g * self.t_falling
            self.t_falling += 0.01
        self.rect = self.rect.move(self.vx, self.vy)
        if not self.vx:
            self.cur = 0
            self.image = self.frames[0]
        else:
            if self.vx > 0:
                self.frames = self.r_frames
            else:
                self.frames = self.l_frames
            if not self.vy:
                self.cur = (self.cur + 1) % len(self.frames)
                self.image = self.frames[self.cur]
        return True


def clear_sprite_groups():
    for nmb in groups_dict:
        pygame.sprite.Group.empty(groups_dict[nmb])
    pygame.sprite.Group.empty(person_sprites)
    pygame.sprite.Group.empty(cells_sprites)
    pygame.sprite.Group.empty(horizontal_borders)
    pygame.sprite.Group.empty(vertical_borders)
    pygame.sprite.Group.empty(all_sprites)


def add_borders():
    horizontal_borders.add(Border(-1, -1, 6601, -1))
    horizontal_borders.add(Border(-1, H + 1, 6601, H + 1))
    vertical_borders.add(Border(-1, -1, -1, H + 1))
    vertical_borders.add(Border(6601, -1, 6601, H + 1))


def end(img, over=True):
    if over:
        pygame.mixer.music.load(os.path.join('vol', 'Determination(From Undertale).wav'))
        pygame.mixer.music.play(loops=-1)
    else:
        pygame.mixer.music.load(os.path.join('vol', 'finish.wav'))
        pygame.mixer.music.play(loops=-1)

    clear_sprite_groups()
    image = pygame.image.load(img)
    screen.fill((0, 0, 0))
    screen.blit(image, (0, 0))
    pygame.display.flip()
    run = True
    while run:
        screen.fill(COLOR_BG2)
        screen.blit(image, (0, 0))
        pygame.display.flip()
        for ev in pygame.event.get():
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_TAB:
                clear_sprite_groups()
                pygame.mixer.music.pause()
                start_screen()
                run = False
            if ev.type == pygame.QUIT:
                pygame.quit()
                exit()


def loaded_level(person, camera):
    pygame.mixer.music.load(os.path.join('vol', 'Another_Medium(From Undertale).wav'))
    pygame.mixer.music.play(loops=-1)
    screen.fill(COLOR_BG2)
    run = True
    clock = pygame.time.Clock()
    while run:
        clock.tick(FPS)
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_TAB:
                    clear_sprite_groups()
                    pygame.mixer.music.pause()
                    start_screen()
                pressed = pygame.key.get_pressed()
                if pressed[pygame.K_d] and pygame.sprite.spritecollideany(person, cells_sprites):
                    person.vx += 8

                if pressed[pygame.K_a] and pygame.sprite.spritecollideany(person, cells_sprites):
                    person.vx -= 8

                if pressed[pygame.K_SPACE]:
                    if person.t_falling == 0:
                        person.vy -= 10

        screen.fill(COLOR_BG2)
        run = person.update()
        camera.update(person)
        for sprite in all_sprites:
            camera.apply(sprite)
        cells_sprites.draw(screen)
        person_sprites.draw(screen)
        pygame.display.flip()


def redactor():
    field = Field()
    screen.fill(COLOR_BG2)
    pygame.mixer.music.load(os.path.join('vol', 'Spooktune.mp3'))
    pygame.mixer.music.play(loops=-1)
    run = True
    clock = pygame.time.Clock()
    while run:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    clear_sprite_groups()
                    pygame.mixer.music.pause()
                    start_screen()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    field.lock(event.pos)
                if event.button == 3:
                    field.change(event.pos)
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    field.unlock()
            elif event.type == pygame.MOUSEMOTION:
                field.move(event.pos)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    pygame.mixer.music.pause()
                    clear_sprite_groups()
                    saving(field)
        screen.fill(COLOR_BG2)
        cells_sprites.draw(screen)
        pygame.display.flip()


def saving(field):
    input_box = pygame.Rect(200, 200, 150, 32)
    text = ''
    color = COLOR_INACTIVE
    active = False
    run = True
    clock = pygame.time.Clock()
    while run:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                exit()
            if ev.type == pygame.MOUSEBUTTONDOWN:
                active, color = change_color(input_box, ev, active)
            if ev.type == pygame.KEYDOWN:
                if active:
                    if ev.key == pygame.K_RETURN:
                        if not text == '':
                            field.save_level(text)
                            start_screen()
                    elif ev.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        text += ev.unicode
        screen.fill((30, 30, 30))
        txt_surface = INPUT_FONT.render(text, True, color)
        comment = ['* Чтобы сохранить карту,',
                   '        1. ведите имя файла,',
                   '        2. нажмите enter.', '',
                   '  После этого вы вернётесь на главный экран.']
        display_text(comment, 300, COMMENT_FONT)
        input_box.w = max(200, txt_surface.get_width() + 10)
        screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
        pygame.draw.rect(screen, color, input_box, 2)
        pygame.display.flip()
        clock.tick(FPS)


def start_screen():
    input_box = pygame.Rect(100, 100, 150, 32)
    text = ''
    color = COLOR_INACTIVE
    active = False
    run = True
    clock = pygame.time.Clock()
    while run:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                exit()
            if ev.type == pygame.MOUSEBUTTONDOWN:
                active, color = change_color(input_box, ev, active)
            if ev.type == pygame.KEYDOWN:
                if active:
                    if ev.key == pygame.K_RETURN:
                        if text != '':
                            try:
                                with open(text, 'r', encoding='utf-8') as f:
                                    camera = Camera()
                                    Field(f)
                                    add_borders()
                                    person = Person(0, 1)
                                    person.add(person_sprites)
                                    loaded_level(person, camera)
                            except FileNotFoundError:
                                text = ''
                        else:
                            redactor()
                    elif ev.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        text += ev.unicode
        screen.fill((30, 30, 30))
        txt_surface = INPUT_FONT.render(text, True, color)
        input_box.w = max(200, txt_surface.get_width() + 10)
        comment = ['* Чтобы создать карту,',
                   '        1. нажмите на прямоугольную область,',
                   '        2. нажмите enter.', '',
                   '* Чтобы загрузить готовую карту,',
                   '        1. нажмите на прямоугольную область,',
                   '        2. введите название файла,',
                   '        3. нажмите enter.']
        display_text(comment, 200, COMMENT_FONT)
        screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
        pygame.draw.rect(screen, color, input_box, 2)
        pygame.display.flip()
        clock.tick(FPS)


def display_text(text_to_display, text_coord, font):
    for line in text_to_display:
        string_rendered = font.render(line, True, COLOR_INACTIVE)
        intro_rect = string_rendered.get_rect()
        text_coord += 12
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)


def change_color(input_box, ev, active):
    if input_box.collidepoint(ev.pos):
        active = not active
    else:
        active = False
    color = COLOR_ACTIVE if active else COLOR_INACTIVE
    return active, color


all_sprites = pygame.sprite.Group()
cells_sprites = pygame.sprite.Group()
yellow_cells_sprites = pygame.sprite.Group()
green_cells_sprites = pygame.sprite.Group()
full_cells_sprites = pygame.sprite.Group()
top_half_cells_sprites = pygame.sprite.Group()
down_half_cells_sprites = pygame.sprite.Group()
empty_cells_sprites = pygame.sprite.Group()

person_sprites = pygame.sprite.Group()
horizontal_borders = pygame.sprite.Group()
vertical_borders = pygame.sprite.Group()

groups_dict = {'2': full_cells_sprites, '3': down_half_cells_sprites,
               '4': top_half_cells_sprites, '7': yellow_cells_sprites,
               '8': green_cells_sprites, '1': empty_cells_sprites}

pygame.mixer.init()
pygame.mixer.music.set_volume(0.2)
screen = pygame.display.set_mode((W, H))
screen.fill(COLOR_BG1)
start_screen()
pygame.quit()
