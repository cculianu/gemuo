#
#  GemUO
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
            @x, @y, @z, @direction = x, y, z, direction & 0x7
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

        def to_s
            s = "#{@x},#{@y}"
            s << ",#{@z}" if @z
            s << ";#{@direction}" if @direction
        end
    end

    class BoundedValue
        def initialize(value, max)
            @value = value
            @max = max
        end
        def value
            @value
        end
        def max
            @max
        end

        def to_s
            "#{@value}/#{@max}"
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

        # for open containers and paperdolls
        def gump_id
            @gump_id
        end
        def gump_id=(v)
            @gump_id = v
        end
    end

    class Item < Entity
        def item_id
            @item_id
        end
        def item_id=(v)
            @item_id = v
        end
        def amount
            @amount
        end
        def amount=(v)
            @amount = v
        end
        # serial of the mobile which equips the item
        def parent
            @parent
        end
        def parent=(v)
            @parent = v
            @layer = nil
        end
        # only for equipped items
        def layer
            @layer
        end
        def layer=(v)
            @layer = v
        end

        def to_s
            s = '[Item serial=0x%x id=0x%x' % [ @serial, @item_id ]
            s << " name='#{@name}'" if @name
            s << ' parent=0x%x' % @parent if @parent
            s << ' layer=0x%x' % @layer if @layer
            s << " amount=#{@amount}" if @amount && @amount > 1
            s << " position=#{@position}" if @position
            s << " gump=#{@gump_id}" if @gump_id
            s << ']'
            s
        end
    end

    class Mobile < Entity
        def female
            @female
        end
        def female=(v)
            @female = v
        end
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

        def stats
            @stats
        end
        def stats=(v)
            raise TypeError.new unless v == nil || v.length == 3
            @stats = v
        end
        def stat_locks
            @stat_locks
        end
        def stat_locks=(v)
            raise TypeError.new unless v == nil || v.length == 3
            @stat_locks = v
        end

        def stat_cap
            @stat_cap
        end
        def stat_cap=(v)
            @stat_cap = v
        end

        def hits
            @hits
        end
        def hits=(v)
            @hits = v
        end

        def mana
            @mana
        end
        def mana=(v)
            @mana = v
        end

        def stamina
            @stamina
        end
        def stamina=(v)
            @stamina = v
        end

        def gold
            @gold
        end
        def gold=(v)
            @gold = v
        end

        def mass
            @mass
        end
        def mass=(v)
            @mass = v
        end

        def to_s
            s = '[Mobile serial=0x%x body=0x%x' % [ @serial, @body ]
            s << " name='#{@name}'" if @name
            s << " position=#{@position}" if @position
            s << ']'
            s
        end
    end
end
