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
            self._success()

    def _timeout(self):
        print "OpenBank timeout"
        self._failure()

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
            print "OpenContainer timeout"
            self._failure()

class UseAndTarget(Engine):
    def __init__(self, client, item, target):
        Engine.__init__(self, client)

        if isinstance(item, Entity):
            item = item.serial

        if isinstance(target, Entity):
            target = Target(serial=target.serial)

        self.item = item
        self.target = target

        self.target_mutex = client.target_mutex
        self.target_mutex.get_target(self.target_ok, self.target_abort)

    def target_ok(self):
        client = self._client
        client.send(p.Use(self.item))
        self.engine = SendTarget(client, self.target)
        self.engine.deferred.addCallbacks(self._target_sent, self._target_failed)

    def target_abort(self):
        self.engine.abort()
        self._failure()

    def _target_sent(self, result):
        self.target_mutex.put_target()
        self._success(result)

    def _target_failed(self, fail):
        self.target_mutex.put_target()
        self._failure(fail)
