# anonchat-api.py
Python implementation of anonchat API

## Installation
```bash
$ pip install anonchat
```

## Building
**You need to sync up this repo using git: https://github.com/anonchat-org/anonchat-api.py**

First of all, install 'build' package
```bash
$ py -m pip install --upgrade build
```

Then, build this package. You need to be in root of directory, not in src and etc.
```bash
$ py -m build
```

It will give you two packages:
```
dist/
  anonchat-0.0.1-py3-none-any.whl
  anonchat-0.0.1.tar.gz
```

Install builded package:
```
pip install ./dist/anonchat-0.0.1-py3-none-any.whl
```

## Usage
Import all from anonchat.client

```py
from anonchat.client import *
```

You can check version, if you want.
```py
print(AnonClient._VERSION)
```

Now, lets create your client.

### Basic events and connection
> AnonClient(ip: str, - The IP of the server
>			 port: int, - Port of the server 
>			 name: str - Bot name
>			)

```py
bot = AnonClient("IP", port, "ExampleNickname") # Change this to your info!
```

By default, bot uses API v2. API v1 is supported, but not tested.
To change API version, after bot creation, change this:
```py
bot.version = 2 # Set API 2. This is set by default.
# And to API 1
bot.version = 1 # Set deprecated API 1.
```

Let's send message about bot connection. You need this decorator:

>  @bot.event_connect

```py
@bot.event_connect
def on_connect():
	print(f"Bot {bot.username} connected!")
```

You can send messages with function bot.send
> bot.send(
>		   text: str
>		  )

Add this to our on_connect function!
```py
@bot.event_connect
def on_connect():
	print(f"Bot {bot.username} connected!")
	bot.send("I am connected!")
```
This function is called when bot is fully connected.

If you want to send message on bot disconnect, you can also add this to your code.

> @bot.event_disconnect

```py
@bot.event_disconnect
def on_disconnect():
	bot.send("See you next time!")
	print("Bot disconnecting...")
```
This function will be called before bot disconnect, so you can send messages.

Thats all. Lets connect our bot. Write this function after ALL code. Or, it won't be called.
```py
bot.connect()
```
So, our bot is working. It can be disconnected using another function. <br/>
It it normal, if you get an error here. This is because of closed socket.
```py
bot.close()
```
Lets go to another part.

### Message processing

If you want to get all messages, set your custom message event function.
> @bot.event_message

```py
@bot.event_message
def on_message(message):
```

All messages, which passed to on_message, will be V1Message or V2Message class objects, depending on the selected API version

> V2Message
>	+ Variables:
>	- .contents: str - Message contents
>	- .author: str - Message author
>	- .time: datetime.now - Time, when message was recieved by client.
>	- .me: bool - Is this my message? But, this is not accurate, because anyone can set your name.
>	- .bot: class <AnonClient> - The bot object.
>	
>	+ Functions:
>	- .reply(text: str - Reply text
> 	  ) - Reply to message
>	
>	+ Can be converted to:
>	- bytes - Dumped Encoded JSON
>	- str - Dumped JSON

Message author is not availible on API1, so there is no .author

> V1Message
>	+ Variables:
>	- .contents: str - Message contents
>	- .time: datetime.now - Time, when message was recieved by client.
>   - .me: bool - Is this my message? But, this is not accurate, because anyone can set your name.
>	- .bot: class <AnonClient> - The bot object.
>	
>	+ Functions:
>	- .reply(text: str - Reply text
>		  ) - Reply to message
>	
>	+ Can be converted to:
>	- bytes - Encoded message.contents
>	- str - message.contents


If the server (as the server on Dart does) sends a message to a client with API 2 of API 1 standard, the client will automatically adapt it to API 2 and the one who sent the message will be named "V1-Package". Since the function which adjusts for API 2 is local, it is possible to change the name to something else:
```py
bot.v1_client = "V1MSG" # Or something else, if you like.
```
If the official Python server is used, the server will do it automatically by itself, with exactly the same name "V1-Package", it cannot be changed.

**Next code is only for API2.**

Lets write basic on_message function, which will be detecting, if there is 'Hello' at start, and if message is not from our bot.

```py
@bot.event_message
def on_message(message): 
	if message.contents.startswith("Hello") and not message.me: # If message has 'Hello' at start, and this is not our message.
		message.reply(f"Hello, dear {message.author}!") # Reply to message.
```

This function will be called all time when the message is recieved.

**API1/API2 Code**

If you want to do some processing before message sending, there is also a function.

> @bot.event_send

This function is called before message send, so it uses another objects.

> RequestV2Message
>	+ Variables:
>	- .contents: str - Message contents
>	- .author: str - Message author
>
>	+ Can be converted to:
>	- bytes - Dumped Encoded JSON
>	- str - Dumped JSON

> RequestV1Message
>	+ Variables:
>	- .contents: str - Message contents
>	
>	+ Can be converted to:
>	- bytes - Encoded message.contents
>	- str - message.contents

There is no .bot, .me, .time and .reply, because this message is not sent. Of course, it is our message.

And example code:
```py
@bot.event_send
def on_send(message):
	print(f"Bot will send message with text '{message.contents}'")
```
	
### Errors
There is three type of errors you can get.

> anonchat.SendError

You can get this while sending message in closed/disconnected socket.

> anonchat.SocketError

You can get this while trying to connect to bad server adress or offline server.

> RuntimeError

You can get this if there is an error in your code.

## Good luck!
Thats all you need to know.
This example can be found in examples dir
Good luck in writing bot/client for your server! 