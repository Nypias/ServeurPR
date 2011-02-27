# -*- coding: utf-8 -*-

#from twisted.internet.protocol import Protocol, Factory
from Jeu import Jeu
from Joueur import Joueur
from twisted.web import resource
from websocket import *


class Simple(resource.Resource):
    isLeaf = True
    def render_GET(self, request):
        return "<html>Hello, world!</html>"
    

if __name__ == "__main__":
    from twisted.internet import reactor

    #WebSocketSite = une factory !
    #Simple() est une ressource
    factory = Jeu(Simple())
    factory.addHandler('/game', Joueur)
    reactor.listenTCP(8080, factory)


    print "launching reactor"
    reactor.run()
    print "stop reactor"

