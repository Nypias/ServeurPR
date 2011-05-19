# -*- coding: utf-8 -*-

from Jeu import JeuFactory
from Joueur import Joueur
from twisted.web.static import File
from twisted.web.resource import Resource
from websocket import *
import webbrowser #TESTING purpose
import cgi


class StatsPage(Resource):
    def __init__(self, factory):
        self.factory = factory
    
    def render_GET(self, request):
        page = """<style type='text/css'>
            table {
            border: medium solid #000000;
            border-collapse : collapse;
            width: 50%;
            }
            td, th {
            border: thin solid #6495ed;
            width: 50%;
            }
            th {
            background-color : grey;
            }
        </style>"""
        page += "<p>Nombre de salles : " + str(len(self.factory.jeux)) + "</p>"
        for jeu in self.factory.jeux:
            page += "<table><tr><th>Pseudo</th><th>Score</th><th>IP</th></tr>\n"
            for joueur in jeu.getJoueurs():
                ip = str(joueur.transport.getPeer().host)
                page += "<tr>\n    <td>" + joueur.name +\
                        "</td>\n    <td>" + str(joueur.score) +\
                        "</td>\n    <td><a target=_blank href=\"http://www.dnswatch.info/dns/dnslookup?la=en&host=" + ip + "\">" + ip + "</a>" +\
                        "</td>\n</tr>\n"
            page += "</table>\n\n<br />"
        return str(page)

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
    root.putChild("stats", StatsPage(factory))
    factory.addHandler('/game', Joueur)
    reactor.listenTCP(8080, factory)


    print "launching reactor"
    #webbrowser.open("http://localhost:8080/pongroulette.html")
    #webbrowser.open("http://localhost:8080/pongroulette.html")
    reactor.run()
    print "stop reactor"

