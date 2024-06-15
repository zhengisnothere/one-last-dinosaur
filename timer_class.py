import pygame


class Timer:
  def __init__(self):
    self.tick=0
    self.last_end_tick=0

  def update(self):
    self.tick=pygame.time.get_ticks()-self.last_end_tick

  def reset(self):
    self.tick=0
    self.last_end_tick=pygame.time.get_ticks()