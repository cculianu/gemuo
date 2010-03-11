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

import sys
import uo.packets as p
from gemuo.simple import SimpleClient

client = SimpleClient()
gate = client.world.find_reachable_item(lambda x: x.item_id == 0xf6c)
if gate is None:
    print "No nearby gate found"
    sys.exit(1)

print gate
client.send(p.Use(gate.serial))
