import math
import random

import pygame

from cache import sound_dict
from obstacles_class import Fragment_Group, Laser, Meteorite, Moving_Bullet
from sprite_class import Animated_Sprite, Sprite

font=pygame.font.SysFont('monospace',20)

class Chrome:
  def __init__(self,scr_w,ground_y,scr_h):
    self.scr_w=scr_w
    self.ground_y=ground_y
    self.scr_h=scr_h
    self.head=Animated_Sprite(scr_w/2,80,0,'idle',0.5,'chrome_head_',rect_pos='center')
    self.left_hand=Chrome_Hand(scr_w/2-150,160,4,-135,scr_w,ground_y,scr_h,True)
    self.right_hand=Chrome_Hand(scr_w/2+150,160,4,-45,scr_w,ground_y,scr_h)
    self.meteorites=pygame.sprite.Group()
    self.lasers=pygame.sprite.Group()
    self.moving_bullets=pygame.sprite.Group()
    self.attack_hand=self.left_hand
    self.attack_type=-1
    self.last_attack_type=-1
    self.last_tick_atk_end=True
    self.attack_end=True
    self.atk_end_tick=2000
    self.atk_interval=2000
    self.counter=0
    self.await_start_tick=0
    self.await_time=0
    self.health=1000
    self.max_health=1000
    self.show_health=False
    self.stage=0

  def summon_meteorite_random_x(self,px,py):
    x=random.randint(0,self.scr_w)
    y=-50
    angle=math.degrees(math.atan2(y-py,px-x))
    self.meteorites.add(Meteorite(x,y,3,angle,self.ground_y,self.scr_h))
    self.await_time=500
    self.counter+=1
    if self.counter==7:
      self.attack_end=True

  def summon_meteorites_1(self):
    if self.counter%2==0:
      for i in range(5):
        angle=180+(i+1)*30
        meteorite=Meteorite(self.head.x,self.head.y,3,angle,self.ground_y,self.scr_h)
        self.meteorites.add(meteorite)
    else:
      for i in range(4):
        angle=195+(i+1)*30
        meteorite=Meteorite(self.head.x,self.head.y,3,angle,self.ground_y,self.scr_h)
        self.meteorites.add(meteorite)
    self.await_time=400
    self.counter+=1
    if self.counter==6:
      self.attack_end=True

  def summon_meteorites_2(self):
    self.counter+=1
    meteorite1=Meteorite(self.head.x,self.head.y,3,self.counter*12+210,self.ground_y,self.scr_h)
    meteorite2=Meteorite(self.head.x,self.head.y,3,-self.counter*12+330,self.ground_y,self.scr_h)
    self.meteorites.add(meteorite1)
    self.meteorites.add(meteorite2)
    self.await_time=200
    if self.counter==10:
      self.attack_end=True

  def summon_meteorites_3(self):
    if self.counter==0:
      for s in range(2):
        for i in range(4):
          meteorite=Meteorite(self.head.x,self.head.y,2,i*10+220+s*70,self.ground_y,self.scr_h)
          self.meteorites.add(meteorite)
      self.counter+=1
      self.await_time=600
    elif self.counter==1:
      for i in range(3):
        meteorite=Meteorite(self.head.x,self.head.y,3,i*10+260,self.ground_y,self.scr_h)
        self.meteorites.add(meteorite)
      self.attack_end=True

  def summon_meteorites_4(self):
    if (self.counter//6)%2==0:
      meteorite=Meteorite(self.head.x,self.head.y,2,self.counter%6*10+220,self.ground_y,self.scr_h)
      self.meteorites.add(meteorite)
    else:
      meteorite=Meteorite(self.head.x,self.head.y,2,-(self.counter%6)*10+320,self.ground_y,self.scr_h)
      self.meteorites.add(meteorite)
    if self.counter%6==5:
      self.await_time=500
    else:
      self.await_time=50
    if (self.counter+1)//6==4:
      self.attack_end=True
    self.counter+=1

  def fist_attack_1(self,px,py):
    if self.counter==0:
      self.attack_hand=random.choice([self.left_hand,self.right_hand])
      self.counter=1
    elif self.counter==1:
      self.attack_hand.fist_attack(px,py)
      if self.attack_hand.attack_stage==2:
        self.await_time=200
        self.counter=2
    elif self.counter==2:
      self.attack_hand.fist_attack(px,py)
      if not self.attack_hand.attacking:
        self.attack_end=True

  def fist_attack_2(self,px):
    if self.counter==0:
      self.left_hand.attacking=True
      self.right_hand.attacking=True
      self.counter=1
    if self.left_hand.attacking:
      self.left_hand.fist_attack(px-80,self.ground_y)
    if self.right_hand.attacking:
      self.right_hand.fist_attack(px+80,self.ground_y)
    if (not self.left_hand.attacking) and (not self.right_hand.attacking):
      self.attack_end=True

  def hand_attack_1(self):
    if self.counter==0:
      self.attack_hand=random.choice([self.left_hand,self.right_hand])
      self.counter=1
    elif self.counter==1:
      self.attack_hand.hand_attack()
      if not self.attack_hand.attacking:
        self.attack_end=True

  def hand_attack_2(self):
    self.left_hand.hand_attack()
    self.right_hand.hand_attack()
    if (not self.left_hand.attacking) and (not self.right_hand.attacking):
      self.attack_end=True

  def laser_1(self,px,py,tick):
    angle=math.degrees(math.atan2(self.head.y-py,px-self.head.x))
    self.lasers.add(Laser(self.head.x,self.head.y,600,30,angle,tick,400,400))
    self.counter+=1
    self.await_time=400
    if self.counter==4:
      self.attack_end=True

  def laser_2(self,tick):
    for i in range(self.scr_w//110+1):
      x=i*110
      self.lasers.add(Laser(x,-20,500,25,270,tick,600,300))
    self.attack_end=True

  def laser_3(self,tick):
    x=self.counter*30
    self.lasers.add(Laser(x,-20,500,30,270,tick,1,100))
    self.counter+=1
    self.await_time=100
    if self.counter==25:
      self.attack_end=True

  def laser_4(self,tick):
    y=self.ground_y-self.counter*60
    self.lasers.add(Laser(-20,y,800,20,0,tick,600,100))
    self.counter+=1
    self.await_time=1200
    if self.counter==4:
      self.attack_end=True

  def stage_zero_attack(self,px,py,tick):
    if self.attack_type==0:
      self.summon_meteorite_random_x(px,py)
    elif self.attack_type==1:
      self.summon_meteorites_1()
    elif self.attack_type==2:
      self.summon_meteorites_2()
    elif self.attack_type==3:
      self.summon_meteorites_3()
    elif self.attack_type==4:
      self.summon_meteorites_4()
    elif self.attack_type==5:
      self.fist_attack_1(px,py)
    elif self.attack_type==6:
      self.fist_attack_2(px)
    elif self.attack_type==7:
      self.hand_attack_1()
    elif self.attack_type==8:
      self.hand_attack_2()
    elif self.attack_type==9:
      self.laser_1(px,py,tick)
    elif self.attack_type==10:
      self.laser_2(tick)
    elif self.attack_type==11:
      self.laser_3(tick)
    elif self.attack_type==12:
      self.laser_4(tick)

  def sky_laser_1(self,px,py,tick):
    angle=math.degrees(math.atan2(self.head.y-py,px-self.head.x))
    if self.counter==0:
      self.lasers.add(Laser(self.head.x,self.head.y,600,20,angle,tick,800,200))
      self.await_time=800
    else:
      self.lasers.add(Laser(self.head.x,self.head.y,500,20,angle,tick,200,200))
      self.await_time=200
    self.counter+=1
    if self.counter==10:
      self.attack_end=True

  def sky_laser_2(self,tick):
    if self.counter%2==0:
      for i in range(4):
        laser=Laser(self.head.x,self.head.y,500,40,i*90,tick,500,200)
        self.lasers.add(laser)
    else:
      for i in range(4):
        laser=Laser(self.head.x,self.head.y,500,40,i*90+45,tick,500,200)
        self.lasers.add(laser)
    self.counter+=1
    self.await_time=500
    if self.counter==4:
      self.attack_end=True

  def sky_laser_3(self,px,py,tick):
    r_angle=self.counter*10
    x=math.cos(math.radians(r_angle))*800+px
    y=py-math.sin(math.radians(r_angle))*800
    laser=Laser(x,y,1600,15,r_angle+180,tick,600,100)
    self.lasers.add(laser)
    self.counter+=1
    self.await_time=100
    if self.counter==37:
      self.attack_end=True

  def sky_laser_4(self,tick):
    for i in range(6):
      dir = 1 if self.counter // 60 % 2 == 0 else -1
      angle=dir*self.counter*1+i*60
      laser_await = 1000 if self.counter == 0 else 1
      laser=Laser(self.head.x,self.head.y,500,10,angle,tick,laser_await,1)
      self.lasers.add(laser)
    if self.counter==0:
      self.await_time=1000
    else:
      self.await_time=0
    self.counter+=1
    if self.counter==180:
      self.attack_end=True

  def bullet_1(self):
    for i in range(4):
      angle=i*90+self.counter*20
      bullet=Moving_Bullet(self.head.x,self.head.y,4,angle,'line')
      self.moving_bullets.add(bullet)
    self.counter+=1
    self.await_time=150
    if self.counter==19:
      self.attack_end=True

  def bullet_2(self):
    for i in range(12):
      angle=i*30
      speed=4 if self.counter%2==0 else 6
      func=['line','sin','line','cos','line'][self.counter]
      bullet=Moving_Bullet(self.head.x,self.head.y,speed,angle,func,frequency=40,amplitude=50)
      self.moving_bullets.add(bullet)
    self.counter+=1
    self.await_time=500
    if self.counter==5:
      self.attack_end=True

  def bullet_3(self):
    for i in range(8):
      angle=i*45 if self.counter==0 else i*45+22.5
      x=self.head.x+math.cos(math.radians(angle))*500
      y=self.head.y-math.sin(math.radians(angle))*500
      bullet=Moving_Bullet(x,y,6,angle+180,'line')
      self.moving_bullets.add(bullet)
    self.counter+=1
    self.await_time=2000
    if self.counter==2:
      self.attack_end=True
      self.attack_type=-1
      self.await_time=2000

  def stage_one_attack(self,px,py,tick):
    if self.attack_type==0:
      self.sky_laser_1(px,py,tick)
    elif self.attack_type==1:
      self.sky_laser_2(tick)
    elif self.attack_type==2:
      self.sky_laser_3(px,py,tick)
    elif self.attack_type==3:
      self.sky_laser_4(tick)
    elif self.attack_type==4:
      self.bullet_1()
    elif self.attack_type==5:
      self.bullet_2()
    elif self.attack_type==6:
      self.bullet_3()
  
  def attack_update(self,px,py,tick):
    self.last_tick_atk_end=self.attack_end
    if self.attack_end and tick-self.atk_end_tick>=self.atk_interval:
      if self.stage!=1:
        self.attack_type=random.randint(0,12)
        while self.attack_type==self.last_attack_type:
          self.attack_type=random.randint(0,12)
      else:
        self.attack_type=random.randint(0,6)
        while self.attack_type==self.last_attack_type:
          self.attack_type=random.randint(0,6)
      self.last_attack_type=self.attack_type
      self.attack_end=False
      return
    if not self.attack_end and tick-self.await_start_tick>self.await_time:
      self.await_time=0
      if self.stage!=1:
        self.stage_zero_attack(px,py,tick)
      else:
        self.stage_one_attack(px,py,tick)
      if self.await_time!=0:
        self.await_start_tick=tick
    if self.attack_end and not self.last_tick_atk_end:
      self.atk_end_tick=tick
      self.counter=0

  def draw_health_bar(self,screen):
    pygame.draw.rect(screen,(255,255,255),(0,0,self.scr_w,30))
    health_bar_width=(self.scr_w-10)*self.health/self.max_health
    pygame.draw.rect(screen,(83,83,83),(5,5,health_bar_width,20))
    if self.show_health:
      text=str(self.health)+'/'+str(self.max_health)
      text_surface=font.render(text,True,(0,255,255))
      text_rect=text_surface.get_rect(center=(self.scr_w/2,15))
      screen.blit(text_surface,text_rect)
  
  def draw(self,screen,tick):
    for meteorite in self.meteorites:
      meteorite.draw(screen)
    for laser in self.lasers:
      laser.draw(screen,tick)
    for bullet in self.moving_bullets:
      bullet.draw(screen)
    self.head.draw(screen)
    if self.stage!=1:
      self.left_hand.draw(screen,tick)
      self.right_hand.draw(screen,tick)
    self.draw_health_bar(screen)

  def stage_update(self,player,tick):
    if self.max_health*0.1<self.health<=self.max_health*0.5 and self.stage==0:
      self.meteorites.empty()
      self.lasers.empty()
      self.attack_end=True
      self.counter=0
      self.await_time=2000
      self.attack_type=-1
      self.stage=1
      self.atk_interval=1500
      player.gravity_mode=1
      self.head.y=self.scr_h/2
      self.head.rect.centery=self.head.y
      self.left_hand.reset()
      self.right_hand.reset()
    elif self.health<=self.max_health*0.1 and self.stage==1:
      self.moving_bullets.empty()
      self.meteorites.empty()
      self.lasers.empty()
      self.attack_end=True
      self.await_time=2000
      self.counter=0
      self.attack_type=-1
      player.gravity_mode=0
      player.is_jumping=True
      player.set_invincible(1000,tick)
      self.atk_interval=400
      self.head.y=80
      self.head.rect.centery=self.head.y
      self.stage=2
  
  def update(self,player,tick):
    self.last_tick_stage=self.stage
    self.head.animate()
    if self.stage!=1:
      self.left_hand.update()
      self.right_hand.update()
    self.stage_update(player,tick)
    self.attack_update(player.rect.centerx,player.rect.centery,tick)
    for meteorite in self.meteorites:
      meteorite.update(tick)
    for laser in self.lasers:
      laser.update(tick)
    for bullet in self.moving_bullets:
      bullet.update()

  def reset(self):
    self.head.y=80
    self.head.rect.centery=self.head.y
    self.left_hand.reset()
    self.right_hand.reset()
    self.meteorites.empty()
    self.lasers.empty()
    self.moving_bullets.empty()
    self.attack_type=0
    self.last_tick_atk_end=True
    self.attack_end=True
    self.atk_end_tick=2000
    self.atk_interval=2000
    self.counter=0
    self.await_start_tick=0
    self.await_time=0
    self.health=self.max_health
    self.stage=0

class Chrome_Hand(Sprite):
  def __init__(self,x,y,speed,angle,scr_w,ground_y,scr_h,inverse=False):
    self.ox,self.oy=x,y
    self.scr_w=scr_w
    self.ground_y=ground_y
    self.scr_h=scr_h
    self.inverse=inverse
    self.inverse_num=-1 if inverse else 1
    super().__init__(x,y,speed,'chrome_hand.png',rect_pos='center')
    self.o_angle=angle
    self.angle_toward_angle(angle)
    self.attacking=False
    self.attack_stage=0
    self.fragment_groups=pygame.sprite.Group()

  def load_image(self, image_name=None, copy_bool=False):
    super().load_image(image_name, copy_bool)
    self.image=pygame.transform.scale_by(self.image,1.2)
    self.o_image=self.image.copy()
    if self.inverse:
      self.image=pygame.transform.flip(self.image,False,True)
      self.o_image=pygame.transform.flip(self.o_image,False,True)

  def draw(self,screen,tick):
    draw_y=self.rect.y*(math.sin(tick/400)/10+1) if not self.attacking else self.rect.y
    screen.blit(self.image,(self.rect.x,draw_y))
    for group in self.fragment_groups:
      group.draw(screen)

  def update(self):
    for group in self.fragment_groups:
      group.update()

  def reset(self):
    self.load_image('chrome_hand.png')
    self.x,self.y=self.ox,self.oy
    self.create_rect(self.x,self.y)
    self.angle_toward_angle(self.o_angle)
    self.attacking=False
    self.attack_stage=0
    self.fragment_groups.empty()

  def fist_attack(self,tx,ty):
    if self.attack_stage==0:
      self.load_image('chrome_fist.png')
      self.angle=self.calc_angle_toward_point(tx,ty)
      self.angle_toward_angle(self.angle)
      self.attack_stage=1
      self.attacking=True
    elif self.attack_stage==1:
      for i in range(5):
        self.move_toward_angle(self.angle)
        if self.y>self.ground_y:
          sound_dict['bang.wav'].play()
          self.attack_stage=2
          self.fragment_groups.add(Fragment_Group(self.x,self.ground_y+15,15,self.scr_h))
          break
    elif self.attack_stage==2:
      for i in range(5):
        self.move_toward_point(self.ox,self.oy)
        if math.dist((self.ox,self.oy),(self.x,self.y))<=self.speed:
          self.x,self.y=self.ox,self.oy
          self.rect.centerx,self.rect.centery=self.ox,self.oy
          self.attack_stage=3
          break
    elif self.attack_stage==3:
      self.attack_stage=0
      self.load_image('chrome_hand.png')
      self.angle_toward_angle(self.o_angle)
      self.angle=self.o_angle
      self.attacking=False

  def hand_attack(self):
    if self.attack_stage==0:
      if self.inverse_num==-1:
        self.angle=self.calc_angle_toward_point(0,self.ground_y)
      else:
        self.angle=self.calc_angle_toward_point(self.scr_w,self.ground_y)
      self.angle_toward_angle(self.angle)
      self.attack_stage=1
      self.attacking=True
    elif self.attack_stage==1:
      for i in range(5):
        self.move_toward_angle(self.angle)
        if self.y>self.ground_y-30:
          self.attack_stage=2
          break
    elif self.attack_stage==2:
      for i in range(6):
        self.x_move(-self.speed*self.inverse_num)
        self.angle_toward_angle(self.calc_angle_toward_point(self.ox,self.oy)+180)
        if (self.inverse_num==1 and self.x<0) or (self.inverse_num==-1 and self.x>self.scr_w):
          self.attack_stage=3
          break
      sound_dict['bang.wav'].play()
      self.fragment_groups.add(Fragment_Group(self.x,self.ground_y+15,3,self.scr_h))
    elif self.attack_stage==3:
      for i in range(5):
        self.move_toward_point(self.ox,self.oy)
        if math.dist((self.ox,self.oy),(self.x,self.y))<=self.speed:
          self.x,self.y=self.ox,self.oy
          self.rect.centerx,self.rect.centery=self.ox,self.oy
          self.attack_stage=4
          break
    elif self.attack_stage==4:
      self.angle_toward_angle(self.o_angle)
      self.angle=self.o_angle
      self.attack_stage=0
      self.attacking=False