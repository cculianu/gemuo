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
from gemuo.entity import Entity
from gemuo.engine import Engine
from gemuo.timer import TimerEvent
from gemuo.target import Target, SendTarget
from gemuo.engine.util import FinishCallback

class OpenBank(Engine):
    def __init__(self, client):
        Engine.__init__(self, client)
        self._client.send(p.TalkUnicode(type=0xc0, hue=0, font=1, text='.', keyword=0x02))

    def abort(self):
        self._failure()

    def on_open_container(self, container):
        if container.is_bank(self._client.world.player):
            self._success()

class OpenContainer(Engine, TimerEvent):
    """Double-click a container, and return successfully when the gump
    opens"""

    def __init__(self, client, container):
        Engine.__init__(self, client)
        TimerEvent.__init__(self, client)

        self._serial = container.serial

        if container.is_bank(client.world.player):
            self._client.send(p.TalkUnicode(type=0xc0, hue=0, font=1, text='.', keyword=0x02))
        else:
            if not self._client.world.is_empty(container):
                # we know its contents, it seems already open
                self._success()
                return

            client.send(p.Use(self._serial))

        self._schedule(3)

    def abort(self):
        self._unschedule()
        self._failure()

    def on_open_container(self, container):
        if container.serial == self._serial and not self._client.world.is_empty(container):
            self._unschedule()
            self._success()

    def on_container_content(self, container):
        if container.serial == self._serial:
            self._unschedule()
            self._success()

    def tick(self):
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
        FinishCallback(client, self.engine, self._target_sent)

    def target_abort(self):
        self.engine.abort()
        self._failure()

    def _target_sent(self, success):
        self.target_mutex.put_target()

        if success:
            self._success()
        else:
            self._failure()
