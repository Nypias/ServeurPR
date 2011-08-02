# -*- coding: utf-8 -*-

from websocket import *
from Trajectory import Trajectory

import random

"""
This Factory manages a list of rooms, a room is where 2 players are playing but there could be only 1 player (poor guy).
If there is a solo player we pair it with the new one. If there isn't any solo player we create a new room.
"""

class RoomFactory(WebSocketSite):
    def __init__(self, resource):
        WebSocketSite.__init__(self, resource)
        # list of the game rooms = 2 player playing together
        self.rooms = []
        
    def msgTotalNumberOfRooms(self,player=None):
        """
        Implements the sending of the message RoomsStat from protocol to all players
        """
        msg = {}
        msg["msg"] = "RoomsStats"
        msg["rooms"] = len(self.rooms)
        if player == None:
            #we send it to all the players
            for room in self.rooms:
                for player in room.getPlayers():
                    player.send(msg)
        else:
            player.send(msg)
                  
    
    def addPlayerToARoom(self, player):
        """
        Adds a player into the first not full (1 player) game room
        """
        for room in self.rooms[:]: # [:] to create a temp copy of "rooms", it allows the modification of "rooms" during loop
        #we loop over the existing rooms
            if room.player_nb() < 2:
                player.room = room
                #id of the player's racket's axis (0 means left racket, 1 means right racket)
                #when we are here, this new player hasn't been yet added in self.room.players => +1
                player.axis = room.players.values().index(None)
                room.addPlayer(player)
                    
                #this room has just been given a new player, so we move it at the end of the list, it's important
                #if we want to pair the new player with the solo player who has been waiting for the longest time
                self.rooms.remove(room)
                self.rooms.append(room)

                self.msgTotalNumberOfRooms(player)
                break
                
        else:
            #strange Pythonic construction, this "else" is paired with "for" and is called if the for hasn't been "breaked"
            #it means that we haven't found any suitable room (solo player) so we create a new one !
            room = Room(self)
            player.room = room
            player.axis = room.players.values().index(None) #TODO : this is a new game so the axis is obviously #1, right ?
            #room.addPlayer(player)
            room.players[0] = player
            room.trajectory = Trajectory(room)
            #player.msgGstat() # TODO : enlever ?
            self.rooms.append(room)
            self.msgTotalNumberOfRooms() #tell all the players that a new room is born
        
        
"""
This class manages a playing room which is constitued by 1 or 2 players. We have
some convenient methods.
"""
class Room():
    def __init__(self, site):
        self.players = { 0 : None , 1 : None} #0 is left axis and 1 is right axis
        self.site = site #site is the websocket's lib entity used to talk with the player
        self.rooms = site.rooms #all the rooms
        #self.trajectory = Trajectory(self)
        
    def addPlayer(self,player):
        """
        Adds a player in this room
        """
        #we look for the first free racket to give to the player, if there was 3 players and the second one left
        #the new player will play in second position
        #TODO : it would be better to search for the None value and insert there instead of for-break !!! check : no
        #regression !
        for axisID in self.players.keys():
            if self.players[axisID] == None:
                #free racket found
                self.players[axisID] = player
                newPseudo = False
                #if the new player uses a name which is already in use, we add some random digits at the end and tell
                #him !
                if player.name == self.players[axisID ^ 1].name:
                    newPseudo = True
                    player.name += str(random.randint(1, 9))
                if player.name != "" and newPseudo:
                    player.msgNewPseudo(player.name)

                #restart the trajectory (we must because the number of players has changed so have the rules)
                self.trajectory.stop()
                del self.trajectory
                self.trajectory = Trajectory(self)
                break
            
    def removePlayer(self, player):
        """
        Delete a player from the room.
        """
        self.players[player.axis] = None
        player.msgGstat() #tells the players that there is one player less
        if self.player_nb() == 0: #empty room => deleted room
            self.trajectory.stop()
            del self.trajectory
            self.rooms.remove(self)
            self.site.msgTotalNumberOfRooms() #tells the player that there is one room less
        elif self.player_nb() == 1:
            #we try to pair the player left alone with an other solo player 
            for room in self.rooms[:]:
                if room.player_nb() == 1 and room != self:
                    #we have found a game "room" with 1 player ("room!=self" allows not to choose the previous game of the player)
                    playerToMove = self.players[player.axis ^ 1] #player.axis ^ 1 gives the other player of the room
                    self.trajectory.stop()
                    del self.trajectory
                    self.rooms.remove(self)
                    #playerToMove.reset() #use it if we want that the coming player beginns with score = 0 
                    playerToMove.room = room
                    playerToMove.axis = room.players.values().index(None)
                    room.addPlayer(playerToMove)
                    playerToMove.msgGstat()
                    playerToMove.msgSyncJ()
                    self.rooms.remove(room)
                    self.rooms.append(room)
                    self.site.msgTotalNumberOfRooms()
                    break
            else:
                otherPlayer = self.players[player.axis ^ 1]
                self.trajectory.stop()
                del self.trajectory
                self.trajectory = Trajectory(self)
                #if otherPlayer.axis == 1:
                #    self.players[1]= None
                #    otherPlayer.axis =0
                #    self.players[0] = otherPlayer
                otherPlayer.msgGstat()
                otherPlayer.msgSyncJ()
                self.site.msgTotalNumberOfRooms(otherPlayer)
            
            
        
    def getPlayers(self):
        """
        Returns all players, without the empty slots (where player left).
        """
        return filter(lambda x : x!=None, self.players.values())
    
    def player_nb(self):
        """
        How many players do we have ?
        """
        return len(self.getPlayers())
        
