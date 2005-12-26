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
    class Blocking
        def initialize(client)
            @client = client
        end

        # thread functions

        def start
            raise "already running" if @thread

            @thread = Thread.new do
                Thread.stop
                begin
                    result = run
                    @client.signal_disconnect(self)
                    if result
                        @client.signal_fire(:on_engine_complete, self)
                    else
                        @client.signal_fire(:on_engine_failed, self)
                    end
                rescue
                    $stderr << $!.message << "\n"
                    $stderr << "    " << $!.backtrace.join("\n    ") << "\n"

                    @client.signal_disconnect(self)
                    @client.signal_fire(:on_engine_failed, self)
                end
            end

            @client.signal_connect(self)

            @thread.wakeup
        end

        def stop
            @client.signal_disconnect(self)

            if @thread
                @thread.kill
                @thread = nil
            end
        end

        def run
            raise "implement this"
        end

        # internal

        def wait_for_signal(sig)
            raise "already waiting" if @waiting
            @waiting = sig
            Thread.stop
            result = @waiting_result
            @waiting_result = nil
            @waiting = nil
            return result
        end

        # signal handlers

        def on_signal(sig, *args)
            if @waiting == sig
                @waiting_result = args
                @thread.wakeup
            end
        end

        def on_equip(item)
            if item.parent == @client.world.serial &&
                    item.layer == 0x15
                
            end
        end

        # blocking functions

        def skills
            raise "wrong thread" unless Thread.current == @thread

            if @client.world.skills.empty?
                # query skills
                @client << UO::Packet::MobileQuery.new(0x05, @client.world.player.serial)
                wait_for_signal(:on_skill_update)
            end

            return @client.world.skills
        end

        def skill_free
            sum = 0
            down = 0
            skills.each_value do
                |skill|
                sum += skill.base
                down += skill.base if skill.lock == UO::SKILL_LOCK_DOWN
            end

            return down if sum >= 700
            return down + 700 - sum
        end

        def backpack
            if @client.world.backpack == nil
                # open paperdoll
                @client << UO::Packet::Use.new(UO::SERIAL_PLAYER | @client.world.player.serial)
                wait_for_signal(:on_equip)
            end

            return @client.world.backpack
        end

        def item_in_backpack(item_id)
            items = @client.world.items_in(backpack)
            if items.empty?
                @client << UO::Packet::Use.new(backpack.serial)
                sleep(2)
                items = @client.world.items_in(backpack)
            end
            items.each do
                |item|
                return item if item.item_id == item_id
            end
            return nil
        end

        def use_and_target(item, target)
            @client << UO::Packet::Use.new(item.serial)
            allow_ground, target_id, flags = wait_for_signal(:on_target)
            @client << UO::Packet::TargetResponse.new(0, target_id, flags, target.serial,
                                                      0xffff, 0xffff, 0xffff, 0)
        end
    end
end
