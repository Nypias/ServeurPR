# -*- coding: utf-8 -*-

import random, math

""" Méthode de calcul de trajectoire, doit implémenter une méthode pour
transformer la trajectoire en string JSON """
class Trajectoire:
    def __init__(self):
        angle = random.random()*360
        print "orientation départ = %f" % angle
        self.ball = [50,50]
        print ("%f;%f" % (self.ball[0], self.ball[1])).replace(".", ",")

        for i in range(10):
            self.ball[0] = self.ball[0] + math.cos(math.radians(angle))
            self.ball[1] = self.ball[1] - math.sin(math.radians(angle)) # "-" car l'axe des Y est vers le bas
            while(self.ball[0] > 0 and self.ball[0] < 100 and self.ball[1] > 0 and self.ball[1] < 100):
                self.ball[0] = self.ball[0] + math.cos(math.radians(angle))
                self.ball[1] = self.ball[1] - math.sin(math.radians(angle)) # "-" car l'axe des Y est vers le bas
            self.ball[0] = self.ball[0]
            self.ball[1] = self.ball[1]
            if (self.ball[0] <= 0 or self.ball[0] >= 100): #si x = 0 ou 100 => collision sur un bord vertical (// axe y) => a' = 180 - a
                angle = 180 - angle
            elif (self.ball[1] <= 0 or self.ball[1] >= 100): #si y = 0 ou 100 => collision sur un bord horizontal (// axe x) => a' = - a
                angle = 360 - angle
            print ("%f;%f" % (self.ball[0], self.ball[1])).replace(".", ",")



traj = Trajectoire()