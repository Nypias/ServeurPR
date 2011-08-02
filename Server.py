# -*- coding: utf-8 -*-

from RoomFactory import RoomFactory
from Player import Player
from twisted.web.static import File
from twisted.web.resource import Resource
from websocket import *
import webbrowser #TESTING purpose
import cgi


class StatsPage(Resource):
    """
    One has a statistics page at the url /stats where one can see all the connected olayers, the rooms and the scores.
    """
    def __init__(self, factory):
        self.factory = factory #factory = access to the play rooms
    
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
        for jeu in self.factory.jeux: #for each room
            page += "<table><tr><th class=\"colpseudo\">Pseudo</th><th class=\"colscore\">Score</th><th class=\"colip\">IP</th></tr>\n"
            for joueur in jeu.getJoueurs():
                ip = str(joueur.transport.getPeer().host) #player's IP
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
    """
    At the url /gamePage there is the HTML canvas and all the stuff needed to play.
    """

    def render_GET(self, request):
        #One should not access this page through a GET request, redirect to index
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
        #The index page make the client POST his pseudo here, one injects it into the gamePage
        pageFile = open("../ClientPR/pongroulette.html")
        page = pageFile.read()
        page = page.replace("$PSEUDO$", cgi.escape(request.args["nomdujoueur"][0]))
        pageFile.close()
        return page


if __name__ == "__main__":
    from twisted.internet import reactor

    root = File("../ClientPR/") #root of the webserver
    factory = RoomFactory(root) #factory handles websocket requests
    factory.addHandler('/game', Player)
    root.putChild("gamePage", GamePage())
    root.putChild("stats", StatsPage(factory))
    reactor.listenTCP(8080, factory)


    print "launching reactor"

    #For testing purpose we can automatically open a pair pages of the game in a browser
    #webbrowser.open("http://localhost:8080/")
    #webbrowser.open("http://localhost:8080/")

    reactor.run()
    print "stop reactor"

