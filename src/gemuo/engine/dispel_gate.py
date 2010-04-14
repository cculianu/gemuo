#
#  GemUO
#
#  (c) 2005-2010 Max Kellermann <max@duempel.org>
#                Kai Sassmannshausen <kai@sassie.org>
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
from uo.spells import SPELL_DISPEL_FIELD
from gemuo.engine import Engine
from gemuo.target import Target
from uo.entity import ITEM_GATE

class DispelGate(Engine):
    """For death gates into houses. The Engines precasts Dispel Field on Vas Rel Por and targets the gate that appears."""

    def __init__(self, client):
        Engine.__init__(self, client)

    def on_packet(self, packet):
        if isinstance(packet, p.AsciiMessage):
            if "Vas Rel Por" in packet.text:
                self.cast_dispel_field()

    def cast_dispel_field(self):
        self._client.send(p.Cast(SPELL_DISPEL_FIELD))
        WaitAndSendTarget(self._client)


class WaitAndSendTarget(Engine):

    def __init__(self, client):
        Engine.__init__(self, client)
        self.target_request = None
        self.target = None

    def on_packet(self, packet):
        if isinstance(packet, p.TargetRequest):
            self.target_request = packet
        elif isinstance(packet, p.WorldItem):
            if self.target_request is not None:
                if packet.item_id == ITEM_GATE:
                    self.target = Target(packet.serial, packet.x, packet.y, packet.z, packet.item_id)
                    self._client.send(self.target.response(self.target_request.target_id, self.target_request.flags))
                    self._success()
