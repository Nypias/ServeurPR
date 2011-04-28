# -*- coding: utf-8 -*-

from websocket import *
from Trajectoire import Trajectoire

""" Cette classe va gérer le jeu, càd conserver la liste des joueurs,
gérer leurs points, et déclencher des calculs de trajectoire """


class Jeu(WebSocketSite):
     
    

    def __init__(self, resource):
        WebSocketSite.__init__(self, resource)
        self.joueurs = { 0 : None , 1 : None} # Mode deux joueurs pour l'instant, les numeros représentants l'axe de la raquette
                                    # 1 = axe de gauche , 2 = axe de droite
        trajectoire = Trajectoire(self)
        
    def ajouterJoueur(self,joueur):
        for numAxe in self.joueurs.keys():
            if self.joueurs[numAxe] == None:
                self.joueurs[numAxe] = joueur
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
            