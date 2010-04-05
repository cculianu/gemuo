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
from uo.entity import ITEM_BANDAGE
from gemuo.defer import deferred_find_item_in_backpack
from gemuo.engine import Engine
from gemuo.engine.util import FinishCallback, DelayedCallback
from gemuo.engine.items import UseAndTarget
from gemuo.engine.bandage import CutCloth

class UseBandageOn(Engine):
    def __init__(self, client, target):
        Engine.__init__(self, client)

        self.target = target

        d = deferred_find_item_in_backpack(client, lambda x: x.item_id == ITEM_BANDAGE)
        d.addCallbacks(self._found_bandage, self._failure)

    def _found_bandage(self, bandage):
        client = self._client
        FinishCallback(client, UseAndTarget(client, bandage, self.target), self._healed)

    def _healed(self, success):
        if success:
            DelayedCallback(self._client, 6, self._success)
        else:
            self._failure()

class AutoHeal(Engine):
    def __init__(self, client):
        Engine.__init__(self, client)

        self._next()

    def _should_heal(self, m):
        if not m.is_human():
            return False

        if m.hits is None:
            self._client.send(p.MobileQuery(0x04, m.serial))
            return False

        # heal if below 2/3 health
        return m.hits.value <= (m.hits.limit * 2) / 3

    def _next(self):
        client = self._client
        m = client.world.find_reachable_mobile(self._should_heal)
        if m is None:
            reactor.callLater(1, self._next)
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
