# coding=utf-8
""""
OpalShooter

Main file

Made by BlockMaster777 and Marinich Timyr
"""

import math
import random
from typing import Tuple

import pygame as pg
from config import *

pg.init()
pg.mixer.init()
pg.display.init()
pg.font.init()

clock = pg.time.Clock()

pg.display.set_caption('OpalShooter')
screen = pg.display.set_mode((WIDTH, HEIGHT), pg.FULLSCREEN)

bg_img = pg.transform.scale_by(pg.image.load('resources/images/bg.png').convert(), 4)
player_img = pg.transform.scale_by(pg.image.load('resources/images/player.png').convert_alpha(), 4)
enemy_img = pg.transform.scale_by(pg.image.load('resources/images/enemy.png').convert_alpha(), 4)
bullet_img = pg.transform.scale_by(pg.image.load('resources/images/bullet.png').convert_alpha(), 4)
wall_img = pg.transform.scale_by(pg.image.load('resources/images/wall.png').convert_alpha(), 4)

walk_sound = pg.mixer.Sound('resources/sounds/walk.mp3')

font40 = pg.font.Font("resources/pixel_font.ttf", 40)

dt = clock.tick(FPS) / 1000

objects = []
upd_objects = []
buttons = pg.sprite.Group()


def limit_number(num, minimum, maximum):
    return max(minimum, min(num, maximum))


def angle_to(sx, sy, px, py) -> float:
    return math.atan2(py - sy, px - sx)


def rad_to_ang(rad) -> float:
    return (180 / math.pi) * -rad


class Button(pg.sprite.Sprite):
    def __init__(self, font_: pg.font.Font, size: Tuple, pos: Tuple, text, text_color, button_color, action_on_click, action_params=()):
        pg.sprite.Sprite.__init__(self)
        self.font = font_
        self.size = size
        self.pos = pos
        self.text = text
        self.text_color = text_color
        self.button_color = button_color
        self.image = pg.Surface(self.size)
        self.image.fill(self.button_color)
        self.text_render = self.font.render(self.text, True, self.text_color)
        self.text_rect = self.text_render.get_rect(center=(self.image.get_width() / 2, self.image.get_height() / 2))
        self.image.blit(self.text_render, self.text_rect)
        self.rect = self.image.get_rect(topleft=self.pos)
        self.action_on_click = action_on_click
        self.action_params = action_params
        self.add(buttons)
    
    
    def handle_event(self, e):
        if e.type == pg.MOUSEBUTTONDOWN and self.rect.collidepoint(e.pos):
            if self.action_params == ():
                self.action_on_click()
            else:
                self.action_on_click(self.action_params)


class IMGButton(pg.sprite.Sprite):
    def __init__(self, size, pos, img, action_on_click, action_params=()):
        pg.sprite.Sprite.__init__(self)
        self.size = size
        self.pos = pos
        self.image = img
        self.rect = self.image.get_rect(topleft=self.pos)
        self.action_on_click = action_on_click
        self.action_params = action_params
        self.add(buttons)
    
    
    def handle_event(self, e):
        if e.type == pg.MOUSEBUTTONDOWN and self.rect.collidepoint(e.pos):
            if self.action_params == ():
                self.action_on_click()
            else:
                self.action_on_click(self.action_params)


class Object(pg.sprite.Sprite):
    def __init__(self, x, y, image, collision=True):
        pg.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.image = image
        self.collision = collision
        self.rect = self.image.get_rect(topleft=(self.x, self.y))
        objects.append(self)
    
    
    def update_rect(self):
        self.rect = self.image.get_rect(topleft=(self.x, self.y))
    
    
    def update(self):
        self.update_rect()
    
    
    def draw(self):
        if (camera_x <= self.x <= camera_x + WIDTH and camera_y <= self.y <= camera_y + HEIGHT or
            camera_x <= self.rect.right <= camera_x + WIDTH and camera_y <= self.y <= camera_y + HEIGHT or
            camera_x <= self.x <= camera_x + WIDTH and camera_y <= self.rect.bottom <= camera_y + HEIGHT or
            camera_x <= self.rect.right <= camera_x + WIDTH and camera_y <= self.rect.bottom <= camera_y + HEIGHT):
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
        for obj in objects:
            if obj.collision and self.rect.colliderect(obj.rect) and obj != self and type(obj) != Player:
                self.collide()
    
    
    def collide(self):
        try:
            upd_objects.remove(self)
            objects.remove(self)
            self.kill()
        except:
            pass

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
        self.update_rect()
        
        for obj in objects:
            if self.rect.colliderect(obj.rect):
                if obj.collision and obj != self and type(obj) != Bullet:
                    if x_speed > 0:
                        self.x = obj.rect.left - self.rect.width
                    elif x_speed < 0:
                        self.x = obj.rect.right
                    self.update_rect()
                    x_speed = 0
                    break
        
        self.y += y_speed
        self.update_rect()
        
        for obj in objects:
            if self.rect.colliderect(obj.rect):
                if obj.collision and obj != self and type(obj) != Bullet:
                    if y_speed > 0:
                        self.y = obj.rect.top - self.rect.height
                    elif y_speed < 0:
                        self.y = obj.rect.bottom
                    self.update_rect()
                    y_speed = 0
                    break
        
        self.x = round(self.x)
        self.y = round(self.y)
        
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
    
    
    def draw(self):
        pass
    
    
    def player_draw(self):
        screen.blit(self.image, (self.x - camera_x, self.y - camera_y))


for x in range(0, WORLD_SIZE[0], 680):
    for y in range(0, WORLD_SIZE[1], 680):
        Object(x, y, bg_img, collision=False)

for x in range(0, WORLD_SIZE[0], 680):
    for y in range(0, WORLD_SIZE[1], 680):
        Object(x, y, wall_img)


def draw_objects():
    for obj in objects:
        obj.draw()


def update_objects():
    for obj in upd_objects:
        obj.update()


player = Player(0, 0, player_img, PLAYER_SPEED)
player.x = WORLD_SIZE[0] // 2 - player.rect.w // 2
player.y = WORLD_SIZE[1] // 2 - player.rect.h // 2
player.update_rect()

max_stamina = 5
stamina = 5
is_min_stamina_reached = False
real_speed = PLAYER_SPEED

running = True


def exit_game():
    global running
    running = False


Button(font40, (150, 50), (1770, 0), "Exit", "Black", "#B0305C", exit_game)

shoot_delay = 1
shoot_timer = 0


def shoot():
    mouse_pos_realitive = pg.mouse.get_pos()
    mouse_pos_absolute = mouse_pos_realitive[0] + camera_x, mouse_pos_realitive[1] + camera_y
    shoot_angle = angle_to(player.rect.centerx, player.rect.centery, mouse_pos_absolute[0], mouse_pos_absolute[1]) + (random.random() - 0.5) / 10
    Bullet(player.rect.centerx - 10, player.rect.centery - 10, bullet_img, shoot_angle, BULLET_SPEED, 3, 2000)


camera_x, camera_y = (player.rect.centerx - WIDTH // 2, player.rect.centery - HEIGHT // 2)

is_mouse_down = False

while running:
    dt = clock.tick(FPS) / 1000
    
    keys = pg.key.get_pressed()
    
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        if event.type == pg.MOUSEBUTTONDOWN and not is_mouse_down:
            is_mouse_down = True
        if event.type == pg.MOUSEBUTTONUP:
            is_mouse_down = False
        for button in buttons:
            button.handle_event(event)
    
    screen.fill("green")
    
    player.update()
    
    if is_mouse_down:
        if shoot_timer <= 0:
            shoot_timer = shoot_delay
            shoot()
        else:
            shoot_timer -= dt
    else:
        shoot_timer -= dt
    
    
    if keys[pg.K_LSHIFT]:
        if stamina > 0 and not is_min_stamina_reached:
            player.speed = RUN_SPEED
            stamina -= dt
        elif stamina <= 0:
            is_min_stamina_reached = True
            player.speed = PLAYER_SPEED
            if stamina < max_stamina:
                stamina += dt
        elif stamina >= max_stamina:
            is_min_stamina_reached = False
        else:
            player.speed = PLAYER_SPEED
            if stamina < max_stamina:
                stamina += dt
    else:
        player.speed = PLAYER_SPEED
        if stamina < max_stamina:
            stamina += dt
    
    camera_target_x, camera_target_y = (player.rect.centerx - WIDTH // 2, player.rect.centery - HEIGHT // 2)
    camera_x += (camera_target_x - camera_x) * CAMERA_SMOOTHING
    camera_y += (camera_target_y - camera_y) * CAMERA_SMOOTHING
    camera_x, camera_y = (limit_number(camera_x, 0, WORLD_SIZE[0] - WIDTH), limit_number(camera_y, 0, WORLD_SIZE[1] - HEIGHT))
    
    update_objects()
    draw_objects()
    player.player_draw()
    buttons.draw(screen)
    
    pg.display.update()

pg.quit()
