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

from twisted.internet import reactor
from uo.entity import *
from gemuo.simple import simple_run
from gemuo.defer import deferred_nearest_reachable_item, deferred_skills
from gemuo.engine import Engine
from gemuo.engine.messages import PrintMessages
from gemuo.engine.guards import Guards
from gemuo.engine.watch import Watch
from gemuo.engine.items import UseAndTarget
from gemuo.engine.tailoring import Tailoring

class Cut(Engine):
    def __init__(self, client):
        Engine.__init__(self, client)

        d = deferred_nearest_reachable_item(client,
                                            lambda x: x.item_id in ITEMS_SCISSORS)
        d.addCallbacks(self._found_scissors, self._failure)

    def _found_scissors(self, result):
        self.scissors = result
        self._next()

    def _next(self):
        client = self._client
        world = client.world
        target = world.find_player_item(lambda x: x.item_id in ITEMS_TAILORING_PRODUCTS)
        if target is None:
            self._success()
            return

        d = UseAndTarget(client, self.scissors, target).deferred
        d.addCallbacks(self._cutted, self._failure)

    def _cutted(self, result):
        reactor.callLater(1, self._next)

class AutoTailoring(Engine):
    def __init__(self, client):
        Engine.__init__(self, client)
        reactor.callLater(1, self._cut)

    def _cut(self):
        d = Cut(self._client).deferred
        d.addCallbacks(self._cutted, self._failure)

    def _cutted(self, result):
        self._craft()

    def _craft(self):
        d = Tailoring(self._client).deferred
        d.addCallbacks(self._crafted, self._failure)

    def _crafted(self, result):
        reactor.callLater(9, self._cut)

def got_skills(skills, client):
    return AutoTailoring(client)

def run(client):
    PrintMessages(client)
    Guards(client)
    Watch(client)

    d = deferred_skills(client)
    d.addCallback(got_skills, client)
    return d

simple_run(run)
