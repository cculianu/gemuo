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
import uo.packets as p
from gemuo.entity import Item
from gemuo.engine import Engine
from gemuo.engine.items import OpenContainer

def drop_into(client, item, container, amount=0xffff):
    dest = client.world.find_item_in(container, lambda x: x.item_id == item.item_id and x.amount < 60000)
    if dest is None or dest.amount == 1:
        dest = container
    client.send(p.LiftRequest(item.serial, amount))
    client.send(p.Drop(item.serial, 0, 0, 0, dest.serial))

class MoveItems(Engine):
    def __init__(self, client, items, container):
        Engine.__init__(self, client)

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

        reactor.callLater(1, self._next)

def move_items(client, source, destination, func):
    items = []
    for x in client.world.items_in(source):
        if func(x):
            items.append(x)
    return MoveItems(client, items, destination)

class Restock(Engine):
    def __init__(self, client, container, counts=(), func=None):
        Engine.__init__(self, client)

        self._source = client.world.backpack()
        if self._source is None:
            self._failure()
            return

        self._destination = container
        self._counts = []
        if isinstance(counts, dict):
            self._counts.extend(counts.iteritems())
        else:
            self._counts.extend(counts)
        self._func = func

        d = OpenContainer(client, self._source).deferred
        d.addCallbacks(self._source_opened, self._failure)

    def _source_opened(self, result):
        reactor.callLater(1, self._source_opened2)

    def _source_opened2(self):
        client = self._client

        if self._destination.is_bank(client.world.player):
            self._destination_opened(None)
        else:
            d = OpenContainer(client, self._destination).deferred
            d.addCallbacks(self._destination_opened, self._failure)

    def _destination_opened(self, result):
        if self._func is None:
            self._moved(True)
            return

        d = move_items(self._client, self._source, self._destination, self._func).deferred
        d.addCallbacks(self._moved, self._failure)

    def _moved(self, result):
        self._do_counts()

    def _do_counts(self):
        if len(self._counts) == 0:
            self._success()
            return

        x = self._counts[0]
        item_id, count = x
        if isinstance(item_id, int):
            item_ids = (item_id,)
        else:
            item_ids = item_id
        item_ids = set(item_ids)

        client = self._client
        world = client.world

        n = 0
        for x in world.items_in(self._source):
            if x.item_id in item_ids:
                if x.amount is None:
                    n += 1
                else:
                    n += x.amount

        if n > count:
            x = world.find_item_in(self._source, lambda x: x.item_id in item_ids)
            if x is None:
                self._failure()
                return

            client.send(p.LiftRequest(x.serial, n - count))
            client.send(p.Drop(x.serial, 0, 0, 0, self._destination.serial))

            reactor.callLater(1, self._do_counts)
        elif n < count:
            x = world.find_item_in(self._destination, lambda x: x.item_id in item_ids)
            if x is None:
                print "Not found:", item_ids
                self._failure()
                return

            client.send(p.LiftRequest(x.serial, count - n))
            client.send(p.Drop(x.serial, 0, 0, 0, self._source.serial))

            reactor.callLater(1, self._do_counts)
        else:
            self._counts = self._counts[1:]
            reactor.callLater(0, self._do_counts)

class Trash(Engine):
    """Find a trash can and throw items from the backpack into it."""

    def __init__(self, client, ids):
        Engine.__init__(self, client)

        self._source = client.world.backpack()
        if self._source is None:
            self._failure()
            return

        self.ids = ids

        d = OpenContainer(client, self._source).deferred
        d.addCallbacks(self._source_opened, self._failure)

    def _find_trash_can(self):
        return self._client.world.nearest_reachable_item(lambda x: x.parent_serial is None and x.item_id == 0xe77)

    def _source_opened(self, result):
        items = []
        for x in self._client.world.items_in(self._source):
            if x.item_id in self.ids:
                items.append(x)

        if len(items) == 0:
            self._success()
            return

        destination = self._find_trash_can()
        if destination is None:
            print "No trash can"
            self._failure()
            return

        d = MoveItems(self._client, items, destination).deferred
        d.addCallbacks(self._success, self._failure)
