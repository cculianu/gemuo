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

from twisted.internet.defer import Deferred

class Engine:
    def __init__(self, client):
        self._client = client
        self._client.add_engine(self)
        self.deferred = Deferred()

    def _signal(self, name, *args, **keywords):
        self._client.signal(name, *args, **keywords)

    def __stop(self):
        self._client.remove_engine(self)

    def _success(self, result=None):
        self.__stop()
        self.deferred.callback(result)

    def _failure(self, fail='Engine failed'):
        self.__stop()
        self.deferred.errback(fail)

    def abort(self):
        """Aborts this engine, does not emit a signal."""
        self.__stop()
