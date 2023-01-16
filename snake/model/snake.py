import copy
import random

import pygame

from config import SCREEN_SIZE, WHITE, PIXEL_SIZE, DIRECTIONS, SNAKE_INIT_LENGTH, YELLOW


class Snake(pygame.sprite.Sprite):

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

        self.head_coord = [random.randint(0, SCREEN_SIZE[0] // PIXEL_SIZE - 1), random.randint(0, SCREEN_SIZE[0] // PIXEL_SIZE - 1)]
        self.tail_coords = []
        for i in range(1, SNAKE_INIT_LENGTH):
            self.tail_coords.append([self.head_coord[0] - i, self.head_coord[1]])

        self.direction = random.choice(list(DIRECTIONS.keys()))
        self.score = 0

    @property
    def coords(self):
        return [self.head_coord] + self.tail_coords

    def change_direction(self, direction):
        if DIRECTIONS[self.direction] + DIRECTIONS[direction] != 0:
            self.direction = direction

    def update(self, food):
        self.tail_coords.insert(0, copy.deepcopy(self.head_coord))
        if self.direction == 'UP':
            self.head_coord[1] -= 1
        elif self.direction == 'DOWN':
            self.head_coord[1] += 1
        elif self.direction == 'LEFT':
            self.head_coord[0] -= 1
        elif self.direction == 'RIGHT':
            self.head_coord[0] += 1

        if self.head_coord == food.coord:
            self.score += 1
            return True
        else:
            self.tail_coords = self.tail_coords[:-1]
            return False

    def draw(self, screen):
        head_x, head_y = self.head_coord[0] * PIXEL_SIZE, self.head_coord[1] * PIXEL_SIZE
        rect = pygame.Rect(head_x, head_y, PIXEL_SIZE, PIXEL_SIZE)
        pygame.draw.rect(screen, YELLOW, rect)
        for coord in self.tail_coords:
            x, y = coord[0] * PIXEL_SIZE, coord[1] * PIXEL_SIZE
            rect = pygame.Rect(x, y, PIXEL_SIZE, PIXEL_SIZE)
            pygame.draw.rect(screen, WHITE, rect)
