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

from uo.skills import SKILL_FLETCHING
from uo.entity import *
import uo.packets as p
from gemuo.engine import Engine
from gemuo.engine.util import FinishCallback, DelayedCallback, Fail
from gemuo.engine.menu import MenuResponse

class Fletching(Engine):
    def __init__(self, client, choice):
        Engine.__init__(self, client)

        self.tool = client.world.find_reachable_item(lambda x: x.item_id in ITEMS_FLETCHING_TOOLS)
        if self.tool is None:
            print "No tool"
            self._failure()
            return

        self.choice = choice

        self.wood = client.world.find_item_in(client.world.backpack(), lambda x: x.item_id in (ITEMS_LOGS + ITEMS_BOARDS))
        if self.wood is None:
            print "No wood"
            self._failure()
            return

        self.target_mutex = client.target_mutex
        self.target_locked = False

        self.target_mutex.get_target(self._target_ok, self._target_abort)

    def _target_ok(self):
        self.target_locked = True
        self._client.send(p.Use(self.tool.serial))

    def _target_abort(self):
        self._failure()

    def _on_target_request(self, allow_ground, target_id, flags):
        if not self.target_locked: return

        client = self._client
        client.send(p.TargetResponse(0, target_id, flags, self.wood.serial,
                                     0xffff, 0xffff, 0xffff, 0))
        self.target_mutex.put_target()
        FinishCallback(client, MenuResponse(client, self.choice),
                       self._responded)

    def on_packet(self, packet):
        if isinstance(packet, p.TargetRequest):
            self._on_target_request(packet.allow_ground, packet.target_id,
                                    packet.flags)

    def _responded(self, success):
        if success:
            DelayedCallback(self._client, 9, self._success)
        else:
            self._success()

def fletching_choice(skill):
    if skill < 300:
        return None
    if skill < 600:
        return ('Weapons', 'bow')
    if skill < 800:
        return ('Weapons', 'crossbow')
    if skill < 1000:
        return ('Weapons', 'heavy crossbow')
    return None

def TrainFletching(client):
    skills = client.world.player.skills
    if skills is None or SKILL_FLETCHING not in skills:
        print "No fletching skill"
        return Fail(client)

    choice = fletching_choice(skills[SKILL_FLETCHING].value)
    if choice is None:
        print "No fletching choice"
        return Fail(client)

    return Fletching(client, choice)
