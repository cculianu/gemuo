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
from gemuo.engine.util import FinishCallback
from gemuo.timer import TimerEvent
from gemuo.engine.items import OpenContainer

def drop_into(client, item, container, amount=0xffff):
    dest = client.world.find_item_in(container, lambda x: x.item_id == item.item_id)
    if dest is None:
        dest = container
    client.send(p.LiftRequest(item.serial, amount))
    client.send(p.Drop(item.serial, 0, 0, 0, dest.serial))

class MoveItems(Engine, TimerEvent):
    def __init__(self, client, items, container):
        Engine.__init__(self, client)
        TimerEvent.__init__(self, client)

        self._items = []
        self._items.extend(items)
        self._container = container

        self._next()

    def _next(self):
        if len(self._items) == 0:
            # no more items: we're done
            self._success()
            return

        item, self._items = self._items[0], self._items[1:]
        drop_into(self._client, item, self._container)

        self._schedule(1)

    def tick(self):
        self._next()

def move_items(client, source, destination, func):
    items = []
    for x in client.world.items_in(source):
        if func(x):
            items.append(x)
    return MoveItems(client, items, destination)

class Restock(Engine, TimerEvent):
    def __init__(self, client, container, counts={}, func=None):
        Engine.__init__(self, client)
        TimerEvent.__init__(self, client)

        self._source = client.world.backpack()
        if self._source is None:
            self._failure()
            return

        self._destination = container
        self._counts = []
        self._counts.extend(counts.iteritems())
        self._func = func

        FinishCallback(client, OpenContainer(client, self._source),
                       self._source_opened)

    def _source_opened(self, success):
        print "_source_opened", success
        if not success:
            self._failure()
            return

        client = self._client
        FinishCallback(client, OpenContainer(client, self._destination),
                       self._destination_opened)

    def _destination_opened(self, success):
        print "_destination_opened", success
        if not success:
            self._failure()
            return

        client = self._client

        if self._func is None:
            self._moved(True)
            return

        FinishCallback(client, move_items(client, self._source, self._destination,
                                          self._func), self._moved)

    def _moved(self, success):
        self._do_counts()

    def _do_counts(self):
        if len(self._counts) == 0:
            self._success()
            return

        x = self._counts[0]
        item_id, count = x

        client = self._client
        world = client.world

        n = 0
        for x in world.items_in(self._source):
            if x.item_id == item_id:
                if x.amount is None:
                    n += 1
                else:
                    n += x.amount

        if n > count:
            x = world.find_item_in(self._source, lambda x: x.item_id == item_id)
            if x is None:
                self._failure()
                return

            client.send(p.LiftRequest(x.serial, n - count))
            client.send(p.Drop(x.serial, 0, 0, 0, self._destination.serial))

            self._schedule(1)
        elif n < count:
            x = world.find_item_in(self._destination, lambda x: x.item_id == item_id)
            if x is None:
                print "Not found:", hex(item_id)
                self._failure()
                return

            client.send(p.LiftRequest(x.serial, count - n))
            client.send(p.Drop(x.serial, 0, 0, 0, self._source.serial))

            self._schedule(1)
        else:
            self._counts = self._counts[1:]
            self._schedule(0)

    def tick(self):
        self._do_counts()
