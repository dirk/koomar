# koomar is a simple IRC bot written for fun.
# Grab your updates from: http://github.com/anandkunal/koomar/
# Peep the IRC RFC: http://www.irchelp.org/irchelp/rfc/rfc.html

import datetime
import random
import socket
import re

server = "irc.freenode.net"
channel = "whatspop"
nickname = "koomar"
port = 6667
command = "koomar"
# Used to send admin commands to koomar
password = "test"

quotes = ["Stop exploding, you cowards!", "Take a dip!"]

class Koomar:
    def __init__(self, server, channel, nickname, password, port, command):
        self.server = server
        self.channel = channel
        self.nickname = nickname
        self.password = password
        self.port = port
        self.command = command
        self.irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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
        
    def loop(self):
        while 1:
            self.buffer += self.irc.recv(4096)
            temp_buffer = self.buffer.split("\n")
            self.buffer = temp_buffer.pop()

            for line in temp_buffer:
                line = line.strip().split()
                if line[0] == "PING":
                    self.irc.send("PONG %s\r\n" % line[1])
                else:
                    try:
                        if line[3] == ":%s" % (self.command):
                            if len(line) <= 4:
                                self.send_message("Type `%s quote`" % (self.command))
                            else:
                                if line[4] == "quote":
                                    quote = random.randint(0, len(quotes)-1)
                                    self.send_message("\"%s\"" % (quotes[quote]))
                                elif line[4] == "disconnect":
                                    if line[5] == self.password:
                                        self.disconnect()
                                        return
                                    else:
                                        if not line[2].startswith('#'):
                                            matches = re.match(':([A-Za-z0-9_-]+)!', line[0])
                                            sender = matches.groups()[0]
                                            self.send_private_message("Dear %s, you gave an invalid password." % sender, sender)
                                        else:
                                            self.send_message("Invalid password.")
                                else:
                                    self.send_message("I don't know that command!")
                    except IndexError:
                        pass # Each line may not be a conversation                    
            
    def disconnect(self):
        self.irc.close()
    
    def send_message(self, message):
        self.irc.send("PRIVMSG #%s :%s\r\n" % (self.channel, message))
    def send_private_message(self, message, recipient):
        msg = "PRIVMSG %s :%s\r\n" % (recipient, message)
        #print msg
        self.irc.send(msg)
        
Koomar(server, channel, nickname, password, port, command)
