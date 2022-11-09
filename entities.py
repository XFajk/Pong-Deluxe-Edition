import pygame
from pygame.locals import *

import math
import time
import random

import effects

def surf_circle(r:float,color_of_circle:tuple,colorkey:tuple) -> pygame.Surface:
    
    s = pygame.Surface((r*2,r*2))
    pygame.draw.circle(s,color_of_circle,(r,r),r)

    try:
        s.set_colorkey(colorkey)
    except ValueError:
        print("This is invalid colorkey:", colorkey)

    return s


class Ball:
    def __init__(self,DS,color,sprite=None):
        # constants
        self.DS = DS

        # movment logic variables
        self.w, self.h = 1, 16
        self.size = 16
        self.pos = pygame.Vector2(DS[0]/2-self.w/2,DS[1]/2-self.h/2)
        self.rect = pygame.Rect(self.pos.x, self.pos.y, self.w, self.h)
        self.dir = pygame.Vector2(random.choice([-1,1]),random.choice([-1,1]))
        self.vel = pygame.Vector2(5,2)
        self.vel.x, self.vel.y = self.vel.x*self.dir.x, self.vel.y*self.dir.y

        # logic
        self.started = False
        self.add_to_velocity = True
        self.velocity_increment = 1/12
        self.max_velocity = 13

        # effects and graphics
        self.sprite = sprite
        self.color = color
        self.sparks = []
        self.particles = []
        self.follow_particles = []
        self.screen_shake_time:int = 0

    def Render(self,surface,dt):
        #pygame.draw.rect(surface,(255,255,255),self.rect)

        for i, s in sorted(enumerate(self.sparks), reverse=True):
            s.move(dt)
            s.draw(surface)
            if not s.alive:
                self.sparks.pop(i)

        for i, p in sorted(enumerate(self.follow_particles), reverse=True):
            p[0] += p[1]*dt
            p[2] -= 0.5*dt

            pygame.draw.circle(surface,(0,150,0),(p[0].x,p[0].y),p[2])

            if p[2] <= 0:
                self.follow_particles.pop(i)
            
        for i, p in sorted(enumerate(self.particles), reverse=True):
            p[0] += p[1]*dt
            p[2] -= 0.25*dt

            pygame.draw.circle(surface,self.color,(p[0].x,p[0].y),p[2])

            if p[2] <= 0:
                self.particles.pop(i)

    
        #pygame.draw.rect(surface,(255,0,0),(self.rect))
        pygame.draw.circle(surface,self.color,(self.pos.x+self.w/2,self.pos.y+self.h/2),self.w/2)

    def Update(self,dt):
        self.rect = pygame.Rect(self.pos.x, self.pos.y, self.w, self.h)
        if self.w < self.size:
            self.w += 0.5

        self.h = self.w

        if self.started and self.w == self.size:
            if self.pos.y <= 0 or self.pos.y+self.h >= self.DS[1]:
                self.pos.y = 1 if self.pos.y <= 0 else self.DS[1] - self.h
                self.vel.y = -self.vel.y
                for i in range(40):
                    rand_color = random.randint(150,255)
                    rand_ang = random.randint(180,360) if self.vel.y/abs(self.vel.y) == -1 else random.randint(0,180)
                    self.sparks.append(effects.Spark([self.pos.x,self.pos.y-((self.vel.y/abs(self.vel.y))*self.h)],math.radians(rand_ang),random.randint(2,6),(rand_color,rand_color,rand_color),2))
            self.pos += self.vel*dt
            self.follow_particles.append([pygame.Vector2(self.pos.x+self.w/2,self.pos.y+self.h/2),pygame.Vector2(0,0),self.w/2])
        else:
            self.pos = pygame.Vector2(self.DS[0]/2-self.w/2,self.DS[1]/2-self.h/2)
            self.vel = pygame.Vector2(5,2)

            

class Player:
    def __init__(self,pos:tuple,DS:list,color:tuple=(255,255,255),sprite:pygame.Surface=None,id:int=1):
        # constants
        self.DS = DS
        self.ID:int = id

        # movment variables
        self.w, self.h = 16,90
        self.pos = pygame.Vector2(pos)
        self.vel = pygame.Vector2(0,0)
        self.max_vel = pygame.Vector2(0,5)
        self.vel_increment = pygame.Vector2(0,0.25)
        self.rect = pygame.Rect(self.pos.x, self.pos.y, self.w, self.h)
        
        # logic variables
        self.score = 0

        # effects and graphics
        self.color = color
        self.sprite = sprite
    
    def Render(self,surface,dt):
        if self.sprite != None:
            surface.blit(self.sprite,self.pos)
        else:
            pygame.draw.rect(surface,self.color,self.rect)

    def Update(self,dt,ball):
        keys = pygame.key.get_pressed()
        self.rect = pygame.Rect(self.pos.x, self.pos.y, self.w, self.h)

        # the movment
        if self.ID == 1:
            # input and moving
            if keys[pygame.K_w]:
                if self.vel.y > -self.max_vel.y:
                    self.vel -= self.vel_increment

            if keys[pygame.K_s]:
                if self.vel.y < self.max_vel.y:
                    self.vel += self.vel_increment
            
            # slowing down
            if not keys[pygame.K_s] and not keys[pygame.K_w]:
                if self.vel.y > 0:
                    self.vel -= self.vel_increment
                if self.vel.y < 0:
                    self.vel += self.vel_increment

        if self.ID == 2:
            # input and moving
            if keys[pygame.K_UP]:
                if self.vel.y > -self.max_vel.y:
                    self.vel -= self.vel_increment

            if keys[pygame.K_DOWN]:
                if self.vel.y < self.max_vel.y:
                    self.vel += self.vel_increment

            # slowing down
            if not keys[pygame.K_DOWN] and not keys[pygame.K_UP]:
                if self.vel.y > 0:
                    self.vel -= self.vel_increment
                if self.vel.y < 0:
                    self.vel += self.vel_increment

        self.pos += self.vel * dt

        if self.pos.y < 0:
            self.vel = -self.vel

        if self.pos.y+self.h > self.DS[1]:
            self.vel = -self.vel

        # collision detection
        if self.ID == 1 and ball.rect.colliderect(self.rect):
            ball.vel.x = abs(ball.vel.x)
            if ball.add_to_velocity and ball.vel.x < ball.max_velocity:
                ball.vel.x += ball.velocity_increment
            ball.screen_shake_time = 15
            for i in range(20):
                rand_color = random.randint(150,255)
                rand_ang = random.randint(90,275) if ball.vel.x/abs(ball.vel.x) == -1 else random.randint(-90,90)
                ball.sparks.append(effects.Spark([ball.pos.x-((ball.vel.x/abs(ball.vel.x))),ball.pos.y],math.radians(rand_ang),random.randint(3,9),(rand_color,rand_color,rand_color),2))
        if self.ID == 2 and ball.rect.colliderect(self.rect):
            ball.vel.x = -abs(ball.vel.x)
            if ball.add_to_velocity and ball.vel.x > -ball.max_velocity:
                ball.vel.x -= ball.velocity_increment
            ball.screen_shake_time = 15
            for i in range(20):
                rand_color = random.randint(150,255)
                rand_ang = random.randint(90,275) if ball.vel.x/abs(ball.vel.x) == -1 else random.randint(-90,90)
                ball.sparks.append(effects.Spark([ball.pos.x-((ball.vel.x/abs(ball.vel.x))),ball.pos.y],math.radians(rand_ang),random.randint(3,9),(rand_color,rand_color,rand_color),2))

        # point assignments
        if ball.pos.x <= -16 and self.ID == 2:
            self.score += 1
            ball.started = False
            ball.w = 1
            ball.screen_shake_time = 30
            for i in range(60):
                ball.particles.append([pygame.Vector2(ball.pos),pygame.Vector2(random.randint(5,10),random.randint(-10,10))/3,random.randint(-25,34)])
        
        if ball.pos.x >= ball.DS[0] and self.ID == 1:
            self.score += 1
            ball.started = False
            ball.w = 1
            ball.screen_shake_time = 30
            for i in range(60):
                ball.particles.append([pygame.Vector2(ball.pos),pygame.Vector2(random.randint(-10,-5),random.randint(-10,10))/3,random.randint(-25,34)])

                
class RandomizeParticle:
    def __init__(self,DS:tuple):
        # constants
        self.DS = DS

        # movement logic variables
        self.w, self.h = 6,6
        self.pos = pygame.Vector2(random.randint(100,DS[0]-100),random.choice([-10,DS[1]+10]))
        self.vel = pygame.Vector2(0,random.randint(10,30)/10 if self.pos.y < 0 else random.randint(-30,-10)/10)
        self.end_pos = DS[1]+18 if self.pos.y < 0 else -18
        self.rect = pygame.Rect(self.pos.x, self.pos.y, self.w, self.h)

        # logic variables
        self.effect_ID = random.randint(0,1)
        self.alive = True

        # effects and graphics
        self.color = (random.randint(100,255),random.randint(100,255),random.randint(100,255))
        self.change_color_timer = time.perf_counter()
        self.explosion_dictionary = {"r":16,"color":(255,255,255),"r2":0}
        self.explosion_surf = surf_circle(self.explosion_dictionary.get("r"),self.explosion_dictionary.get("color"),(0,0,0))


    def Draw(self,surface):
        pygame.draw.circle(surface,self.color,(self.pos.x,self.pos.y),self.self.w)
        if (time.perf_counter()-self.change_color_timer) > 1:
            self.color = (random.randint(100,255),random.randint(100,255),random.randint(100,255))

    def Update(self,dt):
        self.h = self.w
        self.pos += self.vel * dt

        if self.end_pos == -18 and self.pos.y < self.end_pos:
            self.alive = False
        if self.end_pos == self.DS[1]+18 and self.pos.y > self.end_pos:
            self.alive = False



