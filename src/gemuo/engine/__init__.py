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

class Engine:
    def __init__(self, client):
        self._client = client
        self._client.add_engine(self)
        self.__finished = False
        #elf.active = True

    def finished(self):
        return self.__finished

    def _signal(self, name, *args, **keywords):
        self._client.signal(name, *args, **keywords)

    def _stop(self):
        assert not self.__finished
        self.__finished = True
        self._client.remove_engine(self)

    def _success(self, *args, **keywords):
        self._stop()
        self._signal('on_engine_success', self, *args, **keywords)

    def _failure(self, *args, **keywords):
        self._stop()
        self._signal('on_engine_failure', self, *args, **keywords)
