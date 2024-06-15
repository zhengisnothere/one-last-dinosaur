import math
import random

import pygame

from cache import sound_dict
from sprite_class import Animated_Sprite, Sprite

font=pygame.font.SysFont('monospace',15)

class Obstacle_Spawner:
  def __init__(self, spawn_x,spawn_y,speed):
    self.spawn_x=spawn_x
    self.spawn_y=spawn_y
    self.speed=speed
    self.group=pygame.sprite.Group()
    self.spawn_interval=1800
    self.last_spawn_tick=0
    self.show_health=False

  def reset(self):
    self.group.empty()
    self.last_spawn_tick=0
  
  def spawn(self,tick):
    if tick-self.last_spawn_tick>=self.spawn_interval:
      self.spawn_interval=1800+random.randint(-400,0)
      self.last_spawn_tick=tick
      type=random.choice(['cactus','cactus','cactus','bird','bird'])
      if type=='cactus':
        ri=random.randint(0,5)
        obstacle=Cactus(self.spawn_x,self.spawn_y,self.speed,'cactus_'+str(ri)+'.png')
        self.group.add(obstacle)
      elif type=='bird':
        y_offset=random.randint(0,80)
        obstacle=Bird(self.spawn_x,self.spawn_y-y_offset,self.speed)
        self.group.add(obstacle)

  def draw(self,screen):
    for obstacle in self.group:
      obstacle.draw(screen)
      if self.show_health:
        text=font.render(str(obstacle.health),True,(0,0,0))
        text_rect=text.get_rect(center=(obstacle.rect.centerx,obstacle.rect.centery-30))
        screen.blit(text,text_rect)

  def update(self,meteorite_group,left_hand,right_hand,tick):
    self.spawn(tick)
    for obstacle in self.group:
      collide_meteorite=any(not meteorite.exploded and obstacle.rect.colliderect(meteorite.rect) and obstacle.mask.overlap(meteorite.mask,(meteorite.rect.x-obstacle.rect.x,meteorite.rect.y-obstacle.rect.y)) for meteorite in meteorite_group)
      collide_left_hand=obstacle.rect.colliderect(left_hand.rect)  and obstacle.mask.overlap(left_hand.mask,(left_hand.rect.x-obstacle.rect.x,left_hand.rect.y-obstacle.rect.y))
      collide_right_hand=obstacle.rect.colliderect(right_hand.rect) and obstacle.mask.overlap(right_hand.mask,(right_hand.rect.x-obstacle.rect.x,right_hand.rect.y-obstacle.rect.y))
      if collide_meteorite or collide_left_hand or collide_right_hand:
        obstacle.kill()
      obstacle.update()
      

class Cactus(Sprite):
  def __init__(self,x,y,speed,image_name):
    super().__init__(x,y,speed,image_name)
    self.health=5

  def update(self):
    self.x_move(-self.speed)
    if self.x<-self.rect.width or self.health<=0:
      self.kill()
  
class Bird(Animated_Sprite):
  def __init__(self,x,y,speed):
    super().__init__(x,y,speed,animation_name='fly',animation_speed=0.1,image_prefix='bird_')
    self.health=5
    self.mask_1=pygame.mask.from_surface(self.animations['fly'][0])
    self.mask_2=pygame.mask.from_surface(self.animations['fly'][1])
    self.mask=self.mask_1

  def update(self):
    self.x_move(-self.speed)
    self.animate()
    self.mask=self.mask_1 if math.floor(self.animation_index)==0 else self.mask_2
    if self.x<-self.rect.width or self.health<=0:
      self.kill()

class Meteorite(Sprite):
  def __init__(self, x, y,speed,angle,ground_y,scr_h):
    self.ground_y=ground_y
    self.scr_h=scr_h
    super().__init__(x,y,speed,'meteorite.png',rect_pos='center')
    self.angle=angle
    self.exploded=False
    self.smoke_group=pygame.sprite.Group()

  def generate_smoke(self,tick):
    ri=random.randint(0,2)
    image_name=f'smoke_{ri}.png'
    self.smoke_group.add(Smoke(self.x,self.y,image_name,tick))
  
  def generate_fragments(self):
    self.fragment_group=Fragment_Group(self.x,self.y,10,self.scr_h)
      

  def draw(self,screen):
    if not self.exploded:
      super().draw(screen)
      for smoke in self.smoke_group:
        smoke.draw(screen)
    else:
      self.fragment_group.draw(screen)

  def move_meteorite(self,tick):
    for i in range(5):
      self.move_toward_angle(self.angle)
      self.generate_smoke(tick)
      if self.rect.centery>=self.ground_y:
        self.exploded=True
        self.generate_fragments()
        sound_dict['bang.wav'].play()
        return
  
  def update(self,tick):
    if not self.exploded:
      self.move_meteorite(tick)
      for smoke in self.smoke_group:
        smoke.update(tick)
    else:
      if len(self.fragment_group.group)>0:
        self.fragment_group.update()
      else:
        self.kill()

class Fragment(Sprite):
  def __init__(self,x,y,speed,image_name,x_dir,jump_speed,scr_h):
    super().__init__(x,y,speed,image_name,rect_pos='center')
    self.x_dir=x_dir
    self.jump_speed=jump_speed
    self.gravity=1.4
    self.scr_h=scr_h

  def apply_gravity(self):
    self.y-=self.jump_speed
    self.jump_speed-=self.gravity
    self.rect.centery=self.y

  def update(self):
    self.x_move(self.x_dir*self.speed)
    self.apply_gravity()
    if self.rect.top>self.scr_h:
      self.kill()

class Fragment_Group(pygame.sprite.Sprite):
  def __init__(self,x,y,num,scr_h):
    super().__init__()
    self.group=pygame.sprite.Group()
    for i in range(num):
      speed=random.randint(1,6)
      ri=random.randint(0,5)
      image_name='fragment_'+str(ri)+'.png'
      x_dir=random.choice([-1,1])
      jump_speed=random.randint(6,12)
      fragment=Fragment(x,y,speed,image_name,x_dir,jump_speed,scr_h)
      self.group.add(fragment)

  def update(self):
    for fragment in self.group:
      fragment.update()
    if len(self.group)==0:
      self.kill()

  def draw(self,screen):
    for fragment in self.group:
      fragment.draw(screen)

class Smoke(Sprite):
  def __init__(self,x,y,image_name,tick):
    super().__init__(x,y,0,image_name,rect_pos='center',copy_bool=True)
    self.generate_tick=tick
    self.max_tick=150
    if random.randint(0,1):
      self.image=pygame.transform.flip(self.image,True,False)
    if random.randint(0,1):
      self.image=pygame.transform.flip(self.image,False,True)

  def update(self,tick):
    self.image.set_alpha(255-255/self.max_tick*(tick-self.generate_tick))
    if tick-self.generate_tick>=self.max_tick:
      self.kill()

class Laser(Sprite):
  def __init__(self,x,y,width,height,angle,tick,await_time,last_time):
    self.width=width
    self.height=5
    self.max_height=height
    super().__init__(x,y,0,rect_pos='center')
    self.create_image(width,height)
    self.rotate_around_midleft(angle)
    self.create_tick=tick
    self.resizing=False
    self.await_time=await_time
    self.last_time=last_time
    self.attack_tick=0
    self.attacking=False

  def create_image(self,width,height):
    self.image=pygame.Surface((width,height),pygame.SRCALPHA,32)
    self.image.fill((200,200,200))
    pygame.draw.rect(self.image,(83,83,83),(2,2,width-4,height-4))
    self.o_image=self.image.copy()

  def create_rect(self, x, y):
    super().create_rect(x+self.width/2,y)
    self.ocx=x+self.width/2
    self.ocy=y

  def rotate_around_midleft(self,angle):
    self.angle=angle
    self.image=pygame.transform.rotate(self.o_image,angle)
    r_mr_x=-self.width/2*math.cos(math.radians(angle))
    r_mr_y=-self.width/2*math.sin(math.radians(angle))
    self.rect=self.image.get_rect(center=(self.ocx,self.ocy))
    self.rect.centerx-=r_mr_x+self.width/2
    self.rect.centery+=r_mr_y
    self.mask=pygame.mask.from_surface(self.image)

  def draw(self,screen,tick):
    if not self.resizing and not self.attacking:
      ex=self.x+math.cos(math.radians(self.angle))*self.width
      ey=self.y-math.sin(math.radians(self.angle))*self.width
      bri=255-255/self.await_time*(tick-self.create_tick)
      pygame.draw.line(screen,(bri,bri,bri),(self.x,self.y),(ex,ey),1)
    else:
      super().draw(screen)

  def update(self,tick):
    if tick-self.create_tick>self.await_time and not self.resizing and not self.attacking:
      self.resizing=True
      sound_dict['laser.wav'].play()
    if self.resizing and self.height<self.max_height:
      self.height+=5
      self.create_image(self.width,self.height)
      self.rotate_around_midleft(self.angle)
    if self.resizing and self.height>=self.max_height:
      self.resizing=False
      self.attacking=True
      self.attack_tick=tick
    if self.attacking and tick-self.attack_tick>self.last_time:
      self.height-=5
      self.create_image(self.width,self.height)
      self.rotate_around_midleft(self.angle)
      if self.height<5:
        self.kill()
        return

class Moving_Bullet(Sprite):
  def __init__(self,x,y,speed,angle,function,**func_arg):
    super().__init__(x,y,speed,'moving_bullet.png',rect_pos='center')
    self.ox=x
    self.oy=y
    self.angle=angle
    self.func=function
    self.func_arg=func_arg
    self.distance=0

  def move(self,func,**func_arg):
    self.distance+=self.speed
    x=self.distance
    y=0
    if func=='sin':
      frequency=func_arg['frequency']
      amplitude=func_arg['amplitude']
      y=math.sin(self.distance/frequency)*amplitude
    elif func=='cos':
      frequency=func_arg['frequency']
      amplitude=func_arg['amplitude']
      y=math.cos(self.distance/frequency)*amplitude
    dir=math.radians(self.angle)
    self.x=x*math.cos(dir)-y*math.sin(dir)+self.ox
    self.y=-x*math.sin(dir)-y*math.cos(dir)+self.oy
    self.rect.center=self.x,self.y

  def update(self):
    self.move(self.func,**self.func_arg)
    if self.distance>=self.speed*200:
      self.kill()