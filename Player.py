# -*- coding: utf-8 -*-
from websocket import *
from twisted.internet import task
import json
import time
import random


class Player(WebSocketHandler):
    """
    There exists one Player object per player, useful to save the pseudo, the score etc... his WebSocketHandler object
    (used to communicate with him.
    This class is used to handle the incoming and sent JSON messages specified in the protocol.
    """

    TIMEOUT = 1000000 #max time length a player can stay without moving
    
    
    def __init__(self, transport):
        WebSocketHandler.__init__(self, transport)
        #timestamp, in ms, of the last time one has heard about this client, used to detect timeouts
        self.lastTimeSeen = 0
        #initialize it
        self.setAlive()
        #player's score
        self.score = 0
        #player's pseudo
        self.name = ""
        #time offset, in milliseconds, between server time and client time
        self.offset = 0
        #position of the center of the racket_position on its axis between 0 and 100
        self.racket_position = 50
        self.previous_racket_position = 50
        
        self.last_movement_time = time.time()
        
    def reset(self):
        """
        Reset player's score.
        """
        self.score = 0

    def sendAll(self, msg):
        """
        Send a JSON message to all players in this room.
        """
        for client in self.room.getPlayers():
            client.send(msg)

    def send(self, msgJSON):
        """
        Send a JSON message to this client.
        """
        self.transport.write(json.dumps(msgJSON))

    def calcOffset(self, hour):
        #OFFSET = REMOTE - LOCAL  ! in milliseconds
        #the offset can come from 2 factors : the lag and the timezone difference between client and server
        return (hour - time.time()*1000)
    
    def getHourClient(self):
        """
        Compute the present time as it must be in the client's computer considering the offset.
        Returns a timestamp in ms !
        """
        return (self.offset +  time.time()*1000)

    def isAlive(self):
        #TODO : to be rewritten it should be better that the game itself call this method but only for one client,
        #here there is multiple calls
        for client in self.room.getPlayers(): 
			#si on n'a pas entendu parler du client depuis plus de TIMEOUT secondes
			if ((time.time()*1000 - client.lastTimeSeen) > (self.TIMEOUT*1000)):
				print "%s is offline (timeout) !" % client.name
				#TODO : à améliorer, appeler msgQuit() avec "Timeout" comme message de quit par ex
				client.transport.write("Get out!")
				client.transport.loseConnection()
                

    def setAlive(self):
        """
        When we receive something from the client, we remember the timestamp.
        This is used to check, periodically, if he's still there.
        """
        self.lastTimeSeen = time.time()*1000


    def lose(self):
        """
        The player lost a ball, score = score - 1
        """
        if self.score > 0:
            self.score -= 1
        self.msgCollision(False) #tell the player he failed
        self.msgGstat() #tells everyone the new score
        
    def win(self):
        """
        The player won a point, because the other player lost.
        """
        self.score +=1
        #TODO : as in "lose" we should send a msgCollision and a Gstat, shouldn't we ?
        

    def msgCollision(self, hit):
        """
        Tells every players that the last collision with a racket_position was a success, or a fail.
        """
        msg = {}
        msg["msg"] = "Collision"
        if hit:
            msg["status"] = "HIT"
        else:
            msg["status"] = "MISS"
        self.sendAll(msg)
        

    def msgHello(self, msg):
        #TODO il est interdit de faire un Hello une deuxième fois quand le joueur est déjà connecté : à détecter !
        newPseudo = False
        #if an empty pseudo is used, we assign the player a random one
        if msg["pseudo"] == "":
            newPseudo = True
            self.name = random.choice(["DSK","SofiMAIDS", "TieCops", \
                                       "CompCube", "NotF9", "GLADoS", \
                                       "G. Berger", "J. Capelle", "A.Einstein", \
                                       "C3ndrill0n", "Gr1nch3ux", "W4ll-F"])
        else:
            #one truncates pseudos longer than 10 chars
            if len(msg["pseudo"]) >= 10:
                self.name = msg["pseudo"][0:9]
                newPseudo = True
            else:
                self.name = msg["pseudo"]
        if self.room.player_nb() == 2:
            #if there is 2 players, one adds digits to the pseudo until it is different from the other
            if (self.name == self.room.players[self.axis^1].name):
                newPseudo = True
                self.name += str(random.randint(1, 9))
        if newPseudo:
            self.msgNewPseudo(self.name) #if we picked a different pseudo than what the player choosed, one tells him
        #updates the time offset    
        self.offset = self.calcOffset(msg["time"])
        #when a player is connecting, one informs everyone
        self.msgGstat()
        #and one sends SyncJ to the player in order for him to know others' players' rackets
        self.msgSyncJ()
        
    def msgNewPseudo(self,pseudo):
        """
        Informs the player that he has been given a different pseudo than what he choosed.
        """
        msg = {}
        msg["msg"] = "newPseudo"
        msg["pseudo"] = pseudo
        self.send(msg)

    def msgBouge(self, msg):
        """
        The player moved his racket_position to a new position.
        """
        #TODO déclencher erreur si n'est pas compris entre 0 et 100 : hack !
        self.previous_racket_position = self.racket_position
        self.racket_position = msg["raquette"]
        self.offset = self.calcOffset(msg["time"])

    def msgSyncJ(self):
        """
        Sends to every player the position of every racket_position.
        """
        msg = {}
        msg["msg"] = "SyncJ"
        msg["raquettes"] = {}
        for client in self.room.getPlayers():
            msg["raquettes"][client.name] = client.racket_position
        client.sendAll(msg)
        
        
    def msgSyncJMove(self):
        """
        Send to every player except self the racket position of self.
        """
        
        msg = {}
        msg["msg"] = "SyncJ"
        msg["raquettes"] = {}
        msg["raquettes"][self.name] = self.racket_position
        for client in self.room.getPlayers():
            if client != self:
                client.send(msg)
        

    def msgGstat(self):
        """
        Sends to every client the informations about everyone.
       
        Each player's informations are : pseudo, axis and score.
        """
        msg = {}
        msg["msg"] = "GStat"
        msg["players"] = {}
        for client in self.room.getPlayers():
            msg["players"][client.name] = {}
            msg["players"][client.name]["points"] = client.score
            msg["players"][client.name]["axe"] = client.axis
        self.sendAll(msg)
            
    def decode(self, msg):
        """
        Incoming message, it could be a Hello or Bouge message.
        """
        #print "Message reçu : \n%s" % json.dumps(msg, indent = 2)
        if (msg["msg"] == "Hello"):
            self.msgHello(msg)
        elif (msg["msg"] == "Bouge"):
            self.msgBouge(msg)
            self.last_movement_time = time.time()
            if self.room.player_nb() == 2:
                self.msgSyncJMove() #TODO : please COMMENT, it is undocumented in the protocol !
        else:
            print "Message inconnu !"

        self.setAlive()
            

    def frameReceived(self, frame):
        #Called by the websocket library when a new frame is received.
        self.decode(json.loads(frame))
        
       
    def connectionMade(self):
        #Called by the websocket library when the connection with the client has been established.
        #print 'Connected to client.'
        self.site.addPlayerToARoom(self)
        #TODO : refactor it, there should be one pingLoop by room and not one by player object
        #on va créer une boucle pour tester si le joueur est alive, avant on regarde si on n'a pas déjà créé cette boucle
        #en fait on la crée une seule fois, quand le premier client se connecte
        if (not hasattr(self.room, "pingLoop")):
            #on définit un appel en boucle de isAlive avec comme paramètre self
            self.room.pingLoop = task.LoopingCall(Player.isAlive, self)
            #elle se déclenche toutes les secondes
            self.room.pingLoop.start(1.0)
        

    def connectionLost(self, reason):
        #Called by the websocket library, the connection has been lost
        self.room.removePlayer(self)

