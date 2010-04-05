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
from uo.skills import SKILL_FLETCHING
from uo.entity import *
from gemuo.engine import Engine
from gemuo.engine.util import Fail
from gemuo.engine.items import UseAndTarget
from gemuo.engine.menu import MenuResponse

class Fletching(Engine):
    def __init__(self, client, choice):
        Engine.__init__(self, client)

        tool = client.world.find_reachable_item(lambda x: x.item_id in ITEMS_FLETCHING_TOOLS)
        if tool is None:
            print "No tool"
            self._failure()
            return

        self.choice = choice

        wood = client.world.find_item_in(client.world.backpack(), lambda x: x.item_id in (ITEMS_LOGS + ITEMS_BOARDS))
        if wood is None:
            print "No wood"
            self._failure()
            return

        d = UseAndTarget(client, tool, wood)
        d.addCallbacks(self._target_sent, self._failure)

    def _target_sent(self, result):
        d = MenuResponse(self._client, self.choice).deferred
        d.addCallbacks(self._responded, self._failure)

    def _responded(self, result):
        reactor.callLater(9, self._success)

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
