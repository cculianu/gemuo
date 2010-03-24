#!/usr/bin/python
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
from gemuo.simple import SimpleClient
from gemuo.engine import Engine
from gemuo.engine.messages import PrintMessages
from gemuo.engine.guards import Guards
from gemuo.engine.watch import Watch
from gemuo.engine.util import FinishCallback, DelayedCallback
from gemuo.engine.tailoring import Tailoring

class Cut(Engine):
    def __init__(self, client):
        Engine.__init__(self, client)

        world = client.world
        self.scissors = world.nearest_reachable_item(lambda x: x.item_id in (0xf9e, 0xf9f))
        if self.scissors is None:
            print "No scissors"
            self._failure()
            return

        self._next()

    def _next(self):
        client = self._client
        world = client.world
        self.target = world.find_player_item(lambda x: x.item_id in (0x1F00, 0x1EFF))
        if self.target is None:
            self._success()
            return

        client.send(p.Use(self.scissors.serial))

    def _on_target_request(self, allow_ground, target_id, flags):
        self._client.send(p.TargetResponse(0, target_id, flags, self.target.serial,
                                           0xffff, 0xffff, 0xffff, 0))
        DelayedCallback(client, 1, self._next)

    def on_packet(self, packet):
        if isinstance(packet, p.TargetRequest):
            self._on_target_request(packet.allow_ground, packet.target_id,
                                    packet.flags)

class AutoTailoring(Engine):
    def __init__(self, client):
        Engine.__init__(self, client)
        DelayedCallback(client, 1, self._cut)

    def _cut(self):
        client = self._client
        FinishCallback(client, Cut(self._client), self._cutted)

    def _cutted(self, success):
        self._craft()

    def _craft(self):
        client = self._client
        FinishCallback(client, Tailoring(self._client), self._crafted)

    def _crafted(self, success):
        if not success:
            self._failure()
            return

        DelayedCallback(self._client, 9, self._cut)

client = SimpleClient()

PrintMessages(client)
Guards(client)
Watch(client)
client.until(AutoTailoring(client).finished)
