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

class Translate(Engine):
    """Translates packets into high-level signals."""

    def __init__(self, client):
        Engine.__init__(self, client)

    def on_packet(self, packet):
        if isinstance(packet, p.AsciiMessage):
            if packet.type == 0 and packet.serial == 0xffffffff and \
               packet.name == 'System':
                self._signal('on_system_message', packet.text)
