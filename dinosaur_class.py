import random

import pygame

from cache import image_dict, sound_dict
from obstacles_class import Smoke
from sprite_class import Animated_Sprite
from weapon_class import Gun


class Dinosaur(Animated_Sprite):
  def __init__(self, x, y, ground_y):
    super().__init__(x, y, 8,'idle',0.3,'dino_idle_')
    self.load_one_animation('run', 'dino_run_')
    self.load_one_animation('jump', 'dino_jump_')
    self.load_one_animation('duck', 'dino_duck_')
    self.load_one_animation('dead', 'dino_dead_')
    self.start_x,self.start_y=x,y
    self.ground_y = ground_y
    self.run_rect = self.animations['run'][0].get_rect(bottomleft=(self.x,self.y))
    self.duck_rect = self.animations['duck'][0].get_rect(bottomleft=(self.x, self.y))
    self.dir_x=1
    self.rect = self.run_rect
    self.run_mask=pygame.mask.from_surface(self.animations['run'][0])
    self.duck_mask=pygame.mask.from_surface(self.animations['duck'][0])
    self.mask=self.run_mask
    self.gravity_mode=0
    self.gravity = 1.4
    self.jump_speed = 15
    self.max_jump_speed = 15
    self.is_jumping = True
    self.is_ducking = False
    self.is_dashing=False
    self.dash_counter=0
    self.dash_cooldown=1000
    self.last_dash_tick=0
    self.life=10
    self.invincible_mode=False
    self.invincible_time=0
    self.invincible_start_tick=0
    self.invincible=False
    self.collision=False
    self.heart=image_dict['heart.png']
    self.gun=Gun(self.x,self.y)
    self.smokes=pygame.sprite.Group()

  def movement_x(self, key, min_x, max_x):
    self.dir_x=1
    if key[pygame.K_a] or key[pygame.K_LEFT]:
      self.dir_x=-1
      self.x_move(-self.speed, min_x, max_x)
    elif key[pygame.K_d] or key[pygame.K_RIGHT]:
      self.x_move(self.speed, min_x, max_x)
    self.run_rect.bottomleft = (self.x, self.y)
    self.duck_rect.bottomleft = (self.x, self.y)

  def movement_y(self, key, min_y, max_y):
    if key[pygame.K_w] or key[pygame.K_UP]:
      self.y_move(self.speed, min_y, max_y)
    elif key[pygame.K_s] or key[pygame.K_DOWN]:
      self.y_move(-self.speed, min_y, max_y)
    self.run_rect.bottomleft = (self.x, self.y)
    self.duck_rect.bottomleft = (self.x, self.y)

  def animation_name_update(self):
    if self.life>0:
      if self.is_ducking:
        self.change_animation('duck')
      elif self.is_jumping:
        self.change_animation('jump')
      else:
        self.change_animation('run')
    else:
      self.change_animation('dead')
      self.rect=self.run_rect
      self.mask=self.run_mask

  def duck(self, key):
    if key[pygame.K_s] or key[pygame.K_DOWN]:
      self.is_ducking = True
      self.rect = self.duck_rect
      self.mask=self.duck_mask
    else:
      self.is_ducking = False
      self.rect = self.run_rect
      self.mask=self.run_mask
    if self.is_jumping and self.is_ducking:
      self.jump_speed = -1.2*self.max_jump_speed

  def jump(self, key):
    if (key[pygame.K_w] or key[pygame.K_UP]) and not self.is_jumping and not self.is_ducking:
      self.is_jumping = True
      self.jump_speed = self.max_jump_speed

  def dash(self,key,tick):
    if key[pygame.K_SPACE] and tick-self.last_dash_tick>=self.dash_cooldown:
      self.is_dashing=True
    if self.is_dashing and self.dash_counter==0:
      sound_dict['dash.wav'].play()
    if self.is_dashing and self.dash_counter<5:
      self.set_invincible(100,tick)
      self.x_move(self.dir_x*self.speed*3.5)
      self.dash_counter+=1
    if self.dash_counter>=5:
      self.dash_counter=0
      self.is_dashing=False
      self.last_dash_tick=tick

  def apply_gravity(self):
    if self.is_jumping:
      self.y -= self.jump_speed
      self.jump_speed -= self.gravity
    if self.y >= self.ground_y:
      self.y = self.ground_y
      self.is_jumping = False
      self.jump_speed = 0
    self.run_rect.bottomleft = (self.x, self.y)
    self.duck_rect.bottomleft = (self.x, self.y)

  def check_collisoin_obstacle(self,obstacle_group,meteorite_group,laser_group,moving_bullets,left_hand,right_hand,tick):
    if not self.invincible:
      collide_obstacle=self.gravity_mode==0 and  any(self.rect.colliderect(obstacle.rect) and self.mask.overlap(obstacle.mask,(obstacle.rect.x-self.rect.x,obstacle.rect.y-self.rect.y)) for obstacle in obstacle_group)
      collide_meteorite= any(not meteorite.exploded and self.rect.colliderect(meteorite.rect) and self.mask.overlap(meteorite.mask,(meteorite.rect.x-self.rect.x,meteorite.rect.y-self.rect.y)) for meteorite in meteorite_group)
      collide_laser=any((laser.resizing or laser.attacking) and self.rect.colliderect(laser.rect) and self.mask.overlap(laser.mask,(laser.rect.x-self.rect.x,laser.rect.y-self.rect.y)) for laser in laser_group)
      collide_moving_bullets=self.gravity_mode==1 and  any(self.rect.colliderect(bullet.rect) and self.mask.overlap(bullet.mask,(bullet.rect.x-self.rect.x,bullet.rect.y-self.rect.y)) for bullet in moving_bullets)
      collide_left_hand=self.gravity_mode==0 and left_hand.attacking and self.rect.colliderect(left_hand.rect)  and self.mask.overlap(left_hand.mask,(left_hand.rect.x-self.rect.x,left_hand.rect.y-self.rect.y))
      collide_right_hand=self.gravity_mode==0 and right_hand.attacking and self.rect.colliderect(right_hand.rect) and self.mask.overlap(right_hand.mask,(right_hand.rect.x-self.rect.x,right_hand.rect.y-self.rect.y))
      if collide_obstacle or collide_meteorite or collide_laser or collide_moving_bullets or collide_left_hand or collide_right_hand:
        self.life-=1
        self.collision=True
        self.set_invincible(1000,tick)

  def set_invincible(self,time,tick):
    self.invincible=True
    self.invincible_time=time
    self.invincible_start_tick=tick
  
  def check_invincible_end(self,tick):
    if self.invincible and tick-self.invincible_start_tick>self.invincible_time:
      self.invincible=False
      self.collision=False

  def draw_hearts(self,screen):
    if self.life>0:
      for i in range(self.life):
        x=(self.heart.get_width()+5)*i+5
        screen.blit(self.heart,(x,35))
  
  def draw(self, screen,tick):
    if self.gravity_mode==1:
      for smoke in self.smokes:
        smoke.draw(screen)
    super().draw(screen)
    self.draw_hearts(screen)
    if self.collision:
      td=tick-self.invincible_start_tick
      t_image=pygame.transform.scale_by(self.image,1+td*1.6/1000)
      t_image_rect=t_image.get_rect(center=self.rect.center)
      t_image.set_alpha(int(255-td*255/1000))
      screen.blit(t_image,t_image_rect)
    self.gun.draw(screen)
  
  def update(self, scr_w,scr_h,obstacle_group,chrome,tick):
    if self.gravity_mode==1:
      for i in range(3):
        self.smokes.add(Smoke(self.rect.centerx,self.rect.centery,f'smoke_{random.randint(0,2)}.png',tick))
      
      for smoke in self.smokes:
        smoke.rect.y+=random.randint(8,14)
        smoke.update(tick)
    key = pygame.key.get_pressed()
    if self.gravity_mode==0:
      self.duck(key)
      self.jump(key)
      self.apply_gravity()
    else:
      self.movement_y(key,0,scr_h)
    self.dash(key,tick)
    self.movement_x(key, 0, scr_w)
    if not self.invincible_mode:
      self.check_collisoin_obstacle(obstacle_group,chrome.meteorites,chrome.lasers,chrome.moving_bullets,chrome.left_hand,chrome.right_hand,tick)  
    self.check_invincible_end(tick)
    self.animation_name_update()
    self.animate()
    self.gun.update(self.rect.centerx,self.rect.centery,scr_w,scr_h,chrome,obstacle_group,tick)

  def reset(self):
    self.life=10
    self.x=self.start_x
    self.y=self.start_y
    self.run_rect.bottomleft=(self.x,self.y)
    self.duck_rect.bottomleft=(self.x,self.y)
    self.rect=self.run_rect
    self.gravity_mode=0
    self.jump_speed = 14
    self.is_jumping = True
    self.is_ducking = False
    self.is_dashing=False
    self.dash_counter=0
    self.last_dash_tick=0
    self.invincible_start_tick=0
    self.invincible=False
    self.collision=False
    self.invincible_time=0
    self.gun.reset()
    self.smokes.empty()