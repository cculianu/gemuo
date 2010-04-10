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

from uo.entity import *
from gemuo.entity import Item
from gemuo.simple import simple_run
from gemuo.engine.messages import PrintMessages
from gemuo.engine.items import MergeStacks

def find_box_at(world, x, y):
    for e in world.iter_entities_at(x, y):
        if isinstance(e, Item) and e.item_id in ITEMS_LARGE_CRATE:
            return e
    return None

def find_restock_box(world):
    """Find the large crate one tile north of the player.  It is used
    for restocking."""
    return find_box_at(world, world.player.position.x, world.player.position.y - 1)

def run(client):
    PrintMessages(client)

    box = find_restock_box(client.world)
    #box = client.world.backpack()
    if box is None:
        raise NoSuchEntity('No box')

    return MergeStacks(client, box, ITEMS_INGOT + ITEMS_LOCKPICK)

simple_run(run)
