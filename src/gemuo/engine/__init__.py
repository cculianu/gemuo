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
        self.__result = None
        #elf.active = True

    def finished(self):
        return self.__result is not None

    def result(self):
        assert self.__result == True or self.__result == False
        return self.__result

    def _signal(self, name, *args, **keywords):
        self._client.signal(name, *args, **keywords)

    def __stop(self):
        assert self.__result is None
        self._client.remove_engine(self)

    def _success(self, *args, **keywords):
        self.__stop()
        self.__result = True
        self._signal('on_engine_success', self, *args, **keywords)

    def _failure(self, *args, **keywords):
        self.__stop()
        self.__result = False
        self._signal('on_engine_failure', self, *args, **keywords)

    def abort(self):
        """Aborts this engine, does not emit a signal."""
        self.__stop()
