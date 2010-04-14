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

# This script double-clicks on the nearest moongate.

from twisted.internet import defer
import uo.packets as p
from gemuo.simple import simple_run
from uo.entity import ITEM_GATE

def run(client):
    gate = client.world.find_reachable_item(lambda x: x.item_id == ITEM_GATE)
    if gate is None:
        return defer.fail('No nearby gate found')

    print gate
    client.send(p.Use(gate.serial))

simple_run(run)
