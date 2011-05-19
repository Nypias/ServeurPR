# -*- coding: utf-8 -*-

from websocket import *
from Trajectoire import Trajectoire

import random

""" Cette classe va gérer le jeu, càd conserver la liste des joueurs,
gérer leurs points, et déclencher des calculs de trajectoire """


                
class JeuFactory(WebSocketSite):
    
    
    def __init__(self, resource):
        WebSocketSite.__init__(self, resource)
        self.jeux = []
        
    def msgRoomStat(self):
            msg = {}
            msg["msg"] = "RoomsStats"
            msg["rooms"] = len(self.jeux)
            for jeu in self.jeux:
                for joueur in jeu.getJoueurs():
                    joueur.send(msg)
                    
    def msgRoomStatOnePlayer(self,joueur):
        msg = {}
        msg["msg"] = "RoomsStats"
        msg["rooms"] = len(self.jeux)
        joueur.send(msg)
                
        
    
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
                self.msgRoomStatOnePlayer(joueur)
                break
            
        else:
            jeu = Jeu(self)
            joueur.jeu = jeu
            joueur.axe = jeu.joueurs.values().index(None)
            #jeu.ajouterJoueur(joueur)
            jeu.joueurs[0] = joueur
            jeu.trajectoire = Trajectoire(jeu)
            #joueur.msgGstat() # TODO : enlever ?
            self.jeux.append(jeu)
            self.msgRoomStat()
        
        

class Jeu():
     
    def __init__(self, site):
        self.joueurs = { 0 : None , 1 : None}
        self.site = site
        self.jeux = site.jeux
        #self.trajectoire = Trajectoire(self)
        
    def ajouterJoueur(self,joueur):
        for numAxe in self.joueurs.keys():
            if self.joueurs[numAxe] == None:
                
                self.joueurs[numAxe] = joueur
                newPseudo = False
                while joueur.name == self.joueurs[numAxe ^ 1].name:
                    newPseudo = True
                    joueur.name += str(random.randint(1, 9))
                if joueur.name != "" and newPseudo:
                    joueur.msgNewPseudo(joueur.name)
                self.trajectoire.stop()
                del self.trajectoire
                self.trajectoire = Trajectoire(self)
                break
            
    def enleverJoueur(self,joueur):
        
        self.joueurs[joueur.axe] = None
        joueur.msgGstat()
        if self.nbJoueurs() == 0:
            self.trajectoire.stop()
            del self.trajectoire
            self.jeux.remove(self)
            self.site.msgRoomStat()
        elif self.nbJoueurs() == 1:
            # On va essayer de mettre le joueur resté seul dans une partie où un autre joueur est seul
            for jeu in self.jeux[:]:
                if jeu.nbJoueurs() == 1 and jeu != self:
                    joueurABouger = self.joueurs[joueur.axe ^ 1] #joueur.axe ^ 1 donne l'autre joueur de la partie
                    self.trajectoire.stop()
                    del self.trajectoire
                    self.jeux.remove(self)
                    self.site.msgRoomStat()
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
                self.trajectoire.stop()
                del self.trajectoire
                self.trajectoire = Trajectoire(self)
                #if autreJoueur.axe == 1:
                #    self.joueurs[1]= None
                #    autreJoueur.axe =0
                #    self.joueurs[0] = autreJoueur
                autreJoueur.msgGstat()
                autreJoueur.msgSyncJ()
                self.site.msgRoomStatOnePlayer(autreJoueur)
            
            
        
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
        
        
	
            