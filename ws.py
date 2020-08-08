
import asyncio
import websockets
import json
import socket
import threading
import string
import random
from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket


state = {
    "websocket": None
}

class ConnectionHandler (WebSocket):
    clients = []

    def __init__(self, server, sock, address):
        super().__init__( server, sock, address )
        state["websocket"] = self

    def broadcast ( self, msg ):
        for client in ConnectionHandler.clients:
            client.sendMessage( msg )
                
    def handleMessage(self ):
        print("message recieved")
        for client in ConnectionHandler.clients:
            if client != self:
                client.sendMessage(self.address[0] + u' - ' + self.data)

    def handleConnected(self):
        print(self.address, 'connected')
        for client in ConnectionHandler.clients:
            client.sendMessage(self.address[0] + u' - connected')
        ConnectionHandler.clients.append(self)

    def handleClose(self):
        ConnectionHandler.clients.remove(self)
        print(self.address, 'closed')
        for client in ConnectionHandler.clients:
            client.sendMessage(self.address[0] + u' - disconnected')

class WS:
    server_started = False
    server = None
    session_id = None

    def randomword(self, length):
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(length))

    def start( self, host="localhost", port=9900 ):
        print(f"starting websockets server at {host}:{port} ...")
        if WS.server_started:
            print("server already running. Refusing")
            return False

        if WS.session_id == None:
            WS.session_id = self.randomword(32)

        WS.server_started = True
        t1 = threading.Thread(target=self.run_server, args=( host, str(port) ) )
        t1.daemon = True
        t1.start()

        # self.run_server( host, port )

    def run_server ( self, host, port ):
        ""
        print(int(port))
        self.server = SimpleWebSocketServer( host, int(port), ConnectionHandler )
        self.server.serveforever()

    def emit ( self, event_name, payload={} ):
        for ws in ConnectionHandler.clients:
            try: ws.broadcast( json.dumps( {
                "session_id": WS.session_id,
                "event": event_name,
                "data": payload
            } ) )
            except Exception as e:
                print(f"ws: error while emitting event over websockets: {str(e)}")
     

    def broadcast ( self, data ):
        for ws in ConnectionHandler.clients:
            try: 
                data["session_id"] = WS.session_id
                ws.broadcast( json.dumps( data ) )
            except Exception as e:
                print(f"ws: error while broadcasting data over websockets: {str(e)}")

            

            

