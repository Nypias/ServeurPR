# -*- coding: utf-8 -*-

from websocket import *
from Trajectoire import Trajectoire

""" Cette classe va gérer le jeu, càd conserver la liste des joueurs,
gérer leurs points, et déclencher des calculs de trajectoire """


class Jeu(WebSocketSite):
    joueurs = { 0 : None , 1 : None} # Mode deux joueurs pour l'instant, les numeros représentants l'axe de la raquette
                                    # 1 = axe de gauche , 2 = axe de droite
    trajectoire = Trajectoire(joueurs)

    def __init__(self, resource):
        WebSocketSite.__init__(self, resource)
        
    def ajouterJoueur(self,joueur):
        for numAxe in Jeu.joueurs.keys():
            if Jeu.joueurs[numAxe] == None:
                Jeu.joueurs[numAxe] = joueur
                break
        else:
            print "Nombre max de joueurs atteints"
            # TODO : Dire au client que plus de place... (cas du pong à 2 joueurs pour l'instant)
            
    def enleverJoueur(self,joueur):
        numeroAxeJoueur = Jeu.joueurs.values().index(joueur)
        print numeroAxeJoueur
        Jeu.joueurs[numeroAxeJoueur] = None
            