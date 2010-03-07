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

import socket, select
import struct
from uo.serialize import packet_lengths, PacketReader
from uo.compression import Decompress

class Client:
    def __init__(self, host, port, seed=42, decompress=False):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.connect((host, port))
        self._socket.send(struct.pack('>I', seed))
        self._decompress = None
        if decompress:
            self._decompress = Decompress()
        self._input = ''

    def _poll(self, timeout):
        x = select.select([self._socket], [], [], timeout)
        print x

    def _fill_buffer(self):
        x = self._socket.recv(4096)
        if x == '':
            raise "Connection closed"

        if self._decompress:
            x = self._decompress.decompress(x)
        self._input += x

    def _packet_from_buffer(self):
        if self._input == '':
            return None

        cmd = ord(self._input[0])
        l = packet_lengths[cmd]
        if l == 0xffff:
            raise "Unsupported packet"
        if l == 0:
            if len(self._input) < 3: return None
            l = struct.unpack('>H', self._input[1:3])[0]
            if l < 3 or l > 0x8000:
                raise "Malformed packet"
            if len(self._input) < l: return None
            x, self._input = self._input[3:l], self._input[l:]
        else:
            if len(self._input) < l: return None
            x, self._input = self._input[1:l], self._input[l:]
        return PacketReader(cmd, x)

    def receive(self, timeout=None):
        while True:
            x = self._packet_from_buffer()
            if x is not None: return x

            if timeout is not None:
                x = select.select([self._socket], [], [], timeout)
                if len(x[0]) == 0:
                    return None

            self._fill_buffer()

    def send(self, data):
        self._socket.send(data)
