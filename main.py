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
pistol_shoot_sound = pg.mixer.Sound('resources/sounds/pistol_shoot.mp3')

font40 = pg.font.Font("resources/pixel_font.ttf", 40)
font20 = pg.font.Font("resources/pixel_font.ttf", 20)

dt = clock.tick(FPS) / 1000

objects = []
buttons = pg.sprite.Group()


def limit_number(num, minimum, maximum):
    return max(minimum, min(num, maximum))


def angle_to(sx, sy, px, py) -> float:
    return math.atan2(py - sy, px - sx)


def rad_to_ang(rad) -> float:
    return (180 / math.pi) * -rad


def shoot(angle, start: Tuple[int, int]):
    angle += (random.random() - 0.5) / 10
    Bullet(start[0], start[1], bullet_img, angle, BULLET_SPEED, 3, 2000)
    pistol_shoot_sound.play()


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
    def __init__(self, x, y, image, updating, collision=True):
        pg.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.image = image
        self.updating = updating
        self.collision = collision
        self.rect = self.image.get_rect(topleft=(self.x, self.y))
        objects.append(self)
    
    
    def update_rect(self):
        self.rect = self.image.get_rect(topleft=(self.x, self.y))
    
    
    def update(self):
        self.update_rect()
    
    
    def kill(self):
        objects.remove(self)
        del self
    
    
    def draw(self):
        if (
                camera_x <= self.x <= camera_x + WIDTH and camera_y <= self.y <= camera_y + HEIGHT or camera_x <= self.rect.right <= camera_x + WIDTH and camera_y <= self.y <= camera_y + HEIGHT or camera_x <= self.x <= camera_x + WIDTH and camera_y <= self.rect.bottom <= camera_y + HEIGHT or camera_x <= self.rect.right <= camera_x + WIDTH and camera_y <= self.rect.bottom <= camera_y + HEIGHT):
            screen.blit(self.image, (self.x - camera_x, self.y - camera_y))


class Bullet(Object):
    def __init__(self, x, y, image, angle, speed, damage, distance):
        super().__init__(x, y, image, True)
        self.angle = angle
        self.speed = speed
        self.damage = damage
        self.distance = distance
        self.raw_image = self.image
    
    
    def update(self):
        speed = self.speed * dt
        self.distance -= speed
        if self.distance <= 0:
            self.kill()
        self.x += math.cos(self.angle) * speed
        self.y += math.sin(self.angle) * speed
        self.image = pg.transform.rotate(self.raw_image, rad_to_ang(self.angle))
        super().update()
        for obj in objects:
            if (obj.collision or type(obj) == Enemy) and self.rect.colliderect(obj.rect) and obj != self and type(obj) != Player:
                self.collide(obj)
                break
    
    
    def collide(self, obj):
        try:
            obj.hit(self.damage)
        except:
            pass
        try:
            self.kill()
        except:
            pass


class Player(Object):
    def __init__(self, x, y, image, walk_speed, run_speed, max_stamina):
        super().__init__(x, y, image, True)
        self.walk_speed = walk_speed
        self.run_speed = run_speed
        self.speed = self.walk_speed
        self.is_walking = False
        self.weapon_type = "pistol"
        self.weapon_stats = {"pistol": {"shoot_delay": 1, "round_size": 14, "reload_time": 3}}
        self.shoot_timer = 0
        self.max_stamina = max_stamina
        self.stamina = self.max_stamina
        self.is_min_stamina_reached = False
    
    
    def update(self):
        keys = pg.key.get_pressed()
        if is_mouse_down:
            if self.shoot_timer <= 0:
                self.shoot_timer = self.weapon_stats[self.weapon_type]["shoot_delay"]
                mouse_x, mouse_y = pg.mouse.get_pos()
                absolute_x, absolute_y = mouse_x + camera_x, mouse_y + camera_y
                angle = angle_to(self.rect.centerx - 10, self.rect.centery - 10, absolute_x, absolute_y)
                shoot(angle, (self.rect.centerx - 10, self.rect.centery - 10))
            else:
                self.shoot_timer -= dt
        else:
            self.shoot_timer -= dt
        
        if keys[pg.K_LSHIFT]:
            if self.stamina > 0 and not self.is_min_stamina_reached:
                self.speed = self.run_speed
                self.stamina -= dt
            elif self.stamina <= 0:
                self.is_min_stamina_reached = True
                self.speed = self.walk_speed
                if self.stamina < self.max_stamina:
                    self.stamina += dt
            elif self.stamina >= self.max_stamina:
                self.is_min_stamina_reached = False
            else:
                self.speed = self.walk_speed
                if self.stamina < self.max_stamina:
                    self.stamina += dt
        else:
            self.speed = self.walk_speed
            if self.stamina < self.max_stamina:
                self.stamina += dt
        
        movement_speed = self.speed * dt
        x_speed = 0
        y_speed = 0
        
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


class Enemy(Object):
    def __init__(self, x, y, image, speed, health):
        super().__init__(x, y, image, True)
        self.speed = speed
        self.health = health
    
    
    def update(self):
        movement_speed = self.speed * dt
        angle = angle_to(self.rect.centerx, self.rect.centery, player.rect.centerx, player.rect.centery)
        x_speed = math.cos(angle) * movement_speed
        y_speed = math.sin(angle) * movement_speed
        
        self.x += x_speed
        self.update_rect()
        
        for obj in objects:
            if self.rect.colliderect(obj.rect):
                if obj.collision and obj != self:
                    if x_speed > 0:
                        self.x = obj.rect.left - self.rect.width
                    elif x_speed < 0:
                        self.x = obj.rect.right
                    self.update_rect()
                    break
        
        self.y += y_speed
        self.update_rect()
        
        for obj in objects:
            if self.rect.colliderect(obj.rect):
                if obj.collision and obj != self:
                    if y_speed > 0:
                        self.y = obj.rect.top - self.rect.height
                    elif y_speed < 0:
                        self.y = obj.rect.bottom
                    self.update_rect()
                    break
        
        self.x = round(self.x)
        self.y = round(self.y)
        
        self.x, self.y = (limit_number(self.x, 0, WORLD_SIZE[0] - self.rect.w), limit_number(self.y, 0, WORLD_SIZE[1] - self.rect.h))
        
        super().update()
    
    
    def hit(self, damage):
        self.health -= damage
        if self.health <= 0:
            try:
                self.kill()
            except:
                pass


for x in range(0, WORLD_SIZE[0], 680):
    for y in range(0, WORLD_SIZE[1], 680):
        Object(x, y, bg_img, False, collision=False)

for x in range(0, WORLD_SIZE[0], 680):
    for y in range(0, WORLD_SIZE[1], 680):
        Enemy(x, y, enemy_img, ENEMY_SPEED, 3)


def draw_objects():
    for obj in objects:
        obj.draw()


def update_objects():
    for obj in objects:
        if obj.updating:
            obj.update()


player = Player(0, 0, player_img, PLAYER_SPEED, RUN_SPEED, 5)
Object(128, 0, wall_img, False)
Object(128, 64, wall_img, False)
Object(128, 128, wall_img, False)
Object(0, 128, wall_img, False)
Object(64, 128, wall_img, False)
player.x = WORLD_SIZE[0] // 2 - player.rect.w // 2
player.y = WORLD_SIZE[1] // 2 - player.rect.h // 2
player.update_rect()

running = True


def exit_game():
    global running
    running = False


Button(font40, (150, 50), (WIDTH - 150, 0), "Exit", "Black", "#B0305C", exit_game)

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
    
    camera_target_x, camera_target_y = (player.rect.centerx - WIDTH // 2, player.rect.centery - HEIGHT // 2)
    camera_x += (camera_target_x - camera_x) * CAMERA_SMOOTHING
    camera_y += (camera_target_y - camera_y) * CAMERA_SMOOTHING
    camera_x, camera_y = (limit_number(camera_x, 0, WORLD_SIZE[0] - WIDTH), limit_number(camera_y, 0, WORLD_SIZE[1] - HEIGHT))
    
    update_objects()
    draw_objects()
    player.player_draw()
    buttons.draw(screen)
    
    fps_text = font20.render(str(round(clock.get_fps())), True, "#B0305C")
    screen.blit(fps_text, (3, 3))
    
    pg.display.update()

pg.quit()
