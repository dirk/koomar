from koomar import Koomar

server = "irc.freenode.net"
channel = "whatspop"
nickname = "koomar"
port = 6667
command = "koomar"
# Used to send admin commands to koomar
password = "test"

quotes = ["Stop exploding, you cowards!", "Take a dip!"]
sender_exceptions = ['NickServ', 'freenode-connect']

koomar = Koomar(server, channel, nickname, password, port, command)
def core_parser(koomar, message):
    command = message.command(koomar.command)
    if command.__str__() == 'disconnect':
        if not message.argv(koomar.command) == koomar.password:
            if message.is_public():
                koomar.send_message('Incorrect password.')
            else:
                koomar.send_private_message("Dear %s, you gave an invalid password." % message.sender, message.sender)
            return True
        else:
            return 'disconnect'
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
    return False
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
    return False
koomar.add_function([core_parser, quote_parser, help_parser])
koomar.connect()