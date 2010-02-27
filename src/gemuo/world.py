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

import uo.packets as p
from gemuo.engine import Engine
from gemuo.player import Walk
from gemuo.entity import Position, BoundedValue, Entity, Item, Mobile

class World(Engine):
    def __init__(self, client):
        Engine.__init__(self, client)
        #self.active = False
        self.entities = dict()
        self.player = None
        self.walk = None
        self.map_width = None
        self.map_height = None

    def _reachable(self, position):
        assert self.player is not None
        player = self.player.position
        return position.x >= player.x - 1 and position.x <= player.x + 1 \
            and position.y >= player.y - 1 and position.y <= player.y + 1 \

    def _reachable_item(self, entity):
        return isinstance(entity, Item) and entity.parent_serial is None and \
            entity.position is not None and self._reachable(entity.position)

    def mobiles(self):
        return filter(lambda x: isinstance(x, Mobile), self.entities.itervalues())

    def items_in(self, parent):
        if isinstance(parent, Entity):
            parent = parent.serial
        return filter(lambda x: isinstance(x, Item) and x.parent_serial == parent, self.entities.itervalues())

    def equipped_item(self, parent, layer):
        for x in self.items_in(parent):
            if x.layer == layer: return x
        return None

    def backpack(self, mobile=None):
        if mobile is None: mobile = self.player
        if mobile is None: return None
        return self.equipped_item(mobile, 0x15)

    def find_item_in(self, parent, func):
        for x in self.items_in(parent):
            if func(x): return x
        return None

    def find_player_item(self, func):
        # check equipped items first
        if self.player is not None:
            x = self.find_item_in(self.player, func)
            if x is not None: return x

        # then search backpack
        backpack = self.backpack()
        if backpack is not None:
            x = self.find_item_in(backpack, func)
            if x is not None: return x

        return None

    def find_reachable_item(self, func):
        if self.player is None: return None
        for x in self.entities.itervalues():
            if self._reachable_item(x) and func(x):
                return x
        return x

    def _clear(self):
        self.entities.clear()
        self.player = None
        self.walk = None
        self.map_width = None
        self.map_height = None

    def _make_mobile(self, serial):
        if serial in self.entities:
            return self.entities[serial]
        m = Mobile(serial)
        self.entities[serial] = m
        return m

    def _new_item(self, serial):
        i = Item(serial)
        self.entities[serial] = i
        return i

    def _delete_items_in(self, serial):
        for item in self.items_in(serial):
            del self.entities[item.serial]
            self._delete_items_in(item.serial)

    def _delete_entity(self, serial):
        if serial not in self.entities: return
        del self.entities[serial]
        self._delete_items_in(serial)

    def on_packet(self, packet):
        if isinstance(packet, p.MobileStatus):
            mobile = self._make_mobile(packet.serial)
            mobile.name = packet.name
            mobile.hits = BoundedValue(packet.hits, packet.hits_max)
            mobile.female = packet.female
            mobile.stats = packet.stats
            mobile.stamina = BoundedValue(packet.stamina, packet.stamina_max)
            mobile.mana = BoundedValue(packet.mana, packet.mana_max)
            mobile.gold = packet.gold
            mobile.armor = packet.armor
            mobile.mass = packet.mass
            mobile.stat_cap = packet.stat_cap

            self._signal('on_mobile_status', mobile)
        elif isinstance(packet, p.WorldItem):
            item = self._new_item(packet.serial)
            item.item_id = packet.item_id
            item.amount = packet.amount
            item.hue = packet.hue
            item.flags = packet.flags
            item.position = Position(packet.x, packet.y,
                                     packet.z, packet.direction)

            self._signal('on_world_item', item)
        elif isinstance(packet, p.LoginConfirm):
            self._clear()

            self.map_width = packet.map_width
            self.map_height = packet.map_height

            self.player = self._make_mobile(packet.serial)
            self.player.body = packet.body
            self.player.position = Position(packet.x, packet.y,
                                            packet.z, packet.direction)
            self.walk = Walk(self.player)
        elif isinstance(packet, p.Delete):
            self._delete_entity(packet.serial)
        elif isinstance(packet, p.MobileUpdate):
            mobile = self._make_mobile(packet.serial)
            mobile.body = packet.body
            mobile.hue = packet.hue
            mobile.flags = packet.flags
            mobile.position = Position(packet.x, packet.y,
                                       packet.z, packet.direction)

            self._signal('on_mobile_update', mobile)
        elif isinstance(packet, p.WalkReject):
            if self.walk is not None:
                self.walk.walk_reject(packet.seq, packet.x, packet.y,
                                      packet.z, packet.direction)

            self._signal('on_walk_reject')
        elif isinstance(packet, p.WalkAck):
            if self.walk is not None:
                self.walk.walk_ack(packet.seq, packet.notoriety)

            self._signal('on_walk_ack')
        elif isinstance(packet, p.OpenContainer):
            if packet.serial in self.entities:
                container = self.entities[packet.serial]
                container.gump_id = packet.gump_id
                self._signal('on_open_container', container)
        elif isinstance(packet, p.ContainerItem):
            item = self._new_item(packet.serial)
            item.item_id = packet.item_id
            item.hue = packet.hue
            item.parent_serial = packet.parent_serial
            item.amount = packet.amount
            item.position = Position(packet.x, packet.y)

            self._signal('on_container_item', item)
        elif isinstance(packet, p.EquipItem):
            item = self._new_item(packet.serial)
            item.item_id = packet.item_id
            item.hue = packet.hue
            item.parent_serial = packet.parent_serial
            item.layer = packet.layer

            self._signal('on_equip_item', item)
        elif isinstance(packet, p.SkillUpdate):
            if self.player is not None:
                self.player.update_skills(packet.skills)
                self._signal('on_skill_update', self.player.skills)
        elif isinstance(packet, p.ContainerContent):
            for x in packet.items:
                self.on_packet(x)
        elif isinstance(packet, p.MobileIncoming):
            mobile = self._make_mobile(packet.serial)
            mobile.body = packet.body
            mobile.hue = packet.hue
            mobile.flags = packet.flags
            mobile.position = Position(packet.x, packet.y,
                                       packet.z, packet.direction)
            mobile.notoriety = packet.notoriety

            for x in packet.items:
                item = self._new_item(x.serial)
                item.parent_serial = mobile.serial
                item.item_id = x.item_id
                item.layer = x.layer
                item.hue = x.hue

            self._signal('on_mobile_incoming', mobile)
        elif isinstance(packet, p.MobileMoving):
            mobile = self._make_mobile(packet.serial)
            oldpos = mobile.position
            mobile.body = packet.body
            mobile.hue = packet.hue
            mobile.flags = packet.flags
            mobile.position = Position(packet.x, packet.y,
                                       packet.z, packet.direction)
            mobile.notoriety = packet.notoriety

            self._signal('on_mobile_moving', mobile, oldpos)
        elif isinstance(packet, p.MobileHits):
            mobile = self._make_mobile(packet.serial)
            mobile.hits = BoundedValue(packet.hits, packet.hits_max)

            self._signal('on_mobile_hits', mobile)
        elif isinstance(packet, p.MobileMana):
            mobile = self._make_mobile(packet.serial)
            mobile.mana = BoundedValue(packet.mana, packet.mana_max)

            self._signal('on_mobile_mana', mobile)
        elif isinstance(packet, p.MobileStamina):
            mobile = self._make_mobile(packet.serial)
            mobile.stamina = BoundedValue(packet.stamina, packet.stamina_max)

            self._signal('on_mobile_stamina', mobile)
        elif isinstance(packet, p.Extended):
            if packet.extended == 0x0019 and packet.extended2 == 2:
                # statlock info
                mobile = self._make_mobile(packet.serial)
                mobile.stat_locks = packet.stat_locks
