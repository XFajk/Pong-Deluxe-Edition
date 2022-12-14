import pygame
from pygame.locals import *

import math
import time
import random


def surf_circle(r:float,color_of_circle:tuple,colorkey:tuple) -> pygame.Surface:
    
    s = pygame.Surface((r*2,r*2))
    pygame.draw.circle(s,color_of_circle,(r,r),r)

    try:
        s.set_colorkey(colorkey)
    except ValueError:
        print("This is invalid colorkey:", colorkey)

    return s

def surf_rect(size:tuple,color=(255,255,255)) -> pygame.Surface:
    s = pygame.Surface((size[0], size[1]))
    pygame.draw.rect(s,color,(0,0,size[0],size[1]))
    return s

class Spark:
    def __init__(self, loc:list, angle:float, speed, color:tuple=(255,255,255), scale:float=1):
        self.loc = loc
        self.angle = angle
        self.speed = speed
        self.scale = scale
        self.color = color
        self.alive = True

    def calculate_movement(self, dt):
        return [math.cos(self.angle) * self.speed * dt, math.sin(self.angle) * self.speed * dt]

    def move(self, dt):
        movement = self.calculate_movement(dt)
        self.loc[0] += movement[0]
        self.loc[1] += movement[1]

        self.speed -= 0.25*dt

        if self.speed <= 0:
            self.alive = False

    def draw(self, surf, offset=[0, 0]):
        if self.alive:
            points = [
                [self.loc[0] + math.cos(self.angle) * self.speed * self.scale, self.loc[1] + math.sin(self.angle) * self.speed * self.scale],
                [self.loc[0] + math.cos(self.angle + math.pi / 2) * self.speed * self.scale * 0.3, self.loc[1] + math.sin(self.angle + math.pi / 2) * self.speed * self.scale * 0.3],
                [self.loc[0] - math.cos(self.angle) * self.speed * self.scale * 3.5, self.loc[1] - math.sin(self.angle) * self.speed * self.scale * 3.5],
                [self.loc[0] + math.cos(self.angle - math.pi / 2) * self.speed * self.scale * 0.3, self.loc[1] - math.sin(self.angle + math.pi / 2) * self.speed * self.scale * 0.3],
                ]
            pygame.draw.polygon(surf, self.color, points)

        
    