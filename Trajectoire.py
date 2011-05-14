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
        
        # for multiplayer mode
        self.Xfield = [50,90] # list of the ordinate starting with the field center and next the field corners
        self.Yfield = [50,50] # list of the abscissa ...
        self.Xball = [random.random()*100,50] 
        self.Yball = [random.random()*100,50]
        
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
        if self.jeu.nbJoueurs <= 2:
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
        
        else:
            # creation of the field
            print "Passage en mode multi-joueur!"
            angle = 360/self.jeu.nbJoueurs
            i = 1
            while i<self.jeu.nbJoueurs:
                self.Xfield.append(50 + 40*math.cos(angle*i)) # trunc isn't needed, python is so high
                self.Yfield.append(50 + 40*math.sin(angle*i))
                i = i + 1
            print "Terrain multi-joueur cree"
            # throw the ball
            pointCollision = (self.Xball[1], self.Yball[1])
            self.sendPoint(pointCollision,time)
            self.multi_get_first_point()
            
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
        a_before = A/(A+B)
        b_before = B/(A+B)
            
        # création of the collided line
        A = self.Xfield[nb_sender] - self.Xfield[nb_sender+1]
        B = self.Yfield[nb_sender] - self.Yfield[nb_sender+1]
        a_border = A/(A+B)
        b_border = B/(A+B)
            
        # création of the new trajectory
        scalar_product_border = a_before*a_border + b_before*b_border # to get the pojection on the border
        # in order to build the correct perpendicular unit vector to project the second part of the _before vector you have to understand that
        # the field is build in the counterclockwise (sens trigonometrique) so a -PI/2 rotation from _border vector is needed.
        a_perpendicular = - a_border
        b_perpendicular = b_border
        scalar_product_perpendicular = a_before*a_perpendicular + b_before*b_perpendicular
        a_after = a_border*scalar_product_border - a_perpendicular*scalar_product_perpendicular
        b_after = b_border*scalar_product_border - b_perpendicular*scalar_product_perpendicular

        #for each player we look for intersect between this new trajectory and a player segment
        i = 1
        while i < self.jeu.nbJoueurs+1:
            if i != nb_sender:
                nb_player = i
                playerPlusUn = i+1
                if i == self.jeu.nbJoueurs:
                    playerPlusUn = 1
                # création of the line supporting the player segment
                A = self.Xfield[i]-self.Xfield[playerPlusUn]
                B = self.Yfield[i]-self.Yfield[playerPlusUn]
                a_intersect_line = A/(A+B)
                b_intersect_line = B/(A+B)
                # determination of the intersection point
                Xintersect = (self.Yfield[nb_player] - self.Yball[len(self.Yball)-1] - (self.Xfield[nb_player]*b_intersect_line/a_intersect_line) + (self.Xball[len(self.Xball)-1]*b_after/a_after) ) / ( b_after/a_after - b_intersect_line/a_intersect_line)
                Yintersect = self.Yfield[nb_player] + (Xintersect-self.Xfield[nb_player])*b_intersect_line/a_intersect_line
                # is this intersection point in the player segment ?
                if ( (self.Xfield[nb_player]<=Xintersect and Xintersect<=self.Xfield[playerPlusUn]) or (self.Xfield[playerPlusUn]<=Xintersect and Xintersect<=self.Xfield[nb_player]) ) and ( (self.Yfield[nb_player]<=Yintersect and Yintersect<=self.Yfield[playerPlusUn]) or (self.Yfield[playerPlusUn]<=Yintersect and Yintersect<=self.Yfield[nb_player]) ):
                    # if yes then set the news X,Yball
                    Xball[0] = Xball[1]
                    Xball[1] = Xintersection
                    Yball[0] = Yball[1]
                    Yball[1] = Yintersection
                    self.multi_time_calculation(self, i)
                    i = self.jeu.nbJoueurs # to end the loop
            i = i+1
        print "multi_get_new_point FIN"    
                
    def multi_get_first_point(self):
    
        print "multi_get_first_point"
        print "point de depart : " + str(self.Xball[0]) + " , " + str(self.Yball[0])
        # création of the vector before collision
        A = self.Xball[1]-self.Xball[0]
        B = self.Yball[1]-self.Yball[0]
        a_before = A/(A+B)
        b_before = B/(A+B)
            
        # création of the collided line
        a_border = 0.1
        b_border = 0.9
            
        # création of the new trajectory
        scalar_product_border = a_before*a_border + b_before*b_border # to get the pojection on the border
        # in order to build the correct perpendicular unit vector to project the second part of the _before vector you have to understand that
        # the field is build in the counterclockwise (sens trigonometrique) so a -PI/2 rotation from _border vector is needed.
        a_perpendicular = - a_border
        b_perpendicular = b_border
        scalar_product_perpendicular = a_before*a_perpendicular + b_before*b_perpendicular
        a_after = a_border*scalar_product_border - a_perpendicular*scalar_product_perpendicular
        b_after = b_border*scalar_product_border - b_perpendicular*scalar_product_perpendicular

        #for each player we look for intersect between this new trajectory and a player segment
        i = 1
        while i < self.jeu.nbJoueurs+1:
                print "joueur " + str(i) + " test"
                nb_player = i
                playerPlusUn = i+1
                if i == self.jeu.nbJoueurs:
                    playerPlusUn = 1
                # création of the line supporting the player segment
                A = self.Xfield[i]-self.Xfield[playerPlusUn]
                B = self.Yfield[i]-self.Yfield[playerPlusUn]
                a_intersect_line = A/(A+B)
                b_intersect_line = B/(A+B)
                # determination of the intersection point
                #print "self.Yball[len(self.Yball)-1] : " + str(self.Yball[len(self.Yball)-1])
                #print "a_intersect_line : " + str(a_intersect_line)
                #print "a_after : " + str(a_after)
                #print "( b_after/a_after - b_intersect_line/a_intersect_line) : " + str( b_after/a_after - b_intersect_line/a_intersect_line)
                Xintersect = (self.Yfield[nb_player] - self.Yball[len(self.Yball)-1] - (self.Xfield[nb_player]*b_intersect_line/a_intersect_line) + (self.Xball[len(self.Xball)-1]*b_after/a_after) ) / ( b_after/a_after - b_intersect_line/a_intersect_line)
                Yintersect = self.Yfield[nb_player] + (Xintersect-self.Xfield[nb_player])*b_intersect_line/a_intersect_line
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
                    i = self.jeu.nbJoueurs # to end the loop
                    self.multi_time_calculation(i)
                i = i+1
        print "multi_get_first_point FIN"         

                    
    def multi_time_calculation(self, nb_player):
        # calculate the time to cross the distance between the two ball coordinates and call the reactor
        time = math.sqrt((self.Xball[0]-self.Xball[1])*(self.Xball[0]-self.Xball[1]) + (self.Yball[0]-self.Yball[1])*(self.Yball[0]-self.Yball[1]))
        pointCollision = (self.Xball[1], self.Yball[1])
        self.sendPoint(pointCollision,time)       
        print "COLLISION dans " + str(time) + " avec positionCollision = " + str(pointCollision)
        reactor.callLater(time, self.multi_get_new_point, nb_player)
        
        
        
        
        
        
        
        
