# -*- coding: utf-8 -*-
import random, math

import json

from twisted.internet import reactor
""" Méthode de calcul de trajectoire, doit implémenter une méthode pour
transformer la trajectoire en string JSON """


class Trajectoire :
    
    TAILLE_RAQ = 20
    TIME_INT = 0.03
    

    def __init__(self, jeu):

        self.jeu = jeu;
        self.joueurs = self.jeu.joueurs
        time = 0
        angle = random.random()*360
        self.ball = [50, 50]
        self.ball[0] = self.ball[0] + math.cos(math.radians(angle))
        self.ball[1] = self.ball[1] - math.sin(math.radians(angle)) # "-" car l'axe des Y est vers le bas
        while(self.ball[0] > 0 and self.ball[0] < 100 and self.ball[1] > 0 and self.ball[1] < 100):
            self.ball[0] = self.ball[0] + math.cos(math.radians(angle))
            self.ball[1] = self.ball[1] - math.sin(math.radians(angle)) # "-" car l'axe des Y est vers le bas
            #print self.ball[0], self.ball[1]
            time += Trajectoire.TIME_INT
        self.ball[0] = self.ball[0]
        self.ball[1] = self.ball[1]

        pointCollision = (self.ball[0], self.ball[1])
        
        print "COLLISION dans " + str(time) + " avec positionCollision = " + str(pointCollision)
        
        self.sendPoint(pointCollision,time)
        reactor.callLater(time, self.choisirTrajectoire, pointCollision, angle)
        
        
    def sendPoint(self, point,temps):
        
        for client in self.jeu.getJoueurs():
                message = { "msg" : "Trajectoire", "point" : (point,client.getHourClient() + temps)}
                client.transport.write(json.dumps(message))

    def choisirTrajectoire(self, pointDepart, angle):

        axeJoueur = False
        rebondSurRaquette = False
        
        if self.ball[0] <= 0: # axe 0
            if self.joueurs[0] != None:
                joueur = self.joueurs[0]
                axeJoueur = True
                
        elif self.ball[0] >= 100: # axe 1
            if self.joueurs[1] != None:
                joueur = self.joueurs[1]
                axeJoueur = True
                
        if axeJoueur:
            if (joueur.raquette + Trajectoire.TAILLE_RAQ / 2) > self.ball[1] and (joueur.raquette - Trajectoire.TAILLE_RAQ / 2) < self.ball[1]:
                rebondSurRaquette = True
                print "rebondSurRaquette SUR RAQUETTE"
                # TODO : envoyer un message Collision avec STATUS = "HIT" + Gstat
        
        if (not axeJoueur) or (rebondSurRaquette) :
            
            if self.ball[0] <= 0 or self.ball[0] >= 100: #si x = 0 ou 100 => collision sur un bord vertical (// axe y) => a' = 180 - a
                angle = 180 - angle
            elif (self.ball[1] <= 0 or self.ball[1] >= 100): #si y = 0 ou 100 => collision sur un bord horizontal (// axe x) => a' = - a
                angle = 360 - angle
            self.genererTrajectoire(pointDepart, angle) # generation nouvelle trajectoire à partir du point courant
        else :
              print "JOUEUR LOSE"
              joueur.score -= 1 # TODO : faire une méthode "joueur.perdre()" qui envoie un message Collision avec STATUS = MISS" + Gstat
              self.genererTrajectoire((50,50),0) # generation nouvelle trajectoire à partir du point initial
        
    def genererTrajectoire(self, pointDepart, angle):
        time = 0
        if pointDepart == (50,50):
            angle = random.random()*360
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
        #print self.joueurs.items()
        reactor.callLater(time, self.choisirTrajectoire, pointCollision, angle)
        
        
        
        
        
        
        
        
        
        
        
