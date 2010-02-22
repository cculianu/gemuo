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

module GemUO
    class Position
        def initialize(x, y, z = nil, direction = nil)
            @x, @y, @z, @direction = x, y, z, direction & 0x7
        end

        attr_reader :x, :y, :z, :direction

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

        attr_reader :value, :max

        def to_s
            "#{@value}/#{@max}"
        end
    end

    class Entity
        def initialize(serial)
            @serial = serial
        end

        attr_reader :serial
        attr_accessor :name, :position, :hue

        # for open containers and paperdolls
        attr_accessor :gump_id
    end

    class Item < Entity
        attr_accessor :item_id, :amount

        # serial of the mobile which equips the item
        attr_accessor :parent

        # only for equipped items
        attr_accessor :layer

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

        def dagger?
            return @item_id == 0xf52
        end

        def instrument?
            return @item_id == 0xeb2 # leap harp
        end
    end

    class Mobile < Entity
        attr_accessor :female, :body, :notoriety
        attr_accessor :stats, :stat_locks, :stat_cap
        attr_accessor :hits, :mana, :stamina
        attr_accessor :gold, :mass

        def to_s
            s = '[Mobile serial=0x%x body=0x%x' % [ @serial, @body ]
            s << " name='#{@name}'" if @name
            s << " position=#{@position}" if @position
            s << ']'
            s
        end
    end
end
