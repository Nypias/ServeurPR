# -*- coding: utf-8 -*-

""" Un objet de cette classe sera créé pour chaque joueur,
utile pour mémoriser ses points/pseudo etc, son objet WebSocketHandler (histoire
de pouvoir communiquer avec le joueur)... """

from websocket import *
import json
import time

class Joueur(WebSocketHandler):
    

    def __init__(self, transport):
        WebSocketHandler.__init__(self, transport)
        self.score = 0
        self.name = ""
        self.offset = 0
        self.raquette = 50

    def __del__(self):
        print 'Deleting handler'

    def sendAll(self, msg):
        for client in self.site.joueurs:
            client.transport.write(msg)

    def calcOffset(self, hour):
        #OFFSET = LOCAL - REMOTE ! en millisecondes
        #OFFSET négatif => client en retard sur le serveur, indique aussi la valeur du lag
        return - (time.time()*1000 - hour)

    def msgHello(self, msg):
        #TODO il est interdit de faire un Hello une deuxième fois quand le joueur est déjà connecté : à détecter !
        self.name = msg["pseudo"]
        self.offset = self.calcOffset(msg["time"])

    def msgBouge(self, msg):
        #TODO déclencher erreur si n'est pas compris entre 0 et 100 : hack !
        self.raquette = msg["raquette"]
        self.offset = self.calcOffset(msg["time"])

    def msgSyncJ(self):
        msg = {}
        msg["msg"] = "SyncJ"
        msg["raquettes"] = {}
        for player in self.site.joueurs:
            msg["raquettes"][str(player.name)] = player.raquette
        self.sendAll(msg)

    def msgGstat(self):
        """ Envoi aux clients les informations sur tous les clients
        
        Les informations de chaque joueur sont son pseudo et son score"""
        
        msg = {}
        msg["msg"] = "GStat"
        msg["players"] = {}
        for player in self.site.joueurs:
            msg["players"][player.name] = player.score
        self.sendAll(json.dumps(msg))
    
    def decode(self, msg):
        print "#######\nMessage reçu : %s\n#######" % msg
        if (msg["msg"] == "Hello"):
            self.msgHello(msg)
            self.msgGstat()
        elif (msg["msg"] == "Bouge"):
            self.msgBouge(msg)
            self.msgSyncJ()
        else:
            print "Message inconnu !"

        print vars(self)
            

    def frameReceived(self, frame):
        self.decode(json.loads(frame))
        
       
    def connectionMade(self):
        print 'Connected to client.'
        self.site.joueurs.append(self)
        

    def connectionLost(self, reason):
        print 'Lost connection.'
        self.site.joueurs.remove(self)
        self.msgGstat()
