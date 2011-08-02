# -*- coding: utf-8 -*-
import random, math
import json
from twisted.internet import reactor, defer
import time

import RoomFactory

class Trajectory :
    """ This class calculates the ball trajectory. """
    
    RACKET_LEN = 20 # lenght (in  axis percentage) of a racket
    SPEED = 0.020 # speed of the ball
    HIGH_SPEED = 0.007 # high speed (case of acceleration)
    
    #Constant time which is used to know if the player's racket is moving
    #at the moment of collision
    DELAY_MOVEMENT_CONST = 0.1
    

    def __init__(self, room):

        self.room = room
        self.players = self.room.players
        self.delay = reactor.callLater(1 , self.generateTrajectory,(50,50), 0)
        self.speed = Trajectory.SPEED
        self.effect = 0
     
    def sendPoint(self, point,time):
        """
        This method sends to all the players information about the next movement of the ball.
        
        More precisely, it sends the coordinates of the next collision point and the time moment
        of this collision.
        """
        
        for client in self.room.getPlayers():
                message = { "msg" : "Trajectoire", "point" : (point, int(client.getHourClient() + time*1000))}
                json.encoder.FLOAT_REPR = lambda f: ("%.2f" % f)
                client.transport.write(json.dumps(message))

    def chooseTrajectory(self, start_point, angle):
        """
        This method allows to determine the next movement of the ball according to its current position
        and the angle of its last movement.
        
        """
        
        angle = angle%360
        player_axis = False
        bounce_on_racket = False
        
        if self.ball[0] <= 1.5: # axis 0
            self.speed = Trajectory.SPEED
            if self.players[0] != None:
                #there is a player on this axis
                player = self.players[0]
                player_axis = True
                
        elif self.ball[0] >= 98.5: # axis 1
            self.speed = Trajectory.SPEED
            if self.players[1] != None:
                #there is a player on this axis
                player = self.players[1]
                player_axis = True
                
        if player_axis:
            if (player.racket_position + Trajectory.RACKET_LEN / 2) > self.ball[1] and \
                    (player.racket_position - Trajectory.RACKET_LEN / 2) < self.ball[1]:
                #The ball has bounced over the racket
                bounce_on_racket = True

                #We check if the player is currently moving
                if time.time() - player.last_movement_time <= Trajectory.DELAY_MOVEMENT_CONST:
                    #Acceleration
                    self.speed = Trajectory.HIGH_SPEED
                    #We set the effect
                    if player.racket_position > player.previous_racket_position and (angle) > 0 and (angle) < 180:
                        self.effect = 2*angle
                    elif player.racket_position < player.previous_racket_position and (angle) > 180 and (angle) < 360:
                        self.effect = 2*angle
        
        if (not player_axis) or (bounce_on_racket) :
            #case of bounce over a racket, a corner or a wall
            if (self.ball[0] == 1.5 or self.ball[0] == 98.5 ) and (self.ball[1] == 1 or self.ball[1]==99 ):
                #the ball has hit a corner
                angle = 180 + angle
            elif self.ball[0] <= 1.5 or self.ball[0] >= 98.5:
                #case of bounce on a racket
                angle = 180 - angle + self.effect
            elif (self.ball[1] <= 1) or (self.ball[1] >= 99) :
                #case of bounce on a wall
                angle = 360 - angle
            #We are going to generate the new trajectory from the current ball point
            self.generateTrajectory(start_point, angle) # generation nouvelle trajectoire à partir du point courant
        else :
              #player has lost
              if self.players[player.axis ^ 1] != None: #player.axis ^ 1 stands for the other player of the room
                  self.players[player.axis ^ 1].win()
              player.lose()
              self.speed = Trajectory.SPEED
              self.delay = reactor.callLater(0.7, self.generateTrajectory, (50,50), 0)
              #self.genererTrajectoire((50,50),0) # generation nouvelle trajectoire à partir du point initial
        
    def generateTrajectory(self, start_point, start_angle):
        """
        This method allows to generate the new trajectory of the ball according to its start_point
        and its start_angle.
        """
        
        start_angle = start_angle%360
        self.effect = 0
        movement_duration = 0

        if start_point == (50,50):
            #case of a new ball located in the middle of the field (a player have just lost)
            
            #We randomly generate the first start_angle avoiding vertical and horizontal directions
            little_angle = random.random()*35
            dg = 180
            if random.random() > 0.5:
                dg = 0
            hb = -1
            if random.random() > 0.5:
                hb = 1
            start_angle = dg + hb*(little_angle+10)
            
        self.ball = list(start_point)
        
        # determination of the shortest length to face a wall 
        u = (1.5 - self.ball[0]) / math.cos(math.radians(start_angle))
        if u<=0:
            u = (98.5 - self.ball[0]) / math.cos(math.radians(start_angle))      
        v = (self.ball[1] - 1) / math.sin(math.radians(start_angle))
        if v<=0:
            v = (self.ball[1] - 99) / math.sin(math.radians(start_angle))
        u = min(u,v)
        # result
        self.ball[0] = round(self.ball[0] + u*math.cos(math.radians(start_angle)),2)
        self.ball[1] = round(self.ball[1] - u*math.sin(math.radians(start_angle)),2)
        
        #We set the movement_duration multiplying the norm of movement vector by the speed
        movement_duration = u * self.speed
        
        collision_point = (self.ball[0], self.ball[1])
        
        #We sent this collision_point and the time before the collision happens. 
        #We send these information to all the players.
        self.sendPoint(collision_point,movement_duration)
        
        #We will call self.chooseTrajectory method when the collision happens
        self.delay = reactor.callLater(movement_duration, self.chooseTrajectory, collision_point, start_angle)
        
    def stop(self):
            self.delay.cancel()
   
