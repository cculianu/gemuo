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
from gemuo.entity import Item
from gemuo.simple import simple_run
from gemuo.error import *
from gemuo.defer import deferred_find_item_in, deferred_find_item_in_backpack
from gemuo.engine.messages import PrintMessages
from gemuo.engine.restock import drop_into

ITEMS_UNLOAD = ITEMS_TAILORING_TOOLS + ITEMS_CARPENTRY_TOOLS

def find_box_at(world, x, y):
    for e in world.iter_entities_at(x, y):
        if isinstance(e, Item) and e.item_id in ITEMS_LARGE_CRATE:
            return e
    return None

def found_item(item, client, bag):
    drop_into(client, item, bag)
    return reactor.callLater(1, find_next, client, bag)

def find_next(client, bag):
    d = deferred_find_item_in_backpack(client, lambda x: x.item_id in ITEMS_UNLOAD)
    d.addCallback(found_item, client, bag)
    return d

def found_bag(bag, client):
    return find_next(client, bag)

def run(client):
    PrintMessages(client)

    world = client.world
    box = find_box_at(world, world.player.position.x, world.player.position.y - 1)
    if box is None:
        raise NoSuchEntity('No restock box found')

    d = deferred_find_item_in(client, box, lambda x: x.item_id == ITEM_BAG)
    d.addCallback(found_bag, client)
    return d

simple_run(run)
