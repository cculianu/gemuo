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

from gemuo.timer import TimerEvent
from gemuo.engine import Engine

class FinishCallback(Engine):
    def __init__(self, client, engine, func):
        Engine.__init__(self, client)

        self._engine = engine
        self._func = func

        if engine.finished():
            func(engine.result())
            self._success()
            return

    def on_engine_success(self, engine, *args, **keywords):
        if engine == self._engine:
            self._func(True)
            self._success()

    def on_engine_failure(self, engine, *args, **keywords):
        if engine == self._engine:
            self._func(False)
            self._success()

class DelayedCallback(Engine, TimerEvent):
    def __init__(self, client, delay, func):
        Engine.__init__(self, client)
        TimerEvent.__init__(self, client)

        self._func = func
        self._schedule(delay)

    def tick(self):
        self._func()
        self._success()
