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
from gemuo.defer import deferred_find_item_in_backpack
from gemuo.engine import Engine

class Equip(Engine):
    def __init__(self, client, func):
        Engine.__init__(self, client)

        self.func = func

        world = client.world
        i = world.equipped_item(world.player, 0x2)
        if i is not None and func(i):
            # already equipped
            self._success()
            return

        d = deferred_find_item_in_backpack(client, func)
        d.addCallbacks(self._found, self._failure)

    def _found(self, item):
        client = self._client
        world = client.world

        client.send(p.LiftRequest(item.serial))
        client.send(p.EquipRequest(item.serial, 0x2, world.player.serial))

        reactor.callLater(1, self._success)
