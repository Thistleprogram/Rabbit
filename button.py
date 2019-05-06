#!/usr/bin/env python
import pygame

class Button(pygame.sprite.Sprite):
    def __init__(self, normal, above, onclick, rect):
        pygame.sprite.Sprite.__init__(self)
        self.normal = normal
        self.above = above
        self.onclick = onclick
        self.rect = rect
        self.image = self.normal

    def update(self):
        cur_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()
        if self.rect.collidepoint(cur_pos):
            if mouse_pressed[0]:
                self.image = self.onclick
            else:
                self.image = self.above
        else:
            self.image = self.normal
            
    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def isclicked(self):
        cur_pos = pygame.mouse.get_pos()
        mouse_pressed=pygame.mouse.get_pressed()
        if self.rect.collidepoint(cur_pos) and mouse_pressed[0]:
            return True
        else:
            return False
    
    def contains(self, x, y):
        cur_pos = (x, y)
        if self.rect.collidepoint(cur_pos):
            return True
        else:
            return False