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

    def __del__(self):
        print 'Deleting handler'

    def calcOffset(self, hour):
        #OFFSET = LOCAL - REMOTE ! en millisecondes
        #OFFSET négatif => client en retard sur le serveur, indique aussi la valeur du lag
        return (time.time()*1000 - hour)

    def decode(self, msg):
        print msg
        if (msg["msg"] == "Hello"):
            self.name = msg["pseudo"]
            self.offset = self.calcOffset(msg["time"])
            print self.offset

    def frameReceived(self, frame):
        self.decode(json.loads(frame))
        
       
    def connectionMade(self):
        print 'Connected to client.'
        self.site.joueurs.append(self)
        

    def connectionLost(self, reason):
        print 'Lost connection.'
        self.site.joueurs.remove(self)
