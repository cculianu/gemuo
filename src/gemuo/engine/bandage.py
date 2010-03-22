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
from gemuo.timer import TimerEvent
from gemuo.engine.util import DelayedCallback

class CutCloth(Engine):
    def __init__(self, client):
        Engine.__init__(self, client)

        self._target_mutex = client.target_mutex
        self._target_locked = False
        self._world = client.world

        self._target_mutex.get_target(self._target_ok, self._target_abort)

    def _target_ok(self):
        scissors = self._world.nearest_reachable_item(lambda x: x.item_id in (0xf9e, 0xf9f))
        if scissors is None:
            print "No scissors"
            self._target_mutex.put_target()
            self._failure()
            return

        self._cloth = self._world.find_player_item(lambda x: x.item_id in (0xf9b, 0x1766))
        if self._cloth is None:
            print "No cloth"
            self._target_mutex.put_target()
            self._success()
            return

        self._target_locked = True
        self._client.send(p.Use(scissors.serial))

    def _target_abort(self):
        self._failure()

    def _on_target_request(self, allow_ground, target_id, flags):
        if not self._target_locked: return

        client = self._client

        client.send(p.TargetResponse(0, target_id, flags, self._cloth.serial,
                                     0xffff, 0xffff, 0xffff, 0))
        self._target_mutex.put_target()

        DelayedCallback(client, 1, self._success)

    def on_packet(self, packet):
        if isinstance(packet, p.TargetRequest):
            self._on_target_request(packet.allow_ground, packet.target_id,
                                    packet.flags)

class CutAllCloth(Engine, TimerEvent):
    def __init__(self, client):
        Engine.__init__(self, client)
        TimerEvent.__init__(self, client)

        self._target_mutex = client.target_mutex
        self._target_locked = False
        self._world = client.world

        self._target_mutex.get_target(self._target_ok, self._target_abort)

    def _target_ok(self):
        scissors = self._world.nearest_reachable_item(lambda x: x.item_id in (0xf9e, 0xf9f))
        if scissors is None:
            print "No scissors"
            self._target_mutex.put_target()
            self._failure()
            return

        self._cloth = self._world.find_player_item(lambda x: x.item_id in (0xf9b, 0x1766))
        if self._cloth is None:
            print "No cloth"
            self._target_mutex.put_target()
            self._success()
            return

        self._target_locked = True
        self._client.send(p.Use(scissors.serial))

    def _target_abort(self):
        self._failure()

    def _on_target_request(self, allow_ground, target_id, flags):
        if not self._target_locked: return

        self._client.send(p.TargetResponse(0, target_id, flags, self._cloth.serial,
                                           0xffff, 0xffff, 0xffff, 0))
        self._target_mutex.put_target()
        self._schedule(1)

    def on_packet(self, packet):
        if isinstance(packet, p.TargetRequest):
            self._on_target_request(packet.allow_ground, packet.target_id,
                                    packet.flags)

    def tick(self):
        self._target_mutex.get_target(self._target_ok, self._target_abort)
