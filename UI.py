import pygame
from pygame.locals import *

import math
import time
import random

from effects import surf_circle, surf_rect
import effects


class Button:
    def __init__(self,DS:tuple,pos:tuple, text:str,font:pygame.font.Font, 
    text_color:tuple=(255,255,255), button_color:tuple=(255,0,0), alternative_color:tuple=(100,0,0), 
    expand:bool=False,change_color:bool=True,if_x_center:bool=False,if_y_center:bool=False):

        self.pos = pygame.Vector2(pos)

        self.text = text
        self.font = font
        self.text_color = text_color
        self.button_color = button_color
        self.original_color = button_color
        self.alternative_color = alternative_color
        self.expand = expand
        self.change_color = change_color
        
        self.rendered_text = self.font.render(self.text,False,self.text_color)
        if if_x_center:
            self.pos.x = DS[0]/2-self.rendered_text.get_width()/2
        if if_y_center:
            self.pos.y = DS[1]/2-self.rendered_text.get_height()/2
        self.w,self.h = self.rendered_text.get_width()+10,self.rendered_text.get_height()+10
        self.text_pos = self.pos + pygame.Vector2(5,5)
        self.min_w,self.min_h = self.w,self.h
        self.max_w,self.max_h = self.w+self.w/10,self.h+self.h/5
        self.rect = pygame.Rect(self.pos.x,self.pos.y,self.w,self.h)
        self.set_timer = False
        self.timer = None
    

    def change_width_and_height(self,w,h):
        self.w,self.h = w,h

    def on_button(self):
        if not self.set_timer:
            self.timer = time.perf_counter()
            self.set_timer = True
        if self.expand:
            if self.w < self.max_w:
                self.pos.x -= 0.5
                self.w += 1
            if self.h < self.max_h:
                self.pos.y -= 0.5
                self.h += 1
        if self.change_color:
            self.button_color = self.alternative_color
        
    def off_button(self):
        if self.set_timer:
            self.timer = None
            self.set_timer = False
        if self.expand:
            if self.w > self.min_w:
                self.pos.x += 0.5
                self.w -= 1
            if self.h > self.min_h:
                self.pos.y += 0.5
                self.h -= 1
        if self.change_color:
            self.button_color = self.original_color

    def Render(self,surface):
        self.rect =  pygame.Rect(self.pos.x,self.pos.y,self.w,self.h)
        pygame.draw.rect(surface,self.button_color,self.rect)
        surface.blit(self.rendered_text,(self.text_pos.x,self.text_pos.y))



class Slider:
    def __init__(self,DS:tuple,pos:tuple,value,max_value,min_value,increment,font:pygame.font.Font, 
    text_color:tuple=(255,255,255), button_color:tuple=(255,0,0), alternative_color:tuple=(100,0,0), 
    expand:bool=False,change_color:bool=True,if_x_center:bool=False,if_y_center:bool=False,name_of_slider:str="",if_bool:bool=False):

        
        self.DS = DS

        self.name_of_slider = ""
        self.rendered_name = None
        
        # this makes sure that the name of the slider is not empty
        if name_of_slider == "":
            pass
        else:
            self.name_of_slider = name_of_slider
            self.rendered_name = font.render(self.name_of_slider,False,(text_color))
            

        self.if_bool = if_bool
        self.max_value = max_value
        self.min_value = min_value
        self.increment = increment
        self.pos = pygame.Vector2(pos)
        self.font = font
        self.text_color = text_color 
        self.button_color = button_color
        self.alternative_color = alternative_color
        self.value = value 
        if if_bool:
            self.value = bool(self.value)
        self.rendered_value = self.font.render(f"{self.value}", False, self.text_color)
        self.rendered_value_w_h  = self.font.render(f"{self.max_value}", False, self.text_color).get_width(), self.font.render(f"{self.max_value}", False, self.text_color).get_height()
        if if_bool: self.rendered_value_w_h = self.font.render(f"{bool(self.max_value)}",False, self.text_color).get_width(), self.font.render(f"{bool(self.max_value)}",False, self.text_color).get_height()
        self.change_color = change_color
        self.expand = expand  

        self.sub = Button(DS,self.pos,"<",font,text_color,button_color,alternative_color,expand,change_color)
        self.add = Button(DS,(self.pos.x+20+self.sub.min_w+self.rendered_value_w_h[0]+30,self.pos.y),">",font,text_color,button_color,alternative_color,expand,change_color)

        self.complete_width = self.sub.min_w+20+self.rendered_value_w_h[0]+30+self.add.min_w     

        if if_x_center:
            self.pos.x = self.DS[0]/2-self.complete_width/2
        if if_y_center:
            self.pos.y = self.DS[1]/2-self.sub.min_w/2

        self.sub = Button(DS,self.pos,"<",font,text_color,button_color,alternative_color,expand,change_color)
        self.add = Button(DS,(self.pos.x+20+self.sub.min_w+self.rendered_value_w_h[0]+30,self.pos.y),">",font,text_color,button_color,alternative_color,expand,change_color)

    def Render(self,surface:pygame.Surface):
        self.rendered_value = self.font.render(f"{self.value}", False, self.text_color)
        self.add.pos.x = self.pos.x+20+self.sub.min_w+self.rendered_value_w_h[0]+30

        self.add.Render(surface)
        self.sub.Render(surface)
        surface.blit(self.rendered_value,(self.pos.x+self.complete_width/2-self.rendered_value.get_width()/2, self.pos.y+5))

        # drawing the name of the Slider
        if self.rendered_name != None:
            surface.blit(self.rendered_name,(self.pos.x+(self.complete_width-self.rendered_name.get_width())/2,self.pos.y-10-self.rendered_name.get_height()))

    def basic_slider_logic(self,pos:tuple,mouse_input,sound_effect:pygame.mixer.Sound=None,input_timeout:float=0.15):
        if self.sub.rect.collidepoint(pos):
            self.sub.on_button()
            self.add.text_pos = self.add.pos + pygame.Vector2(5,5)
            if mouse_input[0]:
                if (time.perf_counter() - self.sub.timer) > input_timeout:
                    if sound_effect != None:
                        sound_effect.play()
                    self.value *= 10
                    if self.value > self.min_value*10:
                        self.value -= self.increment*10
                    self.value /= 10
                    if self.if_bool: self.value = bool(self.value)
                    self.sub.timer = time.perf_counter()
        else:
            self.sub.off_button()


        if self.add.rect.collidepoint(pos):
            self.add.on_button()
            if mouse_input[0]:
                self.add.text_pos = self.add.pos + pygame.Vector2(6,8)
                if (time.perf_counter() - self.add.timer) > input_timeout:
                    if sound_effect != None:
                        sound_effect.play()
                    self.value *= 10
                    if self.value < self.max_value*10:
                        self.value += self.increment*10
                    self.value /= 10
                    if self.if_bool: self.value = bool(self.value)
                    self.add.timer = time.perf_counter()
        else:
            self.add.off_button()
            if self.add.w == self.add.min_w:
                self.add.text_pos = self.add.pos + pygame.Vector2(5,5)


        
    


class Menu:
    def __init__(self,DS,volume:float,sd:list): 
        # constants
        self.DS = DS    
        self.lighting = sd[7]
        self.volume = volume
        self.ball_color = sd[5]
        self.player1_color = sd[3]
        self.player2_color = sd[4]
        self.background_color = sd[6]
        self.amount_of_RandomizeParticles = sd[8]
        self.ball_add_to_vel = bool(sd[9])
        self.play_until = sd[10]
        self.power_up_spawn_time = sd[11]
        self.ball_interesting_physics = sd[12]

        self.default_font = pygame.font.Font('assets/ghostclanital.ttf', 50)
        self.slider_font = pygame.font.Font('assets/ghostclanital.ttf', 30)

        # state variables
        self.player1_win = False
        self.player2_win = False
        self.menu_on = True
        self.game_on = False
        self.options_on = False
        self.game_menu_on = False

        # logic variables 
        self.scores = [0,0]

        # sound effects
        self.select_sound = pygame.mixer.Sound("assets/sound-effects/Select_sound.wav")
        self.select_sound.set_volume(1.0*self.volume)
        self.firework_sounds = [pygame.mixer.Sound("assets/sound-effects/firework.mp3"),pygame.mixer.Sound("assets/sound-effects/firework2.mp3")]


        ### MAIN MENU BUTTON'S ###
        self.Start = Button(self.DS,(0,DS[1]/2-100),"START",self.default_font,(255,255,255),(32, 107, 10),(59, 196, 18),True,True,True)
        self.Continue = Button(self.DS,(0,DS[1]/2-35),"CONTINUE",self.default_font,(255,255,255),(107, 107, 11),(222, 222, 22),True,True,True)
        self.Options = Button(self.DS,(0,DS[1]/2+30),"OPTIONS",self.default_font,(255,255,255),(10, 58, 107),(17, 111, 207),True,True,True)
        self.Quit = Button(self.DS,(0,DS[1]/2+95),"QUIT",self.default_font,(255,255,255),(107, 12, 12),(222, 22, 22),True,True,True)

        ### OPTION BUTTON'S ###
        self.Back = Button(self.DS,(0,DS[1]/2+240),"BACK",self.default_font,(255,255,255),(10, 58, 107),(17, 111, 207),True,True,True)

        # volume slider
        self.VolumeSlider = Slider(self.DS,(0,100),self.volume,1.0,0.0,0.1,self.slider_font,(255,255,255),(10,58,107),(17,111,207),True,True,True,False,"volume")

        # if lighting slider
        self.LightSlider = Slider(self.DS,(100,100),self.lighting,1.0,0.0,1.0,self.slider_font,(255,255,255),(10, 58, 107),(17, 111, 207),True,True,False,False,"LIGHTING",True)

        # ball color slider's
        self.ballRedSlider = Slider(self.DS,(100,200),self.ball_color[0],255,0,5,self.slider_font,(255,255,255),(107, 12, 12),(222, 22, 22),True,True)
        self.ballGreenSlider = Slider(self.DS,(0,200),self.ball_color[1],255,0,5,self.slider_font,(255,255,255),(32, 107, 10),(59, 196, 18),True,True,True,False,"BALL COLOR")
        self.ballBlueSlider = Slider(self.DS,(534,200),self.ball_color[2],255,0,5,self.slider_font,(255,255,255),(10, 58, 107),(17, 111, 207),True,True,False,False)

        # player1 color slider's
        self.playerOneRedSlider = Slider(self.DS,(100,350),self.player1_color[0],255,0,5,self.slider_font,(255,255,255),(107, 12, 12),(222, 22, 22),True,True)
        self.playerOneGreenSlider = Slider(self.DS,(0,350),self.player1_color[1],255,0,5,self.slider_font,(255,255,255),(32, 107, 10),(59, 196, 18),True,True,True,False,"COLOR OF PLAYERS")
        self.playerOneBlueSlider = Slider(self.DS,(534,350),self.player1_color[2],255,0,5,self.slider_font,(255,255,255),(10, 58, 107),(17, 111, 207),True,True)

        # player2 color slider's
        self.playerTwoRedSlider = Slider(self.DS,(100,400),self.player2_color[0],255,0,5,self.slider_font,(255,255,255),(107, 12, 12),(222, 22, 22),True,True)
        self.playerTwoGreenSlider = Slider(self.DS,(0,400),self.player2_color[1],255,0,5,self.slider_font,(255,255,255),(32, 107, 10),(59, 196, 18),True,True,True)
        self.playerTwoBlueSlider = Slider(self.DS,(534,400),self.player2_color[2],255,0,5,self.slider_font,(255,255,255),(10, 58, 107),(17, 111, 207),True,True)

        # background color slider's
        self.backgroundRedSlider = Slider(self.DS,(100,500),self.background_color[0],255,0,5,self.slider_font,(255,255,255),(107, 12, 12),(222, 22, 22),True,True)
        self.backgroundGreenSlider = Slider(self.DS,(0,500),self.background_color[1],255,0,5,self.slider_font,(255,255,255),(32, 107, 10),(59, 196, 18),True,True,True,False,"BACKGROUND COLOR")
        self.backgroundBlueSlider = Slider(self.DS,(534,500),self.background_color[2],255,0,5,self.slider_font,(255,255,255),(10, 58, 107),(17, 111, 207),True,True)

        ### GAME MENU BUTTON'S ###
        self.Go = Button(self.DS, (650,DS[1]/2+240),"GO->",self.default_font,(255,255,255),(32,107,10),(59, 196, 18),True,True,False,False)  
        self.GoBack = Button(self.DS, (30,DS[1]/2+240),"<-BACK",self.default_font,(255,255,255),(107, 12, 12), (222, 22, 22), True,True,False,False)
        
        self.randomParticleAmountSlider = Slider(self.DS,(100,100),self.amount_of_RandomizeParticles,8,0,1,self.slider_font,(255,255,255),(10,58,107),(17, 111, 207),True,True,False,False,"POWER UP'S")
        self.ballVelocitySlider = Slider(self.DS,(0,100),self.ball_add_to_vel,1,0,1,self.slider_font,(255,255,255),(10,58,107),(17,111,207),True,True,True,False,"increase vel", True)
        self.playUntilSlider = Slider(self.DS,(550,100),self.play_until,20,1,1,self.slider_font,(255,255,255),(10,58,107),(17,111,207),True,True,False,False, "play until")
        self.powerUpSpawnTimeSlider = Slider(self.DS,(0,250),self.power_up_spawn_time,15,1,0.1, self.slider_font,(255,255,255),(10,58,107),(17,111,207),True,True,True,False,"power up spawn time") 
        self.ballInterestingPhysicsSlider = Slider(self.DS,(0,400),self.ball_interesting_physics,1,0,1,self.slider_font,(255,255,255),(10,58,107),(17,111,207),True,True,True,False,"interesting ball physics",True)


        # graphics variables 
        self.title_img = pygame.image.load("assets/sprites/Title.png").convert()
        self.title_img.set_colorkey((0,0,0))
        self.fireworks = []
        self.firework_particles = []
        self.firework_spawn_timer = 0.0

        # text's
        self.player1_won_text = self.default_font.render("PLAYER 1 WON", False, (255,255,255))
        self.player2_won_text = self.default_font.render("PLAYER 2 WON", False, (255,255,255))

    def Render(self,surface:pygame.Surface,dt:float):
        if not self.options_on and not self.game_menu_on and not self.player1_win and not self.player2_win:

            surface.blit(self.title_img, (245,30))            

            self.Start.Render(surface)
            self.Options.Render(surface)
            self.Continue.Render(surface)
            self.Quit.Render(surface)

        elif self.options_on and not self.game_menu_on:

            pygame.draw.rect(surface,self.background_color,pygame.Rect(1,1,799,639))
            self.Back.Render(surface)
            self.VolumeSlider.Render(surface)
            self.LightSlider.Render(surface)

            # ball slider's
            self.ballRedSlider.Render(surface)
            self.ballGreenSlider.Render(surface)
            self.ballBlueSlider.Render(surface)
            # render the ball
            pygame.draw.circle(surface,self.ball_color,(self.DS[0]/2,270),10)
            if bool(self.LightSlider.value):
                ball_light_surface = surf_circle(20,(self.ball_color[0]/3,self.ball_color[1]/3,self.ball_color[2]/3),(0,0,0))
                surface.blit(ball_light_surface,(int((self.DS[0]/2)-ball_light_surface.get_width()/2),int((270)-ball_light_surface.get_height()/2)),special_flags=BLEND_RGB_ADD)

            # player 1 slider's
            self.playerOneRedSlider.Render(surface)
            self.playerOneGreenSlider.Render(surface)
            self.playerOneBlueSlider.Render(surface)
            # player 2 slider's
            self.playerTwoRedSlider.Render(surface)
            self.playerTwoGreenSlider.Render(surface)
            self.playerTwoBlueSlider.Render(surface)
            # render of the player's
            pygame.draw.rect(surface,self.player1_color,pygame.Rect(10,self.DS[1]/2-45,16,90))
            if bool(self.LightSlider.value):
                player1_light_surface = surf_rect((16+10,90+10),(self.player1_color[0]/3,self.player1_color[1]/3,self.player1_color[2]/3))
                surface.blit(player1_light_surface, (10-5,(self.DS[1]/2-45)-5),special_flags=BLEND_RGB_ADD) 

            pygame.draw.rect(surface,self.player2_color,pygame.Rect(self.DS[0]-16-10,self.DS[1]/2-45,16,90))
            if bool(self.LightSlider.value):
                player2_light_surface = surf_rect((16+10,90+10),(self.player2_color[0]/3,self.player2_color[1]/3,self.player2_color[2]/3))
                surface.blit(player2_light_surface, ((self.DS[0]-16-10)-5,(self.DS[1]/2-45)-5),special_flags=BLEND_RGB_ADD) 

            # background slider's
            self.backgroundRedSlider.Render(surface)
            self.backgroundGreenSlider.Render(surface)
            self.backgroundBlueSlider.Render(surface)

        elif not self.options_on and self.game_menu_on:

            self.Go.Render(surface)
            self.GoBack.Render(surface)

            self.randomParticleAmountSlider.Render(surface)
            self.ballVelocitySlider.Render(surface)
            self.playUntilSlider.Render(surface)
            self.powerUpSpawnTimeSlider.Render(surface)
            self.ballInterestingPhysicsSlider.Render(surface)

        elif self.menu_on and self.player1_win:
            if (time.perf_counter() - self.firework_spawn_timer) > 0.5:
                rand_color = (random.randint(100,255),random.randint(100,255),random.randint(100,255))
                ang = -90
                rand_pos = pygame.Vector2(random.randint(60,int(self.DS[0]-60)), self.DS[1])
                self.fireworks.append(effects.Spark([rand_pos.x,rand_pos.y],math.radians(ang),random.randint(13,15),rand_color,2))
                self.firework_spawn_timer = time.perf_counter()

            for i, firework in sorted(enumerate(self.fireworks), reverse=True):
                firework.move(dt)
                firework.draw(surface)
                if not firework.alive:
                    for x in range(60):
                        rand_ang = random.randint(0,360)
                        self.firework_particles.append(effects.Spark([firework.loc[0],firework.loc[1]],math.radians(rand_ang),random.randint(4,9),firework.color,2))
                    self.firework_sounds[random.randint(0, 1)].play()
                    self.fireworks.pop(i)

            for i, firework_particle in sorted(enumerate(self.firework_particles), reverse=True): 
                firework_particle.move(dt)
                firework_particle.draw(surface) 
                if not firework_particle.alive:
                    self.firework_particles.pop(i)


            surface.blit(self.player1_won_text,(self.DS[0]/2-self.player1_won_text.get_width()/2,self.DS[1]/2-self.player1_won_text.get_height()/2))
        elif self.menu_on and self.player2_win:
            if (time.perf_counter() - self.firework_spawn_timer) > 0.5:
                rand_color = (random.randint(100,255),random.randint(100,255),random.randint(100,255))
                ang = -90
                rand_pos = pygame.Vector2(random.randint(60,int(self.DS[0]-60)), self.DS[1])
                self.fireworks.append(effects.Spark([rand_pos.x,rand_pos.y],math.radians(ang),random.randint(13,15),rand_color,2))
                self.firework_spawn_timer = time.perf_counter()

            for i, firework in sorted(enumerate(self.fireworks), reverse=True):
                firework.move(dt)
                firework.draw(surface)
                if not firework.alive:
                    for x in range(60):
                        rand_ang = random.randint(0,360)
                        self.firework_particles.append(effects.Spark([firework.loc[0],firework.loc[1]],math.radians(rand_ang),random.randint(4,9),firework.color,2))
                    self.firework_sounds[random.randint(0, 1)].play()
                    self.fireworks.pop(i)

            for i, firework_particle in sorted(enumerate(self.firework_particles), reverse=True): 
                firework_particle.move(dt)
                firework_particle.draw(surface) 
                if not firework_particle.alive:
                    self.firework_particles.pop(i)


            surface.blit(self.player2_won_text,(self.DS[0]/2-self.player2_won_text.get_width()/2,self.DS[1]/2-self.player2_won_text.get_height()/2))





    def Update(self,dt:float,save_data:list):

        x,y = pygame.mouse.get_pos()
        mouse_input = pygame.mouse.get_pressed()
        self.select_sound.set_volume(1.0*self.volume)

        if not self.options_on and not self.game_menu_on:

            if self.Start.rect.collidepoint((x,y)):
                self.Start.on_button()
                if mouse_input[0]:
                    self.select_sound.play()
                    self.scores[0] = 0
                    self.scores[1] = 0
                    self.game_menu_on = True
            else:
                self.Start.off_button()


            if self.Options.rect.collidepoint((x,y)):
                self.Options.on_button()
                if mouse_input[0]:
                    self.select_sound.play()
                    self.options_on = True
            else:
                self.Options.off_button()

            if self.Continue.rect.collidepoint((x,y)):
                self.Continue.on_button()
                if mouse_input[0]:
                    self.select_sound.play()
                    self.scores[0] = save_data[0]
                    self.scores[1] = save_data[1]
                    self.menu_on = False
                    self.game_on = True
            else:
                self.Continue.off_button()

            if self.Quit.rect.collidepoint((x,y)):
                self.Quit.on_button()
                if mouse_input[0]:
                    self.select_sound.play()
                    self.menu_on = False
                    self.game_on = False
            else:
                self.Quit.off_button()

        elif self.options_on and not self.game_menu_on:
            if self.Back.rect.collidepoint((x,y)):
                self.Back.on_button()
                if mouse_input[0]:
                    self.select_sound.play()
                    self.options_on = False
            else:
                self.Back.off_button()

            # volume slider
            self.VolumeSlider.basic_slider_logic((x,y),mouse_input,self.select_sound)

            # lighting slider
            self.LightSlider.basic_slider_logic((x,y),mouse_input,self.select_sound)

            # ball slider's
            self.ballRedSlider.basic_slider_logic((x,y),mouse_input,self.select_sound)
            self.ballGreenSlider.basic_slider_logic((x,y),mouse_input,self.select_sound)
            self.ballBlueSlider.basic_slider_logic((x,y),mouse_input,self.select_sound)

            # player 1 slider's
            self.playerOneRedSlider.basic_slider_logic((x,y),mouse_input,self.select_sound)
            self.playerOneGreenSlider.basic_slider_logic((x,y),mouse_input,self.select_sound)
            self.playerOneBlueSlider.basic_slider_logic((x,y),mouse_input,self.select_sound)

            # player 2 slider's
            self.playerTwoRedSlider.basic_slider_logic((x,y),mouse_input,self.select_sound)
            self.playerTwoGreenSlider.basic_slider_logic((x,y),mouse_input,self.select_sound)
            self.playerTwoBlueSlider.basic_slider_logic((x,y),mouse_input,self.select_sound)

            # background slider's
            self.backgroundRedSlider.basic_slider_logic((x,y),mouse_input,self.select_sound)
            self.backgroundGreenSlider.basic_slider_logic((x,y),mouse_input,self.select_sound)
            self.backgroundBlueSlider.basic_slider_logic((x,y),mouse_input,self.select_sound)

            self.volume = self.VolumeSlider.value
            self.lighting = self.LightSlider.value
            self.ball_color = (self.ballRedSlider.value,self.ballGreenSlider.value,self.ballBlueSlider.value)
            self.player1_color = (self.playerOneRedSlider.value,self.playerOneGreenSlider.value,self.playerOneBlueSlider.value)
            self.player2_color = (self.playerTwoRedSlider.value,self.playerTwoGreenSlider.value,self.playerTwoBlueSlider.value)
            self.background_color = (self.backgroundRedSlider.value,self.backgroundGreenSlider.value,self.backgroundBlueSlider.value)

        elif not self.options_on and self.game_menu_on:

            if self.Go.rect.collidepoint((x,y)):
                self.Go.on_button()
                if mouse_input[0]:
                    self.select_sound.play()
                    self.menu_on = False
                    self.game_on = True
            else:
                self.Go.off_button()


            if self.GoBack.rect.collidepoint((x,y)):
                self.GoBack.on_button()
                if mouse_input[0]:
                    self.select_sound.play()
                    self.game_menu_on = False
            else:
                self.GoBack.off_button()


            self.randomParticleAmountSlider.basic_slider_logic((x,y),mouse_input,self.select_sound)
            self.ballVelocitySlider.basic_slider_logic((x,y),mouse_input,self.select_sound) 
            self.playUntilSlider.basic_slider_logic((x,y),mouse_input,self.select_sound)       
            self.powerUpSpawnTimeSlider.basic_slider_logic((x,y), mouse_input,self.select_sound)
            self.ballInterestingPhysicsSlider.basic_slider_logic((x,y), mouse_input,self.select_sound)

            self.ball_interesting_physics = bool(self.ballInterestingPhysicsSlider.value)
            self.power_up_spawn_time = self.powerUpSpawnTimeSlider.value
            self.amount_of_RandomizeParticles = self.randomParticleAmountSlider.value
            self.ball_add_to_vel = bool(self.ballVelocitySlider.value)
            self.play_until = self.playUntilSlider.value
