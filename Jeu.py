# -*- coding: utf-8 -*-

from websocket import *
from Trajectoire import Trajectoire

""" Cette classe va gérer le jeu, càd conserver la liste des joueurs,
gérer leurs points, et déclencher des calculs de trajectoire """


class Jeu(WebSocketSite):
     
    

    def __init__(self, resource):
        WebSocketSite.__init__(self, resource)
        self.joueurs = { 0 : None , 1 : None} 
        self.trajectoire = Trajectoire(self)
        
    def ajouterJoueur(self,joueur):
        for numAxe in self.joueurs.keys():
            if self.joueurs[numAxe] == None:
                self.joueurs[numAxe] = joueur
                self.trajectoire.stop()
                del self.trajectoire
                self.trajectoire = Trajectoire(self)
                break			    
        else:
            print "Nombre max de joueurs atteints"
            # TODO : Créer un nouveau Jeu! ou bien DECO le joueur
            
    def enleverJoueur(self,joueur):
        numeroAxeJoueur = self.joueurs.values().index(joueur)
        print numeroAxeJoueur
        self.joueurs[numeroAxeJoueur] = None
        
    def getJoueurs(self):
        joueurs = []
        for joueur in self.joueurs.values():
            if joueur != None:
                joueurs.append(joueur)
        return joueurs
	
            