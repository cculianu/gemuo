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

import sys
from uo.entity import ITEM_GM_ROBE
from gemuo.entity import Item
from gemuo.engine import Engine

# uosecondage.com
GM_SERIALS = (
    0x92f, # Derrick
    0x434d, # Braden
    0x4ace, # Maahes
    0x4d4c, # Ezp
    0x683c, # Kaivan
    0x9a90, # Yoda
    0xf321, # Protostar
    0x15487, # Phoenix
    0x1a510, # Yoda
    0x209ff, # Nevermore
)

class DetectGameMaster(Engine):
    """Detect the presence of a GameMaster, and stop the macro
    immediately."""

    def __init__(self, client):
        Engine.__init__(self, client)

        for item in client.world.iter_items():
            self._check_item(item)

    def _panic(self, entity):
        print "\x1b[41mGM detected!\x1b[0m"

        all_entities = self._client.world.entities
        while True:
            print entity
            if not isinstance(entity, Item):
                break
            parent = entity.parent_serial
            if parent is None or parent not in all_entities:
                break
            entity = all_entities[parent]

        sys.exit(2)

    def _check_item(self, item):
        if item.item_id == ITEM_GM_ROBE:
            self._panic(item)

    def on_world_item(self, item):
        self._check_item(item)

    def on_container_item(self, item):
        self._check_item(item)

    def on_equip_item(self, item):
        self._check_item(item)

    def on_mobile_incoming(self, mobile):
        if mobile.body == 0x3db or mobile.serial in GM_SERIALS:
            self._panic(mobile)
