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

module GemUO::Engines
    class WalkDump
        def on_ingame
            player = client.world.player
            puts "GemUO::Position.new(#{player.position.x}, #{player.position.y})\n"
        end
        def on_walk_ack
            player = client.world.player
            puts "GemUO::Position.new(#{player.position.x}, #{player.position.y})\n"
        end
        def on_mobile_update(mobile)
            player = client.world.player
            return unless mobile == player
            puts "GemUO::Position.new(#{player.position.x}, #{player.position.y})\n"
        end
    end

    class EntityDump
        def on_world_item(item)
            puts "world_item #{item}\n"
        end
        def on_equip(item)
            puts "equip #{item}\n"
        end
        def on_delete_entity(entity)
            puts "delete #{entity}\n"
        end
        def on_container_update(item)
            puts "container_update #{item}\n"
        end
    end

    class MessageDump
        def initialize(client)
            @client = client
        end

        def start
            @client.signal_connect(self)
        end

        def stop
            @client.signal_disconnect(self)
        end

        def on_ascii_message(serial, graphic, type, name, text)
            puts "message from '#{name}': #{text}"
        end
    end
end
