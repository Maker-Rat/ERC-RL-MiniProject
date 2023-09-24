import pygame
from math import sin,cos,tan,radians,degrees,pi,atan,sqrt
import numpy as np

# Define colours
WHITE=(255,255,255)
BLUE=(0,0,255)
BLACK=(0,0,0)


# General position object
class pos(object):
    def __init__(self,x,y):
        self.x=x
        self.y=y


# RaceCar Object
class Player(pygame.sprite.Sprite):
    def __init__(self,screen,TrackObj,position=pos(100, 300)):
        #init displays
        pygame.font.init()
        self.screen=screen
        self.track=TrackObj
        self.delta=0
        self.distances=[0,0,0,0,0]
        self.score=0
        self.length=60
        self.width=30
        self.l_r=sqrt( pow(self.width,2)+ pow(self.length,2) )/2
        
        #init dynamics
        self.maxSteeringAngle=pi/6
        self.forwardSpeed=0
        self.forward=0
        self.canMove=True
        self.prev_orientation = 0
        self.orientation=0

        self.cur_pose = 0
        self.prev_pose = 0 

        #init player Sprite
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('Race_Car_Custom/img/car.png').convert_alpha()
        self.image=pygame.transform.scale(img, (self.length,self.width)) 
        self.mask=pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.x,self.rect.y=position.x,position.y
        self.old_center=self.rect.center
        self.initial=self.image
        
        self.draw()

    def setOrientation(self, orient):
        self.image = pygame.transform.rotozoom(self.initial, degrees(orient)%360, 1)
        self.rect = self.image.get_rect(center=self.rect.center)

    def updateDynamics(self, action):
        self.prev_orientation = self.orientation
        self.prev_pose = self.cur_pose
        L=self.length
        if action == 0:
            self.delta = 0.03
            self.forward = 0.0

        elif action == 1:
            self.delta = 0.0
            self.forward = 5.0

        elif action == 2:
            self.delta = -0.03
            self.forward = 0.0

        # elif action == 3:
        #     self.delta = 0.0
        #     self.forward = 0.0
        
        x,y=self.rect.center
        delta=self.delta
        theta=self.orientation
        bita=atan( self.l_r*tan(delta)/L ) 

        x=x+self.forward*cos(theta+bita)
        y=y-self.forward*sin(theta+bita)
        theta = theta + delta

        if x == 400:
            self.cur_pose = pi/2
        else:
            self.cur_pose = atan((y-600)/(x-400)) % (2*pi)
                        
        self.rect.center=(x,y)
        self.orientation=theta
        self.setOrientation(self.orientation)

    def collision_check(self):
        return self.collide_with(self.track)
            
    def draw(self):
        self.screen.blit(self.image, self.rect)
        pygame.draw.rect(self.screen, (255, 0, 0),self.rect, 2)
        pygame.draw.circle(self.screen, (0, 0, 255), self.rect.center, 2)

    def drawDistances(self):
        font = pygame.font.Font('freesansbold.ttf', 20)
        y_pos=30
        for distance in self.distances:
            text = font.render( str(int(distance)) , True, WHITE, None)
            textRect = text.get_rect()
            textRect.center = (1150,y_pos)
            self.screen.blit(text, textRect)
            y_pos+=20    


    def collide_with(self,obj):
        x_offset = obj.rect.left - self.rect.left
        y_offset = obj.rect.top - self.rect.top 
        
        area=self.mask.overlap_area(obj.mask, (x_offset,y_offset) ) 
        if(area<1000):
            self.canMove=False
            return True
        else:
            return False
    
    def pixelOverlapsTrack(self,pixel):
        try:
            return  self.track.mask.get_at(pixel)==1
        except:
            return 0
                
    def getDistances(self):
        
        theta=self.orientation
        dtheta=pi/12
        
        distances=[]
        for i in [ -4, -1, 0, 1, 4]:
            dist = self.getDistanceOfAngle(theta+i*dtheta)
            distances.append(max([dist, 250]))

        self.distances=distances
            
    def getDistanceOfAngle(self,theta):

        x,y=self.rect.center
        
        c=y-tan(-theta)*x
        
        theta_check=((theta)%(2*pi))/pi 

        pointing=0
        if theta_check>1.5 or theta_check<0.5 :
            pointing=1
        else:
            pointing=-1
        
        step=1
        xn,yn=x,y
        normalised_pixel=(int(xn), int(yn))
        screen_height,screen_width=self.screen.get_height(),self.screen.get_width()
        
        check=self.pixelOverlapsTrack( (xn,yn) )
        while( check ):
            xn+=pointing*step 
            yn=xn*tan(-theta)+c
            
            outOfBounds=False
            
            if yn>screen_height or yn<0:
                #print("opa")
                #yn=int(screen_height)
                yn=799
                outOfBounds=True
            if xn>screen_width or xn<0:
                #print("opa2")
                #xn=int(screen_width)
                xn=1199
                outOfBounds=True

            normalised_pixel=(int(xn), int(yn))
            check=self.pixelOverlapsTrack( normalised_pixel )
        
        
        pygame.draw.line(self.screen, (255,0,0), (x,y),normalised_pixel, 2)
        pygame.draw.circle(self.screen, (0, 0, 255),normalised_pixel , 8)

        return sqrt( (x-xn)**2 + (y-yn)**2)
