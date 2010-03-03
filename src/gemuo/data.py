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

# Loader for the UO client data files.

import os
import struct

FLAG_IMPASSABLE = 0x40

class TileData:
    def __init__(self, path):
        f = file(path)

        self.land_flags = []
        for a in range(0x200):
            f.seek(4, 1)
            for b in range(0x20):
                self.land_flags.append(struct.unpack('<I', f.read(4))[0])
                f.seek(22, 1) # skip texture and name
        assert len(self.land_flags) == 0x4000

        self.item_flags = []
        for a in range(0x200):
            f.seek(4, 1)
            for b in range(0x20):
                self.item_flags.append(struct.unpack('<I', f.read(4))[0])
                f.seek(33, 1)
        assert len(self.item_flags) == 0x4000

    def land_passable(self, id):
        assert id >= 0 and id < len(self.land_flags)
        return (self.land_flags[id] & FLAG_IMPASSABLE) == 0

    def item_passable(self, id):
        assert id >= 0 and id < len(self.item_flags)
        return (self.item_flags[id] & FLAG_IMPASSABLE) == 0

class LandBlock:
    def __init__(self, data):
        assert len(data) == 192
        self.data = data

    def get_id(self, x, y):
        assert x >= 0 and x < 8
        assert y >= 0 and y < 8

        i = (y * 8 + x) * 3
        return struct.unpack_from('<H', self.data, i)[0]

    def get_height(self, x, y):
        assert x >= 0 and x < 8
        assert y >= 0 and y < 8

        i = (y * 8 + x) * 3
        return ord(self.data[i + 2])

class LandLoader:
    def __init__(self, path, width, height):
        self.file = file(path)
        self.width = width
        self.height = height

    def load_block(self, x, y):
        assert x >= 0 and x < self.width
        assert y >= 0 and y < self.height

        self.file.seek(((x * self.height) + y) * 196 + 4)
        return LandBlock(self.file.read(192))

class IndexLoader:
    def __init__(self, path, width, height):
        self.file = file(path)
        self.width = width
        self.height = height

    def load_block(self, x, y):
        assert x >= 0 and x < self.width
        assert y >= 0 and y < self.height

        self.file.seek(((x * self.height) + y) * 12)
        data = self.file.read(8)
        offset, length = struct.unpack('<ii', data)
        if offset < 0 or length <= 0:
            return None, 0
        return offset, length

class StaticsList:
    def __init__(self, data):
        self.data = data

    def iter_at(self, x, y):
        i = 0
        while i < len(self.data):
            current_id, current_x, current_y, current_z, current_hue \
                        = struct.unpack_from('<HBBbH', self.data, i)
            if x == current_x and y == current_y:
                yield current_id, current_z, current_hue
            i += 7

    def is_passable(self, tile_data, x, y, z):
        for current_id, current_z, current_hue in self.iter_at(x, y):
            if not tile_data.item_passable(current_id):
                return False
        return True

class StaticsLoader:
    def __init__(self, path):
        self.file = file(path)

    def load_block(self, offset, length):
        self.file.seek(offset)
        return StaticsList(self.file.read(length))

class StaticsGlue:
    def __init__(self, index, static):
        self.index = index
        self.static = static

    def load_block(self, x, y):
        offset, length = self.index.load_block(x, y)
        if length == 0: return None
        return self.static.load_block(offset, length)

class MapGlue:
    def __init__(self, tile_data, map_path, index_path, statics_path, width, height):
        self.tile_data = tile_data
        self.land = LandLoader(map_path, width, height)
        self.statics = StaticsGlue(IndexLoader(index_path, width, height),
                                   StaticsLoader(statics_path))

    def land_tile_id(self, x, y):
        block = self.land.load_block(x / 8, y / 8)
        return block.get_id(x % 8, y % 8)

    def land_tile_flags(self, x, y):
        return self.tile_data.land_flags[self.land_tile_id(x, y)]

    def land_tile_height(self, x, y):
        block = self.land.load_block(x / 8, y / 8)
        return block.get_height(x % 8, y % 8)

    def is_passable(self, x, y, z):
        block = self.land.load_block(x / 8, y / 8)
        if not self.tile_data.land_passable(block.get_id(x % 8, y % 8)):
            return False

        #bz = block.get_height(x % 8, y % 8)
        #if bz > z: return False

        statics = self.statics.load_block(x / 8, y / 8)
        if statics is not None and not statics.is_passable(self.tile_data, x % 8, y % 8, z):
            return False

        return True

class BlockCache:
    def __init__(self, loader):
        self._loader = loader
        self._cache = dict()

    def load_block(self, x, y):
        i = x * 65536 + y
        if i in self._cache:
            return self._cache[i]
        b = self._loader.load_block(x, y)
        self._cache[i] = b
        return b

class CachedMapGlue(MapGlue):
    def __init__(self, *args, **keywords):
        MapGlue.__init__(self, *args, **keywords)
        self.land = BlockCache(self.land)
        self.statics = BlockCache(self.statics)

class TileCache:
    def __init__(self, path):
        self._path = path
        self._tile_data = TileData(os.path.join(self._path, 'tiledata.mul'))
        self._maps = {}

    def get_map(self, i):
        if i in self._maps:
            return self._maps[i]
        m = CachedMapGlue(self._tile_data,
                          os.path.join(self._path, 'map%u.mul' % i),
                          os.path.join(self._path, 'staidx%u.mul' % i),
                          os.path.join(self._path, 'statics%u.mul' % i),
                          768, 512)
        self._maps[i] = m
        return m
