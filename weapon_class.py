import pygame

from cache import sound_dict
from sprite_class import Sprite


class Gun(Sprite):
  def __init__(self,x,y):
    super().__init__(x,y,0,'gun.png',rect_pos='center')
    self.bullets=pygame.sprite.Group()
    self.cooldown=100
    self.last_fire_tick=0
    self.image=pygame.transform.scale_by(self.o_image,1.2)
    self.o_image=self.image.copy()
    self.create_rect(self.x,self.y)

  def draw(self,screen):
    for bullet in self.bullets:
      bullet.draw(screen)
    super().draw(screen)

  def fire(self,tick):
    if pygame.mouse.get_pressed()[0] and tick-self.last_fire_tick>=self.cooldown:
      self.last_fire_tick=tick
      self.bullets.add(Bullet(self.x,self.y,5,self.angle))
      sound_dict['shoot.wav'].play()
  
  def update(self,px,py,scr_w,scr_h,chrome,obstacles,tick):
    self.x,self.y=px,py
    self.rect.center=self.x,self.y
    mx,my=pygame.mouse.get_pos()
    self.angle_toward_point(mx,my)
    self.angle=self.calc_angle_toward_point(mx,my)
    self.fire(tick)
    for bullet in self.bullets:
      bullet.update(scr_w,scr_h,chrome,obstacles)

  def reset(self):
    self.last_fire_tick=0
    self.bullets.empty()

class Bullet(Sprite):
  def __init__(self,x,y,speed,angle):
    super().__init__(x,y,speed,'bullet.png',rect_pos='center')
    self.image=pygame.transform.scale_by(self.o_image,1.2)
    self.o_image=self.image.copy()
    self.create_rect(self.x,self.y)
    self.angle=angle
    self.angle_toward_angle(angle)

  def update(self,scr_w,scr_h,chrome,obstacles):
    for i in range(4):
      self.move_toward_angle(self.angle)
      if chrome.head.rect.colliderect(self.rect) and chrome.head.mask.overlap(self.mask,(self.rect.x-chrome.head.rect.x,self.rect.y-chrome.head.rect.y)):
        chrome.health-=1
        self.kill()
        return
      for obstacle in obstacles:
        if obstacle.rect.colliderect(self.rect) and obstacle.mask.overlap(self.mask,(self.rect.x-obstacle.rect.x,self.rect.x-obstacle.rect.x)):
          obstacle.health-=1
          self.kill()
          return
      if self.rect.left<0 or self.rect.right>scr_w or self.rect.y<0 or self.rect.y>scr_h:
        self.kill()
        return