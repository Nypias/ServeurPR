# -*- coding: utf-8 -*-

#from twisted.internet.protocol import Protocol, Factory
from twisted.web.static import File
from twisted.web import server, resource
import Jeu, Joueur, Trajectoire
from websocket import *

class EchoHandler(WebSocketHandler):
    clients = []
    
    def __init__(self, transport):
        WebSocketHandler.__init__(self, transport)
        self.joueur = Joueur()

    def __del__(self):
        #print 'Deleting handler'
        del self.joueur

    def frameReceived(self, frame):
        print "Received : \""+frame+"\""
        for client in self.clients:
            if client != self:
                client.transport.write(frame)

    def connectionMade(self):
        #print 'Connected to client.'
        self.clients.append(self)

    def connectionLost(self, reason):
        #print 'Lost connection.'
        self.clients.remove(self)

class Simple(resource.Resource):
    isLeaf = True
    def render_GET(self, request):
        return "<html>Hello, world!</html>"

if __name__ == "__main__":
    from twisted.internet import reactor

    #WebSocketSite = une factory !
    #Simple() est une ressource
    factory = WebSocketSite(Simple())
    factory.addHandler('/test', EchoHandler)
    reactor.listenTCP(8080, factory)

    jeu = Jeu()

    print "launching reactor"
    reactor.run()
    print "stop reactor"

