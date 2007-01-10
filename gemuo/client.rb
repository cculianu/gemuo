#
#  GemUO
#  $Id$
#
#  (c) 2005-2007 Max Kellermann <max@duempel.org>
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

require 'socket'

require 'gemuo/glue'
require 'gemuo/packet'
require 'gemuo/entity'
require 'gemuo/timer'
require 'gemuo/player'
require 'gemuo/world'

module GemUO
    NORTH = 0x0
    NORTH_EAST = 0x1
    EAST = 0x2
    SOUTH_EAST = 0x3
    SOUTH = 0x4
    SOUTH_WEST = 0x5
    WEST = 0x6
    NORTH_WEST = 0x7
    RUNNING = 0x80

    class Client
        def initialize(host, port, seed, username, password, character)
            @handlers = []
            @signals = []
            @timer = Timer.new

            @username = username
            @password = password
            @character = character

            @world = World.new

            register do
                |packet|
                handle_packet(packet)
            end

            connect(host, port, seed)

            self << GemUO::Packet::AccountLogin.new(@username, @password)
        end

        def timer
            @timer
        end

        def world
            @world
        end

        def delete_recursive(entity)
            @world.delete(entity.serial)

            children = []
            @world.each_item_in(entity) do
                |child|
                children << child
            end

            children.each do
                |child|
                delete_recursive(child)
            end

            signal_fire(:on_delete_entity, entity)
        end

        def signal_connect(handler)
            @signals << handler
        end
        def signal_disconnect(handler)
            @signals.delete(handler)
        end
        def signal_fire(sig, *args)
            @signals.clone.each do
                |handler|
                method = nil
                begin
                    method = handler.method(sig)
                rescue NameError
                end
                method.call(*args) if method

                method = nil
                begin
                    method = handler.method(:on_signal)
                rescue NameError
                end
                method.call(sig, *args) if method if method
            end
        end

        def connect(host, port, seed = nil)
            if @io
                @io.close 
                @io = nil
            end

            @io = TCPSocket.new(host, port)
            # write seed
            @io << [seed||42].pack('N')
            @io.flush
            @reader = GemUO::Packet::Reader.new(@io)
            signal_fire(:on_connect)
        end

        def run
            loop do
                packet = @reader.read
                handled = false
                @handlers.each do
                    |handler|
                    handled ||= handler.call(packet)
                end
                unless handled
                    if packet.command == 0xbf
                        puts "Received unknown 0xbf #{'0x%04x' % packet.extended}\n" 
                    else
                        puts "Received unknown #{'0x%02x' % packet.command}\n"
                    end
                end

                @timer.tick
            end
        end

        def <<(packet)
            raise "not a packet" unless packet.kind_of?(GemUO::Packet::Writer)
            @io << packet.to_s
        end

        def register(&handler)
            @handlers << handler
        end
        def register_extended(&handler)
            @extended_handlers << handler
        end

        def handle_packet(packet)
            case packet.command
            when 0x0b # damage
                serial = packet.uint
                amount = packet.ushort

                mobile = @world.entity(serial)
                signal_fire(:on_damage, mobile, amount) if mobile

            when 0x11 # mobile status
                serial = packet.uint
                name = packet.fixstring(30)
                hits, hits_max = packet.ushort, packet.ushort
                rename = packet.byte
                flags = packet.byte

                mobile = @world.make_mobile(serial)
                mobile.name = name
                mobile.hits = BoundedValue.new(hits, hits_max)

                if flags >= 0x03
                    mobile.female = packet.byte != 0
                    mobile.stats = [packet.ushort, packet.ushort, packet.ushort]
                    mobile.stamina = BoundedValue.new(packet.ushort, packet.ushort)
                    mobile.mana = BoundedValue.new(packet.ushort, packet.ushort)
                    mobile.gold = packet.uint
                    packet.ushort # armor
                    mobile.mass = packet.ushort
                    mobile.stat_cap = packet.ushort
                    # XXX
                end

                signal_fire(:on_mobile_status, mobile)

            when 0x1a # world item
                serial = packet.uint
                item_id = packet.ushort

                amount = 0
                if (serial & 0x80000000) != 0
                    serial &= ~0x80000000
                    amount = packet.ushort
                end

                x, y = packet.ushort, packet.ushort

                direction = 0
                if (x & 0x8000) != 0
                    x &= ~0x8000
                    direction = packet.byte
                end

                z = packet.byte

                hue = 0
                if (y & 0x8000) != 0
                    y &= ~0x8000
                    hue = packet.ushort
                end

                flags = 0
                if (y & 0x4000) != 0
                    y &= ~0x4000
                    flags = packet.byte
                end

                item = @world.new_item(serial)
                item.item_id = item_id
                item.amount = amount
                item.hue = hue
                item.position = Position.new(x, y, z, direction)

                signal_fire(:on_world_item, item)

            when 0x1b # start
                serial = packet.uint
                packet.uint
                body = packet.ushort
                x, y, z = packet.ushort, packet.ushort, packet.ushort
                direction = packet.byte
                packet.byte
                packet.uint
                packet.ushort
                packet.ushort
                @map_width, @map_height = packet.ushort, packet.ushort

                @world = World.new
                player = @world.player = @world.make_mobile(serial)
                player.body = body
                player.position = Position.new(x, y, z, direction)

            when 0x1c # speak ascii
                # XXX

            when 0x1d # delete
                serial = packet.uint

                entity = world.entity(serial)
                delete_recursive(entity) if entity

            when 0x20 # mobile update
                serial = packet.uint
                body = packet.ushort
                packet.byte
                hue = packet.ushort
                flags = packet.byte
                x, y = packet.ushort, packet.ushort
                packet.ushort
                direction = packet.byte
                z = packet.byte

                mobile = @world.make_mobile(serial)
                mobile.body = body
                mobile.hue = hue
                mobile.position = Position.new(x, y, z, direction)

                signal_fire(:on_mobile_update, mobile)

            when 0x21 # walk reject
                seq = packet.byte
                x, y = packet.ushort, packet.ushort
                direction = packet.byte
                z = packet.byte
                @world.walk.walk_reject(seq, x, y, z, direction) if @world.get_walk

                signal_fire(:on_walk_reject) if @world.player

            when 0x22 # walk ack
                seq, notoriety = packet.byte, packet.byte
                @world.get_walk.walk_ack(seq, notoriety) if @world.get_walk

                signal_fire(:on_walk_ack) if @world.player

            when 0x23 # drag effect

            when 0x24 # container open
                serial = packet.uint
                gump_id = packet.ushort

                entity = @world.entity(serial)
                entity.gump_id = gump_id if entity

            when 0x25 # container update
                serial = packet.uint
                item_id = packet.ushort
                packet.byte
                amount = packet.ushort
                x = packet.ushort
                y = packet.ushort
                parent_serial = packet.uint
                hue = packet.ushort

                item = @world.new_item(serial)
                item.item_id = item_id
                item.hue = hue
                item.parent = parent_serial
                item.amount = amount
                item.position = Position.new(x, y)

                signal_fire(:on_container_update, item)

            when 0x27 # lift reject
                reason = packet.byte

                signal_fire(:on_lift_reject, reason)

            when 0x2e # equip
                serial = packet.uint
                item_id = packet.ushort
                packet.byte
                layer = packet.byte
                parent_serial = packet.uint
                hue = packet.ushort

                item = @world.new_item(serial)
                item.item_id = item_id
                item.hue = hue
                item.parent = parent_serial
                item.layer = layer

                signal_fire(:on_equip, item)

            when 0x3a # skill update
                type = packet.byte
                case type
                when 0x02
                    while (skill_id = packet.ushort) > 0
                        skill_id -= 1
                        value, base = packet.ushort, packet.ushort
                        lock = packet.byte
                        cap = packet.ushort
                        @world.skills[skill_id] = SkillValue.new(skill_id, value, base, lock, cap)
                    end

                when 0xdf
                    skill_id = packet.ushort
                    value, base = packet.ushort, packet.ushort
                    lock = packet.byte
                    cap = packet.ushort
                    @world.skills[skill_id] = SkillValue.new(skill_id, value, base, lock, cap)

                else
                    puts "unknown skill_update #{type}\n"
                end

                signal_fire(:on_skill_update)

            when 0x3c # container content
                num = packet.ushort
                (1..num).each do
                    serial = packet.uint
                    item_id = packet.ushort
                    packet.byte
                    amount = packet.ushort
                    x = packet.ushort
                    y = packet.ushort
                    parent_serial = packet.uint
                    hue = packet.ushort

                    item = @world.new_item(serial)
                    item.item_id = item_id
                    item.hue = hue
                    item.parent = parent_serial
                    item.amount = amount
                    item.position = Position.new(x, y)

                    signal_fire(:on_container_update, item)
                end

            when 0x4e # personal light level
            when 0x4f # global light level
            when 0x54 # sound

            when 0x55 # redraw all
                signal_fire(:on_ingame)

            when 0x5b # time
            when 0x65 # wheather

            when 0x6c # target
                allow_ground = packet.bool
                target_id = packet.uint
                flags = packet.byte
                signal_fire(:on_target, allow_ground, target_id, flags)

            when 0x6e # char action

            when 0xb0 # gump dialog
                # XXX close gump

            when 0x72 # war mode

            when 0x77 # mobile moving
                serial = packet.uint
                body = packet.ushort
                x, y, z = packet.ushort, packet.ushort, packet.byte
                direction = packet.byte
                hue = packet.ushort
                flags = packet.byte
                notoriety = packet.byte

                mobile = @world.make_mobile(serial)
                oldpos = mobile.position
                mobile.body = body
                mobile.hue = hue
                mobile.position = Position.new(x, y, z, direction)
                mobile.notoriety = notoriety

                signal_fire(:on_mobile_moving, mobile, oldpos)

            when 0x78 # mobile incoming
                serial = packet.uint
                body = packet.ushort
                x, y, z = packet.ushort, packet.ushort, packet.byte
                direction = packet.byte
                hue = packet.ushort
                flags = packet.byte
                notoriety = packet.byte

                mobile = @world.make_mobile(serial)
                mobile.body = body
                mobile.hue = hue
                mobile.position = Position.new(x, y, z, direction)
                mobile.notoriety = notoriety

                while (serial = packet.uint) != 0
                    item = world.new_item(serial)
                    item.parent = mobile.serial
                    item_id = packet.ushort
                    item.layer = packet.byte
                    if (item_id & 0x8000) == 0
                        item.hue = 0
                    else
                        item.hue = packet.ushort
                        item_id &= ~0x8000
                    end
                    item.item_id = item_id
                end

                signal_fire(:on_mobile_incoming, mobile)

            when 0x82 # account login reject
                reason = packet.byte
                puts "account login reject: reason=#{reason}"
                exit(2)

            when 0x8c # relay
                ip = packet.data(4).unpack('C4').join('.')
                port = packet.ushort
                auth_id = packet.uint
                puts "relay to #{ip}:#{port}\n"
                connect(ip, port, auth_id)
                puts "after connect\n"
                @reader = GemUO::Packet::Reader.new(GemUO::Decompress.new(@io))
                self << GemUO::Packet::GameLogin.new(auth_id, @username, @password)

            when 0xa1 # mobile hits
                serial = packet.uint
                hits_max, hits = packet.ushort, packet.ushort

                mobile = @world.make_mobile(serial)
                mobile.hits = BoundedValue.new(hits, hits_max)

                signal_fire(:on_mobile_hits, mobile)

            when 0xa2 # mobile mana
                serial = packet.uint
                mana, mana_max = packet.ushort, packet.ushort

                mobile = @world.make_mobile(serial)
                mobile.mana = BoundedValue.new(mana, mana_max)

                signal_fire(:on_mobile_mana, mobile)

            when 0xa3 # mobile stamina
                serial = packet.uint
                stamina, stamina_max = packet.ushort, packet.ushort

                mobile = @world.make_mobile(serial)
                mobile.stamina = BoundedValue.new(stamina, stamina_max)

                signal_fire(:on_mobile_stamina, mobile)

            when 0xa8 # server list
                puts "server list:\n"
                packet.byte
                count = packet.ushort
                (1..count).each do
                    index = packet.ushort
                    name = packet.fixstring(32)
                    packet.byte
                    packet.byte
                    packet.uint
                    puts "\t#{name}\n"
                end

                self << GemUO::Packet::PlayServer.new(0)

            when 0xa9 # char list
                puts "character list:\n"
                count = packet.byte
                @characters = []
                (1..count).each do
                    name = packet.fixstring(30)
                    packet.fixstring(30)
                    if name != ''
                        puts "\t#{name}\n"
                        @characters << name
                    end
                end

                index = @characters.index(@character)
                raise "character #{@character} not in list" unless index

                self << GemUO::Packet::PlayCharacter.new(index)

            when 0xae # speak unicode
                # xXX

            when 0xb9 # supported features
            when 0xbc # season

            when 0xbf # extended
                case packet.extended
                when 0x0008 # map change
                    @map_id = packet.byte

                when 0x0010 # equipment info

                when 0x0018 # map patch

                when 0x0019
                    case packet.byte
                    when 2 # statlock info
                        serial = packet.uint
                        packet.byte
                        lockbits = packet.byte
                        mobile = @world.make_mobile(serial)
                        mobile.stat_locks = [(lockbits >> 4) & 0x3,
                                             (lockbits >> 2) & 0x3,
                                             lockbits & 0x3]

                        signal_fire(:on_stat_lock, mobile)

                    end

                else
                    return false
                end

                return true

            when 0xc0 # UnkHuedEffect
            when 0xc1 # SpeakTable

            else
                return false
            end

            return true
        end

        def walk(direction)
            return unless @world.get_walk
            packet = @world.get_walk.walk(direction)
            self << packet if packet
            return packet != nil
        end
    end
end
