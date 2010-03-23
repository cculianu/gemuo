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

import os, sys
import curses, traceback
from uo.entity import TREES
from gemuo.simple import simple_run, simple_later
from gemuo.util import AllFinished
from gemuo.engine.player import QuerySkills, QueryStats
from gemuo.data import TileCache
from gemuo.entity import Item, Mobile

COLOR_TREE = 1
COLOR_WALL = 2
COLOR_INNOCENT = 3
COLOR_CRIMINAL = 4
COLOR_MURDERER = 5
COLOR_ALLY = 6
COLOR_ENEMY = 7
COLOR_INVULNERABLE = 8
COLOR_WATER = 9

tc = TileCache('/home/max/.wine/drive_c/uo')
m = tc.get_map(0)

def restorescreen():
    curses.nocbreak()
    curses.echo()
    curses.endwin()

class GameWindow:
    def __init__(self, window, world):
        self.window = window
        self.world = world

    def draw_land(self, origin_x, origin_y, width, height):
        window = self.window

        for cursor_y in range(height):
            window.move(cursor_y, 0)
            y = origin_y + cursor_y
            for cursor_x in range(width):
                x = origin_x + cursor_x
                land_id = m.land_tile_id(x, y)
                if land_id == 0x64:
                    window.addch('~', curses.color_pair(COLOR_WATER))
                elif m.tile_data.land_passable(land_id):
                    window.addch(' ')
                else:
                    window.addch('X', curses.color_pair(COLOR_WALL))

    def draw_static_block(self, origin_x, origin_y, width, height, block):
        window = self.window

        for item_id, x, y, z, hue in block:
            x += origin_x
            y += origin_y
            if x < 0 or x >= width or y < 0 or y >= height: continue

            masked_id = ((item_id & 0x3fff) | 0x4000)

            window.move(y, x)
            if masked_id in TREES:
                window.addch('T', curses.color_pair(COLOR_TREE))
            elif not m.tile_data.item_passable(item_id):
                window.addch('X')

    def draw_static_blocks(self, origin_x, origin_y, width, height):
        start_y, end_y = origin_y / 8, (origin_y + height + 7) / 8
        start_x, end_x = origin_x / 8, (origin_x + width + 7) / 8
        block_y = start_y * 8 - origin_y
        for y in range(start_y, end_y):
            block_x = start_x * 8 - origin_x
            for x in range(start_x, end_x):
                block = m.statics.load_block(x, y)
                if block is not None:
                    self.draw_static_block(block_x, block_y,
                                           width, height, block)
                block_x += 8
            block_y += 8

    def draw_statics(self, origin_x, origin_y, width, height):
        self.draw_static_blocks(origin_x, origin_y, width, height)

    def draw_item(self, item):
        self.window.addch('.', curses.A_DIM)

    def draw_mobile(self, mobile):
        if mobile.notoriety == 1:
            color = COLOR_INNOCENT
        elif mobile.notoriety == 2:
            color = COLOR_ALLY
        elif mobile.notoriety == 5:
            color = COLOR_ENEMY
        elif mobile.notoriety == 6:
            color = COLOR_MURDERER
        elif mobile.notoriety == 7:
            color = COLOR_INVULNERABLE
        else:
            color = COLOR_CRIMINAL
        self.window.addch('m', curses.color_pair(color))

    def draw_entity(self, e):
        if isinstance(e, Item):
            self.draw_item(e)
        elif isinstance(e, Mobile):
            self.draw_mobile(e)
        else:
            self.window.addch('?', curses.A_DIM)

    def draw_entities(self, origin_x, origin_y, width, height):
        window = self.window
        for e in self.world.entities.itervalues():
            if e.position is None or \
               (e is Item and e.parent_serial is not None):
                continue
            cursor_x = e.position.x - origin_x
            cursor_y = e.position.y - origin_y
            if cursor_x < 0 or cursor_x >= width or \
               cursor_y < 0 or cursor_y >= height:
                continue
            window.move(cursor_y, cursor_x)
            self.draw_entity(e)

    def draw(self, player):
        window = self.window

        p = player.position
        if p is None:
            window.clear()
            return

        height, width = window.getmaxyx()
        width -= 1
        origin_x = player.position.x - width / 2
        origin_y = player.position.y - height / 2

        self.draw_land(origin_x, origin_y, width, height)

        self.draw_statics(origin_x, origin_y, width, height)
        self.draw_entities(origin_x, origin_y, width, height)

        window.move(p.y - origin_y, p.x - origin_x)

def update(screen, map_window, client):
    map_window.draw(client.world.player)
    screen.refresh()
    return simple_later(0.5, update, screen, map_window, client)

def main(client):
    global screen
    screen = curses.initscr()
    curses.noecho()
    curses.cbreak()
    curses.start_color()
    curses.init_pair(COLOR_TREE, curses.COLOR_WHITE, curses.COLOR_GREEN)
    curses.init_pair(COLOR_WALL, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(COLOR_INNOCENT, curses.COLOR_BLACK, curses.COLOR_CYAN)
    curses.init_pair(COLOR_CRIMINAL, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(COLOR_MURDERER, curses.COLOR_BLACK, curses.COLOR_RED)
    curses.init_pair(COLOR_ALLY, curses.COLOR_BLACK, curses.COLOR_GREEN)
    curses.init_pair(COLOR_ENEMY, curses.COLOR_BLACK, curses.COLOR_MAGENTA)
    curses.init_pair(COLOR_INVULNERABLE, curses.COLOR_BLACK, curses.COLOR_YELLOW)
    curses.init_pair(COLOR_WATER, curses.COLOR_BLUE, curses.COLOR_WHITE)

    map_window = GameWindow(screen, client.world)
    return update(screen, map_window, client)

if __name__ == '__main__':
    try:
        simple_run(main)
        restorescreen()
    except:
        restorescreen()
        traceback.print_exc()
