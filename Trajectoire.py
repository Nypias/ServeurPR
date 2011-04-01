# -*- coding: utf-8 -*-
import time
import random, math

import json

from twisted.internet import reactor
""" Méthode de calcul de trajectoire, doit implémenter une méthode pour
transformer la trajectoire en string JSON """


class Trajectoire :
    
    TAILLE_RAQ = 100
    TIME_INT = 0.05
    

    def __init__(self, joueurs):

        self.joueurs = joueurs
        time = 0
        angle = random.random()*360
        self.ball = [50, 50]
        self.ball[0] = self.ball[0] + math.cos(math.radians(angle))
        self.ball[1] = self.ball[1] - math.sin(math.radians(angle)) # "-" car l'axe des Y est vers le bas
        while(self.ball[0] > 0 and self.ball[0] < 100 and self.ball[1] > 0 and self.ball[1] < 100):
            self.ball[0] = self.ball[0] + math.cos(math.radians(angle))
            self.ball[1] = self.ball[1] - math.sin(math.radians(angle))
            #print self.ball[0], self.ball[1]
            time += Trajectoire.TIME_INT # "-" car l'axe des Y est vers le bas
        self.ball[0] = self.ball[0]
        self.ball[1] = self.ball[1]

        pointCollision = (self.ball[0], self.ball[1])
        
        print "COLLISION dans " + str(time) + " avec positionCollision = " + str(pointCollision)
        
        self.sendPoint(pointCollision,time)
        reactor.callLater(time, self.choisirTrajectoire, pointCollision, angle)
        
        
    def sendPoint(self, point,temps):
        
        for client in self.joueurs:
            message = { "msg" : "Trajectoire", "point" : point, "collisionTime" : client.getHourClient() + temps}
            client.transport.write(json.dumps(message))

    def choisirTrajectoire(self, pointDepart, angle):
        # TODO : faire une fonction "trouver joueur en fonction de l'axe d'arret  de la balle"
        axeJoueur = False
        rebondSurRaquette = False
        if self.ball[0] <= 0: 
            try:
                joueur = self.joueurs[0]
            except:
                pass
            else:
                axeJoueur = True
                
        elif self.ball[0] >= 100:
            try:
                joueur = self.joueurs[1]
            except:
                pass
            else:
                axeJoueur = True
                
        if axeJoueur == True:
            if (joueur.raquette + Trajectoire.TAILLE_RAQ / 2) > self.ball[1] and (joueur.raquette - Trajectoire.TAILLE_RAQ / 2) < self.ball[1]:
                rebondSurRaquette = True
                print "rebondSurRaquette SUR RAQUETTE"
                # TODO : envoyer un message Collision avec STATUS = "HIT" + Gstat
        
        if axeJoueur == False or rebondSurRaquette == True :
            
            if self.ball[0] <= 0 or self.ball[0] >= 100: #si x = 0 ou 100 => collision sur un bord vertical (// axe y) => a' = 180 - a
                angle = 180 - angle
            elif (self.ball[1] <= 0 or self.ball[1] >= 100): #si y = 0 ou 100 => collision sur un bord horizontal (// axe x) => a' = - a
                angle = 360 - angle
            self.genererTrajectoire(pointDepart, angle) # generation nouvelle trajectoire à partir du point courant
        else :
  
              joueur.score -= 1 # TODO : faire une méthode "joueur.perdre()" qui envoie un message Collision avec STATUS = MISS" + Gstat
              self.genererTrajectoire() # generation nouvelle trajectoire à partir du point initial
        
    def genererTrajectoire(self, pointDepart=(50, 50), angle=random.random()*360):
        time = 0
        self.ball = list(pointDepart)

        self.ball[0] = self.ball[0] + math.cos(math.radians(angle))
        self.ball[1] = self.ball[1] - math.sin(math.radians(angle)) # "-" car l'axe des Y est vers le bas
        while(self.ball[0] > 0 and self.ball[0] < 100 and self.ball[1] > 0 and self.ball[1] < 100):
            self.ball[0] = self.ball[0] + math.cos(math.radians(angle))
            self.ball[1] = self.ball[1] - math.sin(math.radians(angle))
            #print self.ball[0], self.ball[1]
            time += Trajectoire.TIME_INT # "-" car l'axe des Y est vers le bas
        self.ball[0] = self.ball[0]
        self.ball[1] = self.ball[1]
        
        pointCollision = (self.ball[0], self.ball[1])
        
        self.sendPoint(pointCollision,time)
        
        print "COLLISION dans " + str(time) + " avec positionCollision = " + str(pointCollision)
        reactor.callLater(time, self.choisirTrajectoire, pointCollision, angle)
        
        
        
        
        
        
        
        
        
        
        
