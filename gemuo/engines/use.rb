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

require 'gemuo/rules'

module GemUO::Engines
    class Use < GemUO::TimerEvent
        def initialize(client, item_id)
            @client = client
            @item_id = item_id
        end

        def start
            @client.signal_connect(self)

            if @client.world.backpack
                @client << GemUO::Packet::Use.new(@client.world.backpack.serial)
            end

            tick
        end

        def stop
            @client.signal_disconnect(self)
        end

        def find_item
            backpack = @client.world.backpack
            return unless backpack
            @client.world.each_item_in(backpack) do
                |item|
                return item if item.item_id == @item_id
            end
            nil
        end

        def tick
            item = find_item()
            if item
                @client << GemUO::Packet::Use.new(item.serial)
            else
                puts "No item #{@item_id}"
                if @client.world.backpack
                    @client << GemUO::Packet::Use.new(@client.world.backpack.serial)
                end
            end

            restart(2)
            @client.timer << self
        end
    end
end
