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

class OpenContainer(Engine):
    """Double-click a container, and return successfully when the gump
    opens"""

    def __init__(self, client, container):
        Engine.__init__(self, client)
        self._serial = container.serial
        client.send(p.Use(self._serial))

    def abort(self):
        self._failure()

    def on_open_container(self, container):
        if container.serial == self._serial:
            self._success()
