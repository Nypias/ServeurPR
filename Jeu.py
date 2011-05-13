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
            if jeu.nbJoueurs() < 2:
                #numéro de l'axe sur lequel est la raquette du joueur (0 : raquette gauche, 1 : raquette droite)
                #quand on est ici, ce nouveau joueur n'a pas encore été ajouté dans self.jeu.joueurs => +1
                joueur.jeu = jeu
                joueur.axe = jeu.joueurs.values().index(None)
                jeu.ajouterJoueur(joueur)
                #joueur.msgGstat() # TODO : enlever ?
                self.jeux.remove(jeu)
                self.jeux.append(jeu)
                break
            
        else:
            jeu = Jeu(self.jeux)
            joueur.jeu = jeu
            joueur.axe = jeu.joueurs.values().index(None)
            jeu.ajouterJoueur(joueur)
            #joueur.msgGstat() # TODO : enlever ?
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
        
        self.joueurs[joueur.axe] = None
        if self.nbJoueurs() == 0:
            self.trajectoire.stop()
            del self.trajectoire
            self.jeux.remove(self)
        elif self.nbJoueurs() == 1:
            # On va essayer de mettre le joueur resté seul dans une partie où un autre joueur est seul
            for jeu in self.jeux[:]:
                if jeu.nbJoueurs() == 1 and jeu != self:
                    joueurABouger = self.joueurs[joueur.axe ^ 1] #joueur.axe ^ 1 donne l'autre joueur de la partie
                    self.trajectoire.stop()
                    del self.trajectoire
                    self.jeux.remove(self)
                    #joueurABouger.reset() A mettre si on veut que le joueur qui arrive dans une nouvelle partie ait un score de 0
                    joueurABouger.jeu = jeu
                    joueurABouger.axe = jeu.joueurs.values().index(None)
                    jeu.ajouterJoueur(joueurABouger)
                    joueurABouger.msgGstat()
                    joueurABouger.msgSyncJ()
                    self.jeux.remove(jeu)
                    self.jeux.append(jeu)
                    break
            else:
                autreJoueur = self.joueurs[joueur.axe ^ 1]
                if autreJoueur.axe == 1:
                    self.joueurs[1]= None
                    autreJoueur.axe =0
                    self.joueurs[0] = autreJoueur
                autreJoueur.msgGstat()
                autreJoueur.msgSyncJ()
            
            
        
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
        
        
	
            