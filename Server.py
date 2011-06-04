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
        page = """<!DOCTYPE html>
        <html>
          <head>
            <title>Pongroulette</title>
            <meta charset="utf-8" />
            <link href="pongroulette.css" rel="stylesheet" />
          </head>
          <body onload="setTimeout('window.location.reload()', 3000)">        
            <div id="statsPage">
              <h2>Statistiques</h2>
        """
        page += "<p class=\"contnbsalle\">Nombre de salles : <strong>" + str(len(self.factory.jeux)) + "</strong></p>"
        for jeu in self.factory.jeux:
            page += "<table><tr><th class=\"colpseudo\">Pseudo</th><th class=\"colscore\">Score</th><th class=\"colip\">IP</th></tr>\n"
            for joueur in jeu.getJoueurs():
                ip = str(joueur.transport.getPeer().host)
                page += "<tr>\n    <td>" + joueur.name +\
                        "</td>\n    <td>" + str(joueur.score) +\
                        "</td>\n    <td><a target=\"_blank\" href=\"http://www.dnswatch.info/dns/dnslookup?la=en&host=" + ip + "\">" + ip + "</a>" +\
                        "</td>\n</tr>\n"
            page += "</table>\n\n"            
        page += """
            </div>
          </body>
        </html>"""
        return str(page)

class GamePage(Resource):
    def render_GET(self, request):
        return """<!DOCTYPE html>
        <html>
          <head>
            <title>Redirection en cours...</title>
            <meta charset="utf-8" />
            <link href="pongroulette.css" rel="stylesheet" />
            <meta http-equiv="refresh" content="1; ./" />
          </head>
          <body>
            <p style="text-align: center; margin-top: 200px;">
              <a href="./" style="color: white;">Redirection vers l'accueil du jeu...</a>
            </p>
          </body>
        </head>
        """

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

    webbrowser.open("http://localhost:8080/pongroulette.html")
    webbrowser.open("http://localhost:8080/pongroulette.html")
    webbrowser.open("http://localhost:8080/pongroulette.html")

    reactor.run()
    print "stop reactor"

