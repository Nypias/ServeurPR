# -*- coding: utf-8 -*-
from Joueur import Joueur


""" Cette classe va gérer le jeu, càd conserver la liste des joueurs,
gérer leurs points, et déclencher des calculs de trajectoire """
class Jeu:
    joueurs = []
    
    def __init__(self):
        pass

    def addJoueur(self, handler):
        joueur = Joueur()
        self.joueurs.append((joueur, handler))
