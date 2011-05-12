# -*- coding: utf-8 -*-

from Jeu import Jeu
from Joueur import Joueur
from twisted.web.static import File
from websocket import *
import webbrowser #TESTING purpose


if __name__ == "__main__":
    from twisted.internet import reactor

    #WebSocketSite = une factory !
    #Simple() est une ressource
    root = File("../ClientPR/")
    factory = Jeu(root)
    factory.addHandler('/game', Joueur)
    reactor.listenTCP(8080, factory)


    print "launching reactor"
    webbrowser.open("http://localhost:8080/pongroulette.html")
#    webbrowser.open("http://localhost:8080/pongroulette.html")
    reactor.run()
    print "stop reactor"

