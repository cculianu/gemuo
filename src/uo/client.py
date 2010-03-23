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

import struct
from twisted.internet.protocol import Protocol
from uo.serialize import packet_lengths, PacketReader
from uo.compression import Decompress

class UOProtocol(Protocol):
    def __init__(self, seed=42, decompress=False):
        self.__seed = seed
        self.__decompress = decompress

    def connectionMade(self):
        Protocol.connectionMade(self)

        self.transport.write(struct.pack('>I', self.__seed))
        self._input = ''

        self._decompress = None
        if self.__decompress:
            self._decompress = Decompress()

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

    def on_packet(self, packet):
        self.handler(packet)

    def dataReceived(self, data):
        if self._decompress:
            data = self._decompress.decompress(data)

        self._input += data

        while True:
            packet = self._packet_from_buffer()
            if packet is None: break

            self.on_packet(packet)

    def send(self, data):
        self.transport.write(data)
