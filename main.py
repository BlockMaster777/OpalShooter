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

dt = clock.tick(FPS) / 1000

while True:
    dt = clock.tick(FPS) / 1000
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            break
    
    screen.fill("green")
    
    screen.blit(screen, (0, 0))
    pg.display.update()
