import pygame
from pygame.locals import *

import math
import time
import random
import sys

import entities
import effects
import UI

pygame.init()


def draw_debug(surface:pygame.Surface,font:pygame.font.Font,*args:tuple):
    # arg structure will be 0 = name, 1 = value
    for i, a in sorted(enumerate(args), reverse=True):
        surface.blit(font.render(f"{a[0]}: {a[1]}",True,(255,255,255)),(5,5+i*17))

def main() -> None:

    # loading save
    # data structure p1.score p2.score volume p1.color p2.color ball.color background.color

    load = open("save.txt", 'r')
    saved_data = load.readline()
    load.close()
    saved_data = saved_data.split(' ')

    try:
        for i in range(len(saved_data)):
            if saved_data[i].find(',')>-1:
                saved_data[i] = list(saved_data[i].split(','))
                for j in range(len(saved_data[i])):
                    saved_data[i][j] = int(saved_data[i][j])
                saved_data[i] = tuple(saved_data[i])
            elif saved_data[i].find('.')>-1:
                saved_data[i] = float(saved_data[i])
            else:
                saved_data[i] = int(saved_data[i])
    except:
        print("err")
        saved_data = [0, 0, 0.5, (255,255,255), (255,255,255), (0,220,0), (0,0,100)]

    print(saved_data)


    ZOOM = 1
    WS = (800,640)
    DS = (WS[0]/ZOOM,WS[1]/ZOOM)
    window = pygame.display.set_mode(WS,FULLSCREEN)
    display = pygame.Surface(DS)
    UI_display = pygame.Surface(DS)
    clock = pygame.time.Clock()

    last_time = time.perf_counter()

    # constants
    bgcolor = saved_data[6]

    # debug stuff
    debug = False
    debug_font = pygame.font.Font(None,15)
    max_fps = 1000
    volume = saved_data[2]


    # dictionary's and simple objects/structures
    Game_font = pygame.font.Font('assets/ghostclanital.ttf', 30)


    #pygame.load.image("assets/sprites/jump_scare.png")


    # entities and objects
    ball = entities.Ball(DS,saved_data[5])
    player1 = entities.Player((10,DS[1]/2),DS,id=1,color=saved_data[3])
    player2 = entities.Player((DS[0]-16-10,DS[1]/2),DS,id=2,color=saved_data[4])
    RandomizeParticles = []
    amount_of_RandomizeParticles = 8

    menu = UI.Menu(DS)

    # text


    # timers


    # logic
    display_offset = [0,0]
    display_rotation_offset = 0

    RandomizeParticle_timer = 0.0

    while menu.menu_on or menu.game_on:
        dt = time.perf_counter() - last_time
        dt *= 60
        last_time = time.perf_counter()

        display.fill((0,1,0))
        UI_display.fill((0,0,0))
        if menu.game_on and not menu.menu_on:
            pygame.draw.rect(display,bgcolor,pygame.Rect(1,1,799,639))

            #---DISPLAY---#

            # Logic
            ball.Update(dt)
            player1.Update(dt,ball)
            player2.Update(dt,ball)


            if (time.perf_counter() - RandomizeParticle_timer) > 10 and ball.started:
                for i in range(amount_of_RandomizeParticles):
                    RandomizeParticles.append(entities.RandomizeParticle(DS))
                    RandomizeParticle_timer = time.perf_counter()


            # Rendering 
            pygame.draw.rect(display,(255,255,255),pygame.Rect(DS[0]/2-2,0,4,DS[1]))
            ball.Render(display,dt)
            player1.Render(display,dt)
            player2.Render(display,dt)

            # RandomizeParticles
            for i,p in sorted(enumerate(RandomizeParticles), reverse=True):
                p.Update(dt,ball,player1,player2)
                p.Render(display,dt)
                if not p.alive:
                    RandomizeParticles.pop(i)

            #--UI_DISPLAY---#

            # Logic


            # Rendering
            player_score_text = Game_font.render(f"{player1.score}    {player2.score}",False,(255,255,255))
            UI_display.blit(player_score_text,(DS[0]/2-player_score_text.get_width()/2,10))

            if debug:
                draw_debug(UI_display,debug_font,
                    ("fps",clock.get_fps()),
                    ("ball velocity", ball.vel),("player1 velocity",player1.vel),("player2 velocity",player2.vel),
                    ("",""),
                    ("ball position", ball.pos), ("player1 position", player1.pos), ("player2 position", player2.pos))
            
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_SPACE and not ball.started:
                        RandomizeParticle_timer = time.perf_counter()
                        ball.dir = pygame.Vector2(random.choice([-1,1]),random.choice([-1,1]))
                        ball.vel.x, ball.vel.y = ball.vel.x*ball.dir.x, ball.vel.y*ball.dir.y
                        ball.started = True
                    if event.key == K_F10:
                        if debug:
                            debug = False
                        else:
                            debug = True

                if event.type == QUIT:
                    menu.menu_on = False
                    menu.game_on = False
            
            if ball.screen_shake_time > 0:

                display_offset[0] = random.randint(-5,5)
                display_offset[1] = random.randint(-5,5)
                # display_rotation_offset += random.randint(-1,1)/10
                # WS[0] -= 2
                # WS[1] -= 2
                ball.screen_shake_time -= 1*dt
            else:
                WS = [800,640]
                display_rotation_offset = 0 
                display_offset = [0,0]
            
        elif menu.menu_on and not menu.game_on:

            # logic
            menu.Update(dt,saved_data)
            player1.score = menu.scores[0]
            player2.score = menu.scores[1]
            
            
            #--DISPLAY--#

            #--UI_DISPLAY--#

            # Rendering
            menu.Render(UI_display)

            for event in pygame.event.get():
                if event.type == QUIT:
                    menu.menu_on = False
                    menu.game_on = False
        pygame.display.update()
        UI_display.set_colorkey((0,0,0))
        window.fill((1,0,0))
        surf = pygame.transform.scale(display,WS) 
        surf_rot = pygame.transform.rotate(surf,display_rotation_offset)    
        UI_surf = pygame.transform.scale(UI_display,WS)
        UI_surf_rot = pygame.transform.rotate(UI_surf,display_rotation_offset)

        if FULLSCREEN:
            w,h = window.get_width(), window.get_height()
            #print(w,h)
            w2,h2 = surf_rot.get_width(), surf_rot.get_height()

            window.blit(surf_rot,(int(w/2-w2/2+display_offset[0]-surf_rot.get_width()/2)+surf.get_width()/2,int(h/2-h2/2+display_offset[1]-surf_rot.get_height()/2)+surf.get_height()/2))
            window.blit(UI_surf_rot,(int(w/2-w2/2+display_offset[0]-surf_rot.get_width()/2)+surf.get_width()/2,int(h/2-h2/2+display_offset[1]-surf_rot.get_height()/2)+surf.get_height()/2))
            #pygame.draw.rect(window,(0,0,0),pygame.Rect(0,0,(w-w2)/2,1200))
            #pygame.draw.rect(window,(0,0,0),pygame.Rect(w2+((w-w2)/2),0,(w-w2)/2,1200))
        else:
            window.blit(surf_rot,(int(0+display_offset[0] - surf_rot.get_width()/2)+surf.get_width()/2,int(0+display_offset[1] - surf_rot.get_height()/2)+surf.get_width()/2))
            window.blit(UI_surf_rot,(int(0+display_offset[0] - surf_rot.get_width()/2)+surf.get_width()/2,int(0+display_offset[1] - surf_rot.get_height()/2)+surf.get_width()/2))


        clock.tick(max_fps)
        pygame.display.set_caption(f"pong deluxe")

    save = open("save.txt", "w")
    # data structure p1.score p2.score volume p1.color p2.color ball.color background.color
    save.write(f"{player1.score} {player2.score} {volume} {player1.color[0]},{player1.color[1]},{player1.color[2]} {player2.color[0]},{player2.color[1]},{player2.color[2]} {ball.color[0]},{ball.color[1]},{ball.color[2]} {bgcolor[0]},{bgcolor[1]},{bgcolor[2]}")
    save.close()


if __name__ == "__main__":
    main()
    pygame.quit()
    sys.exit()
