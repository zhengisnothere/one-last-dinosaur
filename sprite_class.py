import math

import pygame

from cache import image_dict


class Sprite(pygame.sprite.Sprite):
  def __init__(self, x, y,speed,image_name=None,copy_bool=False,rect_pos='bottomleft'):
    super().__init__()
    self.x,self.y=x,y
    self.rect_pos=rect_pos
    self.speed=speed
    self.load_image(image_name,copy_bool)
    self.create_rect(x,y)
    self.angle=0

  def load_image(self,image_name=None,copy_bool=False):
    if image_name:
      if copy_bool:
        self.image=image_dict[image_name].copy()
      else:
        self.image=image_dict[image_name]
    else:
      self.image=pygame.Surface((0,0))
    self.o_image=self.image.copy()

  def create_rect(self,x,y):
    self.rect=eval(f'self.image.get_rect({self.rect_pos}=(x,y))')
    self.mask=pygame.mask.from_surface(self.image)
  
  def draw(self,screen):
    screen.blit(self.image,self.rect)
    # pygame.draw.rect(screen,(0,0,0),(self.rect.x,self.rect.y,self.rect.width,self.rect.height),1)

  def x_move(self,x_dir,min_x=None,max_x=None):
    self.x+=x_dir
    if min_x is not None:
      self.x=max(min_x,self.x)
    if max_x is not None:
      self.x=min(max_x-self.rect.width,self.x)
    setattr(self.rect, self.rect_pos, (self.x, self.y))

  def y_move(self,y_dir,min_y=None,max_y=None):
    self.y-=y_dir
    if min_y is not None:
      self.y=max(self.rect.height,self.y)
    if max_y is not None:
      self.y=min(max_y,self.y)
    setattr(self.rect, self.rect_pos, (self.x, self.y))

  def calc_angle_toward_point(self,px,py):
    return math.degrees(math.atan2(self.y-py,px-self.x))%360
  
  def angle_toward_angle(self,angle):
    angle%=360
    self.image=pygame.transform.rotate(self.o_image,angle)
    self.create_rect(self.x,self.y)

  def angle_toward_point(self,px,py):
    angle=self.calc_angle_toward_point(px,py)
    self.angle_toward_angle(angle)

  def move_toward_point(self,px,py):
    dist=math.dist((px,py),(self.x,self.y))
    dx,dy=px-self.x,self.y-py
    ratio=0 if self.speed==0 else dist/self.speed
    mx=0 if ratio==0 else dx/ratio
    my=0 if ratio==0 else dy/ratio
    self.x_move(mx)
    self.y_move(my)

  def move_toward_angle(self,angle):
    mx=math.cos(math.radians(angle))*self.speed
    my=math.sin(math.radians(angle))*self.speed
    self.x_move(mx)
    self.y_move(my)
    

class Animated_Sprite(Sprite):
  def __init__(self, x, y,speed, animation_name,animation_speed,image_prefix,copy_bool=False,rect_pos='bottomleft'):
    super().__init__(x,y,speed)
    self.rect_pos=rect_pos
    self.animations = {}
    self.animation_index = 0
    self.animation_speed = animation_speed
    self.load_one_animation(animation_name, image_prefix,copy_bool)
    self.animation_name=list(self.animations.keys())[0]
    self.image=self.animations[self.animation_name][self.animation_index]
    self.rect=eval(f'self.image.get_rect({self.rect_pos}=(x,y))')
    self.mask=pygame.mask.from_surface(self.image)

  def animate(self):
    self.animation_index += self.animation_speed
    if self.animation_index >= len(self.animations[self.animation_name]):
      self.animation_index = 0
    self.image = self.animations[self.animation_name][math.floor(self.animation_index)]

  def load_one_animation(self,animation_name,image_prefix,copy_bool=False):
    images={}
    for image_name,image in image_dict.items():
      if image_name.startswith(image_prefix):
        if copy_bool:
          images[image_name]=image.copy()
        else:
          images[image_name]=image
    self.animations[animation_name]=list(dict(sorted(images.items())).values())

  def change_animation(self,new_animation_name):
    if new_animation_name != self.animation_name:
      self.animation_index = 0
      self.animation_name = new_animation_name