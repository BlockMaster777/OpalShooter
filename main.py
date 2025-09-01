# coding=utf-8
""""
OpalShooter

Main file

Made by BlockMaster777 and Marinich Timyr
"""

import pygame as pg
from config import *

pg.init()
pg.mixer.init()
pg.display.init()

clock = pg.time.Clock()

pg.display.set_caption('OpalShooter')
screen = pg.display.set_mode((1920, 1080), pg.FULLSCREEN)

player_img = pg.transform.scale_by(pg.image.load('resources/images/player.png').convert_alpha(), 4)

dt = clock.tick(FPS) / 1000


class Player(pg.sprite.Sprite):
    def __init__(self, x, y, image):
        pg.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.speed = 200
        self.image = image
        self.rect = self.image.get_rect(topleft=(self.x, self.y))
    
    
    def update_rect(self):
        self.rect = self.image.get_rect(topleft=(self.x, self.y))
    
    
    def update(self):
        speed = self.speed * dt
        
        keys = pg.key.get_pressed()
        if keys[pg.K_w]:
            if keys[pg.K_a] or keys[pg.K_d]:
                self.y -= speed / 2
            else:
                self.y -= speed
        if keys[pg.K_s]:
            if keys[pg.K_a] or keys[pg.K_d]:
                self.y += speed / 2
            else:
                self.y += speed
        if keys[pg.K_a]:
            if keys[pg.K_w] or keys[pg.K_s]:
                self.x -= speed / 2
            else:
                self.x -= speed
        if keys[pg.K_d]:
            if keys[pg.K_w] or keys[pg.K_s]:
                self.x += speed / 2
            else:
                self.x += speed
        
        self.x, self.y = round(self.x), round(self.y)
        
        self.update_rect()
    
    
    def draw(self):
        screen.blit(self.image, self.rect)


player = Player(100, 100, player_img)

escape_pressed = False

while True:
    dt = clock.tick(FPS) / 1000
    
    keys = pg.key.get_pressed()
    
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            break
        if event.type == pg.USEREVENT + EXIT_EVENT:
            pg.quit()
            break
    
    if keys[pg.K_ESCAPE]:
        if not escape_pressed:
            pg.time.set_timer(pg.USEREVENT + EXIT_EVENT, 2000, loops=1)
            escape_pressed = True
    else:
        if escape_pressed:
            pg.time.set_timer(pg.USEREVENT + EXIT_EVENT, 0)
            escape_pressed = False
    
    screen.fill("green")
    
    player.update()
    player.draw()
    
    screen.blit(screen, (0, 0))
    pg.display.update()
