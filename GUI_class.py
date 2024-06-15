import pygame

from cache import image_dict


class Text_Area:
  def __init__(self, x, y, text, text_color=(83,83,83), text_size=15, bg_color=(255,255,255),padding=5,border_width=0, bg_show=False):
    # to run faster, only only create text surface for one time
    # to apply bg_show, split text surface and bg surface
    self.create_text_surface(text,text_size,text_color)
    self.create_bg(bg_color,padding,border_width)
    self.text_rect=self.text_surface.get_rect(center=(x,y))
    self.bg_rect=self.bg.get_rect(center=(x,y))
    self.bg_show=bg_show

  def create_bg(self,bg_color,padding,border_width):
    # create background of text
    width,height=self.text_width,self.text_height
    self.bg_color=bg_color
    self.padding=padding
    self.border_width=border_width
    # background rect
    self.bg=pygame.Surface((width+padding*2,height+padding*2))
    self.bg.fill(bg_color)
    # draw border
    if border_width>0:
      pygame.draw.rect(self.bg,(83,83,83),(0,0,width+padding*2,height+padding*2),border_width)

  def create_text_surface(self,text,text_size,text_color):
    # create text surface
    self.text=text
    self.text_size=text_size
    self.text_color=text_color
    t_font=pygame.font.Font('font/monogram.ttf',text_size)
    self.text_surface=t_font.render(text,False,text_color)
    self.text_width,self.text_height=self.text_surface.get_size()

  def draw(self,screen):
    # if background is show, draw background
    if self.bg_show:
      screen.blit(self.bg,self.bg_rect)
    screen.blit(self.text_surface,self.text_rect)

class Text_Button(Text_Area):
  def __init__(self,x, y,command=None,text='button', text_color=(83,83,83), text_size=15, bg_color=(255,255,255),clickable=True):
    super().__init__(x, y, text, text_color,text_size,bg_color,5,1, bg_show=True)
    self.command=command
    self.create_image()
    self.rect=self.image.get_rect(center=(x,y))
    self.clickable=clickable
    self.last_tick_pressed=False
    self.pressed=False
    self.released=False

  def create_image(self):
    # create image, touched image and pressed image of button
    self.image=self.bg.copy()
    self.image.blit(self.text_surface,(self.padding,self.padding))
    self.touched_image=self.image.copy()
    self.touched_image.set_alpha(180)
    self.pressed_image=self.image.copy()

  def check_touched(self):
    # check if user touch the button
    return self.rect.collidepoint(pygame.mouse.get_pos())

  def check_pressed(self):
    # check if user press the button
    return self.check_touched() and pygame.mouse.get_pressed()[0] and self.clickable

  def check_released(self):
    # check if user release the button
    # if last tick pressed and this tick not pressed, then user release the button
    return self.check_touched() and self.last_tick_pressed and not self.pressed

  def draw(self,screen):
    if self.check_touched():
      if self.pressed:
        # if user press the button, draw pressed image
        screen.blit(self.pressed_image,self.rect)
      else:
        # if user touch the button, draw touched image
        screen.blit(self.touched_image,self.rect)
    else:
      # if not touch the button, draw normal image
      screen.blit(self.image,self.rect)

  def update(self,**arg):
    # last_tick_pressed to recode last tick pressed state
    self.last_tick_pressed=self.pressed
    self.pressed=self.check_pressed()
    self.released=self.check_released()
    if self.released and self.command:
        self.command(**arg)

class Image_Button:
  def __init__(self,x,y,image_name,command=None):
    self.x,self.y=x,y
    self.command=command
    self.load_image(image_name)
    self.rect=self.image.get_rect(center=(self.x,self.y))
    self.mask=pygame.mask.from_surface(self.image)
    self.touched=False
    self.pressed=False
    self.released=False
    self.last_tick_pressed=True

  def load_image(self,image_name):
    self.image=image_dict[image_name]
    self.touched_image=self.image.copy()
    self.touched_image.set_alpha(180)
    self.pressed_image=self.image.copy()

  def draw(self,screen):
    if self.touched:
      if self.pressed:
        screen.blit(self.pressed_image,self.rect)
      else:
        screen.blit(self.touched_image,self.rect)
    else:
      screen.blit(self.image,self.rect)

  def check_mouse_touched(self):
    mx,my=pygame.mouse.get_pos()
    if self.rect.collidepoint((mx,my)) and self.mask.get_at((mx-self.rect.x,my-self.rect.y)):
      self.touched=True
    else:
      self.touched=False

  def check_mouse_pressed(self):
    self.check_mouse_touched()
    self.last_tick_pressed=self.pressed
    if self.touched and pygame.mouse.get_pressed()[0]:
      self.pressed=True
    else:
      self.pressed=False

  def check_mouse_released(self):
    self.check_mouse_pressed()
    if self.touched and self.last_tick_pressed and not self.pressed:
      self.released=True
    else:
      self.released=False

  def update(self,**cmd_arg):
    self.check_mouse_released()
    if self.command and self.released:
        self.command(**cmd_arg)

class Checkbox(Text_Area):
  def __init__(self, x, y,init_value, text, text_color=(83,83,83), text_size=15, bg_color=(255, 255, 255)):
    super().__init__(x, y, text, text_color, text_size, bg_color, 5, 1, True)
    self.value=init_value
    self.create_checkbox()
    self.last_tick_clicked=False

  def create_checkbox(self):
    height=self.bg.get_height()
    self.checkbox=pygame.Surface((height,height))
    self.checkbox.fill((255,255,255))
    pygame.draw.rect(self.checkbox,(83,83,83),(0,0,height,height),1)
    self.checkbox_rect=self.checkbox.get_rect()
    self.checkbox_rect.topleft=self.bg_rect.topright
    self.check_mark=pygame.Surface((height,height),pygame.SRCALPHA,32)
    pygame.draw.lines(self.check_mark,(255,0,0),False,[(height*0.2,height*0.6),(height*0.4,height*0.8),(height*0.8,height*0.2)],2)

  def draw(self,screen):
    super().draw(screen)
    screen.blit(self.checkbox,self.checkbox_rect)
    if self.value:
      screen.blit(self.check_mark,self.checkbox_rect)

  def check_mouse_click(self):
    mx,my=pygame.mouse.get_pos()
    if self.checkbox_rect.collidepoint((mx,my)):
      if pygame.mouse.get_pressed()[0]:
        if not self.last_tick_clicked:
          self.value=not self.value
          self.last_tick_clicked=True
      else:
        self.last_tick_clicked=False