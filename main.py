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
screen = pg.display.set_mode((WIDTH, HEIGHT), pg.FULLSCREEN)

player_img = pg.transform.scale_by(pg.image.load('resources/images/player.png').convert_alpha(), 4)
enemy_img = pg.transform.scale_by(pg.image.load('resources/images/enemy.png').convert_alpha(), 4)

dt = clock.tick(FPS) / 1000

objects = []

def limit_number(num, minimum, maximum):
    return max(minimum, min(num, maximum))


def draw_objects():
    for obj in objects:
        obj.draw()


class Object(pg.sprite.Sprite):
    def __init__(self, x, y, image):
        pg.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.image = image
        self.rect = self.image.get_rect(topleft=(self.x, self.y))
        objects.append(self)
    
    
    def update_rect(self):
        self.rect = self.image.get_rect(topleft=(self.x, self.y))
    
    
    def update(self):
        self.update_rect()
    
    
    def draw(self):
        screen.blit(self.image, (self.x - camera_x, self.y - camera_y))


class Player(Object):
    def __init__(self, x, y, image, speed):
        super().__init__(x, y, image)
        self.speed = speed
    
    
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
        self.x, self.y = (limit_number(self.x, 0, WORLD_SIZE[0] - self.rect.w), limit_number(self.y, 0, WORLD_SIZE[1] - self.rect.h))
        
        super().update()


player = Player(0, 0, player_img, PLAYER_SPEED)
player.x = WORLD_SIZE[0] // 2 - player.rect.w // 2
player.y = WORLD_SIZE[1] // 2 - player.rect.h // 2
player.update_rect()

for x in range(0, WORLD_SIZE[0] - 64, 500):
    for y in range(0, WORLD_SIZE[1] - 64, 500):
        Object(x, y, enemy_img)

camera_x, camera_y = (player.rect.centerx - WIDTH // 2, player.rect.centery - HEIGHT // 2)

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
            pg.time.set_timer(pg.USEREVENT + EXIT_EVENT, EXIT_HOLD_TIME, loops=1)
            escape_pressed = True
    else:
        if escape_pressed:
            pg.time.set_timer(pg.USEREVENT + EXIT_EVENT, 0)
            escape_pressed = False
    
    screen.fill("green")
    
    player.update()
    
    camera_target_x, camera_target_y = (player.rect.centerx - WIDTH // 2, player.rect.centery - HEIGHT // 2)
    camera_x += (camera_target_x - camera_x) * CAMERA_SMOOTHING
    camera_y += (camera_target_y - camera_y) * CAMERA_SMOOTHING
    
    camera_x, camera_y = (limit_number(camera_x, 0, WORLD_SIZE[0] - WIDTH), limit_number(camera_y, 0, WORLD_SIZE[1] - HEIGHT))
    
    draw_objects()
    
    pg.display.update()
