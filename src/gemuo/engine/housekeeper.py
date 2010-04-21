#
#  GemUO
#
#  (c) 2005-2010 Max Kellermann <max@duempel.org>
#                Kai Sassmannshausen <kai@sassie.org>
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
from gemuo.entity import Position
from twisted.python import log

class OpenDoor(Engine):

    def __init__(self, client, door_serial, trigger_spots, friend_list):
        Engine.__init__(self, client)
        self.door = door_serial
        self.trigger = trigger_spots
        self.friends = friend_list

    def on_packet(self, packet):
        if isinstance(packet, p.MobileMoving):
            if self.isfriend(packet.serial):
                self.check_for_trigger(packet)

    def isfriend(self, mobile_serial):
        if mobile_serial in self.friends:
            return True
        return False
    
    def check_for_trigger(self, mobile_moving):
        for pos in self.trigger:
            if pos.x == mobile_moving.x and pos.y == mobile_moving.y:
                self.open_door(mobile_moving.serial)

    def open_door(self, player_serial):
        self._client.send(p.Use(self.door))
        log.msg("Opened door for " + str(player_serial))
