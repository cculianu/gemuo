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
    class World
        def initialize
            @entities = {}
            @player = nil
            @walk = nil
            @skills = {}
        end

        def player
            @player
        end
        def player=(v)
            @player = v
            @walk = Walk.new(@player)
            @skills = {}
        end
        def backpack
            return unless @player
            equipped_item(@player, 0x15)
        end
        def skills
            @skills
        end
        def skill(skill_id)
            @skills[skill_id]
        end
        def get_walk
            @walk
        end

        def entity(serial)
            @entities[serial]
        end
        def delete(serial)
            self.player = nil if @player && @player.serial == serial
            @entities.delete(serial)
        end
        def make_mobile(serial)
            m = @entities[serial]
            m = @entities[serial] = Mobile.new(serial) unless m
            return m
        end
        def new_item(serial)
            @entities[serial] = Item.new(serial)
        end

        def each_entity
            @entities.each_value do
                |entity|
                yield entity
            end
        end
        def each_item
            @entities.each_value do
                |entity|
                yield entity if entity.kind_of?(Item)
            end
        end
        def each_item_in(parent)
            parent_serial = parent.serial
            @entities.each_value do
                |entity|
                yield entity if entity.kind_of?(Item) && entity.parent == parent_serial
            end
        end
        def items_in(parent)
            parent_serial = parent.serial
            items = []
            @entities.each_value do
                |entity|
                items << entity if entity.kind_of?(Item) && entity.parent == parent_serial
            end
            return items
        end
        def each_mobile
            @entities.each_value do
                |entity|
                yield entity if entity.kind_of?(Mobile)
            end
        end
        def equipped_item(parent, layer)
            @entities.each_value do
                |entity|
                next unless entity.kind_of?(Item)
                return entity if entity.parent == parent.serial && entity.layer == layer
            end
            nil
        end
    end
end
