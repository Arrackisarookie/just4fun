import random

import pygame

from config import PIXEL_SIZE, WHITE, SCREEN_SIZE


class Food(pygame.sprite.Sprite):

    def __init__(self, snake_coords):
        pygame.sprite.Sprite.__init__(self)
        self.color = WHITE
        while True:
            self.coord = [random.randint(0, SCREEN_SIZE[0] // PIXEL_SIZE - 1),
                          random.randint(0, SCREEN_SIZE[1] // PIXEL_SIZE - 1)]
            if self.coord not in snake_coords:
                break

    def draw(self, screen):
        food_x, food_y = int((self.coord[0] + 0.5) * PIXEL_SIZE), int((self.coord[1] + 0.5) * PIXEL_SIZE)
        pygame.draw.circle(screen, self.color, (food_x, food_y), PIXEL_SIZE // 2 - 2)
