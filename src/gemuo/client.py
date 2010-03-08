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

import uo.client
import uo.packets as p
from gemuo.timer import TimerManager

class Client(TimerManager):
    def __init__(self, host, port):
        TimerManager.__init__(self)
        self._client = uo.client.Client(host, port)
        self._engines = []

    def relay_to(self, host, port, auth_id):
        """Connect to the game server, and switches compression on."""
        self._client = uo.client.Client(host, port, seed=auth_id,
                                        decompress=True)

    def add_engine(self, engine):
        self._engines.append(engine)

    def remove_engine(self, engine):
        self._engines.remove(engine)

    def signal(self, name, *args, **keywords):
        for engine in self._engines:
            if hasattr(engine, name):
                getattr(engine, name)(*args, **keywords)

    def _handle_packet(self, packet):
        if packet.cmd in p.parsers:
            packet = p.parsers[packet.cmd](packet)
            self.signal('on_packet', packet)
        else:
            print "No parser for packet:", hex(packet.cmd)

    def once(self, timeout=1):
        packet = self._client.receive(timeout)
        if packet is not None:
            self._handle_packet(packet)
        self._tick()
        return packet is not None

    def process(self, timeout=1):
        """Process all pending events.  The timeout is only valid for
        the first packet."""

        if not self.once(timeout):
            return False

        while len(self._engines) > 0 and self.once(0):
            pass
        return True

    def run(self):
        while len(self._engines) > 0:
            self.once()

    def until(self, finished):
        while not finished():
            self.once()

    def send(self, data):
        self._client.send(data)
