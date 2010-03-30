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
import uo.packets as p
from gemuo.engine import Engine

class Guards(Engine):
    """This engine calls the guards automatically.  This is useful
    when those annoying in-town PKs attack."""

    def __init__(self, client):
        Engine.__init__(self, client)

        self.call_id = None

    def call_guards(self):
        print "Calling guards"
        self._client.send(p.TalkUnicode(type=0xc0, hue=0, font=1, text='.', keyword=0x07))

    def call_guards_again(self):
        self.call_id = None
        # cry for help again
        self.call_guards()

    def call_guards_twice(self):
        self.call_guards()
        if self.call_id is not None:
            self.call_id.cancel()
        self.call_id = reactor.callLater(2, self.call_guards_again)

    def on_message(self, serial, name, text):
        if name == '' and text in ('1', '2', '3'):
            self.call_guards_twice()

    def on_combatant(self, serial):
        if serial != 0:
            self.call_guards()

    def on_swing(self, flag, attacker_serial, defender_serial):
        player = self._client.world.player
        if defender_serial == player.serial or attacker_serial == player.serial:
            self.call_guards()

    def on_packet(self, packet):
        if isinstance(packet, p.AsciiMessage):
            self.on_message(packet.serial, packet.name, packet.text)
        elif isinstance(packet, p.ChangeCombatant):
            self.on_combatant(packet.serial)
        elif isinstance(packet, p.Swing):
            self.on_swing(packet.flag, packet.attacker_serial, packet.defender_serial)
