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
from gemuo.target import Target, SendTarget
from gemuo.engine.items import UseAndTarget
from gemuo.engine.util import FinishCallback, DelayedCallback

class CutCloth(Engine):
    def __init__(self, client):
        Engine.__init__(self, client)

        world = client.world

        scissors = world.nearest_reachable_item(lambda x: x.item_id in (0xf9e, 0xf9f))
        if scissors is None:
            print "No scissors"
            self._failure()
            return

        cloth = world.find_player_item(lambda x: x.item_id in (0xf9b, 0x1766))
        if cloth is None:
            print "No cloth"
            self._success()
            return

        FinishCallback(client, UseAndTarget(client, scissors, cloth), self._cutted)

    def _cutted(self, success):
        if success:
            DelayedCallback(self._client, 1, self._success)
        else:
            self._failure()

class CutAllCloth(Engine):
    def __init__(self, client):
        Engine.__init__(self, client)

        self._next()

    def _next(self):
        client = self._client
        world = client.world

        cloth = world.find_player_item(lambda x: x.item_id in (0xf9b, 0x1766))
        if cloth is None:
            self._success()
            return

        FinishCallback(client, CutCloth(client), self._cutted)

    def _cutted(self, success):
        if success:
            self._next()
        else:
            self._failure()
