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

from uo.skills import SKILL_TAILORING
import uo.packets as p
from gemuo.engine import Engine
from gemuo.engine.util import FinishCallback
from gemuo.engine.menu import MenuResponse

def tailoring_target(skill):
    if skill < 500:
        return ('Shirts', 'fancy dress')
    # XXX implement more
    return None

class Tailoring(Engine):
    def __init__(self, client):
        Engine.__init__(self, client)

        tool = client.world.find_item_in(client.world.backpack(), lambda x: x.item_id == 0xf9d)
        if tool is None:
            print "No tool"
            self._failure()
            return

        self.cloth = client.world.find_item_in(client.world.backpack(), lambda x: x.item_id == 0x1766)
        if self.cloth is None:
            print "No cloth"
            self._failure()
            return

        skills = client.world.player.skills
        if skills is None or SKILL_TAILORING not in skills:
            print "No tailoring skill"
            self._failure()
            return

        target = tailoring_target(skills[SKILL_TAILORING].value)
        if target is None:
            print "No tailoring target"
            self._failure()
            return

        client.send(p.Use(tool.serial))

        FinishCallback(client, MenuResponse(client, target),
                       self._responded)

    def _responded(self, success):
        if success:
            self._success()
        else:
            #self._failure()
            self._success()

    def _on_target_request(self, allow_ground, target_id, flags):
        self._client.send(p.TargetResponse(0, target_id, flags, self.cloth.serial,
                                           0xffff, 0xffff, 0xffff, 0))

    def on_packet(self, packet):
        if isinstance(packet, p.TargetRequest):
            self._on_target_request(packet.allow_ground, packet.target_id,
                                    packet.flags)
