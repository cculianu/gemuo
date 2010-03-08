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

from uo.entity import *

class Position:
    def __init__(self, x, y, z=None, direction=None):
        self.x = x
        self.y = y
        self.z = z
        self.direction = direction
        if self.direction is not None:
            self.direction &= 0x7

    def __str__(self):
        s = "%d,%d" % (self.x, self.y)
        if self.z is not None: s += ",%d" % self.z
        if self.direction is not None: s += ";%d" % self.direction
        return s

class BoundedValue:
    def __init__(self, value, limit):
        self.value = value
        self.limit = limit

class Entity:
    def __init__(self, serial, name=None, position=None, hue=None, flags=0):
        self.serial = serial
        self.name = name
        self.position = position
        self.hue = hue
        self.flags = flags

    def is_hidden(self):
        return (self.flags & FLAG_HIDDEN) != 0

class Item(Entity):
    def __init__(self, serial, name=None, position=None, hue=None, flags=0):
        Entity.__init__(self, serial, name, position, hue, flags)
        self.item_id = None
        self.amount = None
        self.parent_serial = None
        self.layer = None
        self.gump_id = None

    def __str__(self):
        s = '[Item serial=0x%x id=0x%x' % ( self.serial, self.item_id or 0 )
        if self.name is not None: s += " name='%s'" % self.name
        s += " flags=0x%x" % self.flags
        if self.parent_serial is not None: s += " parent=0x%x" % self.parent_serial
        if self.layer is not None: s += " layer=0x%x" % self.layer
        if self.amount is not None: s += " amount=%d" % self.amount
        if self.position is not None: s += " position='%s'" % self.position
        if self.gump_id is not None: s += " gump=0x%x" % self.gump_id
        s += ']'
        return s

    def is_dagger(self):
        return self.item_id == 0xf52

    def is_instrument(self):
        return self.item_id in ITEMS_INSTRUMENTS

    def is_food(self):
        return self.item_id in ITEMS_FOOD

    def is_bank(self, mobile):
        return self.layer == 0x1d and \
           self.parent_serial == mobile.serial

class Mobile(Entity):
    def __init__(self, serial, name=None, position=None, hue=None, flags=0):
        Entity.__init__(self, serial, name, position, hue, flags)
        self.female = False
        self.body = None
        self.notoriety = None
        self.stats = None
        self.stat_locks = None
        self.stat_cap = None
        self.hits = None
        self.mana = None
        self.stamina = None
        self.gold = None
        self.mass = None
        self.skills = None

    def __str__(self):
        s = '[Mobile serial=0x%x body=0x%x' % ( self.serial, self.body or 0 )
        if self.name is not None: s += " name='%s'" % self.name
        s += " flags=0x%x" % self.flags
        if self.position is not None: s += " position='%s'" % self.position
        if self.notoriety is not None: s += " notoriety=%d" % self.notoriety
        s += ']'
        return s

    def update_skills(self, skills):
        if self.skills is None: self.skills = dict()
        for x in skills:
            self.skills[x.id] = x

    def is_animal(self):
        return self.body in ANIMALS
