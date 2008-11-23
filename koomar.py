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
                responses = []
                # Stubbing out functionality for custom functions. Eventually the big block below will be gone.
                for function in flatten(self.functions):
                    try:
                        responses.append(function(self, line))
                    except IndexError:
                        # I put this in here just to be safe. (Dirk)
                        pass
                # Standard control library
                try:
                    message = Message(line)
                except IndexError:
                    pass
                line = line.strip().split()
                if line[0] == "PING":
                    self.irc.send("PONG %s\r\n" % line[1])
                else:
                    try:
                        # Disconnect functionality (revisited)
                        command = message.command(self.command)
                        if command.__str__() == 'disconnect':
                            if not message.argv(self.command) == self.password:
                                if message.is_public():
                                    koomar.send_message('Incorrect password.')
                                else:
                                    koomar.send_private_message("Dear %s, you gave an invalid password." % message.sender, message.sender)
                            else:
                                koomar.send_message('Correct password. Disconnecting...')
                                self.disconnect()
                                return
                        if line[3] == ":%s" % (self.command):
                            if len(line) <= 4:
                                self.send_message("Type `%s quote`" % (self.command))
                            else:
                                pass
                                #if line[4] == "disconnect":
                                #    if line[5] == self.password:
                                #        self.disconnect()
                                #        return
                                #    else:
                                #        if not line[2].startswith('#'):
                                #            matches = re.match(':([A-Za-z0-9_-]+)!', line[0])
                                #            sender = matches.groups()[0]
                                #            self.send_private_message("Dear %s, you gave an invalid password." % sender, sender)
                                #        else:
                                #            self.send_message("Invalid password.")
                            #if not responses.__contains__(True):
                                #self.send_message("I don't know that command!")
                    except IndexError:
                        pass # Each line may not be a conversation                    
    def disconnect(self):
        self.irc.close()
    def send_message(self, message):
        self.irc.send("PRIVMSG #%s :%s\r\n" % (self.channel, message))
    def send_private_message(self, message, recipient):
        self.irc.send("PRIVMSG %s :%s\r\n" % (recipient, message))
        
koomar = Koomar(server, channel, nickname, password, port, command)
def quote_parser(koomar, line):
    message = Message(line)
    command = message.command(koomar.command)
    if command == 'quote':
        rand = random.randint(0, len(quotes)-1)
        quote = quotes[rand]
        if message.is_public():
            koomar.send_message("\"%s\"" % quote)
        else:
            koomar.send_private_message("\"%s\"" % quote, message.sender)
        return True
def help_parser(koomar, line):
    message = Message(line)
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
koomar.add_function([quote_parser, help_parser])
koomar.connect()



