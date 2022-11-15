import pygame
from pygame.locals import *

import math
import time
import random

class Button:
    def __init__(self,pos:tuple, text,font:pygame.font.Font, text_color:tuple=(255,255,255), button_color:tuple=(255,0,0), alternative_color:tuple=(100,0,0), expand:bool=False,change_color:bool=True):
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
        self.w,self.h = self.rendered_text.get_width(),self.rendered_text.get_height()
        self.min_w,self.min_h = self.w,self.h
        self.max_w,self.max_h = self.w+10,self.h+10
        self.text_pos = pygame.Vector2(self.pos)
        self.rect = pygame.Rect(self.pos.x,self.pos.y,self.w,self.h)
    
    def on_click(self,function,tuple_of_args:tuple):
        return function(tuple_of_args)

    def change_width_and_height(self,w,h):
        self.w,self.h = w,h
    
    
    def make_opposite(self,b:tuple):
        if b[0]:
            b[0] = False
        else:
            b[0] = True
        return b
    
    def on_button(self):
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
        if self.expand:
            if self.w > self.min_w:
                self.pos.x += 0.5
                self.w -= 1
            if self.h > self.min_h:
                self.pos.y += 0.5
                self.h -= 1
        if self.change_color:
            self.button_color = self.original_color

    def Render(self):
        ...

    

class Menu:
    def __init__(self,DS): 
        # constants
        self.DS = DS

        
        self.Start = Button()