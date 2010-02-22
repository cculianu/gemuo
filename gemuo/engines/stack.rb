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
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
#

require 'gemuo/timer'
require 'gemuo/engines/base'

module GemUO::Engines
    class StackItems < Base
        include GemUO::TimerEvent

        def initialize(client, item_id)
            super(client)
            @item_id = item_id
        end

        def start
            @backpack = @client.world.backpack
            unless @backpack
                puts "no backpack\n"
                stop
                @client.signal_fire(:on_engine_failed, self)
                return
            end

            super

            # get backpack contents
            @client << GemUO::Packet::Use.new(@backpack.serial)

            restart(0.7)
            @client.timer << self
        end

        def tick
            next_item
        end

        def drop_target
            backpack = @client.world.backpack
            return unless backpack
            @client.world.each_item_in(backpack) do
                |item|
                return item if item.item_id == @item_id
            end
            return backpack
        end

        def on_delete_entity(entity)
            if @holding && @holding.serial == entity.serial
                puts "dropping #{@holding} onto #{@target}\n"
                @client << GemUO::Packet::Drop.new(@holding.serial, 0, 0, 0, @target.serial)
                @holding = nil
                @target = nil
                restart(0.7)
                @client.timer << self
            end
        end

        def on_lift_reject(reason)
            puts "lift reject #{reason}\n"
            on_delete_entity(@holding)
        end

        def next_item
            items = []
            @client.world.each_item_in(@backpack) do
                |item|
                items << item if item.item_id == @item_id
            end

            if items.length < 2
                puts "stack is done"
                stop
                @client.signal_fire(:on_engine_complete, self)
                return
            end

            items.sort! do
                |a, b|
                a.amount <=> b.amount
            end

            @target = items.pop
            @holding = items.pop

            puts "lifting #{@holding} onto #{@target}\n"
            amount = @holding.amount
            amount = 1 unless amount && amount > 0
            @client << GemUO::Packet::Lift.new(@holding.serial, amount)
        end
    end
end

