#
#  libuoclient-ruby
#  $Id$
#
#  (c) 2005 Max Kellermann <max@duempel.org>
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

module UO
    class Position
        def initialize(x, y, z = nil, direction = nil)
            @x, @y, @z, @direction = x, y, z, direction
        end
        def x
            @x
        end
        def y
            @y
        end
        def z
            @z
        end
        def direction
            @direction
        end
    end

    class Entity
        def initialize(serial)
            @serial = serial
        end
        def serial
            @serial
        end
        def name
            @name
        end
        def name=(v)
            @name = v
        end
        def position
            @position
        end
        def position=(v)
            @position = v
        end
        def hue
            @hue
        end
        def hue=(v)
            @hue = v
        end
    end

    class Item < Entity
        def item_id
            @item_id
        end
        def item_id=(v)
            @item_id = v
        end
    end

    class Mobile < Entity
        def body
            @body
        end
        def body=(v)
            @body = v
        end
        def notoriety
            @notoriety
        end
        def notoriety=(v)
            @notoriety = v
        end
    end
end
