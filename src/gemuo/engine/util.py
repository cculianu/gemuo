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
from gemuo.engine import Engine

class Delayed(Engine):
    def __init__(self, client, delay):
        Engine.__init__(self, client)

        self._call_id = reactor.callLater(delay, self._success)

    def abort(self):
        Engine.abort(self)
        self._call_id.cancel()

class Fail(Engine):
    def __init__(self, client):
        Engine.__init__(self, client)
        self._failure()

class Repeat(Engine):
    def __init__(self, client, delay, func, *args, **keywords):
        Engine.__init__(self, client)

        self.delay = delay
        self.func = func
        self.args = args
        self.keywords = keywords

        reactor.callLater(self.delay, self._next)

    def _next(self):
        d = self.func(self._client, *self.args, **self.keywords).deferred
        d.addCallbacks(self._finished, self._failure)

    def _finished(self, result):
        reactor.callLater(self.delay, self._next)
