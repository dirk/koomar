# koomar is a simple IRC bot written for fun.
# Grab your updates from: http://github.com/anandkunal/koomar/
# Peep the IRC RFC: http://www.irchelp.org/irchelp/rfc/rfc.html

import datetime
import random
import socket
import re
import time

import lib
from lib import Message, flatten

server = "irc.freenode.net"
channel = "whatspop"
nickname = "koomar"
port = 6667
command = "koomar"
# Used to send admin commands to koomar
password = "test"

quotes = ["Stop exploding, you cowards!", "Take a dip!"]

class Koomar:
    def __init__(self, server, channel, nickname, password, port, command, auto_connect = False):
        """Establish beginning variables and start the socket."""
        self.server = server
        self.channel = channel
        self.nickname = nickname
        self.password = password
        self.port = port
        self.command = command
        self.irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # List of functions to call when processing a post
        self.functions = []
        if auto_connect:
            self.connect()

    def __del__(self):
        self.disconnect()

    def connect(self):
        self.irc.connect((self.server, self.port))
        self.buffer = self.irc.recv(4096)
        self.irc.send("NICK %s\r\n" % self.nickname)
        self.irc.send("USER %s %s %s :%s\r\n" % \
            (self.nickname, self.nickname, self.nickname, self.nickname))
        self.irc.send("JOIN #%s\r\n" % self.channel)
        self.send_message("%s is in the house!" % (self.nickname))
        self.loop()
    def add_function(self, function):
        """Add a processing function."""
        self.functions.append(function)
    def loop(self):
        while 1:
            self.buffer += self.irc.recv(4096)
            temp_buffer = self.buffer.split("\n")
            self.buffer = temp_buffer.pop()

            for line in temp_buffer:
                # First make sure if its a PING request.
                parts = line.strip().split()
                if parts[0] == "PING":
                    self.irc.send("PONG %s\r\n" % parts[1])
                    continue
                try:
                    message = Message(line)
                except IndexError:
                    pass
                # Now move on to the main functionality.
                responses = []
                # Stubbing out functionality for custom functions. Eventually the big block below will be gone.
                for function in flatten(self.functions):
                    # Making it very verbose just to be safe.
                    response = function(self, message)
                    if not response == False:
                        responses.append(function)
                    else:
                        # If the function returns False, it is telling koomar to kill itself.
                        self.send_message("%s is disconnecting..." % self.nickname)
                        self.disconnect()
                        return
                # Standard control library
                if not responses.__contains__(True):
                    self.send_message("I don't know that command!")                   
    def disconnect(self):
        self.irc.close()
    def send_message(self, message):
        self.irc.send("PRIVMSG #%s :%s\r\n" % (self.channel, message))
    def send_private_message(self, message, recipient):
        self.irc.send("PRIVMSG %s :%s\r\n" % (recipient, message))
        
koomar = Koomar(server, channel, nickname, password, port, command)
def core_parser(koomar, message):
    command = message.command(koomar.command)
    if command.__str__() == 'disconnect':
        if not message.argv(koomar.command) == koomar.password:
            if message.is_public():
                koomar.send_message('Incorrect password.')
            else:
                koomar.send_private_message("Dear %s, you gave an invalid password." % message.sender, message.sender)
        else:
            return False
def quote_parser(koomar, message):
    command = message.command(koomar.command)
    if command == 'quote':
        rand = random.randint(0, len(quotes)-1)
        quote = quotes[rand]
        if message.is_public():
            koomar.send_message("\"%s\"" % quote)
        else:
            koomar.send_private_message("\"%s\"" % quote, message.sender)
        return True
def help_parser(koomar, message):
    command = message.command(koomar.command)
    help = \
"""Koomar is a currently in development IRC bot.
Type in 'koomar quote' to get a random Futurama quote."""
    if command == 'help':
        if message.is_public():
            for line in help.split('\n'):
                koomar.send_message(line)
        else:
            for line in help.split('\n'):
                koomar.send_private_message(line, message.sender)
        return True
koomar.add_function([core_parser, quote_parser, help_parser])
koomar.connect()



