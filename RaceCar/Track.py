import pygame

class race_track(pygame.sprite.Sprite):
    def __init__(self, screen, lenWidth, track = "track_1"):
        pygame.sprite.Sprite.__init__(self)
        self.length,self.width=lenWidth
        img = pygame.image.load(f'Race_Car_Custom/img/{track}.png')
        self.image=pygame.transform.scale(img, (self.length,self.width)).convert_alpha() 
        self.rect = self.image.get_rect()
        self.rect.x,self.rect.y=0,0
        self.screen=screen

        self.streetColor=(163, 171, 160,255)
        self.mask=pygame.mask.from_threshold(self.image,self.streetColor,(10, 10, 10, 255)) 
        

    def draw(self):
        self.screen.blit(self.image, self.rect)