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

from twisted.internet import defer
from gemuo.engine import Engine

class DeferredEngine(Engine):
    def __init__(self, client, engine):
        Engine.__init__(self, client)

        assert not engine.finished()

        self.engine = engine
        self.d = defer.Deferred()

    def on_engine_success(self, engine, *args, **keywords):
        if engine == self.engine:
            if len(args) > 0:
                result = args[0]
            else:
                result = None
            self.d.callback(result)
            self._success()

    def on_engine_failure(self, engine, *args, **keywords):
        if engine == self.engine:
            if len(args) > 0:
                fail = args[0]
            else:
                fail = 'Engine failed'
            self.d.errback(fail)
            self._success()

def defer_engine(client, engine):
    if engine.finished():
        if engine.result():
            return defer.succeed(None)
        else:
            return defer.fail('Immediate engine failure')

    return DeferredEngine(client, engine).d
