# total 1700 lines of code
# lazy to write comments

import sys

import pygame

from background_class import Cloud_Spawner, Ground_Group
from cache import image_dict
from chrome_class import Chrome
from dinosaur_class import Dinosaur
from GUI_class import Checkbox, Image_Button, Text_Area, Text_Button
from music_player_class import Music_Player
from obstacles_class import Obstacle_Spawner
from timer_class import Timer

pygame.init()

def draw():
  screen.fill((255,255,255))
  if current_page=='title screen':
    screen.blit(cover_image,(0,0))
    play_button.draw(screen)
    setting_button.draw(screen)
    how_button.draw(screen)
  elif current_page=='setting':
    setting_title.draw(screen)
    show_obstacle_health.draw(screen)
    show_chrome_health.draw(screen)
    invincible_mode.draw(screen)
    Gatling_gun.draw(screen)
    setting_back_button.draw(screen)
  elif current_page=='how to play':
    screen.blit(how_to_play_image,(0,0))
    how_title.draw(screen)
    how_back_button.draw(screen)
  elif current_page=='game playing':
    cloud_spawner.draw(screen)
    if player.gravity_mode==0:
      ground_group.draw(screen)
      obstacle_spawner.draw(screen)
    chrome.draw(screen,timer.tick)
    player.draw(screen,timer.tick)
    if player.life==0:
      restart_button.draw(screen)
      dead_text.draw(screen)
    if chrome.health<=0:
      restart_button.draw(screen)
      win_text.draw(screen)
  pygame.display.update()

def update():
  if current_page=='title screen':
    play_button.update()
    setting_button.update()
    how_button.update()
  elif current_page=='setting':
    show_obstacle_health.check_mouse_click()
    obstacle_spawner.show_health=show_obstacle_health.value
    show_chrome_health.check_mouse_click()
    chrome.show_health=show_chrome_health.value
    invincible_mode.check_mouse_click()
    player.invincible_mode=invincible_mode.value
    Gatling_gun.check_mouse_click()
    player.gun.cooldown=20 if Gatling_gun.value else 100
    setting_back_button.update()
  elif current_page=='how to play':
    how_back_button.update()
  elif current_page=='game playing':
    if player.life>0 and chrome.health>0:
      timer.update()
      ground_group.update()
      cloud_spawner.update(timer.tick)
      chrome.update(player,timer.tick)
      obstacle_spawner.update(chrome.meteorites,chrome.left_hand,chrome.right_hand,timer.tick)
      player.update(scr_w,scr_h,obstacle_spawner.group,chrome,timer.tick)
    else:
      restart_button.update()

def game_start():
  global current_page
  current_page='game playing'
  timer.reset()
  music_player.play_random_music()

def game_restart():
  global current_page
  current_page='title screen'
  timer.reset()
  player.reset()
  obstacle_spawner.reset()
  cloud_spawner.reset()
  chrome.reset()
  music_player.play_random_music()

def go_setting_page():
  global current_page
  current_page='setting'

def setting_back():
  global current_page
  current_page='title screen'

def go_how_page():
  global current_page
  current_page='how to play'

def how_back():
  global current_page
  current_page='title screen'

def draw_text(text,x,y):
  text_surface=font.render(str(text),True,(83,83,83))
  screen.blit(text_surface,(x,y))

scr_w, scr_h = 700, 500
screen = pygame.display.set_mode((scr_w, scr_h))
pygame.display.set_caption('one last dinosaur')
scale=2
pygame.display.set_icon(image_dict['dino_idle_0.png'])
clock=pygame.time.Clock()
current_page='title screen'
font=pygame.font.SysFont('monospace',15)


ground_y=scr_h-50
player = Dinosaur(100, 250, ground_y)
ground_group = Ground_Group(scr_w,ground_y,10)
cloud_spawner=Cloud_Spawner(scr_w,ground_y)
obstacle_spawner = Obstacle_Spawner(scr_w, ground_y, 10)
chrome=Chrome(scr_w,ground_y,scr_h)

cover_image=image_dict['cover.png'].copy()
cnh=scr_w/cover_image.get_width()*cover_image.get_height()
cover_image=pygame.transform.scale(cover_image,(scr_w,cnh))
dead_text=Text_Area(scr_w/2,scr_h/2-30,'Game Over',text_color=(83,83,83),text_size=50,bg_show=True)
win_text=Text_Area(scr_w/2,scr_h/2-30,'Game Completed',text_color=(83,83,83),text_size=50,bg_show=True)
restart_button=Image_Button(scr_w//2,scr_h//2+30,'restart_button.png',game_restart)
setting_button=Text_Button(scr_w//2+240,scr_h//2-40,text='Setting',text_color=(83,83,83),text_size=40,command=go_setting_page)
play_button=Text_Button(scr_w//2+240,scr_h//2-120,text='Play',text_color=(83,83,83),text_size=40,command=game_start)
setting_title=Text_Area(scr_w//2,60,'Setting',text_size=50)
show_obstacle_health=Checkbox(scr_w//2,scr_h//2-100,False,'Show obstacle health',text_size=25)
show_chrome_health=Checkbox(scr_w//2,scr_h//2-50,False,'Show chrome health',text_size=25)
invincible_mode=Checkbox(scr_w//2,scr_h//2,False,'Invincible mode',text_size=25)
Gatling_gun=Checkbox(scr_w//2,scr_h//2+50,False,'Gatling gun',text_size=25)
setting_back_button=Text_Button(scr_w//2,scr_h//2+150,text='Back',text_size=30,command=setting_back)
how_button=Text_Button(scr_w//2+240,scr_h//2+40,text='How to play',text_size=40,command=go_how_page)
how_title=Text_Area(scr_w//2,60,'How to play',text_size=50)
how_to_play_image=image_dict['how_to_play.png'].copy()
hnh=scr_w/how_to_play_image.get_width()*how_to_play_image.get_height()
how_to_play_image=pygame.transform.scale(how_to_play_image,(scr_w,hnh))
how_back_button=Text_Button(scr_w//2,scr_h//2+150,text='Back',text_size=30,command=how_back)

timer=Timer()
music_player=Music_Player()
music_player.play_random_music()

while True:
  pygame.display.set_caption(f'fps: {round(clock.get_fps(),1)}')
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      pygame.quit()
      sys.exit()
  
  update()
  draw()
  
  clock.tick(30)