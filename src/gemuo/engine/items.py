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
from gemuo.entity import Entity
from gemuo.engine import Engine
from gemuo.error import *
from gemuo.target import Target, SendTarget

class OpenBank(Engine):
    def __init__(self, client):
        Engine.__init__(self, client)
        self._client.send(p.TalkUnicode(text='Bank!', keyword=0x02))
        self.call_id = reactor.callLater(2, self._timeout)

    def abort(self):
        Engine.abort(self)
        self.call_id.cancel()

    def on_open_container(self, container):
        if container.is_bank(self._client.world.player):
            self.call_id.cancel()
            self._success(container)

    def _timeout(self):
        self._failure(Timeout('Bank timeout'))

class OpenContainer(Engine):
    """Double-click a container, and return successfully when the gump
    opens"""

    def __init__(self, client, container):
        Engine.__init__(self, client)

        self._serial = container.serial
        self._open = False

        if container.is_bank(client.world.player):
            self._client.send(p.TalkUnicode(text='Bank!', keyword=0x02))
        else:
            if not self._client.world.is_empty(container):
                # we know its contents, it seems already open
                self._success()
                return

            client.send(p.Use(self._serial))

        self.call_id = reactor.callLater(3, self._timeout)

    def abort(self):
        Engine.abort(self)
        self.call_id.cancel()

    def on_open_container(self, container):
        if container.serial == self._serial:
            if self._client.world.is_empty(container):
                self._open = True
            else:
                self.call_id.cancel()
                self._success()

    def on_container_content(self, container):
        if container.serial == self._serial:
            self.call_id.cancel()
            self._success()

    def _timeout(self):
        if self._open:
            self._success()
        else:
            self._failure(Timeout("OpenContainer timeout"))

class MergeStacks(Engine):
    def __init__(self, client, container, ids):
        Engine.__init__(self, client)
        self.container = container
        self.ids = ids

        d = OpenContainer(client, container).deferred
        d.addCallbacks(self._opened, self._failure)

    def _opened(self, result):
        reactor.callLater(1, self._next)

    def _next(self):
        client = self._client
        world = client.world

        exclude = set()

        while True:
            a = world.find_item_in(self.container, lambda i: i.serial not in exclude and i.item_id in self.ids)
            if a is None:
                self._success()
                return

            exclude.add(a.serial)

            b = world.find_item_in(self.container, lambda i: i.serial != a.serial and i.item_id == a.item_id and i.hue == a.hue)
            if b is not None:
                break

        print "merge", a, b

        client.send(p.LiftRequest(a.serial))
        client.send(p.Drop(a.serial, 0, 0, 0, b.serial))
        reactor.callLater(1, self._next)

class UseAndTarget(Engine):
    def __init__(self, client, item, target):
        Engine.__init__(self, client)

        if isinstance(item, Entity):
            item = item.serial

        if isinstance(target, Entity):
            target = Target(serial=target.serial)

        self.item = item
        self.target = target
        self.tries = 2
        self.engine = None

        self.target_mutex = client.target_mutex
        self.target_mutex.get_target(self.target_ok, self.target_abort)

    def target_ok(self):
        self._do()

    def target_abort(self):
        self.engine.abort()
        self._failure(Timeout('Target timeout'))

    def _do(self):
        client = self._client
        client.send(p.Use(self.item))
        self.engine = SendTarget(client, self.target)
        self.engine.deferred.addCallbacks(self._target_sent, self._target_failed)

    def _target_sent(self, result):
        self.target_mutex.put_target()
        self._success(result)

    def _target_failed(self, fail):
        self.target_mutex.put_target()
        self._failure(fail)

    def on_system_message(self, text):
        if 'must wait to perform another action' in text and \
           self.engine is not None and self.tries > 0:
            self.tries -= 1
            self.engine.abort()
            reactor.callLater(0.5, self._do)
