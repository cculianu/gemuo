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

import uo.packets as p
from gemuo.engine import Engine

class Login(Engine):
    def __init__(self, client, username, password, character):
        Engine.__init__(self, client)

        self._username = username
        self._password = password
        self._character = character

        self._client.send(p.AccountLogin(username, password))

    def on_packet(self, packet):
        if isinstance(packet, p.ServerList):
            self._client.send(p.PlayServer(0))
        elif isinstance(packet, p.Relay):
            # connect to the game server
            self._client.relay_to(packet.ip, packet.port, packet.auth_id)
            self._client.send(p.GameLogin(self._username, self._password,
                                          packet.auth_id))
        elif isinstance(packet, p.CharacterList):
            character = packet.find(self._character)
            if character:
                self._client.send(p.PlayCharacter(character.slot))
                self._client.send(p.ClientVersion('5.0.8.3'))
            else:
                self._failure("No such character")
        elif isinstance(packet, p.LoginComplete):
            self._success()
