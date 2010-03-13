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
from gemuo.timer import TimerEvent

class Guards(Engine, TimerEvent):
    """This engine calls the guards automatically.  This is useful
    when those annoying in-town PKs attack."""

    def __init__(self, client):
        Engine.__init__(self, client)
        TimerEvent.__init__(self, client)

        self.queued = False

    def call_guards(self):
        self._client.send(p.TalkAscii(type=0, hue=0, font=1, text='Guards! Help me!'))

    def tick(self):
        self.queued = False
        # cry for help again
        self.call_guards()

    def call_guards_twice(self):
        self.call_guards()
        if self.queued:
            self._unschedule()
        self._schedule(2)
        self.queued = True

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
