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
from gemuo.target import Target
from twisted.python import log

class OpenDoor(Engine):
    """Opens the door for serials in the friend_list that step on a trigger position
    trigger_list is of Format [Position(pos1.x, pos1.y), Position(pos2.y, pos2.y)]
    friend_list is of Format [Serial1, Serial2, ]"""

    def __init__(self, client, door_serial, trigger_list, friend_list):
        Engine.__init__(self, client)
        self.door = door_serial
        self.trigger = trigger_list
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


class AutoEject(Engine):
    """Auto ejects not friended mobiles out of the house.
    house_rectangle is of format [pos1.x, pos1.y, pos2.x, pos2.y] where
    pos1 is the northwest and pos2 the southeast corner"""

    def __init__(self, client, red_friends=[], house_rectangle=[]):
        Engine.__init__(self, client)
        self.target = None
        self.red_friends = red_friends
        self.xmin = house_rectangle[0]
        self.xmax = house_rectangle[2]
        self.ymin = house_rectangle[1]
        self.ymax = house_rectangle[3]

    def on_packet(self, packet):
        if isinstance(packet, p.MobileMoving):
            if self.is_in_house(packet.x, packet.y):
                self.check_visitor(packet)
        elif isinstance(packet, p.TargetRequest):
            self.send_eject_target(packet)

    def check_visitor(self, packet):
        if packet.notoriety == 3:
            self.eject_mobile(packet)
        elif packet.notoriety == 6 and not packet.serial in self.red_friends:
            self.eject_mobile(packet)
    
    def is_in_house(self, x, y):
        if x > self.xmin and x < self.xmax and \
                y > self.ymin and y < self.ymax:
            return True
        return False
    
    def eject_mobile(self, packet):
        self.target = Target(packet.serial, packet.x, packet.y, packet.z, packet.body)
        self._client.send(p.TalkUnicode("remove thyself", 0x33))

    def send_eject_target(self, packet):
        if self.target is not None:
            self._client.send(self.target.response(packet.target_id, packet.flags))
            log.msg("Ejected " + str(self.target.serial))
