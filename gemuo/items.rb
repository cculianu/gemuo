#
#  GemUO
#  $Id$
#
#  (c) 2010 Kai Sassmannshausen <kai@sassie.org>
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
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
#

module GemUO

    ITEM_BANDAGE = 0xe21
    
    ITEM_DRUMS = 0xe9c
    ITEM_TAMOURINE = 0xe9d
    ITEM_TAMOURINE_TASSEL = 0xe9e
    ITEM_LEAP_HARP = 0xeb2
    ITEM_HARP = 0xeb1
    ITEM_LUTE = 0xeb3
    ITEM_BAMBOO_FLUTE = 0x2805
    
    ITEM_DAGGER = 0xf52
    ITEM_BUTCHER_KNIFE1 = 0x13F6
    ITEM_BUTCHER_KNIFE2 = 0x13F7

    ITEM_WAND1 = 0xDF2
    ITEM_WAND2 = 0xDF3
    ITEM_WAND3 = 0xDF4
    ITEM_WAND4 = 0xDF5

    ITEM_RECALL_SCROLL = 0x1f4c
    ITEM_MARK_SCROLL = 0x1f59

    ITEMS_INSTRUMENTS =
    [
        ITEM_DRUMS,
        ITEM_TAMOURINE,
	    ITEM_TAMOURINE_TASSEL,
	    ITEM_LEAP_HARP,
	    ITEM_HARP,
	    ITEM_LUTE,
	    ITEM_BAMBOO_FLUTE
    ]

    ITEMS_SCOLLS = 
    [
        ITEM_RECALL_SCROLL,
        ITEM_MARK_SCROLL
    ]

    ITEMS_WEAPONS_FENCING =
    [
        ITEM_DAGGER 
    ]

    ITEMS_WEAPONS_SWORD =
    [
        ITEM_BUTCHER_KNIFE1,
        ITEM_BUTCHER_KNIFE2
    ]

    ITEM_WEAPONS_MACE =
    [
        ITEM_WAND1,
        ITEM_WAND2,
        ITEM_WAND3,
        ITEM_WAND4
    ]

    ITEMS_WEAPONS = 
    [
        ITEMS_WEAPONS_FENCING,
        ITEMS_WEAPONS_SWORD,
        ITEMS_WEAPONS_MACE
    ]
     
end
