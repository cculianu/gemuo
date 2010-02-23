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

from sys import argv, stderr, exit
from gemuo.client import Client
from gemuo.engine.login import Login
from gemuo.world import World
from gemuo.target import TargetMutex

class SimpleClient(Client):
    def __init__(self):
        if len(argv) != 6:
            print >>stderr, "Usage: %s host port username password charname"
            exit(1)

        host, port, username, password, character = argv[1:]
        port = int(port)

        Client.__init__(self, host, port)
        login = Login(self, username, password, character)
        self.world = World(self)
        self.until(login.finished)

        self.target_mutex = TargetMutex(self)
