import os

import pygame


def cache_all_images(path,scale):
  for file in os.listdir(path):
    if file.endswith('.png'):
      image=pygame.image.load(os.path.join(path,file))
      image=pygame.transform.scale_by(image,scale)
      image_dict[file]=image
    else:
      cache_all_images(os.path.join(path,file),scale)

def cache_all_sounds(path):
  for file in os.listdir(path):
    if file.endswith('.mp3') or file.endswith('.wav'):
      sound=pygame.mixer.Sound(os.path.join(path,file))
      sound_dict[file]=sound

pygame.init()
image_dict={}
cache_all_images('assets',2)
sound_dict={}
cache_all_sounds('sound effects')