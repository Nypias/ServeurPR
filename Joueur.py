# -*- coding: utf-8 -*-

""" Un objet de cette classe sera créé pour chaque joueur,
utile pour mémoriser ses points/pseudo etc, son objet WebSocketHandler (histoire
de pouvoir communiquer avec le joueur)... """

from websocket import *

class Joueur(WebSocketHandler):
    

    def __init__(self, transport):
        print "ici"
        WebSocketHandler.__init__(self, transport)
        self.score=0
        self.name=""

    def __del__(self):
        print 'Deleting handler'

    def frameReceived(self, frame):
    	if self.name == "" :
    		self.name = frame
        # on affiche sur le serveur tous les noms des clients connectes
        for joueur in self.site.joueurs:
        	print joueur.name
        


    def connectionMade(self):
        print 'Connected to client.'
        self.site.joueurs.append(self)
        

    def connectionLost(self, reason):
        print 'Lost connection.'
        self.site.joueurs.remove(self)
