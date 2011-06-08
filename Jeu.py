# -*- coding: utf-8 -*-

from websocket import *
from Trajectoire import Trajectoire

import random

"""
This Factory manages a list of rooms, a room is where 2 players are playing but there could be only 1 player (poor guy).
If there is a solo player we pair it with the new one. If there isn't any solo player we create a new room.
"""
class JeuFactory(WebSocketSite):
    def __init__(self, resource):
        WebSocketSite.__init__(self, resource)
        # list of the game rooms = 2 player playing together
        self.jeux = []
        
    def msgRoomStat(self): # TODO : rename ! doesn't correspond to Room_s_Stat_s_
        """
        Implements the sending of the message RoomsStat from protocol to all players
        """
        msg = {}
        msg["msg"] = "RoomsStats"
        msg["rooms"] = len(self.jeux)
        for jeu in self.jeux:
            for joueur in jeu.getJoueurs():
                joueur.send(msg)
                    
    def msgRoomStatOnePlayer(self,joueur): # TODO : rename ! doesn't correspond to Room_s_Stat_s_
        """
        Implements the sending of the message RoomsStat from protocol to one player
        """
        msg = {}
        msg["msg"] = "RoomsStats"
        msg["rooms"] = len(self.jeux)
        joueur.send(msg)
                
        
    
    def ajouterJoueurDansJeu(self, joueur):
        """
        Adds a player into the first not full (1 player) game room
        """
        for jeu in self.jeux[:]: # [:] to create a temp copy of "jeux", it allows the modification of "jeux" during loop
        #we loop over the existing rooms
            if jeu.nbJoueurs() < 3:
                joueur.jeu = jeu
                #id of the player's racket's axis (0 means left racket, 1 means right racket)
                #when we are here, this new player hasn't been yet added in self.jeu.joueurs => +1
                joueur.axe = jeu.joueurs.values().index(None)
                jeu.ajouterJoueur(joueur)
                
                #joueur.msgGstat() # TODO : enlever ?
                    
                #this room has just been given a new player, so we move it at the end of the list, it's important
                #if we want to pair the new player with the solo player who has been waiting for the longest time
                self.jeux.remove(jeu)
                self.jeux.append(jeu)

                self.msgRoomStatOnePlayer(joueur)
                break

        else:
            #strange Pythonic construction, this "else" is paired with "for" and is called if the for hasn't been "breaked"
            #it means that we haven't found any suitable room (solo player) so we create a new one !
            jeu = Jeu(self)
            joueur.jeu = jeu
            joueur.axe = jeu.joueurs.values().index(None) #TODO : this is a new game so the axis is obviously #1, right ?
            #jeu.ajouterJoueur(joueur)
            jeu.joueurs[0] = joueur
            jeu.trajectoire = Trajectoire(jeu)
            #joueur.msgGstat() # TODO : enlever ?
            self.jeux.append(jeu)
            self.msgRoomStat() #tell all the players that a new room is born
        
        
"""
This class manages a playing room which is constitued by 1 or 2 players. We have
some convenient methods.
"""
class Jeu():
    def __init__(self, site):
        self.joueurs = { 0 : None , 1 : None , 2 : None} 
        self.site = site #site is the websocket's lib entity used to talk with the player
        self.jeux = site.jeux #all the rooms
        #self.trajectoire = Trajectoire(self)
        
    def ajouterJoueur(self,joueur):
        """
        Adds a player in this room
        """
        #we look for the first free racket to give to the player, if there was 3 players and the second one left
        #the new player will play in second position
        #TODO : it would be better to search for the None value and insert there instead of for-break !!! check : no
        #regression !
        for numAxe in self.joueurs.keys():
            if self.joueurs[numAxe] == None:
                #free racket found
                self.joueurs[numAxe] = joueur
                newPseudo = False
                #if the new player uses a name which is already in use, we add some random digits at the end and tell
                #him !
                unique = False
                if not joueur.name in self.joueurs:
                    unique = True
                while unique == False:
                    newPseudo = True
                    joueur.name += str(random.randint(1, 9))
                    if not joueur.name in self.joueurs:
                        unique = True
                if joueur.name != "" and newPseudo:
                    joueur.msgNewPseudo(joueur.name)

                #restart the trajectory (we must because the number of players has changed so have the rules)
                self.trajectoire.stop()
                del self.trajectoire
                self.trajectoire = Trajectoire(self)
                break
            
    def enleverJoueur(self, joueur):
        """
        Delete a player from the room.
        """
        self.joueurs[joueur.axe] = None #TODO : wouldn't be better to remove from the list instead of replacing by None?
        joueur.msgGstat() #tells the players that there is one player less
        if self.nbJoueurs() == 0: #empty room => deleted room
            self.trajectoire.stop()
            del self.trajectoire
            self.jeux.remove(self)
            self.site.msgRoomStat() #tells the player that there is one room less
            
#ICI j'ai vraiment la flème de m'en occuper.
             
        elif self.nbJoueurs() == 1:
            #we try to pair the player left alone with an other solo player 
            for jeu in self.jeux[:]:
                if jeu.nbJoueurs() == 1 and jeu != self:
                    #TODO : Alex could you explain these lines please ? not very clear for me...
                    joueurABouger = self.joueurs[joueur.axe ^ 1] #joueur.axe ^ 1 gives the other player of the room
                    self.trajectoire.stop()
                    del self.trajectoire
                    self.jeux.remove(self)
                    #joueurABouger.reset() #use it if we want that the coming player beginns with score = 0 
                    joueurABouger.jeu = jeu
                    joueurABouger.axe = jeu.joueurs.values().index(None)
                    jeu.ajouterJoueur(joueurABouger)
                    joueurABouger.msgGstat()
                    joueurABouger.msgSyncJ()
                    self.jeux.remove(jeu)
                    self.jeux.append(jeu)
                    self.site.msgRoomStat()
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
        """
        Returns all players, without the empty slots (where player left).
        """
        return filter(lambda x : x!=None, self.joueurs.values())
    
    def nbJoueurs(self):
        """
        How many players do we have ?
        """
        return len(self.getJoueurs()) # beurk .. ?
        
