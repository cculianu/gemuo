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
from uo.entity import ITEM_BANDAGE
from gemuo.engine import Engine
from gemuo.timer import TimerEvent
from gemuo.engine.util import FinishCallback, DelayedCallback
from gemuo.engine.items import OpenContainer, UseAndTarget
from gemuo.engine.bandage import CutCloth

def find_bandage(world):
    return world.nearest_reachable_item(lambda x: x.item_id == ITEM_BANDAGE)

class UseBandageOn(Engine):
    def __init__(self, client, target):
        Engine.__init__(self, client)

        self.target = target

        world = client.world
        bandage = find_bandage(world)

        if bandage is not None:
            self._bandage(bandage)
        else:
            self.backpack = world.backpack()
            if self.backpack is None:
                print "No backpack"
                self._failure()
                return

            FinishCallback(client, OpenContainer(client, self.backpack), self._backpack)

    def _backpack(self, success):
        if not success:
            self._failure()
            return

        client = self._client

        bandage = find_bandage(client.world)
        if bandage is None:
            print "No bandage"
            self._failure()
            return

        self._bandage(bandage)

    def _bandage(self, bandage):
        client = self._client
        FinishCallback(client, UseAndTarget(client, bandage, self.target), self._healed)

    def _healed(self, success):
        if success:
            DelayedCallback(self._client, 6, self._success)
        else:
            self._failure()

class AutoHeal(Engine, TimerEvent):
    def __init__(self, client):
        Engine.__init__(self, client)
        TimerEvent.__init__(self, client)

        self._next()

    def _should_heal(self, m):
        # heal if below 2/3 health
        return m.hits is not None and m.hits.value <= (m.hits.limit * 2) / 3

    def _next(self):
        client = self._client
        m = client.world.find_reachable_mobile(self._should_heal)
        if m is None:
            self._schedule(1)
            return

        FinishCallback(client, UseBandageOn(client, m), self._healed)

    def _healed(self, success):
        if success:
            self._next()
        else:
            # maybe out of bandages?
            client = self._client
            FinishCallback(client, CutCloth(client), self._cutted)

    def _cutted(self, success):
        if not success:
            self._failure()
            return

        self._next()

    def tick(self):
        self._next()
