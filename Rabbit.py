#!/usr/bin/env python
import pygame
import sys
import math
import time
import button
import os

MNT_RECT=pygame.Rect(0,0,1200,700)
SCR_RECT=pygame.Rect(0,0,960,600)
STG_RECT=pygame.Rect(0,0,10000,600)

blocks=[]
walls=[]
enemies=[]
dangers=[]
beams=[]
HPs=[]
DHPs=[]

aqua0 = (153, 217, 234)
aqua1 = (121, 206, 227)
aqua2 = (102, 199, 223)

def button_from_text(text, color_n, color_a, color_o, font_size, rect, text_size):
    sysfont = pygame.font.SysFont(None, font_size)
    s = sysfont.render(text, True, (0,0,0))
    normal = pygame.Surface(rect.size)
    normal.fill(color_n)
    normal.blit(s, text_size)
    above = pygame.Surface(rect.size)
    above.fill(color_a)
    above.blit(s, text_size)
    onclick = pygame.Surface(rect.size)
    onclick.fill(color_o)
    onclick.blit(s, text_size)
    return button.Button(normal, above, onclick, rect)

class Vector():
    def __init__(self,sx,sy,gx,gy):
        self.sx=sx
        self.sy=sy
        self.gx=gx
        self.gy=gy
        self.len2=(gx-sx)*(gx-sx)+(gy-sy)*(gy-sy)
        self.len=math.sqrt(self.len2) 
        self.x=gx-sx
        self.y=gy-sy
        self.nx=self.x/self.len
        self.ny=self.y/self.len

class Player(pygame.sprite.Sprite):
    def __init__(self,x,y,r):
        pygame.sprite.Sprite.__init__(self)
        self.rect=(x,y,2*r,2*r)
        self.pos_x=x-r
        self.pos_y=y-r
        self.rad=r
        self.vy=0
        self.vx=0
        self.ax=0
        self.ay=1000
        self.HRZ=4000
        self.fric=8000
        self.MAX_SPEED=300
        self.MAX_SPEED_Y=4000
        self.JUMP=800
        self.t1=time.time()
        self.t2=time.time()
        self.width=2*r
        self.height=2*r
        self.image=pygame.Surface((self.width,self.height))
        self.image.set_colorkey(self.image.get_at((0,0)),pygame.RLEACCEL)
        pygame.draw.circle(self.image,(0,255,0),(r,r),r)
        self.move_r=False
        self.move_l=False
        self.move_u=False
        self.move_d=False
        self.istouch=False
        self.score=0
        self.HP=100
        self.clear=False
        self.jumping=False
        self.dangerHP=10
        self.jump_rate=-0.3
        
    def update(self):
        self.t2=time.time()
        elap=self.t2-self.t1
        self.t1=self.t2
        
        if self.move_l:
            self.vx-=elap*self.HRZ
        if self.move_r:
            self.vx+=elap*self.HRZ
        if self.move_d:
            self.vy+=elap*450
            
        self.vx+=elap*self.ax
        
        if self.istouch:
            if self.vx>0:
                self.vx-=elap*self.fric
                if self.vx<0:self.vx=0
            if self.vx<0:
                self.vx+=elap*self.fric
                if self.vx>0:self.vx=0
                
        else:
            self.vy+=elap*self.ay
        
        if self.vx>=self.MAX_SPEED:
            self.vx=self.MAX_SPEED
        if self.vx<=-self.MAX_SPEED:
            self.vx=-self.MAX_SPEED
        
        if self.vy>=self.MAX_SPEED_Y:
            self.vy=self.MAX_SPEED_Y
        if self.vy<=-self.MAX_SPEED_Y:
            self.vy=-self.MAX_SPEED_Y
        
        self.pos_x+=elap*self.vx
        self.pos_y+=elap*self.vy
        self.rect=pygame.Rect(self.pos_x-self.rad,self.pos_y-self.rad,self.width,self.height)
        
        self.istouch=False
        
        s=0
        for block in blocks:
            if block.colliderect(self.rect):
                #縺ｮ縺｣縺九ｋ蜃ｦ逅�
                if self.vy>=0 and block.left-self.rad<=self.pos_x<=block.right+self.rad and block.top-self.rad<=self.pos_y<=block.top:
                    self.pos_y=block.top-self.rad
                    self.uprect()
                    if block.left<=self.pos_x<=block.right:
                        if(self.vy<500):
                            self.vy=0
                            self.istouch=True
                        self.vy*=self.jump_rate
                        if(self.move_u or self.jumping):
                            self.vy=-self.JUMP
                    else:
                        self.vy*=self.jump_rate
                if self.vy<0 and block.left-self.rad<=self.pos_x<=block.right+self.rad and block.bottom<=self.pos_y<=block.bottom+self.rad:
                    self.pos_y=block.bottom+self.rad
                    self.uprect()
                    self.vy*=self.jump_rate
                if self.vx>0 and block.top-self.rad<=self.pos_y<=block.bottom+self.rad and block.left-self.rad<=self.pos_x<=block.left:
                    self.pos_x=block.left-self.rad
                    self.uprect()
                    self.vx*=self.jump_rate
                    if abs(self.vx)<500:
                        self.vx=0
                if self.vx<0 and block.top-self.rad<=self.pos_y<=block.bottom+self.rad and block.right<=self.pos_x<=block.right+self.rad:
                    self.pos_x=block.right+self.rad
                    self.uprect()
                    self.vx*=self.jump_rate
                    if abs(self.vx)<500:
                        self.vx=0
                if self.dangerHP!=10:
                    blocks.remove(block)
                    HPs.pop(s)
                    self.score+=50
            s+=1
        for block in walls:
            if block.colliderect(self.rect):
                #縺ｮ縺｣縺九ｋ蜃ｦ逅�
                if self.vy>=0 and block.left<=self.pos_x<=block.right and block.top-self.rad<=self.pos_y<=block.top:
                    self.pos_y=block.top-self.rad
                    self.uprect()
                    if block.left<=self.pos_x<=block.right:
                        if(self.vy<500):
                            self.vy=0
                            self.istouch=True
                        self.vy*=-0.3
                        if(self.move_u):
                            self.vy=-self.JUMP
                    else:
                        self.vy*=-0.3
                if self.vy<=0 and block.left<=self.pos_x<=block.right and block.bottom<=self.pos_y<=block.bottom+self.rad:
                    self.pos_y=block.bottom+self.rad
                    self.uprect()
                    self.vy*=-0.3
                if self.vx>=0 and block.top<=self.pos_y<=block.bottom and block.left-self.rad<=self.pos_x<=block.left:
                    self.pos_x=block.left-self.rad
                    self.uprect()
                    self.vx*=-0.3
                if self.vx<=0 and block.top<=self.pos_y<=block.bottom and block.right<=self.pos_x<=block.right+self.rad:
                    self.pos_x=block.right+self.rad
                    self.uprect()
                    self.vx*=-0.3
                    
        for enemy in enemies:
            V=Vector(self.pos_x,self.pos_y,enemy.pos_x,enemy.pos_y)
            if V.len<=self.rad+enemy.rad:
                self.pos_x=enemy.pos_x-V.nx*(self.rad+enemy.rad+1)
                self.pos_y=enemy.pos_y-V.ny*(self.rad+enemy.rad+1)
                self.vx*=-1
                self.vy*=-1
                self.istouch=True
                self.HP-=5
        VR=Vector(self.pos_x,self.pos_y,self.friend.pos_x,self.friend.pos_y)
        if VR.len<=self.rad+self.friend.rad:
            self.pos_x=self.friend.pos_x-VR.nx*(self.rad+self.friend.rad+1)
            self.pos_y=self.friend.pos_y-VR.ny*(self.rad+self.friend.rad+1)
            self.vx*=-1
            self.vy*=-1
            self.istouch=True
            self.clear=True
        if self.boss.alive:
            VR=Vector(self.pos_x,self.pos_y,self.boss.pos_x,self.boss.pos_y)
            if VR.len<=self.rad+self.boss.rad:
                self.pos_x=self.boss.pos_x-VR.nx*(self.rad+self.boss.rad+1)
                self.pos_y=self.boss.pos_y-VR.ny*(self.rad+self.boss.rad+1)
                self.vx*=-1
                self.vy*=-1
                self.istouch=True
                self.HP-=10
        for danger in dangers:
            if danger.colliderect(self.rect):
                self.HP-=self.dangerHP
                if self.vy>=0 and danger.left<=self.pos_x<=danger.right and danger.top-self.rad<=self.pos_y<=danger.top:
                    self.pos_y=danger.top-self.rad
                    self.uprect()
                    if danger.left<=self.pos_x<=danger.right:
                        if(self.vy<500):
                            self.vy=0
                            self.istouch=True
                        self.vy*=-0.3
                        if(self.move_u or self.jumping):
                            self.vy=-self.JUMP
                    else:
                        self.vy*=-0.3
                if self.vy<=0 and danger.left<=self.pos_x<=danger.right and danger.bottom<=self.pos_y<=danger.bottom+self.rad:
                    self.pos_y=danger.bottom+self.rad
                    self.uprect()
                    self.vy*=-0.3
                if self.vx>=0 and danger.top<=self.pos_y<=danger.bottom and danger.left-self.rad<=self.pos_x<=danger.left:
                    self.pos_x=danger.left-self.rad
                    self.uprect()
                    self.vx*=-0.3
                if self.vx<=0 and danger.top<=self.pos_y<=danger.bottom and danger.right<=self.pos_x<=danger.right+self.rad:
                    self.pos_x=danger.right+self.rad
                    self.uprect()
                    self.vx*=-0.3
        
    def uprect(self):
        self.rect=pygame.Rect(self.pos_x-self.rad,self.pos_y-self.rad,self.width,self.height)
    
    def shot(self,drc):
        beams.append(Beam(self,1,drc,self))
        
    def draw(self,screen):
        if self.pos_x<=480:
            screen.blit(self.image,(self.rect.left,self.rect.top))
        elif 480<self.pos_x<=STG_RECT.right-480:
            screen.blit(self.image,(480-self.rad,self.rect.top))
        else:
            screen.blit(self.image,(self.rect.left-(STG_RECT.right-SCR_RECT.right),self.rect.top))
        

class Beam(pygame.sprite.Sprite):
    def __init__(self,owner,mode,drc,player,power=5):
        #mode=1:player mode=2:enemy
        pygame.sprite.Sprite.__init__(self)
        self.right=owner.pos_x
        self.left=owner.pos_x
        self.start=owner.pos_x
        self.y=owner.pos_y
        self.speed=1000
        self.mode=mode
        self.owner=owner
        self.player=player
        self.active=True
        self.height=10
        self.t1=time.time()
        self.t2=time.time()
        self.dir=1
        self.length=60
        self.power=power
        if mode==1:
            self.dir=drc
            self.color=(0,255,255)
        if mode==2:
            self.color=(255,0,0)
            if self.player.pos_x<self.owner.pos_x:
                self.dir=-1
                self.speed*=-1
        
    def update(self):
        self.t2=time.time()
        elap=self.t2-self.t1
        self.t1=time.time()
        if self.mode==1:
            self.right+=self.speed*elap*self.dir
            if (self.dir==1 and self.right-self.start>self.length) or (self.dir==-1 and self.start-self.right>self.length):
                self.left=self.right-self.length
            s=0
            for block in blocks:
                if block.colliderect(self.left,self.y-self.height/2,self.length,self.height):
                    HPs[s]-=1
                    if HPs[s]==0:
                        blocks.remove(block)
                        HPs.pop(s)
                    self.active=False
                    self.player.score+=10
                    
                    break
                s+=1
            for enemy in enemies:
                if enemy.rect.colliderect(self.left,self.y-self.height/2,self.length,self.height):
                    enemies.remove(enemy)
                    self.active=False
                    self.player.score+=20
            if self.player.friend.rect.colliderect(self.left,self.y-self.height/2,self.length,self.height):
                self.active=False
                self.player.friend.HP-=self.power
            if self.player.boss.alive and self.player.boss.rect.colliderect(self.left,self.y-self.height/2,self.length,self.height):
                self.active=False
                self.player.boss.HP-=self.power
                self.player.score+=10
            for block in dangers:
                if block.colliderect(self.left,self.y-self.height/2,self.length,self.height):
                    DHPs[s]-=1
                    if DHPs[s]==0:
                        dangers.remove(block)
                        DHPs.pop(s)
                    self.active=False
                    self.player.score+=10
                    
                    break
        else:
            self.right+=self.speed*elap
            if (self.dir==1 and self.right-self.start>self.length) or (self.dir==-1 and self.start-self.right>self.length):
                self.left=self.right-self.length
            if self.player.rect.colliderect(self.left,self.y-self.height/2,self.length,self.height):
                self.active=False
                self.player.HP-=self.power
            if self.player.friend.rect.colliderect(self.left,self.y-self.height/2,self.length,self.height):
                self.active=False
                self.player.friend.HP-=self.power
            for block in blocks:
                if block.colliderect(self.left,self.y-self.height/2,self.length,self.height):
                    self.active=False
                    break
        
        if (self.left>=self.player.pos_x+1100 or self.right<=self.player.pos_x-1100) or not self.active:
            beams.remove(self)
            
    def draw(self,screen):
        if 0<=self.player.pos_x<=480:
            pygame.draw.line(screen,self.color,(self.left,self.y),(self.right,self.y),self.height)
        elif 480<self.player.pos_x<=STG_RECT.width-480:
            dif=self.player.pos_x+480-SCR_RECT.right
            pygame.draw.line(screen,self.color,(self.left-dif,self.y),(self.right-dif,self.y),self.height)
        else:
            dif=STG_RECT.right-SCR_RECT.right
            pygame.draw.line(screen,self.color,(self.left-dif,self.y),(self.right-dif,self.y),self.height)
        
def drawblocks(screen,player):
    for block in blocks:
        if 0<=player.pos_x<=480:
            pygame.draw.rect(screen,(220,220,220),block)
        elif 480<player.pos_x<=STG_RECT.right-480:
            
            dif=player.pos_x+480-SCR_RECT.right
            pygame.draw.rect(screen,(220,220,220),pygame.Rect(block.left-dif,block.top,block.width,block.height))
        else:
            dif=STG_RECT.right-SCR_RECT.right
            pygame.draw.rect(screen,(220,220,220),pygame.Rect(block.left-dif,block.top,block.width,block.height))
    for block in walls:
        if 0<=player.pos_x<=480:
            pygame.draw.rect(screen,(220,220,220),block)
        elif 480<player.pos_x<=STG_RECT.right-480:
            
            dif=player.pos_x+480-SCR_RECT.right
            pygame.draw.rect(screen,(220,220,220),pygame.Rect(block.left-dif,block.top,block.width,block.height))
        else:
            dif=STG_RECT.right-SCR_RECT.right
            pygame.draw.rect(screen,(220,220,220),pygame.Rect(block.left-dif,block.top,block.width,block.height))
            
    for danger in dangers:
        if 0<=player.pos_x<=480:
            pygame.draw.rect(screen,(250,0,0),danger)
        elif 480<player.pos_x<=STG_RECT.right-480:
            
            dif=player.pos_x+480-SCR_RECT.right
            pygame.draw.rect(screen,(250,0,0),pygame.Rect(danger.left-dif,danger.top,danger.width,danger.height))
        else:
            dif=STG_RECT.right-SCR_RECT.right
            pygame.draw.rect(screen,(250,0,0),pygame.Rect(danger.left-dif,danger.top,danger.width,danger.height))
            
class Enemy(pygame.sprite.Sprite):
    def __init__(self,mode,x,y,r,player,dif=0.7,power=10):
      #mode=0:random  mode=1:player mode=2:ritsu
      self.mode=mode
      self.pos_x=x
      if self.mode==1:
          self.pos_y=player.pos_y
      elif self.mode==0:
          self.pos_y=40
      else:
          self.pos_y=y
      self.height=2*r
      self.width=2*r
      self.rect=pygame.Rect(x-r,y-r,2*r,2*r)
      self.rad=r
      self.image=pygame.Surface((2*r,2*r))
      self.image.set_colorkey(self.image.get_at((0,0)),pygame.RLEACCEL)
      pygame.draw.circle(self.image,(255,255,0),(r,r),r)
      self.t1=time.time()
      self.t2=time.time()
      self.pshot=time.time()
      self.player=player
      self.up=False
      self.speed=500
      self.dif=dif
      self.power=power
      
    def update(self):
        self.t2=time.time()
        elap=self.t2-self.t1
        self.t1=time.time()
        if self.mode==1:
            self.pos_y+=(self.player.pos_y-self.pos_y)*elap*0.99999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999
            self.uprect()
            if(self.t2-self.pshot>=self.dif):
                self.pshot=time.time()
                self.shot()
        elif self.mode==0:
            if self.up:
                self.pos_y-=self.speed*elap
                if self.pos_y<80:
                    self.up=False
            else:
                self.pos_y+=self.speed*elap
                if self.pos_y>500:
                    self.up=True
            self.uprect()
            if(self.t2-self.pshot>=self.dif):
                self.pshot=time.time()
                self.shot()
        else:
            if(self.t2-self.pshot>=self.dif):
                self.pshot=time.time()
                self.shot()
                    
            
    def shot(self):
        beams.append(Beam(self,2,1,self.player,self.power))
        
    def uprect(self):
        self.rect=pygame.Rect(self.pos_x-self.rad,self.pos_y-self.rad,self.width,self.height)
      
    def draw(self,screen):
        if 0<=self.player.pos_x<=480:
            screen.blit(self.image,(self.rect.left,self.rect.top))
        elif 480<self.player.pos_x<=STG_RECT.right-480:
            dif=self.player.pos_x+480-SCR_RECT.right
            screen.blit(self.image,(self.rect.left-dif,self.rect.top))
        else:
            dif=STG_RECT.right-SCR_RECT.right
            screen.blit(self.image,(self.rect.left-dif,self.rect.top))
            
def drawenemies(screen):
    for enemy in enemies:
        enemy.update()
        enemy.draw(screen)
    
def drawbeams(screen):
    for beam in beams:
        beam.update()
        beam.draw(screen)
        
class Friend(pygame.sprite.Sprite):
    def __init__(self,player):
        self.pos_x=9920
        self.pos_y=350
        self.rad=40
        self.HP=80
        self.rect=pygame.Rect(self.pos_x-self.rad,self.pos_y-self.rad,2*self.rad,2*self.rad)
        self.image=pygame.Surface((2*self.rad,2*self.rad))
        pygame.draw.circle(self.image,(255,100,100),(self.rad,self.rad),self.rad)
        colorkey=self.image.get_at((0,0))
        self.image.set_colorkey(colorkey,pygame.RLEACCEL)
        self.player=player
        
        
    def draw(self,screen):
        if 0<=self.player.pos_x<=480:
            screen.blit(self.image,(self.rect.left,self.rect.top))
        elif 480<self.player.pos_x<=STG_RECT.right-480:
            dif=self.player.pos_x+480-SCR_RECT.right
            screen.blit(self.image,(self.rect.left-dif,self.rect.top))
        else:
            dif=STG_RECT.right-SCR_RECT.right
            screen.blit(self.image,(self.rect.left-dif,self.rect.top))
            
class Boss(pygame.sprite.Sprite):
    def __init__(self,player,dif):
        self.pos_x=9500
        self.pos_y=player.pos_y
        self.rad=150
        self.player=player
        self.image=pygame.surface.Surface((2*self.rad,2*self.rad))
        self.width=2*self.rad
        self.height=2*self.rad
        colorkey=self.image.get_at((0,0))
        self.image.set_colorkey(colorkey,pygame.RLEACCEL)
        pygame.draw.circle(self.image,(205,65,202),(self.rad,self.rad),self.rad)
        self.damage=5
        self.top=Enemy(2,self.pos_x+100,self.pos_y-130,10,player,dif,self.damage)
        self.middle=Enemy(2,self.pos_x,self.pos_y,10,player,dif,self.damage)
        self.bottom=Enemy(2,self.pos_x+100,self.pos_y+130,10,player,dif,self.damage)
        self.HP=400
        self.rect=pygame.Rect(self.pos_x-self.rad,self.pos_y-self.rad,2*self.rad,2*self.rad)
        self.t1=time.time()
        self.t2=time.time()
        self.alive=True
        
    def update(self):
        if self.alive:
            self.t2=time.time()
            elap=self.t2-self.t1
            self.t1=time.time()
            self.pos_y+=(self.player.pos_y-self.pos_y)*elap*0.99999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999
            self.uprect()
            self.top.update()
            self.middle.update()
            self.bottom.update()
            self.top.pos_y=self.pos_y-100
            self.middle.pos_y=self.pos_y
            self.bottom.pos_y=self.pos_y+100
            if self.HP<=0 and not self.player.clear:
                self.alive=False
        
    def draw(self,screen):
        if self.alive:
            pygame.draw.rect(self.image,(255,0,0),pygame.Rect(50,120,200,60))
            pygame.draw.rect(self.image,(0,255,255),(50,120,(max(0,self.HP/2)),60))
            if 0<=self.player.pos_x<=480:
                screen.blit(self.image,(self.rect.left,self.rect.top))
            elif 480<self.player.pos_x<=STG_RECT.right-480:
                dif=self.player.pos_x+480-SCR_RECT.right
                screen.blit(self.image,(self.rect.left-dif,self.rect.top))
            else:
                dif=STG_RECT.right-SCR_RECT.right
                screen.blit(self.image,(self.rect.left-dif,self.rect.top))
            
    def uprect(self):
        self.rect=pygame.Rect(self.pos_x-self.rad,self.pos_y-self.rad,self.width,self.height)
        
    def change_damage(self):
        self.top.power=2
        self.middle.power=2
        self.bottom.power=2
		
            
def main():
    pygame.init()
    monitor=pygame.display.set_mode(MNT_RECT.size)
    screen=pygame.Surface((960,600))
    pygame.display.set_caption("Rabbit")
    SceneName="TitleScene"
    
    screen.fill((255,255,255))
    player=Player(80,50,15)
    friend=Friend(player)
    player.friend=friend
    boss=Boss(player,0.4)
    player.boss=boss
    
    player.score=0
    player.HP=400
    sysfont=pygame.font.SysFont(None,50)
    score_title=sysfont.render("Score",True,(0,0,0))
    score=sysfont.render("0",True,(0,0,0))
    HP_title=sysfont.render("HP",True,(0,0,0))
    HP=sysfont.render("0",True,(0,0,0))
    fHP_title=sysfont.render("Friend's HP",True,(0,0,0))
    clearfont=pygame.font.SysFont(None,180)
    CLEAR=clearfont.render("GAME CLEAR!!!",True,(192,192,0))
    finalscore=0
    finalHitPoint=0
    finalfriendHP=0
    
    pos=960
    t1=time.time()
    t2=time.time()
    cleared=False
    
    Titlefont=pygame.font.Font(None,200)
    Title=Titlefont.render("Rabbit",True,(0,0,0))
    Titlefont=pygame.font.Font(None,60)
    Name=Titlefont.render("Made by Thistle",True,(20,20,20))
    startgame=button_from_text("Play Game!!",aqua0,aqua1,aqua2,80,pygame.Rect(300,400,640,100),(170,25))
    gotorules=button_from_text("Watch Rules!!", aqua0, aqua1, aqua2, 80, pygame.Rect(300, 550, 640, 100), (140, 25))
    
    quit_button = button_from_text("Quit Game", (255,0,0), (235,0,0), (215,0,0), 30, pygame.Rect(700,40,500,40), (10,10))
    titlefont = pygame.font.SysFont(None, 100)
    result_title = titlefont.render("Result", True, (0,0,0))
    scorefont = pygame.font.SysFont(None, 70)
    finalHP = scorefont.render("10", True, (0,0,0))
    clearbonus=scorefont.render("10",True,(0,0,0))
    lastscore=scorefont.render("10",True,(0,0,0))
    finalpoint = scorefont.render("10", True, (0,0,0))
    friendHP=scorefont.render("10",True,(0,0,0))
    
    base = os.path.dirname(os.path.abspath(__file__))
    name = os.path.normpath(os.path.join(base, 'text.txt'))
    with open(name) as f:
        list = [int(s.strip()) for s in f.readlines()]
    ranknames = ["1st", "2nd", "3rd", "4th", "5th", "6th",]
    scores=[]
    ranks=[]
    t1=time.time()
    t2=time.time()
    
    base = os.path.dirname(os.path.abspath(__file__))
    name = os.path.normpath(os.path.join(base, 'Rules.png'))
    Rule=pygame.image.load(name).convert()
    back_button = button_from_text("Back To Title", (255,0,0), (235,0,0), (215,0,0), 30, pygame.Rect(700,40,500,40), (10,10))
    show_rab=sysfont.render("Press 'rab' in title scene!!",True,(0,0,0))
    show_2x=sysfont.render("Press '2x' in title scene!!",True,(0,0,0))
    show_beam=sysfont.render("Press 'beam' in title scene!!",True,(0,0,0))
    Titlefont=pygame.font.Font(None,150)
    show_cong=Titlefont.render("Congratulations!!!!!!!!",True,(192,192,0))
    
    life=2
    
    while True:
        
        if SceneName=="TitleScene":
            monitor.fill((255,255,255))
            #text, color_n, color_a, color_o, font_size, rect, text_size
            startgame.update()
            gotorules.update()
            startgame.draw(monitor)
            gotorules.draw(monitor)
            monitor.blit(Title,(400,100))
            monitor.blit(Name,(640,250))
            key_pressed=pygame.key.get_pressed()
            if player.dangerHP!=30 and key_pressed[pygame.K_2] and key_pressed[pygame.K_x]:
                player.MAX_SPEED*=2
                player.jumping=False
            if player.dangerHP!=30 and player.MAX_SPEED==300 and key_pressed[pygame.K_r] and key_pressed[pygame.K_a] and key_pressed[pygame.K_b]:
                player.jumping=True
                boss.change_damage()
            if key_pressed[pygame.K_b] and key_pressed[pygame.K_e] and key_pressed[pygame.K_a] and key_pressed[pygame.K_m]:
                life=1
                player.dangerHP=30
                player.jumping=False
                player.MAX_SPEED=300
                player.HP=450
        
        elif SceneName=="RuleScene":
            monitor.blit(Rule,(0,0))
            back_button.update()
            back_button.draw(monitor)
        
        elif SceneName=="PlayScene":
            monitor.fill((157,217,234))
            screen.fill((255,255,255))
            
            t2=time.time()
            if t2-t1>3:
                player.HP-=1
                t1=time.time()
                
            sscore=str(player.score)
            sHP=str(player.HP)
            sfHP=str(friend.HP)
            if cleared:
                sscore=str(finalscore)
                sHP=str(finalHitPoint)
                sfHP=str(finalfriendHP)
            score=sysfont.render(sscore,True,(0,0,0))
            HP=sysfont.render(sHP,True,(0,0,0))
            friendHP=sysfont.render(sfHP,True,(0,0,0))
            monitor.blit(score_title,(1020,80))
            monitor.blit(score,(1070-len(sscore)*8,140))
            monitor.blit(HP_title,(1050,300))
            monitor.blit(HP,(1070-len(sHP)*9,360))
            monitor.blit(fHP_title,(990,450))
            monitor.blit(friendHP,(1070-len(sfHP)*9,510))
            
            pygame.draw.rect(monitor,(150,150,150),pygame.Rect(30,620,1000,60))
            if player.pos_x<=480:
                pygame.draw.rect(monitor,(255,255,255),pygame.Rect(30,620,96,60))
            elif 480<player.pos_x<=STG_RECT.right-480:
                pygame.draw.rect(monitor,(255,255,255),pygame.Rect((player.pos_x-480)/10+30,620,96,60))
                pygame.draw.rect(monitor,(0,255,100),pygame.Rect(30,620,(player.pos_x-480)/10,60))
            else:
                pygame.draw.rect(monitor,(255,255,255),pygame.Rect((STG_RECT.right-960)/10+30,620,96,60))
                pygame.draw.rect(monitor,(0,255,100),pygame.Rect(30,620,(STG_RECT.width-960)/10,60))
                #1200*750
            player.update()
            player.draw(screen)
        
            drawblocks(screen,player)
            drawenemies(screen)
            
            drawbeams(screen)
            
            friend.draw(screen)
            boss.update()
            if boss.alive:
                boss.draw(screen)
            
            monitor.blit(screen,(0,0))
            
            if player.clear:
                if not cleared:
                    cleared=True
                    t1=time.time()
                    finalscore=player.score
                    finalHitPoint=player.HP
                    finalfriendHP=friend.HP
                    
            elif player.HP<=0 or friend.HP<=0:
                if not cleared:
                    cleared=True
                    t1=time.time()
                    finalscore=player.score
                    finalHitPoint=player.HP
                    finalfriendHP=friend.HP
                    if finalHitPoint<0:
                        finalHitPoint=0
                    if finalfriendHP<0:
                        finalfriendHP=0
                    CLEAR=clearfont.render("GAME OVER!!!",True,(0,0,255))
                    
            if pos>=-1000 and cleared:
                t2=time.time()
                elap=t2-t1
                t1=time.time()
                monitor.blit(CLEAR,(pos,200))
                pos-=400*elap
            if pos<-1000 and cleared:
                #finalscore:int
                #finalHitPoint:int
                #lastscore:Surface    normal 
                #finalHP:Surface      HP bornus
                #clearbonus:Surface   1000 or 0
                #finalpoint:Surface   plus
                tr=finalscore+finalHitPoint
                #plus
                if finalHitPoint<=0 or finalfriendHP<=0:
                    list.append(tr)
                    clearbonus=scorefont.render("Clear Bonus : 0",True,(0,0,0))
                else:
                    list.append(tr+1000)
                    tr+=1000
                    clearbonus=scorefont.render("Clear Bonus : 1000",True,(0,0,0))
                lastscore=scorefont.render("Score : "+str(finalscore),True,(0,0,0))
                finalHP=scorefont.render("HP : "+str(finalHitPoint),True,(0,0,0))
                finalpoint=scorefont.render("Point : "+str(tr),True,(0,0,0))
                list.sort()
                list.reverse()
                stlist = []
                for i in range(6):
                    stlist.append(str(list[i]))
                    
                base = os.path.dirname(os.path.abspath(__file__))
                name = os.path.normpath(os.path.join(base, 'text.txt'))
                with open(name, mode="w") as f:
                    f.write('\n'.join(stlist))
                scores = [scorefont.render((str(list[i]) if list[i]!=-1 else "None"), True, (0,0,0)) for i in range(6)]
                ranks = [scorefont.render(ranknames[i], True, (0,0,0)) for i in range(6)]
                SceneName = "ResultScene"
                
        elif SceneName=="ResultScene":
            monitor.fill((255,255,255))
            quit_button.update()
            quit_button.draw(monitor)
            monitor.blit(result_title, (100, 45))
            monitor.blit(lastscore, (160, 150))
            monitor.blit(finalHP, (160, 200))
            monitor.blit(clearbonus, (160, 250))
            monitor.blit(finalpoint,(160,300))
            
            for i in range(3):
                monitor.blit(ranks[i], (140, 380+i*70))
                monitor.blit(scores[i], (240, 380+i*70))
            for i in range(3):
                monitor.blit(ranks[i+3], (590, 380+i*70))
                monitor.blit(scores[i+3], (690, 380+i*70))
            if player.clear:
                monitor.blit(show_rab,(700,150))
                if player.jumping:
                    monitor.blit(show_2x,(700,200))
                if player.MAX_SPEED!=300:
                    monitor.blit(show_2x,(700,200))
                    monitor.blit(show_beam,(700,250))
                if player.dangerHP==30:
                    monitor.blit(show_beam,(700,250))
                    monitor.blit(show_2x,(700,200))
                    monitor.blit(show_cong,(100,300))

    
        pygame.display.update()
        
            
        for event in pygame.event.get():
            if SceneName=="TitleScene":
                if event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
                    x,y=event.pos
                    if startgame.contains(x,y):
                        SceneName="PlayScene"
                        player.t1=time.time()
                        t1=time.time()
                        dangers.append(pygame.Rect(0,570,10000,30))
                        walls.append(pygame.Rect(0,0,10000,30))
                        walls.append(pygame.Rect(0,0,30,600))
                        walls.append(pygame.Rect(9970,0,30,600))
                        
                        blocks.append(pygame.Rect(0,400,300,30))
                        blocks.append(pygame.Rect(100,250,300,30))
                        blocks.append(pygame.Rect(300,100,300,30))
                        blocks.append(pygame.Rect(500,450,300,30))
                        blocks.append(pygame.Rect(625,350,300,30))
                        blocks.append(pygame.Rect(675,150,200,30))
                        dangers.append(pygame.Rect(900,250,100,60))
                        blocks.append(pygame.Rect(1000,120,200,30))
                        blocks.append(pygame.Rect(1000,400,200,30))
                        blocks.append(pygame.Rect(1100,300,150,30))
                        blocks.append(pygame.Rect(1250,80,200,30))
                        blocks.append(pygame.Rect(1250,500,150,30))
                        blocks.append(pygame.Rect(1450,380,300,30))
                        blocks.append(pygame.Rect(1700,200,100,60))
                        blocks.append(pygame.Rect(1815,100,100,60))
                        blocks.append(pygame.Rect(1875,300,100,60))
                        blocks.append(pygame.Rect(1940,200,100,60))
                        blocks.append(pygame.Rect(1940,450,100,60))
                        blocks.append(pygame.Rect(2100,300,100,60))
                        blocks.append(pygame.Rect(2100,500,100,60))
                        blocks.append(pygame.Rect(2200,200,100,60))
                        blocks.append(pygame.Rect(2200,550,100,60))
                        blocks.append(pygame.Rect(2250,300,100,60))
                        blocks.append(pygame.Rect(2300,100,100,60))
                        blocks.append(pygame.Rect(2430,300,100,60))
                        blocks.append(pygame.Rect(2450,500,100,60))
                        blocks.append(pygame.Rect(2500,250,100,60))
                        blocks.append(pygame.Rect(2600,400,300,60))
                        blocks.append(pygame.Rect(2600,80,100,60))
                        blocks.append(pygame.Rect(2700,200,100,60))
                        blocks.append(pygame.Rect(2800,320,100,60))
                        blocks.append(pygame.Rect(2900,300,650,30))
                        blocks.append(pygame.Rect(3650,270,300,500))
                        blocks.append(pygame.Rect(4100,270,300,500))
                        blocks.append(pygame.Rect(4550,270,300,500))
                        blocks.append(pygame.Rect(5000,270,300,500))
                        blocks.append(pygame.Rect(5450,270,300,500))
                        blocks.append(pygame.Rect(5800,150,300,30))
                        blocks.append(pygame.Rect(5700,400,400,30))
                        blocks.append(pygame.Rect(5900,180,30,220))
                        dangers.append(pygame.Rect(6000,50,60,60))
                        blocks.append(pygame.Rect(6300,150,600,30))
                        blocks.append(pygame.Rect(6300,300,600,30))
                        blocks.append(pygame.Rect(6300,450,600,30))
                        blocks.append(pygame.Rect(7000,150,600,30))
                        blocks.append(pygame.Rect(7000,300,600,30))
                        blocks.append(pygame.Rect(7000,450,600,30))
                        blocks.append(pygame.Rect(7600,350,300,30))
                        blocks.append(pygame.Rect(7800,250,300,30))
                        dangers.append(pygame.Rect(8100,50,100,100))
                        blocks.append(pygame.Rect(8000,350,300,30))
                        blocks.append(pygame.Rect(8400,350,300,30))
                        blocks.append(pygame.Rect(8400,150,300,30))
                        blocks.append(pygame.Rect(8600,250,300,30))
                        blocks.append(pygame.Rect(8850,350,300,30))
                        blocks.append(pygame.Rect(8850,150,300,30))
                        blocks.append(pygame.Rect(9300,540,870,30))
                        for i in range(300):
                            HPs.append(life)
                        for i in range(300):
                            DHPs.append(life)
                            
                        ##mode=0:random  mode=1:player mode=2:ritsu
                        damage=30
                        enemies.append(Enemy(1,2400,0,damage,player))
                        enemies.append(Enemy(0,3600,0,damage,player))
                        enemies.append(Enemy(0,4050,0,damage,player))
                        enemies.append(Enemy(0,4500,100,damage,player))
                        enemies.append(Enemy(1,4950,190,damage,player))
                        enemies.append(Enemy(1,5400,270,damage,player))
                        enemies.append(Enemy(1,6100,0,damage,player))
                        enemies.append(Enemy(2,6800,120,damage,player))
                        enemies.append(Enemy(2,6800,270,damage,player))
                        enemies.append(Enemy(2,6800,420,damage,player)) 
                        enemies.append(Enemy(2,7500,120,damage,player))
                        enemies.append(Enemy(2,7500,270,damage,player))
                        enemies.append(Enemy(2,7500,420,damage,player))
                        
                    if gotorules.contains(x,y):
                        SceneName="RuleScene"
            if SceneName=="RuleScene":
                if event.type==pygame.MOUSEBUTTONDOWN:
                    x,y=event.pos
                    if back_button.contains(x,y):
                        SceneName="TitleScene"
            if SceneName=="PlayScene":
                if event.type==pygame.KEYDOWN:
                    if event.key==pygame.K_RIGHT:
                        player.move_r=True
                    if event.key==pygame.K_LEFT:
                        player.move_l=True
                    if event.key==pygame.K_UP:
                        player.move_u=True
                    if event.key==pygame.K_DOWN:
                        player.move_d=True
                    if event.key==pygame.K_a:
                        player.shot(-1)
                    if event.key==pygame.K_d:
                        player.shot(1)
                        
                if event.type==pygame.KEYUP:
                    if event.key==pygame.K_RIGHT:
                        player.move_r=False
                    if event.key==pygame.K_LEFT:
                        player.move_l=False
                    if event.key==pygame.K_UP:
                        player.move_u=False
                    if event.key==pygame.K_DOWN:
                        player.move_d=False
            if SceneName=="ResultScene":
                if event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
                    x,y=event.pos
                    if quit_button.contains(x,y):
                        pygame.quit()
                        sys.exit()
            
            if event.type==pygame.KEYDOWN:
                if event.key==pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
            if event.type==pygame.QUIT:
                pygame.quit()
                sys.exit()
                        
if __name__=="__main__":
    main()

