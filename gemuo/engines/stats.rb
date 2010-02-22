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

require 'gemuo/engines/base'

module GemUO::Engines
    class StatLock < Base
        def initialize(client, goal)
            super(client)
            @goal = goal
        end

        def on_ingame
            check_stats
        end

        def set_lock(stat, lock)
            if @locks[stat] != lock
                puts "Setting stat lock #{GemUO::STAT_NAMES[stat]} to #{GemUO::LOCK_NAMES[lock]}\n"
                @client << GemUO::Packet::StatLock.new(stat, lock)
            end
        end

        def check_stats
            player = @client.world.player
            return unless player

            cap = player.stat_cap || 225
            stats = player.stats || [0, 0, 0]
            @locks = player.stat_locks || [nil, nil, nil]
            sum = stats[0] + stats[1] + stats[2]

            unless @locks
                puts "no stat lock info available\n"
                return
            end

            if sum < cap
                (0..2).each do
                    |stat|
                    set_lock(stat, GemUO::LOCK_UP)
                end
                return
            end

            complete = true

            (0..2).each do
                |stat|
                if stats[stat] > @goal[stat]
                    set_lock(stat, GemUO::LOCK_DOWN)
                    complete = false
                elsif stats[stat] < @goal[stat]
                    set_lock(stat, GemUO::LOCK_UP)
                    complete = false
                else
                    set_lock(stat, GemUO::LOCK_LOCKED)
                end
            end

            if complete
                stop
                @client.signal_fire(:on_engine_complete, self)
            end
        end

        def on_mobile_status(mobile)
            check_stats if mobile == @client.world.player
        end
    end
end
