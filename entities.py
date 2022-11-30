import math
import random
import time

import pygame
from pygame.locals import *

import effects


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



class Ball:
    def __init__(self,DS,volume,color,sprite=None):
        # constants
        self.DS = DS
        self.volume = volume

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
        self.velocity_increment = 0.25
        self.max_velocity = 13

        # sound effects
        self.collision_hit = pygame.mixer.Sound('assets/sound-effects/collision_hit2.mp3')
        self.collision_hit.set_volume(1.0*self.volume)

        # effects and graphics
        self.light_effect = True
        self.light_surface = surf_circle(self.w*2,(color[0]/3,color[1]/3,color[2]/3),(0,0,0))
        self.sprite = sprite
        self.color = color
        self.sparks = []
        self.particles = []
        self.follow_particles = []
        self.screen_shake_time:int = 0

    def Render(self,surface:pygame.Surface,dt:float):
        #pygame.draw.rect(surface,(255,255,255),self.rect)


        for i, s in sorted(enumerate(self.sparks), reverse=True):
            s.move(dt)
            s.draw(surface)
            if not s.alive:
                self.sparks.pop(i)

        for i, p in sorted(enumerate(self.follow_particles), reverse=True):
            p[0] += p[1]*dt
            p[2] -= 0.5*dt

            pygame.draw.circle(surface,(int(self.color[0]/1.46),int(self.color[1]/1.46),int(self.color[2]/1.46)),(p[0].x,p[0].y),p[2])

            if p[2] <= 0:
                self.follow_particles.pop(i)
            
        for i, p in sorted(enumerate(self.particles), reverse=True):
            p[0] += p[1]*dt
            p[2] -= 0.25*dt
            r = p[2]+8
            s = surf_circle(r,(self.color[0]/3,self.color[1]/3,self.color[2]/3),(0,0,0))

            pygame.draw.circle(surface,self.color,(p[0].x,p[0].y),p[2])
            if p[3]:
                surface.blit(s,(p[0].x-(s.get_width()/2),p[0].y-(s.get_height()/2)),special_flags=BLEND_RGB_ADD)

            if p[2] <= 0:
                self.particles.pop(i)

    
        pygame.draw.circle(surface,self.color,(self.pos.x+self.w/2,self.pos.y+self.h/2),self.w/2)

        if self.light_effect:
            self.light_surface = surf_circle(self.w+4,(self.color[0]/3,self.color[1]/3,self.color[2]/3),(0,0,0))
            surface.blit(self.light_surface,(int((self.pos.x+self.w/2)-self.light_surface.get_width()/2),int((self.pos.y+self.h/2)-self.light_surface.get_height()/2)),special_flags=BLEND_RGB_ADD)

    def Update(self,dt:float):
        self.rect = pygame.Rect(self.pos.x, self.pos.y, self.w, self.h)
        if self.w < self.size:
            self.w += 0.5*dt
        if self.w > self.size:
            self.w -= 0.5*dt

        self.h = self.w

        if self.started:
            if self.pos.y <= 0 or self.pos.y+self.h >= self.DS[1]:
                self.pos.y = 1 if self.pos.y <= 0 else self.DS[1] - self.h
                self.vel.y = -self.vel.y
                self.collision_hit.play()
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
    def __init__(self,volume,pos:tuple,DS:list,color:tuple=(255,255,255),sprite:pygame.Surface=None,id:int=1):
        # constants
        self.DS = DS
        self.ID:int = id
        self.volume = volume

        # movment variables
        self.w, self.h = 16,0
        self.size = 90
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
        self.light_effect = True
        self.light_surface = surf_rect((self.w+10,self.h+10),(self.color[0]/3,self.color[1]/3,self.color[2]/3))

        # sounds
        self.hit = pygame.mixer.Sound('assets/sound-effects/collision_hit.mp3')
        self.explosion = pygame.mixer.Sound('assets/sound-effects/Game_over_explosion.mp3')
        self.explosion.set_volume(0.3*self.volume)
        self.hit.set_volume(1.0*self.volume)
    
    def Render(self,surface:pygame.Surface,dt:float):
        if self.sprite != None:
            surface.blit(self.sprite,self.pos)
        else:
            pygame.draw.rect(surface,self.color,self.rect)
            if self.light_effect:
                self.light_surface = surf_rect((self.w+10,self.h+10),(self.color[0]/3,self.color[1]/3,self.color[2]/3))
                surface.blit(self.light_surface, (self.pos.x-5,self.pos.y-5),special_flags=BLEND_RGB_ADD) 

    def Update(self,dt:float,ball:Ball):
        keys = pygame.key.get_pressed()
        self.rect = pygame.Rect(self.pos.x, self.pos.y, self.w, self.h)
        if self.h < self.size:
            self.pos.y -= 0.5*dt
            self.h += 1*dt
        if self.h > self.size:
            self.pos.y += 0.5*dt
            self.h -= 1*dt

        # the movment
        if self.ID == 1:
            # input and moving
            if keys[pygame.K_w]:
                if self.vel.y > -self.max_vel.y:
                    self.vel -= self.vel_increment*dt
                else:
                    self.vel.y = -self.max_vel.y

            if keys[pygame.K_s]:
                if self.vel.y < self.max_vel.y:
                    self.vel += self.vel_increment*dt
                else:
                    self.vel.y = self.max_vel.y

            # slowing down
            if not keys[pygame.K_s] and not keys[pygame.K_w]:
                if int(self.vel.y) == 0:
                    self.vel.y = 0
                if self.vel.y > 0:
                    self.vel -= self.vel_increment*dt
                if self.vel.y < 0:
                    self.vel += self.vel_increment*dt

        if self.ID == 2:
            # input and moving
            if keys[pygame.K_UP]:
                if self.vel.y > -self.max_vel.y:
                    self.vel -= self.vel_increment*dt
                else:
                    self.vel.y = -self.max_vel.y

            if keys[pygame.K_DOWN]:
                if self.vel.y < self.max_vel.y:
                    self.vel += self.vel_increment*dt
                else:
                    self.vel.y = self.max_vel.y

            # slowing down
            if not keys[pygame.K_DOWN] and not keys[pygame.K_UP]:
                if int(self.vel.y) == 0:
                    self.vel.y = 0
                if self.vel.y > 0:
                    self.vel -= self.vel_increment*dt
                if self.vel.y < 0:
                    self.vel += self.vel_increment*dt

    
        self.pos += self.vel * dt

        if self.pos.y < 0:
            self.vel = -self.vel
            self.pos.y = 0
            

        if self.pos.y+self.h > self.DS[1]:
            self.vel = -self.vel
            self.pos.y = self.DS[1]-self.h
        

        # collision detection
        if self.ID == 1 and ball.rect.colliderect(self.rect):
            self.hit.play()
            ball.vel.x *= -1
            ball.pos.x = self.pos.x+self.w
            if ball.add_to_velocity and ball.vel.x < ball.max_velocity:
                if self.vel.y == self.max_vel.y or self.vel.y == -self.max_vel.y: ball.vel.x += ball.velocity_increment*3
                else: ball.vel.x += ball.velocity_increment 
            
            ball.screen_shake_time = 15
            for i in range(60):
                rand_color = random.randint(150,255)
                rand_ang = random.randint(90,275) if ball.vel.x/abs(ball.vel.x) == -1 else random.randint(-90,90)
                ball.sparks.append(effects.Spark([ball.pos.x-((ball.vel.x/abs(ball.vel.x))),ball.pos.y],math.radians(rand_ang),random.randint(3,9),(rand_color,rand_color,rand_color),2))
        if self.ID == 2 and ball.rect.colliderect(self.rect):
            self.hit.play()
            ball.vel.x *= -1
            ball.pos.x = self.pos.x-ball.w
            if ball.add_to_velocity and ball.vel.x > -ball.max_velocity:
                if self.vel.y == self.max_vel.y or self.vel.y == -self.max_vel.y: ball.vel.x -= ball.velocity_increment*3
                else: ball.vel.x -= ball.velocity_increment 
            ball.screen_shake_time = 15
            for i in range(60):
                rand_color = random.randint(150,255)
                rand_ang = random.randint(90,275) if ball.vel.x/abs(ball.vel.x) == -1 else random.randint(-90,90)
                ball.sparks.append(effects.Spark([ball.pos.x-((ball.vel.x/abs(ball.vel.x))),ball.pos.y],math.radians(rand_ang),random.randint(3,9),(rand_color,rand_color,rand_color),2))

        # point assignments
        if ball.pos.x <= -16 and self.ID == 2:
            self.explosion.play()
            self.score += 1
            ball.started = False
            ball.w = 1
            ball.size = 16
            self.size = 90
            ball.screen_shake_time = 30
            for i in range(30):
                ball.particles.append([pygame.Vector2(ball.pos),pygame.Vector2(random.randint(5,10),random.randint(-10,10))/3,random.randint(25,34),random.choice([True,False])])
        
        if ball.pos.x >= ball.DS[0] and self.ID == 1:
            self.explosion.play()
            self.score += 1
            ball.started = False
            ball.w = 1
            ball.size = 16
            self.size = 90
            ball.screen_shake_time = 30
            for i in range(30):
                ball.particles.append([pygame.Vector2(ball.pos),pygame.Vector2(random.randint(-10,-5),random.randint(-10,10))/3,random.randint(25,34),random.choice([True, False])])

        # making player height reset to original
        if not ball.started:
            self.size = 90

                
class RandomizeParticle:
    def __init__(self,DS:tuple,volme):
        # constants
        self.DS = DS
        self.volme = volme

        # movement logic variables
        self.w, self.h = 12,12
        self.pos = pygame.Vector2(random.randint(100,DS[0]-100),random.choice([-10,DS[1]+10]))
        self.vel = pygame.Vector2(0,random.randint(10,50)/10 if self.pos.y < 0 else random.randint(-50,-10)/10)
        self.end_pos = DS[1]+18 if self.pos.y < 0 else -18
        self.rect = pygame.Rect(self.pos.x, self.pos.y, self.w, self.h)

        # logic variables
        self.effect_ID = random.randint(0,3)
        self.alive = True

        # player effect variables
        self.player_max_height = 180
        self.player_min_height = 30
        self.player_size_increment = 30

        # ball effect variables
        self.ball_max_radius = 64
        self.ball_min_radius = 4
        self.ball_size_multiplier = 2

        # sound effects
        self.collision_hit = pygame.mixer.Sound('assets/sound-effects/randomParticle.mp3')
        self.collision_hit.set_volume(0.1*self.volume)

        # effects and graphics
        self.color = (random.randint(100,255),random.randint(100,255),random.randint(100,255))
        self.light_effect = True
        self.light_surface = surf_circle(self.w+4,(self.color[0]/3,self.color[1]/3,self.color[2]/3),(0,0,0))
        self.change_color_timer = time.perf_counter()
        self.play_explosion = False # not used
        self.explosion_dictionary = {"r":16,"color":(255,255,255),"r2":0}
        self.explosion_surf = surf_circle(self.explosion_dictionary.get("r"),self.explosion_dictionary.get("color"),(0,0,0))

    def pick_effect(self,b:Ball,p1:Player,p2:Player):
        if not self.play_explosion:
            self.collision_hit.play()
            if self.effect_ID == 0 and b.size < self.ball_max_radius: # making ball bigger
                b.size *= self.ball_size_multiplier
            elif self.effect_ID == 1 and b.size > self.ball_min_radius: # making ball smaller
                b.size /= self.ball_size_multiplier
            elif self.effect_ID == 2 and p1.size < self.player_max_height and p2.size < self.player_max_height: # making player bigger
                p1.size += self.player_size_increment
                p2.size += self.player_size_increment
            elif self.effect_ID == 3 and p1.size > self.player_min_height and p2.size > self.player_min_height:
                p1.size -= self.player_size_increment
                p2.size -= self.player_size_increment
            else:
                b.vel.x = -b.vel.x
            
    def Render(self,surface:pygame.Surface,dt:float) -> None:
        #pygame.draw.rect(surface, (255,0,0), self.rect)

        # drawing the player 
        if not self.play_explosion:
            pygame.draw.circle(surface,self.color,(self.pos.x+self.w/2,self.pos.y+self.h/2),self.w/2)
            if self.light_effect:
                self.light_surface = surf_circle(self.w+4,(self.color[0]/3,self.color[1]/3,self.color[2]/3),(0,0,0))
                surface.blit(self.light_surface,(int((self.pos.x+self.w/2)-self.light_surface.get_width()/2),int((self.pos.y+self.h/2)-self.light_surface.get_height()/2)),special_flags=BLEND_RGB_ADD)
        
        # is here to change the color every second
        if (time.perf_counter()-self.change_color_timer) > 1:
            self.color = (random.randint(100,255),random.randint(100,255),random.randint(100,255))
            self.change_color_timer = time.perf_counter()
        
        # drawing the explosion
        if self.play_explosion:
            self.explosion_surf = surf_circle(self.explosion_dictionary.get("r"),self.explosion_dictionary.get("color"),(0,0,0))
            pygame.draw.circle(self.explosion_surf,(0,0,0),(self.explosion_dictionary['r'],self.explosion_dictionary['r']),self.explosion_dictionary['r2'])
            self.explosion_dictionary['r'] += 1*dt
            self.explosion_dictionary['r2'] += 2*dt
            surface.blit(self.explosion_surf,((self.pos.x+self.w/2)-self.explosion_dictionary['r'],(self.pos.y+self.h/2)-self.explosion_dictionary['r']))
            if self.explosion_dictionary['r2'] >= self.explosion_dictionary['r']:
                self.alive = False


    def Update(self,dt:float,ball:Ball,p1:Player,p2:Player) -> None:
        self.rect = pygame.Rect(self.pos.x-2, self.pos.y-2, self.w+4, self.h+4)
        self.h = self.w # the object is a circle so the height should all ways be equal to width

        # movement logic
        self.pos += self.vel * dt

        # kill particle when off screen
        if self.end_pos == -18 and self.pos.y < self.end_pos:
            self.alive = False
        if self.end_pos == self.DS[1]+18 and self.pos.y > self.end_pos:
            self.alive = False
        
        # collision with the ball
        if self.rect.colliderect(ball.rect):
            self.pick_effect(ball,p1,p2)
            self.play_explosion = True


