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

from gemuo.simple import simple_run
from gemuo.engine.items import OpenBank

def print_bank(result, world):
    container = world.bank()
    if container is None:
        raise 'No bank'

    for x in world.items_in(container):
        print x

def run(client):
    d = defer_engine(client, OpenBank(client))
    d.addCallback(print_contents, client.world)
    return d

simple_run(run)
