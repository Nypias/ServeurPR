# -*- coding: utf-8 -*-

from Jeu import JeuFactory
from Joueur import Joueur
from twisted.web.static import File
from twisted.web.resource import Resource
from websocket import *
import webbrowser #TESTING purpose
import cgi


class GamePage(Resource):
    def render_GET(self, request):
        return '<a href="index.html">Aller a l\'accueil du jeu</a>'

    def render_POST(self, request):
        pageFile = open("../ClientPR/pongroulette.html")
        page = pageFile.read()
        page = page.replace("$PSEUDO$", cgi.escape(request.args["nomdujoueur"][0]))
        pageFile.close()        
        return page


if __name__ == "__main__":
    from twisted.internet import reactor

    #WebSocketSite = une factory !
    #Simple() est une ressource
    root = File("../ClientPR/")
    root.putChild("gamePage", GamePage())
    factory = JeuFactory(root)
    factory.addHandler('/game', Joueur)
    reactor.listenTCP(8080, factory)


    print "launching reactor"
    #webbrowser.open("http://localhost:8080/pongroulette.html")
    #webbrowser.open("http://localhost:8080/pongroulette.html")
    reactor.run()
    print "stop reactor"

