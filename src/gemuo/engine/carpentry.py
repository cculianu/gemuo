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

from uo.skills import SKILL_CARPENTRY
from uo.entity import *
import uo.packets as p
from gemuo.defer import deferred_skill, deferred_find_item_in_backpack
from gemuo.engine import Engine
from gemuo.engine.menu import MenuResponse

def carpentry_target(skill):
    if skill < 400:
        return ('Containers', 'wooden box')
    if skill < 480:
        return ('Containers', 'medium crate')
    if skill < 550:
        return ('Misc. Add-Ons', 'ballot box')
    if skill < 684:
        return ('Weapons and Armor', 'wooden shield')
    if skill < 740:
        return ('Weapons and Armor', 'fishing pole')
    if skill < 800:
        return ('Weapons and Armor', 'quarter staff')
    return ('Weapons and Armor', 'gnarled staff')

class Carpentry(Engine):
    def __init__(self, client):
        Engine.__init__(self, client)

        d = deferred_skill(client, SKILL_CARPENTRY)
        d.addCallbacks(self._got_skill, self._failure)

    def _got_skill(self, carpentry):
        self.target = carpentry_target(carpentry.value)
        if self.target is None:
            print "No carpentry target"
            self._failure()
            return

        d = deferred_find_item_in_backpack(self._client, lambda x: x.item_id in ITEMS_CARPENTRY_TOOLS)
        d.addCallbacks(self._found_tool, self._failure)

    def _found_tool(self, tool):
        client.send(p.Use(tool.serial))

        d = MenuResponse(client, target).deferred
        d.addCallbacks(self._success, self._success)
