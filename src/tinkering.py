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

from twisted.internet import reactor, defer
from uo.entity import *
from gemuo.simple import simple_run
from gemuo.entity import Item
from gemuo.engine import Engine
from gemuo.engine.messages import PrintMessages
from gemuo.engine.guards import Guards
from gemuo.engine.watch import Watch
from gemuo.engine.walk import PathFindWalk
from gemuo.engine.restock import Restock, Trash
from gemuo.engine.tinkering import Tinkering

def find_box_at(world, x, y):
    for e in world.iter_entities_at(x, y):
        if isinstance(e, Item) and e.item_id in ITEMS_LARGE_CRATE:
            return e
    return None

def find_restock_box(world):
    """Find the large crate one tile north of the player.  It is used
    for restocking."""
    return find_box_at(world, world.player.position.x, world.player.position.y - 1)

def out_filter(item):
    return item.item_id in ITEMS_LOCKPICK

def restock(client):
    world = client.world
    player = world.player
    box = find_restock_box(world)
    if box is None:
        return defer.fail(NoSuchEntity('No box'))

    counts = (
        (ITEMS_TINKERING_TOOLS, 2),
        (ITEMS_INGOT, 100),
    )

    return Restock(client, box, counts=counts, func=out_filter).deferred

class HouseRestock(Engine):
    def __init__(self, client):
        Engine.__init__(self, client)


        d = OpenContainer(client, box).deferred
        d.addCallbacks(self._box_opened, self._failure)

class AutoTinkering(Engine):
    def __init__(self, client):
        Engine.__init__(self, client)
        self._restock()

    def _restock(self):
        d = restock(self._client)
        d.addCallbacks(self._restocked, self._failure)

    def _restocked(self, result):
        reactor.callLater(1, self._restocked2)

    def _restocked2(self):
        d = Tinkering(self._client).deferred
        d.addCallbacks(self._crafted, self._failure)

    def _crafted(self, result):
        reactor.callLater(5, self._restock)

def run(client):
    PrintMessages(client)
    Guards(client)
    Watch(client)
    return AutoTinkering(client)

simple_run(run)
