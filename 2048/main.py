import copy
import random
import sys

import pygame

from config import CAPTION, SCREEN_SIZE, SCREEN_FPS, GRID_LEN, SPACE_LEN, ROW_SIZE, INIT_EGG_AMOUNT
from config import SCREEN_BG_COLOR, BLOCK_COLOR, CANVAS_COLOR
from config import FONT_FAMILY, FONT_SIZE, FONT_COLOR


class BaseRoundRect(pygame.sprite.Sprite):
    def __init__(self, center_x, center_y, width, height, color, roundness=0):
        pygame.sprite.Sprite.__init__(self)
        self.origin_image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.origin_image.fill(color)
        self.image = self.origin_image
        self.color = color
        self.roundness = roundness

        # 圆角
        self.rect_image = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)
        pygame.draw.rect(self.rect_image, self.color, (0, 0, *self.image.get_size()), border_radius=self.roundness)
        self.image = self.origin_image.copy().convert_alpha()
        self.image.blit(self.rect_image, (0, 0), None, pygame.BLEND_RGBA_MIN)

        self.origin_image = self.image
        self.rect = self.image.get_rect()
        self.rect.center = center_x, center_y


class TextBlock(BaseRoundRect):
    def __init__(self, center_x, center_y, width, height, color=BLOCK_COLOR, roundness=0):
        BaseRoundRect.__init__(self, center_x, center_y, width, height, color, roundness)

    def write(self, content, font_family=FONT_FAMILY, font_size=FONT_SIZE, font_color=FONT_COLOR):
        content = str(content) if content != 0 else '   '
        font_size = int(font_size * (1 - len(content) / 10))
        font = pygame.font.SysFont(font_family, font_size)
        text_image = font.render(content, True, font_color, self.color)
        self.image = self.origin_image.copy()
        self.image.blit(text_image, (self.rect.width/2 - text_image.get_width()/2, self.rect.height/2 - text_image.get_height()/2))


class Matrix(object):
    def __init__(self, rows, cols, init_egg_amount=INIT_EGG_AMOUNT):
        self.rows, self.cols, self.init_egg_amount = rows, cols, init_egg_amount
        self.vals, self.last_vals, self.score = None, None, None
        self.reset()

    def __str__(self):
        return '\n'.join([str(self.vals[i]) for i in range(self.rows)])

    def reset(self):
        self.vals = [[0 * i * j for i in range(self.rows)] for j in range(self.cols)]
        self.last_vals = [[]]
        self.score = 0

        for i in range(self.init_egg_amount):
            self.lay()

    def is_full(self):
        for i in range(self.rows):
            for j in range(self.cols):
                if self.vals[i][j] == 0:
                    return False
        return True

    def is_changed(self):
        return self.vals != self.last_vals

    def is_movable(self):
        if not self.is_full():
            return False
        for i in range(self.rows - 1):
            for j in range(self.cols):
                if self.vals[i][j] == self.vals[i + 1][j]:
                    return False
        for j in range(self.cols - 1):
            for i in range(self.rows):
                if self.vals[i][j] == self.vals[i][j + 1]:
                    return False
        return True

    def move_up(self):
        self.last_vals = copy.deepcopy(self.vals)
        # 将数字向上聚拢，挤出 0
        for j in range(self.cols):
            # 第一次双指针挤出 0 值，k为非零数字数量
            k = 0
            for i in range(self.rows):
                if self.vals[i][j] != 0:
                    self.vals[k][j] = self.vals[i][j]
                    k += 1

            # 将后续空位置零
            for ii in range(k, self.rows):
                self.vals[ii][j] = 0

            # 相邻等值相加赋给前者，后者置零
            i = 1
            while i < k:
                if self.vals[i - 1][j] == self.vals[i][j]:
                    self.vals[i - 1][j] *= 2
                    self.vals[i][j] = 0
                    self.score += self.vals[i - 1][j]
                i += 1

            # 第二次双指针挤出 0 值，k为非零数字数量
            k = 0
            for i in range(self.rows):
                if self.vals[i][j] != 0:
                    self.vals[k][j] = self.vals[i][j]
                    k += 1

            # 将后续空位置零
            for ii in range(k, self.rows):
                self.vals[ii][j] = 0

    def move_down(self):
        self.last_vals = copy.deepcopy(self.vals)
        # 将数字向下聚拢，挤出 0
        for j in range(self.cols):
            # 第一次双指针挤出 0 值
            k = self.rows - 1
            for i in range(self.rows-1, -1, -1):
                if self.vals[i][j] != 0:
                    self.vals[k][j] = self.vals[i][j]
                    k += -1

            # 将后续空位置零
            for ii in range(k+1):
                self.vals[ii][j] = 0

            # 相邻等值相加赋给前者，后者置零
            i = self.rows - 1 - 1
            while i > k:
                if self.vals[i + 1][j] == self.vals[i][j]:
                    self.vals[i + 1][j] *= 2
                    self.vals[i][j] = 0
                    self.score += self.vals[i + 1][j]
                i += -1

            # 第二次双指针挤出 0 值
            k = self.rows - 1
            for i in range(self.rows-1, -1, -1):
                if self.vals[i][j] != 0:
                    self.vals[k][j] = self.vals[i][j]
                    k += -1

            # 将后续空位置零
            for ii in range(k+1):
                self.vals[ii][j] = 0

    def move_left(self):
        self.last_vals = copy.deepcopy(self.vals)
        # 将数字向左聚拢，挤出 0
        for i in range(self.rows):
            # 第一次双指针挤出 0 值，k为非零数字数量
            k = 0
            for j in range(self.cols):
                if self.vals[i][j] != 0:
                    self.vals[i][k] = self.vals[i][j]
                    k += 1

            # 将后续空位置零
            for jj in range(k, self.cols):
                self.vals[i][jj] = 0

            # 相邻等值相加赋给前者，后者置零
            j = 1
            while j < k:
                if self.vals[i][j - 1] == self.vals[i][j]:
                    self.vals[i][j - 1] *= 2
                    self.vals[i][j] = 0
                    self.score += self.vals[i][j - 1]
                j += 1

            # 第二次双指针挤出 0 值，k为非零数字数量
            k = 0
            for j in range(self.cols):
                if self.vals[i][j] != 0:
                    self.vals[i][k] = self.vals[i][j]
                    k += 1

            # 将后续空位置零
            for jj in range(k, self.rows):
                self.vals[i][jj] = 0

    def move_right(self):
        self.last_vals = copy.deepcopy(self.vals)
        # 将数字向右聚拢，挤出 0
        for i in range(self.rows):
            # 第一次双指针挤出 0 值
            k = self.cols - 1
            for j in range(self.cols-1, -1, -1):
                if self.vals[i][j] != 0:
                    self.vals[i][k] = self.vals[i][j]
                    k += -1

            # 将空位置零
            for jj in range(k+1):
                self.vals[i][jj] = 0

            # 相邻等值相加赋给前者，后者置零
            j = self.cols - 1 - 1
            while j > k:
                if self.vals[i][j + 1] == self.vals[i][j]:
                    self.vals[i][j + 1] *= 2
                    self.vals[i][j] = 0
                    self.score += self.vals[i][j - 1]
                j += -1

            # 第二次双指针挤出 0 值，k为非零数字数量
            k = self.cols - 1
            for j in range(self.cols-1, -1, -1):
                if self.vals[i][j] != 0:
                    self.vals[i][k] = self.vals[i][j]
                    k += -1

            # 将空位置零
            for jj in range(k+1):
                self.vals[i][jj] = 0

    def lay(self):
        while not self.is_full():
            order = random.randint(0, ROW_SIZE ** 2 - 1)
            i = order // ROW_SIZE
            j = order % ROW_SIZE
            if self.vals[i][j] == 0:
                self.vals[i][j] = 2
                break


class Chessboard(object):
    def __init__(self, rows, cols, grid_len, space_len, screen_size=SCREEN_SIZE):
        self.screen_size = screen_size

        self.all_sprites = pygame.sprite.Group()
        self.screen_sprites = pygame.sprite.Group()
        self.canvas_sprites = pygame.sprite.Group()

        # 棋盘底板
        self.canvas_pos = screen_size[0]/2, screen_size[1]*0.618
        self.canvas_size = rows * (grid_len + space_len) + space_len, cols * (grid_len + space_len) + space_len
        self.canvas = BaseRoundRect(*self.canvas_pos, *self.canvas_size, CANVAS_COLOR, 10)
        self.all_sprites.add(self.canvas)
        self.screen_sprites.add(self.canvas)

        # 棋盘栅格
        x, y = grid_len / 2, space_len
        self.pos = [[(x * (2 * i + 1) + y * (i + 1), x * (2 * j + 1) + y * (j + 1)) for i in range(rows)] for j in range(cols)]
        self.grids = []

        for i in range(rows):
            self.grids.append([])
            for j in range(cols):
                b = TextBlock(*self.pos[i][j], grid_len, grid_len, roundness=5)
                self.grids[i].append(b)
                self.all_sprites.add(self.grids[i][j])
                self.canvas_sprites.add(self.grids[i][j])

        # 计分板
        self.billboard = TextBlock(self.screen_size[0] / 2, self.screen_size[1] * (1 - 0.618) / 2, 100, 50)
        self.all_sprites.add(self.billboard)
        self.screen_sprites.add(self.billboard)

    def update(self):
        self.all_sprites.update()

    def draw(self, screen):
        self.screen_sprites.draw(screen)
        self.canvas_sprites.draw(self.canvas.image)


class Game(object):
    def __init__(self, rows, cols, grid_len=GRID_LEN, space_len=SPACE_LEN):
        self.rows = rows
        self.cols = cols

        self.matrix = Matrix(rows, cols)  # 数字矩阵
        self.chessboard = Chessboard(rows, cols, grid_len, space_len)  # 棋盘UI
        self.map()

    def map(self):
        self.chessboard.billboard.write(self.matrix.score)
        for i in range(self.rows):
            for j in range(self.cols):
                self.chessboard.grids[i][j].write(self.matrix.vals[i][j])

    def is_over(self):
        return self.matrix.is_movable()

    def reset(self):
        self.matrix.reset()
        self.map()

    def move_up(self):
        self.matrix.move_up()
        self.map()

    def move_down(self):
        self.matrix.move_down()
        self.map()

    def move_left(self):
        self.matrix.move_left()
        self.map()

    def move_right(self):
        self.matrix.move_right()
        self.map()


def main():
    pygame.init()
    screen = pygame.display.set_mode(SCREEN_SIZE, pygame.SRCALPHA)
    pygame.display.set_caption(CAPTION)
    clock = pygame.time.Clock()

    game = Game(ROW_SIZE, ROW_SIZE, 105, 16)
    screen.fill(SCREEN_BG_COLOR)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or game.is_over():
                print(game.matrix)
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_w:
                    game.move_up()
                    print('UP')
                if event.key == pygame.K_s:
                    game.move_down()
                    print('DOWN')
                if event.key == pygame.K_a:
                    game.move_left()
                    print('LEFT')
                if event.key == pygame.K_d:
                    game.move_right()
                    print('RIGHT')
                if event.key == pygame.K_r:
                    game.reset()
                    print('----- Reset -----')

                if event.key in [pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d]:
                    if game.matrix.is_changed():
                        game.matrix.lay()

        # Update
        game.chessboard.update()

        # Draw / render
        game.chessboard.draw(screen)

        pygame.display.flip()
        clock.tick(SCREEN_FPS)


if __name__ == '__main__':
    main()
