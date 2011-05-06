# -*- coding: utf-8 -*-

from websocket import *
from Trajectoire import Trajectoire

""" Cette classe va gérer le jeu, càd conserver la liste des joueurs,
gérer leurs points, et déclencher des calculs de trajectoire """


class Jeu(WebSocketSite):
     
    

    def __init__(self, resource):
        WebSocketSite.__init__(self, resource)
        self.nbJoueurs = 0
        self.joueurs = {0 : None , 1 : None, 2 : None , 3 : None , 4 : None , 5 : None, 6 : None , 7 : None , 8 : None} 
        trajectoire = Trajectoire(self)
        
    def ajouterJoueur(self,joueur):
        if self.nbJoueurs < 8:
                self.nbJoueurs = self.nbJoueurs + 1
                self.joueurs[self.nbJoueurs] = joueur			    
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
	
            