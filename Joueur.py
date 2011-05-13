# -*- coding: utf-8 -*-

""" Un objet de cette classe sera créé pour chaque joueur,
utile pour mémoriser ses points/pseudo etc, son objet WebSocketHandler (histoire
de pouvoir communiquer avec le joueur)... """

from websocket import *
from twisted.internet import task
import json
import time

class Joueur(WebSocketHandler):
    TIMEOUT = 1000000 #durée maximum de présence sans mouvement
    
    
    def __init__(self, transport):
        WebSocketHandler.__init__(self, transport)
        #score du joueur
        self.score = 0
        #pseudo du joueur
        self.name = ""
        #décalage de temps, en ms, entre heure du serveur et heure du client
        self.offset = 0
        #position (du centre) de la raquette sur son axe, entre 0 et 100
        self.raquette = 50
        
        
    def __del__(self):
        print 'Deleting handler'
        
    def reset(self):
        self.score = 0

    def sendAll(self, msg):
		for client in self.jeu.getJoueurs():
			client.send(msg)

    def send(self, msgJSON):
        self.transport.write(json.dumps(msgJSON))

    def calcOffset(self, hour):
        #OFFSET = REMOTE - LOCAL  ! en millisecondes
        #OFFSET négatif => client en retard sur le serveur, indique aussi la valeur du lag
        return - (time.time()*1000 - hour)
    
    def getHourClient(self):
        return (self.offset +  time.time()*1000)

    def isAlive(self):
        for client in self.jeu.getJoueurs():
			#si on n'a pas entendu parler du client depuis plus de TIMEOUT secondes
			if ((time.time()*1000 - client.lastTimeSeen) > (self.TIMEOUT*1000)):
				print "%s is offline (timeout) !" % client.name
				#TODO : à améliorer, appeler msgQuit() avec "Timeout" comme message de quit par ex
				client.transport.write("Dégage")
				client.transport.loseConnection()
                

    def setAlive(self):
        self.lastTimeSeen = time.time()*1000


    def perdre(self):
        self.score -= 1
        self.msgCollision(False)
        self.msgGstat()
        
    #def gagner(self):
        #self.score +=1
        

    def msgCollision(self, hit):
        msg = {}
        msg["msg"] = "Collision"
        if hit:
            msg["status"] = "HIT"
        else:
            msg["status"] = "MISS"
        self.sendAll(msg)
        

    def msgHello(self, msg):
        #TODO il est interdit de faire un Hello une deuxième fois quand le joueur est déjà connecté : à détecter !
        self.name = msg["pseudo"]
        self.offset = self.calcOffset(msg["time"])
        #quand un client se connecte, on le dit à tout le monde
        self.msgGstat()
        #quand un client se connecte, le serveur lui envoie un SyncJ pour qu'il connaisse les raquettes des autres
        self.msgSyncJ()

    def msgBouge(self, msg):
        #TODO déclencher erreur si n'est pas compris entre 0 et 100 : hack !
        self.raquette = msg["raquette"]
        self.offset = self.calcOffset(msg["time"])

    def msgSyncJ(self):
        msg = {}
        msg["msg"] = "SyncJ"
        msg["raquettes"] = {}
        for client in self.jeu.getJoueurs():
            msg["raquettes"][client.name] = client.raquette
        self.sendAll(msg)
        print "SyncJ envoyé : " + json.dumps(msg)

    def msgGstat(self):
        """ Envoi aux clients les informations sur tous les clients.
        
        Les informations de chaque joueur sont son pseudo et son score"""
        
        msg = {}
        msg["msg"] = "GStat"
        msg["players"] = {}
        for client in self.jeu.getJoueurs():
            msg["players"][client.name] = {}
            msg["players"][client.name]["points"] = client.score
            msg["players"][client.name]["axe"] = client.axe
        self.sendAll(msg)
        print "Gstat envoyé : " + json.dumps(msg)
            
    def decode(self, msg):
        #print "Message reçu : \n%s" % json.dumps(msg, indent = 2)
        if (msg["msg"] == "Hello"):
            self.msgHello(msg)
        elif (msg["msg"] == "Bouge"):
            self.msgBouge(msg)
            self.msgSyncJ()
        else:
            print "Message inconnu !"

        self.setAlive()
        #print "Attributs de self : %s" % vars(self)
            

    def frameReceived(self, frame):
        self.decode(json.loads(frame))
        
       
    def connectionMade(self):
        print 'Connected to client.'
        self.site.ajouterJoueurDansJeu(self)
        #heure, en ms, à laquelle on a entendu parler de ce client pour la dernière fois, utilisé pour détecter les timeouts
        self.lastTimeSeen = 0
        #on intialise cette valeur
        self.setAlive()
        #on va créer une boucle pour tester si le joueur est alive, avant on regarde si on n'a pas déjà créé cette boucle
        #en fait on la crée une seule fois, quand le premier client se connecte
        if (not hasattr(self.jeu, "pingLoop")):
            #on définit un appel en boucle de isAlive avec comme paramètre self
            self.jeu.pingLoop = task.LoopingCall(Joueur.isAlive, self)
            #elle se déclenche toutes les secondes
            self.jeu.pingLoop.start(1.0)
        

    def connectionLost(self, reason):
        print 'Lost connection.'
        self.jeu.enleverJoueur(self)
