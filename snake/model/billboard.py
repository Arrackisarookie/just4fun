import pygame

from config import BLACK


class Billboard(pygame.sprite.Sprite):
    def __init__(self, template, left=0, top=0):
        pygame.sprite.Sprite.__init__(self)
        self.template = template
        self.left = left
        self.top = top
        self.content = ''
        self.font = pygame.font.SysFont('consolas', 20)
        self.update()

    def rewrite(self, *args):
        self.content = self.template.format(*args)

    def update(self):
        self.image = self.font.render(self.content, True, (255, 0, 0), BLACK)
        self.rect = self.image.get_rect()
        self.rect.x = self.left
        self.rect.y = self.top
