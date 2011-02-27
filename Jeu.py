# -*- coding: utf-8 -*-

from websocket import *
from Trajectoire import Trajectoire

""" Cette classe va gérer le jeu, càd conserver la liste des joueurs,
gérer leurs points, et déclencher des calculs de trajectoire """


class Jeu(WebSocketSite):
    
    joueurs = []
    trajectoire = Trajectoire()
