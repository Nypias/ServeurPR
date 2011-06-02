# -*- coding: utf-8 -*-
import random, math

import json

from twisted.internet import reactor, defer
""" Méthode de calcul de trajectoire, doit implémenter une méthode pour
transformer la trajectoire en string JSON """


import Jeu

class Trajectoire :
    
    NB_ROUND = 4 # precision des valeurs
    TAILLE_RAQ = 20 #taille de la raquette entre 0 et 100 (en pourcentage)
    TIME_INT = 0.015 #vitesse (sans unité particulière) de la balle
    

    def __init__(self, jeu):

        self.jeu = jeu
        self.joueurs = self.jeu.joueurs
       
        # for multiplayer mode
        self.Xfield = [50,90] # list of the ordinate starting with the field center and next the field corners
        self.Yfield = [50,50] # list of the abscissa ...
        self.Xball = [random.random()*100,50] 
        self.Yball = [random.random()*100,50]

        self.delay = reactor.callLater(1 , self.genererTrajectoire,(50,50), 0) # on commencera à generer la trajectoire 
        # dans 0.5 secondes : cela permet de rendre la main au reactor et d'envoyer un message Gstat avant
     
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
              self.delay = reactor.callLater(0.7, self.genererTrajectoire, (50,50), 0)
              #self.genererTrajectoire((50,50),0) # generation nouvelle trajectoire à partir du point initial
        
    def genererTrajectoire(self, pointDepart, angle):
        if self.jeu.nbJoueurs() <=2:
            Stemps = 0
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
            self.ball[0] = round(self.ball[0] + u*math.cos(math.radians(angle)),Trajectoire.NB_ROUND)
            self.ball[1] = round(self.ball[1] - u*math.sin(math.radians(angle)),Trajectoire.NB_ROUND)

            temps = u * Trajectoire.TIME_INT 
            
            pointCollision = (self.ball[0], self.ball[1])
            self.sendPoint(pointCollision,temps)
            
            #print "COLLISION dans " + str(temps) + " avec positionCollision = (%.2f, %.2f)" % (pointCollision[0], pointCollision[1])
            #print self.joueurs.items()
            self.delay = reactor.callLater(temps, self.choisirTrajectoire, pointCollision, angle)
                    
        else:
            # creation of the field
            print "Passage en mode multi-joueur!"
            angle = 2*math.pi/self.jeu.nbJoueurs()
            print self.jeu.nbJoueurs()
            print "ancre n°1 : " + str(self.Xfield[1]) + " " + str(self.Yfield[1])
            i = 1
            while i<self.jeu.nbJoueurs():
                self.Xfield.append(round(50 + 40*math.cos(angle*i),Trajectoire.NB_ROUND)) # trunc isn't needed, python is so high
                self.Yfield.append(round(50 - 40*math.sin(angle*i),Trajectoire.NB_ROUND)) # because the field is build counterclockwise
                print "ancre n°" + str(i+1) + " : " + str(self.Xfield[i+1]) + " " + str(self.Yfield[i+1])
                i = i + 1
            print "Terrain multi-joueur cree"
            # throw the ball
            pointCollision = (self.Xball[1], self.Yball[1])
            self.multi_get_first_point()
                    
    def stop(self):
            self.delay.cancel()
            
    def multi_collision(self, nb_player):
    # send back 1 if collision 0 if the player lose the game
        # we test if the player is close enought(depending on the raquette size) to the ball impact
        i = 0
        # determination of abscissa and odonate of the raquette center
        Xraquette = Xfield[nb_player]*self.joueurs[nb_player].raquette + Xfield[nb_player+1]*(1-self.joueurs[nb_player].raquette)
        Yraquette = Yfield[nb_player]*self.joueurs[nb_player].raquette + Yfield[nb_player+1]*(1-self.joueurs[nb_player].raquette)
        # i did the arbitrary choise of a 16% lenght raquette regarding the size of the player segment that's why: 8^2 is used
        if ( (self.Xball[len(self.Xball)-1]-Xraquette)^2+(self.Yball[len(self.Yball)-1]-Yraquette)^2 ) < 8^2:
            self.multi_get_new_point(self, nb_player)		
            print "COLLISION sur la raquette du joueur " + nb_player
        else:
            print nb_player + "looser"

    def multi_get_new_point(self, nb_sender):
	 
        print "multi_get_new_point"
        # création of the vector before collision
        A = self.Xball[1]-self.Xball[0]
        B = self.Yball[1]-self.Yball[0]
        longeur = (math.fabs(A)+math.fabs(B))
        a_before = round(A/longeur, Trajectoire.NB_ROUND)
        b_before = round(B/longeur, Trajectoire.NB_ROUND)
        print " a_before : " + str(a_before) + " b_before : " + str(b_before)
            
        # création of the collided line
        senderPlusUn = nb_sender+1
        if nb_sender == self.jeu.nbJoueurs():
            senderPlusUn = 1
        A = self.Xfield[nb_sender] - self.Xfield[senderPlusUn]
        B = self.Yfield[nb_sender] - self.Yfield[senderPlusUn]
        longeur = (math.fabs(A)+math.fabs(B))
        a_border = round(A/longeur, Trajectoire.NB_ROUND)
        b_border = round(B/longeur, Trajectoire.NB_ROUND)
        print " a_border : " + str(a_border) + " b_border : " + str(b_border)
        
        # création of the new trajectory
        scalar_product_border = a_before*a_border + b_before*b_border # to get the pojection on the border
        # in order to build the correct perpendicular unit vector to project the second part of the _before vector you have to understand that
        # the field is build in the counterclockwise (sens trigonometrique) so a -PI/2 rotation from _border vector is needed.
        a_perpendicular = - b_border
        b_perpendicular = a_border
        print " a_perpendicular : " + str(a_perpendicular) + " b_perpendicular : " + str(b_perpendicular)
        scalar_product_perpendicular = a_before*a_perpendicular + b_before*b_perpendicular
        a_after = round(a_border*scalar_product_border - a_perpendicular*scalar_product_perpendicular,Trajectoire.NB_ROUND)
        b_after = round(b_border*scalar_product_border - b_perpendicular*scalar_product_perpendicular,Trajectoire.NB_ROUND)
        print " a_after : " + str(a_after) + " b_after : " + str(b_after)

        #for each player we look for intersect between this new trajectory and a player segment
        i = 1
        while i < self.jeu.nbJoueurs()+1:
            if i != nb_sender:               
                nb_player = i
                playerPlusUn = i+1
                if i == self.jeu.nbJoueurs():
                    playerPlusUn = 1
                # création of the line supporting the player segment
                A = self.Xfield[nb_player]-self.Xfield[playerPlusUn]
                B = self.Yfield[nb_player]-self.Yfield[playerPlusUn]
                longeur = (math.fabs(A)+math.fabs(B))
                a_intersect_line = round(A/longeur, Trajectoire.NB_ROUND)
                b_intersect_line = round(B/longeur, Trajectoire.NB_ROUND)
                # determination of the intersection point
                # the use of "len(self.Yball)-1" will allow us to build more complexe ball's beavior in futur developpement 
                # traitement des exeptions du au modele math utilisé: prendre un feuille de papier pour comprendre. 
                #  Les autres modèles que j'ai essayé sont pire.
                #  Mais j'ai peu être loupé la solution la plus simple essite pas si une idée vous passe par la tête.
                if (a_after == 0.00):
                    Xintersect = self.Xball[len(self.Xball)-1]
                    if b_intersect_line == 0.00:
                        Yintersect = self.Yball[len(self.Yball)-1]
                    elif a_intersect_line == 0:
                        Yintersect =  -1 #infini 
                    else:
                        Yintersect = round(self.Yfield[nb_player] + (Xintersect-self.Xfield[nb_player])*b_intersect_line/a_intersect_line,2)
                else:
                    if b_after == b_intersect_line:
                        Xintersect =  -1 #infini 
                    elif a_intersect_line == 0.00:
                        Xintersect = self.Xfield[nb_player]
                        Yintersect = round(self.Yball[len(self.Yball)-1]+(self.Xball[len(self.Xball)-1]-self.Xfield[nb_player])*b_after,Trajectoire.NB_ROUND)
                    else:    
                        Xintersect = round((self.Yfield[nb_player] - self.Yball[len(self.Yball)-1] - (self.Xfield[nb_player]*b_intersect_line/a_intersect_line) + (self.Xball[len(self.Xball)-1]*b_after/a_after) ) / ( b_after/a_after - b_intersect_line/a_intersect_line), Trajectoire.NB_ROUND)
                        Yintersect = round(self.Yfield[nb_player] + (Xintersect-self.Xfield[nb_player])*b_intersect_line/a_intersect_line,Trajectoire.NB_ROUND)

                # is this intersection point in the player segment ?
                if ( (self.Xfield[nb_player]<=Xintersect and Xintersect<=self.Xfield[playerPlusUn]) or (self.Xfield[playerPlusUn]<=Xintersect and Xintersect<=self.Xfield[nb_player]) ) and ( (self.Yfield[nb_player]<=Yintersect and Yintersect<=self.Yfield[playerPlusUn]) or (self.Yfield[playerPlusUn]<=Yintersect and Yintersect<=self.Yfield[nb_player]) ):
                    # if yes then set the news X,Yball
                    self.Xball[0] = self.Xball[1]
                    self.Xball[1] = Xintersect
                    self.Yball[0] = self.Yball[1]
                    self.Yball[1] = Yintersect
                    self.multi_time_calculation(nb_player)
                    i = self.jeu.nbJoueurs() # to end the loop
            i=i+1
        print "multi_get_new_point FIN"    
                
    def multi_get_first_point(self):
        # the first point is built using a random point and a virtual wall at the field center
        print "multi_get_first_point"
        print "point de depart : " + str(self.Xball[0]) + " , " + str(self.Yball[0])
        # création of the vector before collision
        A = self.Xball[1]-self.Xball[0]
        B = self.Yball[1]-self.Yball[0]
        longeur = (math.fabs(A)+math.fabs(B))
        a_before = round(A/longeur, Trajectoire.NB_ROUND)
        b_before = round(B/longeur, Trajectoire.NB_ROUND)
            
        # création of the collided line
        a_border = 0.5
        b_border = 0.5
            
        # création of the new trajectory
        scalar_product_border = a_before*a_border + b_before*b_border # to get the pojection on the border
        # in order to build the correct perpendicular unit vector to project the second part of the _before vector you have to understand that
        # the field is build in the counterclockwise (sens trigonometrique) so a -PI/2 rotation from _border vector is needed.
        a_perpendicular = - b_border
        b_perpendicular = a_border
        scalar_product_perpendicular = a_before*a_perpendicular + b_before*b_perpendicular
        a_after = round(a_border*scalar_product_border - a_perpendicular*scalar_product_perpendicular, Trajectoire.NB_ROUND)
        b_after = round(b_border*scalar_product_border - b_perpendicular*scalar_product_perpendicular, Trajectoire.NB_ROUND)
       
        #for each player we look for intersect between this new trajectory and a player segment
        i = 1
        while i < self.jeu.nbJoueurs()+1:
            print "joueur " + str(i) + " test"
            nb_player = i
            playerPlusUn = i+1
            if i == self.jeu.nbJoueurs():
                playerPlusUn = 1
            # création of the line supporting the player segment
            A = self.Xfield[i]-self.Xfield[playerPlusUn]
            B = self.Yfield[i]-self.Yfield[playerPlusUn]
            longeur = (math.fabs(A)+math.fabs(B))
            a_intersect_line = round(A/longeur, Trajectoire.NB_ROUND)
            b_intersect_line = round(B/longeur, Trajectoire.NB_ROUND)
            # determination of the intersection point
            # traitement des exeptions du au modele math utilisé: prendre un feuille de papier pour comprendre. 
            #  Les autres modèles que j'ai essayé sont pire.
            #  Mais j'ai peu être loupé la solution la plus simple essite pas si une idée vous passe par la tête.
            if (a_after == 0.00):
                Xintersect = self.Xball[len(self.Xball)-1]
                if b_intersect_line == 0.00:
                    Yintersect = self.Yball[len(self.Yball)-1]
                elif a_intersect_line == 0.00:
                    Yintersect =  -1 #infini 
                else:
                    Yintersect = round(self.Yfield[nb_player] + (Xintersect-self.Xfield[nb_player])*b_intersect_line/a_intersect_line,2)
            else:
                if b_after == b_intersect_line:
                    Xintersect =  -1 #infini 
                elif a_intersect_line == 0:
                    Xintersect = self.Xfield[nb_player]
                    Yintersect = round(self.Yball[len(self.Yball)-1]+(self.Xball[len(self.Xball)-1]-self.Xfield[nb_player])*b_after,Trajectoire.NB_ROUND)
                else:    
                    Xintersect = round((self.Yfield[nb_player] - self.Yball[len(self.Yball)-1] - (self.Xfield[nb_player]*b_intersect_line/a_intersect_line) + (self.Xball[len(self.Xball)-1]*b_after/a_after) ) / ( b_after/a_after - b_intersect_line/a_intersect_line), Trajectoire.NB_ROUND)
                    Yintersect = round(self.Yfield[nb_player] + (Xintersect-self.Xfield[nb_player])*b_intersect_line/a_intersect_line,Trajectoire.NB_ROUND)
            print "Xintersect : " + str(Xintersect) 
            print "Yintersect : " + str(Yintersect) 
            # is this intersection point in the player segment ?
            if ( (self.Xfield[nb_player]<=Xintersect and Xintersect<=self.Xfield[playerPlusUn]) or (self.Xfield[playerPlusUn]<=Xintersect and Xintersect<=self.Xfield[nb_player]) ) and ( (self.Yfield[nb_player]<=Yintersect and Yintersect<=self.Yfield[playerPlusUn]) or (self.Yfield[playerPlusUn]<=Yintersect and Yintersect<=self.Yfield[nb_player]) ):
                # if yes then set the news X,Yball
                self.Xball[0] = self.Xball[1]
                self.Xball[1] = Xintersect
                self.Yball[0] = self.Yball[1]
                self.Yball[1] = Yintersect
                print "fin premier point -> joueur " + str(i) + "  va prendre cher"
                i = self.jeu.nbJoueurs() # to end the loop
                self.multi_time_calculation(nb_player)
            i = i+1
        print "multi_get_first_point FIN"         

                    
    def multi_time_calculation(self, nb_player):
        # calculate the time to cross the distance between the two ball coordinates and call the reactor
        time = math.sqrt((self.Xball[0]-self.Xball[1])*(self.Xball[0]-self.Xball[1]) + (self.Yball[0]-self.Yball[1])*(self.Yball[0]-self.Yball[1]))*Trajectoire.TIME_INT
        pointCollision = (self.Xball[1], self.Yball[1])
        self.sendPoint(pointCollision,time)       
        print "COLLISION dans " + str(time) + " avec positionCollision = " + str(pointCollision) + " joueur n" + str(nb_player) + " prepare toi!"
        reactor.callLater(time, self.multi_get_new_point, nb_player)
        
        
        
        
        
        
        
        
