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
from gemuo.engine.items import OpenContainer
from gemuo.engine.bandage import CutCloth

def find_bandage(world):
    return world.nearest_reachable_item(lambda x: x.item_id == ITEM_BANDAGE)

class UseBandageOn(Engine):
    def __init__(self, client, target):
        Engine.__init__(self, client)

        self.target = target
        self.target_mutex = client.target_mutex
        self.target_locked = False

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
        self.bandage = bandage
        self.target_mutex.get_target(self.target_ok, self.target_abort)

    def target_ok(self):
        self.target_locked = True
        self._client.send(p.Use(self.bandage.serial))

    def target_abort(self):
        self._failure()

    def _on_target_request(self, allow_ground, target_id, flags):
        if not self.target_locked: return

        client = self._client
        client.send(p.TargetResponse(0, target_id, flags, self.target.serial,
                                     0xffff, 0xffff, 0xffff, 0))
        self.target_mutex.put_target()

        DelayedCallback(client, 6, self._success)

    def on_packet(self, packet):
        if isinstance(packet, p.TargetRequest):
            self._on_target_request(packet.allow_ground, packet.target_id,
                                    packet.flags)

class AutoHeal(Engine, TimerEvent):
    def __init__(self, client):
        Engine.__init__(self, client)
        TimerEvent.__init__(self, client)

        self._next()

    def _next(self):
        client = self._client
        m = client.world.nearest_mobile(lambda x: True)
        if m is None:
            self._schedule(1)
            return

        if m.hits is not None and m.hits.value <= (m.hits.limit * 2) / 3:
            # heal if target is below 2/3 health
            FinishCallback(client, UseBandageOn(client, m), self._healed)
        else:
            self._schedule(1)

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
