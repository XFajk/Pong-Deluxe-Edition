import pygame
from pygame.locals import *

import math
import time
import random

class Button:
    def __init__(self,DS:tuple,pos:tuple, text:str,font:pygame.font.Font, text_color:tuple=(255,255,255), button_color:tuple=(255,0,0), alternative_color:tuple=(100,0,0), expand:bool=False,change_color:bool=True,if_x_center:bool=False,if_y_center:bool=False):
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
    def __init__(self,DS:tuple,pos:tuple,value:float | int,font:pygame.font.Font, text_color:tuple=(255,255,255), button_color:tuple=(255,0,0), alternative_color:tuple=(100,0,0), expand:bool=False,change_color:bool=True,if_x_center:bool=False,if_y_center:bool=False):
        
        self.DS = DS

        self.pos = pygame.Vector2(pos)
        self.font = font
        self.text_color = text_color 
        self.button_color = button_color
        self.alternative_color = alternative_color
        self.value = value 
        self.rendered_value = self.font.render(f"{self.value}", False, self.text_color)
        self.change_color = change_color 
        self.expand = expand 

        self.sub = Button(DS,self.pos,"<",font,text_color,button_color,alternative_color,expand,change_color)
        self.add = Button(DS,(self.pos.x+20+self.sub.rect.w+self.rendered_value.get_width(),self.pos.y),">",font,text_color,button_color,alternative_color,expand,change_color)     

    def Render(self,surface:pygame.Surface):        
        self.rendered_value = self.font.render(f"{self.value}", False, self.text_color)
        self.add.pos.x = self.pos.x+20+self.sub.min_w+self.rendered_value.get_width()

        self.add.Render(surface)
        self.sub.Render(surface)
        surface.blit(self.rendered_value,(self.pos.x + self.sub.min_w + 10, self.pos.y+5))
    


class Menu:
    def __init__(self,DS,volume:float): 
        # constants
        self.DS = DS    
        self.volume = volume
        self.default_font = pygame.font.Font('assets/ghostclanital.ttf', 50)
        self.slider_font = pygame.font.Font('assets/ghostclanital.ttf', 30)

        # state variables
        self.menu_on = True
        self.game_on = False
        self.options_on = False

        # logic variables 
        self.scores = [0,0]

        # main menu buttons
        self.Start = Button(self.DS,(0,DS[1]/2-100),"START",self.default_font,(255,255,255),(32, 107, 10),(59, 196, 18),True,True,True)
        self.Continue = Button(self.DS,(0,DS[1]/2-35),"CONTINUE",self.default_font,(255,255,255),(107, 107, 11),(222, 222, 22),True,True,True)
        self.Options = Button(self.DS,(0,DS[1]/2+30),"OPTIONS",self.default_font,(255,255,255),(10, 58, 107),(17, 111, 207),True,True,True)
        self.Quit = Button(self.DS,(0,DS[1]/2+95),"QUIT",self.default_font,(255,255,255),(107, 12, 12),(222, 22, 22),True,True,True)

        # options buttons
        self.Back = Button(self.DS,(0,DS[1]/2+170),"BACK",self.default_font,(255,255,255),(10, 58, 107),(17, 111, 207),True,True,True)
        self.VolumeSlider = Slider(self.DS,(100,100),self.volume,self.slider_font,(255,255,255),(10,58,107),(17,111,207),True,True)


    def Render(self,surface:pygame.Surface):
        if not self.options_on:
            self.Start.Render(surface)
            self.Options.Render(surface)
            self.Continue.Render(surface)
            self.Quit.Render(surface)
        else:
            self.Back.Render(surface)
            self.VolumeSlider.Render(surface)

    def Update(self,dt:float,save_data:list):
        x,y = pygame.mouse.get_pos()
        mouse_input = pygame.mouse.get_pressed()

        if not self.options_on:
            if self.Start.rect.collidepoint((x,y)):
                self.Start.on_button()
                if mouse_input[0]:
                    self.menu_on = False
                    self.game_on = True
            else:
                self.Start.off_button()


            if self.Options.rect.collidepoint((x,y)):
                self.Options.on_button()
                if mouse_input[0]:
                    self.options_on = True
            else:
                self.Options.off_button()

            if self.Continue.rect.collidepoint((x,y)):
                self.Continue.on_button()
                if mouse_input[0]:
                    self.scores[0] = save_data[0]
                    self.scores[1] = save_data[1]
                    self.menu_on = False
                    self.game_on = True
            else:
                self.Continue.off_button()

            if self.Quit.rect.collidepoint((x,y)):
                self.Quit.on_button()
                if mouse_input[0]:
                    self.menu_on = False
                    self.game_on = False
            else:
                self.Quit.off_button()
        else:
            if self.Back.rect.collidepoint((x,y)):
                self.Back.on_button()
                if mouse_input[0]:
                    self.options_on = False
            else:
                self.Back.off_button()

            # volume slider buttons
            if self.VolumeSlider.sub.rect.collidepoint((x,y)):
                self.VolumeSlider.sub.on_button()
                self.VolumeSlider.add.text_pos = self.VolumeSlider.add.pos + pygame.Vector2(5,5)
                if mouse_input[0]:
                    if (time.perf_counter() - self.VolumeSlider.sub.timer) > 0.2:
                        self.VolumeSlider.value *= 10
                        self.VolumeSlider.value -= 1
                        self.VolumeSlider.value /= 10
                        self.VolumeSlider.sub.timer = time.perf_counter()
            else:
                self.VolumeSlider.sub.off_button()


            if self.VolumeSlider.add.rect.collidepoint((x,y)):
                self.VolumeSlider.add.on_button()
                #self.VolumeSlider.add.text_pos = self.VolumeSlider.add.pos + pygame.Vector2(5,7)
                if mouse_input[0]:
                    if (time.perf_counter() - self.VolumeSlider.add.timer) > 0.2:
                        self.VolumeSlider.value *= 10
                        self.VolumeSlider.value += 1
                        self.VolumeSlider.value /= 10
                        self.VolumeSlider.add.timer = time.perf_counter()
            else:
                self.VolumeSlider.add.off_button()


