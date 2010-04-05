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

import os
from twisted.internet import reactor, defer
from twisted.internet.protocol import ClientCreator
from uo.client import UOProtocol
import uo.packets as p
from gemuo.engine import Engine

class Client:
    def __init__(self, client):
        client.handler = self._handle_packet

        self._client = client
        self._engines = []

    def relay_to(self, host, port, auth_id):
        """Connect to the game server, and switches compression on."""
        self._connect(host, port, seed=auth_id, decompress=True)

    def add_engine(self, engine):
        self._engines.append(engine)

    def remove_engine(self, engine):
        self._engines.remove(engine)

    def signal(self, name, *args, **keywords):
        for engine in self._engines:
            if hasattr(engine, name):
                getattr(engine, name)(*args, **keywords)

    def _handle_packet(self, packet):
        if packet.cmd in p.parsers:
            packet = p.parsers[packet.cmd](packet)
            self.signal('on_packet', packet)
        else:
            print "No parser for packet:", hex(packet.cmd)

    def once(self, timeout=1):
        reactor.iterate(timeout)
        self._tick()
        return False

    def process(self, timeout=1):
        """Process all pending events.  The timeout is only valid for
        the first packet."""

        if not self.once(timeout):
            return False

        while self.once(0):
            pass
        return True

    def run(self):
        while len(self._engines) > 0:
            self.once()

    def until(self, finished):
        while not finished():
            self.once()

    def send(self, data):
        self._client.send(data)

def connect(host, port, *args, **keywords):
    d = defer.Deferred()

    c = ClientCreator(reactor, UOProtocol, *args, **keywords)
    e = c.connectTCP(host, port)
    e.addCallback(lambda client: d.callback(Client(client)))
    e.addErrback(lambda f: d.errback(f))

    return d

class GameLogin(Engine):
    def __init__(self, client, username, password, auth_id, character):
        Engine.__init__(self, client)

        client.send(p.GameLogin(username, password, auth_id))

    def on_packet(self, packet):
        if isinstance(packet, p.ServerList):
            self._failure("Refusing to use second server list")
        elif isinstance(packet, p.Relay):
            self._failure("Refusing to follow second relay")
        elif isinstance(packet, p.CharacterList):
            character = packet.find(character)
            if character:
                self._client.send(p.PlayCharacter(character.slot))
                self._client.send(p.ClientVersion('5.0.8.3'))
            else:
                self._failure("No such character")
        elif isinstance(packet, p.LoginComplete):
            self._success(self._client)

class AccountLogin(Engine):
    def __init__(self, client, username, password, character, connect=connect):
        Engine.__init__(self, client)

        self.username = username
        self.password = password
        self.character = character
        self.connect = connect

        client.send(p.AccountLogin(username, password))

    def _on_connect(self, client, auth_id):
        d = GameLogin(client, self.username, self.password,
                      auth_id, self.character).deferred
        d.addCallback(lambda client: self._success(client))
        d.addErrback(lambda f: self._failure(f))

    def on_packet(self, packet):
        if isinstance(packet, p.ServerList):
            self._client.send(p.PlayServer(0))
        elif isinstance(packet, p.Relay):
            # connect to the game server
            d = self.connect(packet.ip, packet.port, seed=packet.auth_id, decompress=True)
            d.addCallback(lambda client: self._on_connect(client, packet.auth_id))
            d.addErrback(lambda f: self._failure(f))
            self._client.send(p.GameLogin(self.username, self.password,
                                          packet.auth_id))
        elif isinstance(packet, p.CharacterList):
            character = packet.find(self.character)
            if character:
                self._client.send(p.PlayCharacter(character.slot))
                self._client.send(p.ClientVersion('5.0.8.3'))
            else:
                self._failure("No such character")
        elif isinstance(packet, p.LoginComplete):
            self._success(self._client)

def login(host, port, username, password, character, connect=connect):
    d = defer.Deferred()

    def on_connect(client):
        e = AccountLogin(client, username, password, character, connect).deferred
        e.addCallback(lambda client: d.callback(client))
        e.addErrback(lambda f: d.errback(f))

    e = connect(host, port)
    e.addCallback(on_connect)
    e.addErrback(lambda f: d.errback(f))
    return d
