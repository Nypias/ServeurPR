# -*- coding: utf-8 -*-

from websocket import *
from Trajectoire import Trajectoire

""" Cette classe va gérer le jeu, càd conserver la liste des joueurs,
gérer leurs points, et déclencher des calculs de trajectoire """



class JeuFactory(WebSocketSite):
    
    
    def __init__(self, resource):
        WebSocketSite.__init__(self, resource)
        self.jeux = []
        
    
    def ajouterJoueurDansJeu(self, joueur):
        
        for jeu in self.jeux[:]: # [:] pour créer une copie temporaire de jeux : cela permet la modification de jeux
                                 # pendant l'itération
            if jeu.nbJoueurs() < 2: # TODO : mettre à 2 !
                jeu.ajouterJoueur(joueur)
                joueur.jeu = jeu
                self.jeux.remove(jeu)
                self.jeux.append(jeu)
                break
            
        else:
            jeu = Jeu(self.jeux)
            joueur.jeu = jeu
            jeu.ajouterJoueur(joueur)
            self.jeux.append(jeu)
    
    


class Jeu():
     
    def __init__(self, jeux):
        self.joueurs = { 0 : None , 1 : None}
        self.jeux = jeux
        self.trajectoire = Trajectoire(self)
        
    def ajouterJoueur(self,joueur):
        for numAxe in self.joueurs.keys():
            if self.joueurs[numAxe] == None:
                self.joueurs[numAxe] = joueur
                self.trajectoire.stop()
                del self.trajectoire
                self.trajectoire = Trajectoire(self)
                break
            
    def enleverJoueur(self,joueur):
        numeroAxeJoueur = self.joueurs.values().index(joueur)
        print numeroAxeJoueur
        self.joueurs[numeroAxeJoueur] = None
        if self.nbJoueurs() == 0:
            self.trajectoire.stop()
            del self.trajectoire
            self.jeux.remove(self)
            
        
    def getJoueurs(self):
        joueurs = []
        for joueur in self.joueurs.values():
            if joueur != None:
                joueurs.append(joueur)
        return joueurs
    
    def nbJoueurs(self):
        nb = 0
        for joueur in self.joueurs.values():
            if joueur != None:
                nb += 1
        return nb
        
        
	
            