import random

import pygame

from cache import image_dict
from sprite_class import Sprite


class Ground_Group:
  def __init__(self,scr_w, ground_y, speed):
    self.ground_image_numbers=7
    self.create_ground_tiles(scr_w, ground_y+5,speed)
  
  def create_ground_tiles(self,scr_w, ground_y, speed):
    self.group=pygame.sprite.Group()
    self.tile_width=image_dict['ground_0.png'].get_width()
    self.num_tiles=scr_w//self.tile_width
    for x in range(self.num_tiles+1):
      ri=random.randint(0,self.ground_image_numbers)
      tile=Sprite(x*self.tile_width,ground_y,speed,'ground_'+str(ri)+'.png')
      self.group.add(tile)

  def draw(self,screen):
    for tile in self.group:
      tile.draw(screen)
      
  def update(self):
    for tile in self.group:
      tile.x_move(-tile.speed)
      if tile.x<=-self.tile_width:
        tile.x=self.num_tiles*self.tile_width
        ri=random.randint(0,self.ground_image_numbers)
        tile.load_image('ground_'+str(ri)+'.png')
        tile.create_rect(tile.x,tile.y)
      # elif tile.x>=self.num_tiles*self.tile_width:
      #   tile.x=-self.tile_width
      #   ri=random.randint(0,len(self.ground_image_numbers)-1)
      #   tile.new_image(self.ground_images[ri])

class Cloud_Spawner:
  def __init__(self,spawn_x,ground_y):
    self.spawn_x=spawn_x
    self.ground_y=ground_y
    self.spawn_interval=8000
    self.last_spawn_tick=0
    self.clouds=pygame.sprite.Group()

  def reset(self):
    self.last_spawn_tick=0
    self.clouds.empty()

  def spawn(self,tick):
    if tick-self.last_spawn_tick>=self.spawn_interval:
      self.last_spawn_tick=tick
      y=random.randint(50,self.ground_y-50)
      speed=random.uniform(0.5,1)
      cloud=Sprite(self.spawn_x,y,speed,'cloud.png')
      self.clouds.add(cloud)

  def draw(self,screen):
    for cloud in self.clouds:
      cloud.draw(screen)

  def update(self,tick):
    self.spawn(tick)
    for cloud in self.clouds:
      cloud.x_move(-cloud.speed)
      if cloud.x<=-cloud.rect.width:
        cloud.kill()