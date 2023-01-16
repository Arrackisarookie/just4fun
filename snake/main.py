import pygame
import sys

from config import CAPTION, SCREEN_SIZE, SCREEN_FPS, BLACK, PIXEL_SIZE
from model import Food, Snake


def draw_game_grid(screen):
    color = (40, 40, 40)
    for x in range(0, SCREEN_SIZE[0], PIXEL_SIZE):
        pygame.draw.line(screen, color, (x, 0), (x, SCREEN_SIZE[1]))
    for y in range(0, SCREEN_SIZE[1], PIXEL_SIZE):
        pygame.draw.line(screen, color, (0, y), (SCREEN_SIZE[0], y))


def main():
    pygame.init()
    screen = pygame.display.set_mode(SCREEN_SIZE)
    pygame.display.set_caption(CAPTION)
    clock = pygame.time.Clock()
    snake = Snake()
    food = Food(snake.coords)

    while True:
        screen.fill(BLACK)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    snake.change_direction('UP')
                    print('UP')
                if event.key == pygame.K_s:
                    snake.change_direction('DOWN')
                    print('DOWN')
                if event.key == pygame.K_a:
                    snake.change_direction('LEFT')
                    print('LEFT')
                if event.key == pygame.K_d:
                    snake.change_direction('RIGHT')
                    print('RIGHT')

        if snake.update(food):
            food = Food(snake.coords)

        draw_game_grid(screen)
        snake.draw(screen)
        food.draw(screen)

        pygame.display.update()
        clock.tick(SCREEN_FPS)


if __name__ == '__main__':
    main()
