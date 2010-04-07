#
#  GemUO
#
#  (c) 2005-2010 Max Kellermann <max@duempel.org>
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; version 2 of the License.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#

from twisted.internet import reactor
from twisted.internet.protocol import ClientFactory
from twisted.words.protocols import irc
import uo.packets as p
from gemuo.engine import Engine

class IRCClient(irc.IRCClient):
    def signedOn(self):
        self.factory.irc = self
        self.join(self.factory.channel)

class IRCBot(Engine, ClientFactory):
    protocol = IRCClient

    def __init__(self, client, server, port, channel):
        Engine.__init__(self, client)

        self.channel = channel
        self.irc = None

        d = reactor.connectTCP(server, port, self)

    def on_packet(self, packet):
        if self.irc is None: return

        if isinstance(packet, p.AsciiMessage) and packet.type != 0x06 and \
           len(packet.text) > 0 and \
           (packet.text[0] != '[' or packet.text[-1] != ']'):
            msg = "<%s> %s" % (packet.name, packet.text)
            self.irc.msg(self.channel, msg)
