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

module UO::Engines
    class SimpleWalk
        def initialize(client, destination)
            @destination = destination
            @client = client
            @client.signal_connect(self)
            next_walk
        end

        def distance2(position)
            dx = @destination.x - position.x
            dy = @destination.y - position.y
            return dx*dx + dy*dy
        end

        def direction_from(position)
            if @destination.x < position.x
                if @destination.y < position.y
                    return UO::NORTH_WEST
                elsif @destination.y > position.y
                    return UO::SOUTH_WEST
                else
                    return UO::WEST
                end
            elsif @destination.x > position.x
                if @destination.y < position.y
                    return UO::NORTH_EAST
                elsif @destination.y > position.y
                    return UO::SOUTH_EAST
                else
                    return UO::EAST
                end
            else
                if @destination.y < position.y
                    return UO::NORTH
                elsif @destination.y > position.y
                    return UO::SOUTH
                else
                    return nil
                end
            end
        end

        def next_walk
            m = @client.player
            return unless m
            position = m.position
            return unless position
            puts "now at #{position.x}, #{position.y}\n"
            direction = direction_from(position)
            if direction == nil
                @client.signal_disconnect(self)
                return
            end
            direction |= UO::RUNNING if distance2(position) >= 4
            @client.walk(direction)
        end

        def on_walk_reject
            @client.signal_disconnect(self)
        end

        def on_walk_ack
            next_walk
        end
    end
end
