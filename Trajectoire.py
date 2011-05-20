# -*- coding: utf-8 -*-
import random, math

import json

from twisted.internet import reactor, defer
""" Méthode de calcul de trajectoire, doit implémenter une méthode pour
transformer la trajectoire en string JSON """

import Jeu

class Trajectoire :
    
    TAILLE_RAQ = 20 #taille de la raquette entre 0 et 100 (en pourcentage)
    TIME_INT = 0.028 #vitesse (sans unité particulière) de la balle
    

    def __init__(self, jeu):

        self.jeu = jeu
        self.joueurs = self.jeu.joueurs
        self.delay = reactor.callLater(1 , self.genererTrajectoire,(50,50), 0) # on commencera à generer la trajectoire 
        # dans 0.5 secondes : cela permet de rendre la main au reactor et d'envoyer un message Gstat avant
        self.vitesse = Trajectoire.TIME_INT
     
    def sendPoint(self, point,temps):
        
        for client in self.jeu.getJoueurs():
                message = { "msg" : "Trajectoire", "point" : (point, int(client.getHourClient() + temps*1000))}
                json.encoder.FLOAT_REPR = lambda f: ("%.2f" % f)
                client.transport.write(json.dumps(message))

    def choisirTrajectoire(self, pointDepart, angle):

        axeJoueur = False
        rebondSurRaquette = False
        
        if self.ball[0] <= 1.5: # axe 0
            if self.joueurs[0] != None:
                joueur = self.joueurs[0]
                axeJoueur = True
                
        elif self.ball[0] >= 98.5: # axe 1
            if self.joueurs[1] != None:
                joueur = self.joueurs[1]
                axeJoueur = True
                
        if axeJoueur:
            if (joueur.raquette + Trajectoire.TAILLE_RAQ / 2) > self.ball[1] and (joueur.raquette - Trajectoire.TAILLE_RAQ / 2) < self.ball[1]:
                rebondSurRaquette = True
                #print "rebondSurRaquette SUR RAQUETTE"
                # TODO : envoyer un message Collision avec STATUS = "HIT" + Gstat
        
        if (not axeJoueur) or (rebondSurRaquette) :
            
            if (self.ball[0] == 1.5 or self.ball[0] == 98.5 ) and (self.ball[1] == 0 or self.ball[1]==100 ):
                angle = 180 + angle
            elif self.ball[0] <= 1.5 or self.ball[0] >= 98.5: #si x = 0 ou 100 => collision sur un bord vertical (// axe y) => a' = 180 - a
                angle = 180 - angle
            elif (self.ball[1] <= 1 or self.ball[1] >= 99): #si y = 0 ou 100 => collision sur un bord horizontal (// axe x) => a' = - a
                angle = 360 - angle
            self.genererTrajectoire(pointDepart, angle) # generation nouvelle trajectoire à partir du point courant
        else :
              #print "JOUEUR LOSE"
              if self.joueurs[joueur.axe ^ 1] != None: # autre joueur de la partie
                  self.joueurs[joueur.axe ^ 1].gagner()
              joueur.perdre()
              self.vitesse = Trajectoire.TIME_INT
              self.delay = reactor.callLater(0.7, self.genererTrajectoire, (50,50), 0)
              #self.genererTrajectoire((50,50),0) # generation nouvelle trajectoire à partir du point initial
        
    def genererTrajectoire(self, pointDepart, angle):
        temps = 0
        if self.vitesse > 0.008: # augmentation de la vitesse
            self.vitesse -= 0.001
        if pointDepart == (50,50):
            petitangle = random.random()*35
            dg = 180
            if random.random() > 0.5:
                dg = 0
            hb = -1
            if random.random() > 0.5:
                hb = 1
            angle = dg + hb*(petitangle+10)
        self.ball = list(pointDepart)
        
        
        # determination of the shortest length to face a wall 
        u = (1.5 - self.ball[0]) / math.cos(math.radians(angle))
        if u<=0:
            u = (98.5 - self.ball[0]) / math.cos(math.radians(angle))      
        v = (self.ball[1] - 1) / math.sin(math.radians(angle))
        if v<=0:
            v = (self.ball[1] - 99) / math.sin(math.radians(angle))
        u = min(u,v)
        # result
        self.ball[0] = round(self.ball[0] + u*math.cos(math.radians(angle)),2)
        self.ball[1] = round(self.ball[1] - u*math.sin(math.radians(angle)),2)

        temps = u * self.vitesse
        
        pointCollision = (self.ball[0], self.ball[1])
        self.sendPoint(pointCollision,temps)
        
        #print "COLLISION dans " + str(temps) + " avec positionCollision = (%.2f, %.2f)" % (pointCollision[0], pointCollision[1])
        #print self.joueurs.items()
        self.delay = reactor.callLater(temps, self.choisirTrajectoire, pointCollision, angle)
        
    def stop(self):
            self.delay.cancel()
   
