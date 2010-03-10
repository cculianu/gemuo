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

def select_option(menu, item):
    for i, option in enumerate(menu.options):
        if option.text == item:
            return i + 1
    return None

class MenuResponse(Engine):
    def __init__(self, client, responses):
        Engine.__init__(self, client)
        assert len(responses) > 0
        self.responses = list(responses)

    def abort(self):
        self._failure()

    def on_packet(self, packet):
        if isinstance(packet, p.Menu):
            response, self.responses = self.responses[0], self.responses[1:]
            option = select_option(packet, response)
            print "option", option
            if option is None:
                print "Option not found"
                self._failure()
                return

            self._client.send(p.MenuResponse(packet.dialog_serial, option))

            if len(self.responses) == 0:
                self._success()
