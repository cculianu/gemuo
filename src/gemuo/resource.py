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

VECTORS = (
    (0, -1),
    (-1, 0),
    (0, 1),
    (1, 0),
)

class Spiral:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.length = 1
        self.remaining = 0
        self.direction = 0

    def step(self):
        if self.remaining == 0:
            self.length += 1
            self.direction = (self.direction + 1) % len(VECTORS)
            self.vector = VECTORS[self.direction]
            self.remaining = self.length / 2
        self.x += self.vector[0]
        self.y += self.vector[1]
        self.remaining -= 1

class Resource:
    def __init__(self, x, y, z, item_id, hue):
        self.x, self.y, self.z = x, y, z
        self.item_id, self.hue = item_id, hue

def iter_statics_in_block(map, block_x, block_y, ids):
    block = map.statics.load_block(block_x, block_y)
    if block is None:
        return

    for item_id, x, y, z, hue in block:
        if ((item_id & 0x3fff) | 0x4000) in ids:
            yield Resource(block_x * 8 + x, block_y * 8 + y, z, item_id, hue)

def find_statics_resource_block(map, position, ids, exhaust_db=None):
    spiral = Spiral(position.x / 8, position.y / 8)
    while True:
        if exhaust_db is None or not exhaust_db.is_exhausted(spiral.x, spiral.y):
            resources = tuple(iter_statics_in_block(map, spiral.x, spiral.y, ids))
            if len(resources) > 0:
                return resources
        spiral.step()

def find_resource(map, position, ids, exhaust_db=None, func=None):
    spiral = Spiral(position.x / 8, position.y / 8)
    while True:
        if exhaust_db is None or not exhaust_db.is_exhausted(spiral.x, spiral.y):
            block = map.statics.load_block(spiral.x, spiral.y)
            if block is not None:
                for item_id, x, y, z, hue in block:
                    if ((item_id & 0x3fff) | 0x4000) in ids and \
                           (func is None or func(item_id, spiral.x * 8 + x, spiral.y * 8 + y, z)):
                        return item_id, spiral.x * 8 + x, spiral.y * 8 + y, z
        spiral.step()

def find_land_resource(map, position, ids, exhaust_db=None, func=None):
    spiral = Spiral(position.x / 8, position.y / 8)
    while True:
        if exhaust_db is None or not exhaust_db.is_exhausted(spiral.x, spiral.y):
            block = map.land.load_block(spiral.x, spiral.y)
            if block is None: continue
            for x in range(8):
                for y in range(8):
                    item_id = block.get_id(x, y)
                    if item_id not in ids: continue
                    z = block.get_height(x, y)
                    if func is None or func(item_id, spiral.x * 8 + x, spiral.y * 8 + y, z):
                        return item_id, spiral.x * 8 + x, spiral.y * 8 + y, z
        spiral.step()
