# -*- coding: utf-8 -*-

from Jeu import Jeu
from Joueur import Joueur
from twisted.web.static import File
from websocket import *


if __name__ == "__main__":
    from twisted.internet import reactor

    #WebSocketSite = une factory !
    #Simple() est une ressource
    root = File(".")
    factory = Jeu(root)
    factory.addHandler('/game', Joueur)
    reactor.listenTCP(8080, factory)


    print "launching reactor"
    reactor.run()
    print "stop reactor"

