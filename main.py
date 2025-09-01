# coding=utf-8
""""
OpalShooter

Main file

Made by BlockMaster777 and Marinich Timyr
"""

import math
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
bullet_img = pg.transform.scale_by(pg.image.load('resources/images/bullet.png').convert_alpha(), 2)

walk_sound = pg.mixer.Sound('resources/sounds/walk.mp3')

dt = clock.tick(FPS) / 1000

objects = []
upd_objects = []

def limit_number(num, minimum, maximum):
    return max(minimum, min(num, maximum))


def angle_to(sx, sy, px, py) -> float:
    return math.atan2(py - sy, px - sx)


def rad_to_ang(rad) -> float:
    return (180 / math.pi) * -rad


def draw_objects():
    for obj in objects:
        obj.draw()

def update_objects():
    for obj in upd_objects:
        obj.update()


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


class Bullet(Object):
    def __init__(self, x, y, image, angle, speed, damage, distance):
        super().__init__(x, y, image)
        self.angle = angle
        self.speed = speed
        self.damage = damage
        self.distance = distance
        self.raw_image = self.image
        upd_objects.append(self)
    
    
    def update(self):
        speed = self.speed * dt
        self.distance -= speed
        if self.distance <= 0:
            upd_objects.remove(self)
            objects.remove(self)
            self.kill()
        self.x += math.cos(self.angle) * speed
        self.y += math.sin(self.angle) * speed
        self.image = pg.transform.rotate(self.raw_image, rad_to_ang(self.angle))
        super().update()



class Player(Object):
    def __init__(self, x, y, image, speed):
        super().__init__(x, y, image)
        self.speed = speed
        self.is_walking = False
    
    
    def update(self):
        movement_speed = self.speed * dt
        x_speed = 0
        y_speed = 0
        
        keys = pg.key.get_pressed()
        if keys[pg.K_w]:
            y_speed = -movement_speed
            x_speed //= 2
        if keys[pg.K_s]:
            y_speed = movement_speed
            x_speed //= 2
        if keys[pg.K_a]:
            x_speed = -movement_speed
            y_speed //= 2
        if keys[pg.K_d]:
            x_speed = movement_speed
            y_speed //= 2
        
        self.x += x_speed
        self.y += y_speed
        self.x, self.y = (limit_number(self.x, 0, WORLD_SIZE[0] - self.rect.w), limit_number(self.y, 0, WORLD_SIZE[1] - self.rect.h))
        
        is_moving = (x_speed != 0) or (y_speed != 0)
        
        if is_moving:
            if not self.is_walking:
                walk_sound.play(-1)
                self.is_walking = True
        else:
            if self.is_walking:
                walk_sound.stop()
                self.is_walking = False
        
        super().update()


player = Player(0, 0, player_img, PLAYER_SPEED)
player.x = WORLD_SIZE[0] // 2 - player.rect.w // 2
player.y = WORLD_SIZE[1] // 2 - player.rect.h // 2
player.update_rect()

for x in range(0, WORLD_SIZE[0] - 64, 500):
    for y in range(0, WORLD_SIZE[1] - 64, 500):
        Object(x, y, enemy_img)

camera_x, camera_y = (player.rect.centerx - WIDTH // 2, player.rect.centery - HEIGHT // 2)


def shoot():
    mouse_pos_realitive = pg.mouse.get_pos()
    mouse_pos_absolute = mouse_pos_realitive[0] + camera_x, mouse_pos_realitive[1] + camera_y
    shoot_angle = angle_to(player.rect.centerx, player.rect.centery, mouse_pos_absolute[0], mouse_pos_absolute[1])
    Bullet(player.rect.centerx, player.rect.centery, bullet_img, shoot_angle, 1000, 3, 2000)


escape_pressed = False
is_mouse_down = False

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
        if event.type == pg.USEREVENT + SHOOT_EVENT:
            shoot()
        if event.type == pg.MOUSEBUTTONDOWN and not is_mouse_down:
            is_mouse_down = True
            pg.time.set_timer(pg.USEREVENT + SHOOT_EVENT, 1000)
        if event.type == pg.MOUSEBUTTONUP:
            is_mouse_down = False
            pg.time.set_timer(pg.USEREVENT + SHOOT_EVENT, 0)
    
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
    
    update_objects()
    draw_objects()
    
    pg.display.update()
