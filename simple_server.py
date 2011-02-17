# -*- coding: utf-8 -*-
""" WebSocket test resource.

This code will run a websocket resource on 8080 and reachable at ws://localhost:8080/test.
For compatibility with web-socket-js (a fallback to Flash for browsers that do not yet support
WebSockets) a policy server will also start on port 843.
See: http://github.com/gimite/web-socket-js
"""

#from twisted.internet.protocol import Protocol, Factory
#from twisted.web import resource
from twisted.web.static import File
from twisted.web import server, resource
#from twisted.internet import task
import time


from websocket import *

clients = []

class EchoHandler(WebSocketHandler):
    def __init__(self, transport):
        WebSocketHandler.__init__(self, transport)

    def __del__(self):
        print 'Deleting handler'

    def frameReceived(self, frame):
        print "Received : \""+frame+"\""
        for client in clients:
            if client != self:
                client.transport.write(frame)

    def connectionMade(self):
        print 'Connected to client.'
        clients.append(self)

    def connectionLost(self, reason):
        print 'Lost connection.'
        clients.remove(self)

class Simple(resource.Resource):
    def render_GET(self, request):
        return "<html>Hello, world!</html>"

def ping():
    while True:
        time.sleep(1)
        for client in clients:
            client.transport.write("t'es là keupin ?")

if __name__ == "__main__":
    from twisted.internet import reactor

    # run our websocket server
    # serve index.html from the local directory
    root = File('.')
    site = WebSocketSite(server.Site(Simple()))
    site.addHandler('/test', EchoHandler)
    reactor.callInThread(ping)
    reactor.listenTCP(8080, site)

    print "launching reactor"
    reactor.run()
    print "stop reactor"

