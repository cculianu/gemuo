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

from twisted.internet import defer
from uo.skills import SKILL_TAILORING
import uo.packets as p
from uo.entity import *
from gemuo.engine import Engine
from gemuo.engine.menu import MenuResponse
from gemuo.defer import deferred_find_item_in_backpack, deferred_skill

def tailoring_target(skill):
    if skill < 475:
        return ('Shirts', 'fancy dress')
    if skill < 560:
        return ('Shirts', 'cloak')
    if skill < 680:
        return ('Shirts', 'robe')
    # XXX implement more
    return None

class Tailoring(Engine):
    def __init__(self, client):
        Engine.__init__(self, client)

        d = deferred_find_item_in_backpack(client, lambda x: x.item_id in ITEMS_TAILORING_TOOLS)
        d.addCallbacks(self._found_tool, self._failure)

    def _found_tool(self, result):
        self.tool = result
        d = deferred_find_item_in_backpack(self._client,
                                           lambda x: x.item_id in ITEMS_CLOTH)
        d.addCallbacks(self._found_cloth, self._failure)

    def _found_cloth(self, result):
        self.cloth = result
        d = deferred_skill(self._client, SKILL_TAILORING)
        d.addCallbacks(self._got_skill, self._failure)

    def _got_skill(self, result):
        target = tailoring_target(result.value)
        if target is None:
            print "No tailoring target"
            self._failure()
            return

        client = self._client
        client.send(p.Use(self.tool.serial))

        d = MenuResponse(client, target).deferred
        d.addCallbacks(self._success, self._success)

    def _on_target_request(self, allow_ground, target_id, flags):
        self._client.send(p.TargetResponse(0, target_id, flags, self.cloth.serial,
                                           0xffff, 0xffff, 0xffff, 0))

    def on_packet(self, packet):
        if isinstance(packet, p.TargetRequest):
            self._on_target_request(packet.allow_ground, packet.target_id,
                                    packet.flags)
