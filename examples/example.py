from anonchat.client import *

bot = AnonClient("localhost", 6969, "ExampleBot")

@bot.event_message
def on_message(message):
    if message.contents.startswith("Hello") and not message.me:
        message.reply(f"Hello, dear {message.author}!")

@bot.event_send
def on_send(text):
    print(f"Bot sended message with text '{text.contents}'")
    
@bot.event_connect
def on_connect():
    bot.send("Hello World!")

@bot.event_disconnect
def on_disconnect():
    bot.send("See you next time!")

bot.connect()
