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
from gemuo.engine.util import FinishCallback
from gemuo.engine.items import OpenContainer

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

        self.backpack = world.backpack()
        if self.backpack is None:
            print "no backpack"
            self._failure()
            return

        if self._find_and_equip():
            self._success()
            return

        FinishCallback(client, OpenContainer(client, self.backpack),
                       self._backpack_opened)

    def _find_and_equip(self):
        client = self._client
        world = client.world

        item = world.find_item_in(self.backpack, self.func)
        if item is None: return False

        client.send(p.LiftRequest(item.serial))
        client.send(p.EquipRequest(item.serial, 0x2, world.player.serial))
        return True

    def _backpack_opened(self, success):
        if not success:
            self._failure()
            return

        if self._find_and_equip():
            self._success()
        else:
            self._failure()
