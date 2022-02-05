import sys, socket
import threading
import traceback
import json
import datetime

class SocketError(OSError): # Socket Error, based on OSError
    def __init__(self, *args):            
        super().__init__(f"Client cannot connect. Recheck adress and ensure what the server is online.")

class SendError(SocketError): # Send Error, based on SendError
    def __init__(self, *args):
        super().__init__(f"Client cannot send message. Recheck adress and ensure what the server is online and you are connected.")

class V2Message: # API V2 Message class
    def __init__(self, bot, message):
        self.contents = message["msg"] # Get "msg" from message JSON 
        self.author = message["user"] # Get author from JSON
        self.time = datetime.datetime.now() # Set timestamp
        self.bot = bot # Set bot object, this is just for reply
        self.me = bot.username == self.author # Set if it is our message
        

    def reply(self, text: str):
        message = f"""To {self.author} message ({self.time}):
> {self.contents}
{text}""" # Reply text
        self.bot.send(message) # Send Reply

    def __str__(self):
        return json.dumps({"user": self.author, "msg": self.contents}, ensure_ascii=False) # Dump it as string
 
    def __bytes__(self):
        return str(self).encode() # dump as string and encode

class V1Message:
    def __init__(self, bot, message):
        self.contents = message # Message contents
        self.time = datetime.datetime.now() # Timestamp
        self.me = message.startswith(f"<{self.username}> ") # If message starts with our nickname, this is maybe our message.
        self.bot = bot # Bot

    def reply(self, text):
        message = f"""To message ({self.time}):
> {self.contents}
{text}""" # Reply text
        self.bot.send(message) # Send reply

    def __str__(self):# Return contents as string
        return self.contents

    def __bytes__(self):
        return self.contents.encode() # Encode contents


class RequestV2Message:
    def __init__(self, message):
        self.contents = message["msg"] # Get "msg" from unsended message
        self.author = message["user"] # Get author, but as always - this is our bot.

    def __str__(self): # dump message as string
        return json.dumps({"user": self.author, "msg": self.contents}, ensure_ascii=False)

    def __bytes__(self):
        return str(self).encode() # dump message as bytes

class RequestV1Message:
    def __init__(self, message):
        self.contents = message # here we can see only contents

    def __str__(self):
        return self.contents # Return contents of message

    def __bytes__(self):
        return self.contents.encode() # encode contents of message and return this

class AnonClient:
    _VERSION = "0.0.3" # The version of client
    
    def __init__(self, ip, port, name): # So, ip of server, port and bot name
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Create socket object
        self.ip = ip # Set up IP and port
        self.port = port

        self.version = 2 # API 2 by default

        self.username = name # Username of bot
        self.v1_client = "V1-Package" # Name of V1 Package, if got by V2-request
        

    def connect(self):
        try:
            self.socket.connect((self.ip, self.port)) # Connect to IP
        except:
            raise SocketError() # Raise socket error if cannot connect

        self.request = threading.Thread(target=self.message_request, args=(), daemon=True) # Create Thread to get messages
        self.request.start() # Start it

        try:
            self.on_connect() # Execute code of on_connect function
        except:
            raise RuntimeError("Unknown error in on_connect execution.") # Raise error if error in on_connect
        
        try:
            while True:
                pass # Because of daemon, bot will exit if no code is running in main thread
        except:
            pass 
        # If Ctrl + C or smth error will be called, the bot will stop
        self.close()

    def close(self):
        try:
            self.on_disconnect() # Execute on_disconnect
        except:
            raise RuntimeError("Unknown error in on_disconnect execution.") 
        
        #self.request.terminate() # this is for multiprocessing.Process, but we using Thread from threading
        self.socket.close() # Close socket

    def v1_send(self, text: str, on_send): # Send message using V1 code
        try:
            on_send(RequestV1Message(text)) # execute on_send with Object of API1 unsent message 
        except:
            raise RuntimeError("Unknown error in on_send execution.")

        text = f"<{self.username}> " + text # Add name to message
        message = text.encode() # Encode it

        self.socket.send(message) # Send it to socket

    def v2_send(self, text: str, on_send):
        message = {"user": self.username, "msg": text} # Create message JSON
        try:
            on_send(RequestV2Message(message)) # Execute on_send function with Object of API2 unsent message
        except:
            raise RuntimeError("Unknown error in on_send execution.")

        message = json.dumps(message, ensure_ascii=False).encode() # Dump it with option ensure_ascii=False, because we need UTF-8, and not ASCII text.

        self.socket.send(message) # Send it to socket

    def send(self, text): # The basic send function
        try:
            if self.version == 1: # If preferred version API1...
                self.v1_send(text, self.on_send) # ...Send it using API 1 send

            if self.version == 2: # And if API2...
                self.v2_send(text, self.on_send) # ... so api2 send comes in
        except:
            raise SendError() # If error in sending, raise error

    def v1_request(self, on_message): # Request message
        while True:
            if self.socket.fileno() == -1: break # If socket closed, break the cycle
            
            try:
                message = self.socket.recv(2048) # Try to recieve message
            except:
                break # If error, just break.

            if not message:
                break # If message is None, break
            
            try:
                message = message.decode() # Try to parse message                
            except: # If message is undecodable, just call an error.
                message = "Message was recieved, but the contents cannot be decoded :("

            try:
                on_message(V1Message(self, message)) # Call on_message event if message is decoded.
            except:
                raise RuntimeError("Unknown error in on_message execution.")

    def v2_request(self, on_message):
        while True:
            if self.socket.fileno() == -1: break # If socket closed, break.
            
            try:
                message = self.socket.recv(2048) # Recieve message
            except:
                pass

            if not message:
                pass
            
            try:
                message = message.decode() # Decode message
                
                try:
                    message = json.loads(message.strip()) # Try to load message as JSON object
                except:
                    message = {"user": self.self.v1_client, "msg": message} # If error - maybe this is an API1 message.
                    
            except:
                message = {"user": "[CLIENT]", "msg": "Message was recieved, but the contents cannot be decoded :("} # But if there is still an error
            try:
                on_message(V2Message(self, message)) # Execute on message with API2 Message
            except:
                raise RuntimeError("Unknown error in on_message execution.")
                

    def message_request(self): # Basic message request thread
        while True:
            try:
                if self.version == 1: # If preferred version is API1, try to get messages in API 1
                    self.v1_request(self.on_message)

                elif self.version == 2: # If API2 -> API2 Request
                    self.v2_request(self.on_message)
            except:
                raise SocketError() # If error in requesting, raise Socket Error.

    # Placeholders for all functions:
    def on_message(self, *args, **kwargs): 
        pass

    def on_send(self, *args, **kwargs):
        pass

    def on_connect(self, *args, **kwargs):
        pass

    def on_disconnect(self, *args, **kwargs):
        pass


    # Functions for decorators.
    # If decorator setted up, set passed function to replace placeholders.
    def event_message(self, func):
        self.on_message = func
        return func

    def event_send(self, func):
        self.on_send = func
        return func
        
    def event_connect(self, func):
        self.on_connect = func
        return func
    
    def event_disconnect(self, func):
        self.on_disconnect = func
        return func
