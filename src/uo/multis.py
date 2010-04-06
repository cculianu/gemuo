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

def standard_multi_passable_at(west, north, width, height, door_x, door_y, num_doors, x, y, z):
    east = west + width - 1
    south = north + height - 1

    # door hole
    if x >= door_x and x < door_x + num_doors and y == door_y:
        return True

    # east and west walls
    if x == west or x == east:
        return y < north or y > south

    # north and south walls
    if y == north or y == south:
        return x < west or x > east

    return True

def multi_passable_at(item_id, x, y, z):
    item_id = item_id & 0x3fff

    if item_id in (0x64, 0x66, 0x68, 0x6a, 0x6c, 0x6e):
        # small house
        return standard_multi_passable_at(-3, -3, 7, 7, 0, 3, 1, x, y, z)

    if item_id == 0x74:
        # large brick
        return standard_multi_passable_at(-7, -7, 14, 14, -1, 6, 2, x, y, z)

    #if item_id in (0x76, 0x78):
        # two story house
        #return standard_multi_passable_at(-7, 0, 14, 7, x, y, z)

    if item_id == 0x7a:
        # tower
        return standard_multi_passable_at(-7, -7, 16, 14, 0, 6, 2, x, y, z)

    if item_id == 0x7c:
        # keep
        return standard_multi_passable_at(-11, -11, 24, 24, 0, 0, 0, x, y, z)

    if item_id == 0x7e:
        # castle
        return standard_multi_passable_at(-15, -15, 31, 31, 0, 0, 0, x, y, z)

    print "Unknown multi: 0x%x\n" % item_id
