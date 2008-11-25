# koomar is a simple IRC bot written for fun.
# Grab your updates from: http://github.com/anandkunal/koomar/
# Peep the IRC RFC: http://www.irchelp.org/irchelp/rfc/rfc.html

#import datetime
import random
import socket
#import re
#import time

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
sender_exceptions = ['NickServ', 'freenode-connect']

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
                    if not response == 'disconnect':
                        responses.append({'function': function, 'response': response})
                    elif response == 'disconnect':
                        # If the function returns False, it is telling koomar to kill itself.
                        self.send_message("%s is disconnecting..." % self.nickname)
                        self.disconnect()
                        return
                # Checks to see if at least one of the parsers responded with either true or a string.
                def check(r):
                    # The old algorithm, I'm keeping it here just for good times' sake.
                    #(r['response'] == True or (not type(r['response']) == bool and r['response'].isalnum()))
                    if r == True or type(r) == str: return True
                    return False
                if not [check(r['response']) for r in responses].__contains__(True):
                    # and...
                    if message.is_command(self.command, sender_exceptions):
                        if message.is_public():
                            self.send_message("I don't know that command!")
                        else:
                            self.send_private_message("I don't know that command!", message.sender)
    def disconnect(self):
        self.irc.close()
    def send_message(self, message):
        self.irc.send("PRIVMSG #%s :%s\r\n" % (self.channel, message))
    def send_private_message(self, message, recipient):
        self.irc.send("PRIVMSG %s :%s\r\n" % (recipient, message))