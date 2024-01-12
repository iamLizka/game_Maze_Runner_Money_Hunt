import pygame
import os
import sys
import random
import pygame.gfxdraw

import screensaver
from const import *
from screensaver import *

"""загрузка изображения"""
def load_image(name, size=None, colorkey=None):
    fullname = os.path.join('data', name)
    # проверяем существует ли такой файл
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    # при необходимости убираем фон
    if colorkey is not None:
        colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    if size:
        image = pygame.transform.scale(image, (size[0], size[1]))
    # возврашаем изображение
    return image


"""загрузка уровня"""
def load_level(filename):
    filename = "data/" + filename
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))

    # дополняем каждую строку пустыми клетками ('.')
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


"""рисование всех предметов на карте уровня"""
def generate_level(level, ghost_image):
    ghost, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '#':
                Wall('wall', x, y)
            elif level[y][x] == '.':
                Grass('grass', x, y)
            elif level[y][x] == '$':
                Grass('grass', x, y)
                ghost = Ghost(ghost_image, x, y)
    # вернем призраков, а также размер поля в клетках
    return ghost, x, y


"""разрезание листа с анимацией игрока"""
def cut_sheet(sheet, columns, rows):
    frames = []
    rect = pygame.Rect(40, 40, sheet.get_width() // columns, sheet.get_height() // rows)
    for j in range(rows):
        for i in range(columns):
            frame_location = (rect.w * i, rect.h * j)
            frames.append(sheet.subsurface(pygame.Rect(frame_location, rect.size)))
    # возвращаем список со всеми обрезанными изображениями
    return frames


"""заставка в конце игры"""
def show_game_over(screen, full_screen):
    stepx, stepy = 0, 0
    if full_screen:
        stepx, stepy = STEP_SCREEN_X * 2, STEP_SCREEN_Y * 2
    text = "GAME OVER"
    font = pygame.font.Font(None, 130)
    string_rendered = font.render(text, 1, pygame.Color('red'))
    intro_rect = string_rendered.get_rect()
    intro_rect.x = 270 + stepx
    intro_rect.y = 300 + stepy
    screen.blit(string_rendered, intro_rect)


# определяем координаты пули и создаем ее
def attack(move_attack, bullet_image, player_coords):
    x = player_coords[0] + 15
    y = player_coords[1] + 20
    Bullet(bullet_image, x, y, move_attack)


"""создание спрайта стены"""
class Wall(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(walls_sprites, all_sprites)
        image1 = blocks_images[tile_type]
        self.image = pygame.transform.scale(image1, (size_block, size_block))
        self.rect = self.image.get_rect().move(
            size_block * pos_x, size_block * pos_y)

    # для обновления координат объекта во время смены режима экрана
    def update_coords(self, step):
        self.rect = self.rect.move(step[0], step[1])


"""создание спрайта травы"""
class Grass(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(grass_sprites, all_sprites)
        image1 = blocks_images[tile_type]
        self.image = pygame.transform.scale(image1, (size_block, size_block))
        self.rect = self.image.get_rect().move(
            size_block * pos_x, size_block * pos_y)

    # для обновления координат объекта во время смены режима экрана
    def update_coords(self, step):
        self.rect = self.rect.move(step[0], step[1])


"""создание спрайта игрока"""
class Player(pygame.sprite.Sprite):
    def __init__(self, player_image, pos_x, pos_y):
        super().__init__(player_sprite, all_sprites)
        self.image = player_image
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = size_block * pos_x
        self.rect.y = size_block * pos_y
        self.count_money = 0
        self.count_lifes = 3

        # индексы в списки с анимацией относительно направления движения игрока
        self.animation_right = [9, 10, 11]
        self.animation_left = [6, 7, 8]
        self.animation_up = [3, 4, 5]
        self.animation_down = [0, 1, 2]

    # изменение количества денег у игрока
    def update_count_money(self, count):
        self.count_money += count

    # получение количества денег у игрока
    def get_count_money(self):
        return self.count_money

    # изменение количества жизней у игрока
    def update_count_lifes(self, count):
        self.count_lifes += count

    # получение количества жизней у игрока
    def get_count_lifes(self):
        return self.count_lifes

    # для обновления координат объекта во время смены режима экрана
    def update_coords(self, step):
        self.rect = self.rect.move(step[0], step[1])

    # координаты игрока
    def get_coords(self):
        return self.rect.x, self.rect.y

    # меняем изображение игрока относительно его движения
    def animation(self, sheet, move):
        if move == "D":
            self.change_image(sheet[self.animation_down[0]])  # ставим первую в списке анимаций изображение
            self.animation_down.append(self.animation_down[0])  # добавляем ее в конец списка
            self.animation_down.pop(0)  # удаляем первое изображение из списка
        elif move == "U":
            self.change_image(sheet[self.animation_up[0]])  # анологично
            self.animation_up.append(self.animation_up[0])
            self.animation_up.pop(0)
        elif move == "L":
            self.change_image(sheet[self.animation_left[0]])
            self.animation_left.append(self.animation_left[0])
            self.animation_left.pop(0)
        elif move == "R":
            self.change_image(sheet[self.animation_right[0]])
            self.animation_right.append(self.animation_right[0])
            self.animation_right.pop(0)

    # смена изображения игрока
    def change_image(self, image):
        self.image = image

    # изменение положения игрока на поле
    def update(self, step):
        self.rect = self.rect.move(step[0], step[1])  # сначала перемещаем игрока
        if pygame.sprite.spritecollideany(self, walls_sprites):  # если игрок касается стен, то перемещаем его обратно
            self.rect = self.rect.move(-step[0], -step[1])
        if pygame.sprite.spritecollideany(self, ghost_sprites):  # если игрок сталкивается с призраком, то игра окончена
            self.rect = self.rect.move(-step[0], -step[1])

        if pygame.sprite.spritecollide(self, money_sprites, True):  # если игрок сталкивается с призраком, то игра окончена
            self.count_money += 50


"""создание спрайта призрака"""
class Ghost(pygame.sprite.Sprite):
    def __init__(self, ghost_image, pos_x, pos_y):
        super().__init__(ghost_sprites, all_sprites)
        self.image = ghost_image
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = size_block * pos_x
        self.rect.y = size_block * pos_y

        # индексы в списки с анимацией относительно направления движения призрака
        self.animation_right = [6, 7, 8]
        self.animation_left = [3, 4, 5]
        self.animation_up = [9, 10, 11]
        self.animation_down = [0, 1, 2]

        self.direction = None

    # для обновления координат объекта во время смены режима экрана
    def update_coords(self, step):
        self.rect = self.rect.move(step[0], step[1])

    # меняем изображение призрака относительно его движения
    def animation(self, sheet, move):
        if move == "D":
            self.change_image(sheet[self.animation_down[0]])  # ставим первую в списке анимаций изображение
            self.animation_down.append(self.animation_down[0])  # добавляем ее в конец списка
            self.animation_down.pop(0)  # удаляем первое изображение из списка
        elif move == "U":
            self.change_image(sheet[self.animation_up[0]])  # анологично
            self.animation_up.append(self.animation_up[0])
            self.animation_up.pop(0)
        elif move == "L":
            self.change_image(sheet[self.animation_left[0]])
            self.animation_left.append(self.animation_left[0])
            self.animation_left.pop(0)
        elif move == "R":
            self.change_image(sheet[self.animation_right[0]])
            self.animation_right.append(self.animation_right[0])
            self.animation_right.pop(0)

    # смена изображения призрака
    def change_image(self, image):
        self.image = image

    # определяем направление призрака
    def choice_direction(self):
        self.direction = random.choice(["R", "L", "U", "D"])
        if self.direction == "R":
            self.step = (STEP_GHOST, 0)
        elif self.direction == "L":
            self.step = (-STEP_GHOST, 0)
        elif self.direction == "U":
            self.step = (0, -STEP_GHOST)
        elif self.direction == "D":
            self.step = (0, STEP_GHOST)

    # изменение положения призрака на поле
    def update(self, timer):
        # флаг для работы выбора направления движения призрака,
        # если Folse значит направление выбрано, иначе продолжаем искать
        can = True
        while can:

            #  проверяем выбрано ли уже направление, если нет, то запускаем функцию для рандомного выбора
            if not self.direction:
                self.choice_direction()
            self.rect = self.rect.move(self.step[0], self.step[1])  # сначала перемещаем призрака

            # если призрак касается стен, то перемещаем его обратно
            if pygame.sprite.spritecollideany(self, walls_sprites):
                self.rect = self.rect.move(-self.step[0], -self.step[1])
                self.direction = None  # значит направление не подошло, повторяем все заново

            # если призрак сталкивается с игроком, то игра окончена
            if pygame.sprite.spritecollideany(self, player_sprite):
                self.rect = self.rect.move(-self.step[0], -self.step[1])

                if (pygame.time.get_ticks() - timer.get_timer()) // 1000 > 0.5:
                    timer.new_timer()
                    player.update_count_money(-50)
                    player.update_count_lifes(-1)

                self.direction = None  # значит направление не подошло, повторяем все заново

            #  проверяем не сталкивается ли призрак с другими призраками, если да, то проделываеем все также
            for sprite in pygame.sprite.spritecollide(self, ghost_sprites, False):
                if sprite is not self:
                    self.rect = self.rect.move(-self.step[0], -self.step[1])
                    self.direction = None
            else:
                can = False  # значит направление выбрано
        return self.direction  # возвращаем направление движения


"""класс таймера для отсчета времени, когда игрок касается призрака"""
class Timer:
    def __init__(self):
        self.start_ticks = pygame.time.get_ticks()

    def get_timer(self):
        return self.start_ticks

    def new_timer(self):
        self.start_ticks = pygame.time.get_ticks()


"""класс камеры для ослеживания положения игрока на поле"""
class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self):
        self.dx = 0
        self.dy = 0

    # координаты передаваемого блока
    def get_coord_block(self, block):
        return block.rect.x, block.rect.y

    # сдвигаем объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    # позиционируем камеру относительно движения объекта
    def update(self, target, old, coord_block, step_player):

        # если игрок находиться в левой части экрана и движеться влево,
        # то проверяем где находится блок стены с координатами (0, 0)
        if target.rect.x <= 250 and step_player[0] < 0:

            if coord_block[0][0] != 0:  # если координата х блока не равна 0, то делаем смещение для всех объектов
                self.dx = old[0] - target.rect.x

            elif coord_block[0][0] == 0:  # если координата х блока равна 0, то смщение не делаем
                self.dx = 0

        # если игрок находиться в правой части экрана и движеться вправо,
        # то проверяем где находится блок стены с координатами (WIDTH_SCREEN - size_block, HEIGHT_SCREEN - size_block),
        # т.е. самого правого нижнего блока
        elif target.rect.x >= WIDTH_SCREEN - 250 and step_player[0] > 0:
            # если координата х блока не равна (WIDTH_SCREEN - size_block), то делаем смещение для всех объектов
            if coord_block[1][0] != WIDTH_SCREEN - size_block:
                self.dx = old[0] - target.rect.x

            # если координата х блока равна (WIDTH_SCREEN - size_block), то смщение не делаем
            elif coord_block[1][0] == WIDTH_SCREEN - size_block:
                self.dx = 0

        # если игрок находиться в верхней части экрана и движеться вверх,
        # то проверяем где находится блок стены с координатами (0, 0)
        elif target.rect.y <= 200 and step_player[1] < 0:

            if coord_block[0][1] != 0:  # если координата у блока не равна 0, то делаем смещение для всех объектов
                self.dy = old[1] - target.rect.y

            elif coord_block[0][1] == 0:  # если координата у блока равна 0, то смщение не делаем
                self.dy = 0

        # если игрок находиться в нижней части экрана и движеться вниз,
        # то проверяем где находится блок стены с координатами (WIDTH_SCREEN - size_block, HEIGHT_SCREEN - size_block),
        # т.е. самого правого нижнего блока
        elif target.rect.y >= HEIGHT_SCREEN - 200 and step_player[1] > 0:

            # если координата у блока не равна (HEIGHT_SCREEN - size_block), то делаем смещение для всех объектов
            if coord_block[1][1] != HEIGHT_SCREEN - size_block:
                self.dy = old[1] - target.rect.y

            # если координата у блока равна (HEIGHT_SCREEN - size_block), то смщение не делаем
            elif coord_block[1][1] == HEIGHT_SCREEN - size_block:
                self.dy = 0
        else:
            self.dx = 0
            self.dy = 0


"""создание спрайта пули игрока"""
class Bullet(pygame.sprite.Sprite):
    def __init__(self, bullet_image, pos_x, pos_y, move):
        super().__init__(bullet_sprites, all_sprites)
        self.image = bullet_image
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = pos_x
        self.rect.y = pos_y
        self.find_step_bullet(move)

    # для обновления координат объекта во время смены режима экрана
    def update_coords(self, step):
        self.rect = self.rect.move(step[0], step[1])

    # определяем шаг пули, исходя из напраления движения
    def find_step_bullet(self, move_attack):
        if move_attack == "D":
            self.step = (0, SPEED_BULLET)
        elif move_attack == "U":
            self.step = (0, -SPEED_BULLET)
        elif move_attack == "R":
            self.step = (SPEED_BULLET, 0)
        elif move_attack == "L":
            self.step = (-SPEED_BULLET, 0)

    # изменение положения пули на поле
    def update(self):
        self.rect = self.rect.move(self.step[0], self.step[1])  # сначала перемещаем пулю
        if pygame.sprite.spritecollideany(self, walls_sprites):  # если пуля касается стен, то удаляем ее
            self.kill()

        # если пуля сталкивается с призраком, то удаляем призрака и пулю
        if pygame.sprite.spritecollide(self, ghost_sprites, True):
            self.kill()


"""создание спрайта денег"""
class Money(pygame.sprite.Sprite):
    def __init__(self, money_image, pos_x, pos_y):
        super().__init__(money_sprites, all_sprites)
        self.image = money_image
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = pos_x + 10
        self.rect.y = pos_y + 15

    # для обновления координат объекта во время смены режима экрана
    def update_coords(self, step):
        self.rect = self.rect.move(step[0], step[1])


"""функция проверяет можно ли делать в этой клетке карты деньги (если эта клетка - трава, то можно)"""
def create_money(level, money_image, pos_x, pos_y, full_screen):
    if level[pos_y][pos_x] == '.':
        if full_screen:
            Money(money_image, pos_x * size_block + STEP_SCREEN_X, pos_y * size_block + STEP_SCREEN_Y)
        else:
            Money(money_image, pos_x * size_block, pos_y * size_block)


"""разворачивает или сворачивает окно игры"""
def full_screen_mode(mode):
    #  сворачиваем экран
    if mode:
        display = (pygame.display.Info().current_w, pygame.display.Info().current_h)  # разрешение экрана пк
        block_coords = camera.get_coord_block(walls_sprites.sprites()[-1])  # координаты самого правого нижнего блока
        pygame.display.set_mode((WIDTH_SCREEN, HEIGHT_SCREEN))  # меняем размер окна

        # если игрок находился в левой части карты при развернутом экране и коордю. х < WIDTH_SCREEN // 2
        # (т.е. меньше половины свернутого экрана), тогда изменение по х = 0
        if WIDTH_SCREEN // 2 > player.rect.x and player.rect.x < display[0] // 2:
            dx = 0

        # если игрок находился в правой части карты при развернутом экране и
        # расстояние display[0] - player.rect.x (т.е. расстояние от игрока до правой стены карты) < WIDTH_SCREEN // 2
        elif WIDTH_SCREEN // 2 > display[0] - player.rect.x and player.rect.x > display[0] // 2:
            # из коорд. крайнего блока вычитаем оступ и ширину экраана и прибавляем размер блока
            dx = block_coords[0] - STEP_SCREEN_X - WIDTH_SCREEN + size_block

        # если игрок находился в левой части карты при развернутом экране и коордю. х > WIDTH_SCREEN // 2
        # (т.е. меньше половины свернутого экрана), тогда изменение по х = 0
        elif player.rect.x < display[0] // 2:
            # из коорд. х игрока вычитаем половину свернутого экрана, а дальше делим
            # и умножаем на size_block, чтобы dx нацело делилось на size_block
            dx = (player.rect.x - WIDTH_SCREEN // 2) // size_block * size_block

        # если игрок находился в правой части карты при развернутом экране и расстояние
        # display[0] - player.rect.x (т.е. расстояние от игрока до правой стены карты) > WIDTH_SCREEN // 2
        else:
            # из коорд.крайнего блока ширину экрана, а дальше делим
            # и умножаем на size_block, чтобы dx нацело делилось на size_block
            dx = (block_coords[0] - WIDTH_SCREEN) // size_block * size_block - size_block

        # дальше по такому же принципу только с координами y
        if HEIGHT_SCREEN // 2 > player.rect.y and player.rect.y < display[1] // 2:
            dy = 0
        elif HEIGHT_SCREEN // 2 > display[1] - player.rect.y and player.rect.y > display[1] // 2:
            dy = block_coords[1] - STEP_SCREEN_Y - HEIGHT_SCREEN + size_block
        elif player.rect.y < display[1] // 2:
            dy = 0
        else:
            dy = (block_coords[1] - HEIGHT_SCREEN) // size_block * size_block - size_block

        for sprite in all_sprites:
            sprite.update_coords((-(dx + STEP_SCREEN_X), -(dy + STEP_SCREEN_Y)))  # передаем в метод спрайта смещение
        return False  # возвращаем False, так как экран свернули

    # разворачиваем экран
    else:
        pygame.display.set_mode((0, 0), pygame.FULLSCREEN)  # меняем размер окна
        coords_1 = camera.get_coord_block(all_sprites.sprites()[0])  # коорд. самого левого вернего блока
        for sprite in all_sprites:
            sprite.update_coords((abs(coords_1[0]) + STEP_SCREEN_X, abs(coords_1[1]) + STEP_SCREEN_Y))
        return True  # возвращаем True, так как экран свернули


"""рисование в углу окна количества денег и жизней"""
def draw_results(screen, image_money, image_heart, count_hearts, full_screen):
    stepx, stepy = 0, 0  # оступ, зависит от развернуто ли окно или нет
    if full_screen:
        stepx, stepy = STEP_SCREEN_X * 2.5, STEP_SCREEN_Y

    # отрисовка полупрозрачного прямоугольника (в нем будет вся инфа)
    pygame.gfxdraw.box(screen, pygame.Rect(WIDTH_SCREEN - 150 + stepx, 20 + stepy, 120, 70), (0, 0, 0, 130))
    screen.blit(image_money, (WIDTH_SCREEN - 140 + stepx, 35 + stepy))  # отрисовка изображения купюры
    step_heart = 0
    for _ in range(count_hearts):
        screen.blit(image_heart, (WIDTH_SCREEN - 140 + step_heart + stepx, 55 + stepy))  # отрисовка сердец
        step_heart += 30

    font = pygame.font.Font(None, 25)
    string_rendered = font.render(str(player.get_count_money()), 1, pygame.Color(255, 255, 255))
    intro_rect = string_rendered.get_rect()
    intro_rect.x = WIDTH_SCREEN - 95 + stepx
    intro_rect.y = 35 + stepy
    screen.blit(string_rendered, intro_rect)  # отрисока количества денег игроока


"""основная функция"""
def main():
    pygame.init()

    screen = pygame.display.set_mode(size)
    timer = Timer()

    step, move = None, "D"

    running = True  # флаг для основного цикла
    moving_player = False  # флаг для обозначения движется ли игрока
    game_playing = True  # флаг для обозначения окончена ли игры
    full_screen = False  # флаг для обозначения развернуто ли окно игры
    game_over = False
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False


            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_r:
                    attack(move, bullet_image, player.get_coords())  # запускаем функцию по созданию пули

                if event.key == pygame.K_ESCAPE:
                    full_screen = full_screen_mode(full_screen)  # передаем включен ли full_screen режим

                if event.key == pygame.K_RIGHT:
                    step, move = (STEP_PLAYER, 0), "R"
                    moving_player = True
                if event.key == pygame.K_LEFT:
                    step, move = (-STEP_PLAYER, 0), "L"
                    moving_player = True
                if event.key == pygame.K_UP:
                    step, move = (0, -STEP_PLAYER), "U"
                    moving_player = True
                if event.key == pygame.K_DOWN:
                    step, move = (0, STEP_PLAYER), "D"
                    moving_player = True

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT\
                        or event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                    moving_player = False
                    player.change_image(frames_player[0])

        screen.fill("#808080")

        if game_playing:

            old_coords = player.get_coords()  # координаты игрока перед ходом

            for sprite in bullet_sprites:  # обновление координат всех пуль
                sprite.update()

            if moving_player:
                player.update(step)
                # передаем в метод анимации игрока список с изображениями(анимация сама) и направление движения
                player.animation(frames_player, move)

                # координаты левого верхнего блока карты и правого нижнего блока
                coords_block = [camera.get_coord_block(walls_sprites.sprites()[0]),
                                  camera.get_coord_block(walls_sprites.sprites()[-1])]

                # обновляем положение камеры, если выключен полноэкранный режим,
                # передавая ей игрока, старые координаты игрока координаты блоков и смещение иг.
                if not full_screen:
                    camera.update(player, old_coords, coords_block, step)

                for sprite in all_sprites:  # обновление координат всех спрайтов
                    camera.apply(sprite)

            for sprite in ghost_sprites:  # обновление координат всех призраков
                move_ghost = sprite.update(timer)
                sprite.animation(frames_ghost, move_ghost)  # анимация призрака

            while len(money_sprites) < MAX_COUNT_MONEY:
                create_money(level, money_image, random.randint(0, level_x), random.randint(0, level_y), full_screen)

            if player.get_count_lifes() == 0:
                game_playing = False
        else:
            game_over = True

        # отрисовка всех объектов
        all_sprites.draw(screen)
        player_sprite.draw(screen)
        ghost_sprites.draw(screen)
        bullet_sprites.draw(screen)

        if game_over:
            show_game_over(screen, full_screen)

        draw_results(screen, money_image_result, heart_image, player.get_count_lifes(), full_screen)

        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()


size = WIDTH_SCREEN, HEIGHT_SCREEN

#  словарь с изображениями стены и травы
blocks_images = {"wall": load_image("wall.png", (size_block, size_block), -1),
                 "grass": load_image("grass.png", (size_block, size_block), -1)}

# создание групп спрайтов
all_sprites = pygame.sprite.Group()
grass_sprites = pygame.sprite.Group()
walls_sprites = pygame.sprite.Group()
ghost_sprites = pygame.sprite.Group()
player_sprite = pygame.sprite.Group()
bullet_sprites = pygame.sprite.Group()
money_sprites = pygame.sprite.Group()

frames_player = cut_sheet(load_image("player.png", (120, 160), -1), 3, 4)  # список с анимацией игрока
frames_ghost = cut_sheet(load_image("ghost.png", (110, 150), -1), 3, 4)  # список с анимацией призрака
bullet_image = load_image("bullet.png", (10, 10), -1)  # загрузка изображения пули
money_image = load_image("money_50.jpg", (20, 10), -1)
money_image_result = load_image("money_50.jpg", (35, 15), -1)
heart_image = load_image("heart.png", (30, 30), -1)

level = load_level("level_1.txt")
# здесь получаем призраков и размеры поля в клетках
ghost, level_x, level_y = generate_level(level, frames_ghost[0])

camera = Camera()  # создаем камеры
player = Player(frames_player[0], 1, 1)  # создаем игрока

while len(money_sprites) != MAX_COUNT_MONEY:
    create_money(level, money_image, random.randint(0, level_x), random.randint(0, level_y), False)

clock = pygame.time.Clock()
FPS = 15

if __name__ == "__main__":
    screensaver.screensaver_game()
