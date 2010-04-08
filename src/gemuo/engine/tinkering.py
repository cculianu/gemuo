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

from uo.skills import SKILL_TINKERING
from uo.entity import *
from gemuo.engine import Engine
from gemuo.defer import deferred_find_item_in_backpack, deferred_skill
from gemuo.engine.menu import MenuResponse
from gemuo.engine.items import UseAndTarget

class NoTinkeringTarget(Exception):
    def __init__(self, message='No tinkering target'):
        Exception.__init__(self, message)

def tinkering_target(skill):
    if skill < 450:
        # XXX implement
        return None
    if skill < 900:
        return ('Tools', 'lockpick')
    # XXX implement more
    return None

class Tinkering(Engine):
    def __init__(self, client):
        Engine.__init__(self, client)

        d = deferred_find_item_in_backpack(client, lambda x: x.item_id in ITEMS_TINKERING_TOOLS)
        d.addCallbacks(self._found_tool, self._failure)

    def _found_tool(self, result):
        self.tool = result
        d = deferred_find_item_in_backpack(self._client,
                                           lambda i: i.item_id in ITEMS_INGOT and (i.hue is None or i.hue == 0))
        d.addCallbacks(self._found_ingot, self._failure)

    def _found_ingot(self, result):
        self.ingot = result
        d = deferred_skill(self._client, SKILL_TINKERING)
        d.addCallbacks(self._got_skill, self._failure)

    def _got_skill(self, result):
        self.target = tinkering_target(result.value)
        if self.target is None:
            self._failure(NoTinkeringTarget())
            return

        d = UseAndTarget(self._client, self.tool, self.ingot).deferred
        d.addCallbacks(self._used, self._failure)

    def _used(self, result):
        d = MenuResponse(self._client, self.target).deferred
        d.addCallbacks(self._success, self._success)
