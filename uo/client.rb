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

require 'socket'

require 'uoclient'
require 'uo/packet'
require 'uo/entity'

module UO
    class SignalOnce
        def initialize(handler)
            @handler = handler
        end

        def call(client, sig, *args)
            client.signal_disconnect(sig, self)
            @handler.call(client, sig, *args)
        end
    end

    class Client
        def initialize(host, port, seed, username, password)
            @handlers = []
            @signals = {}

            @username = username
            @password = password

            @entities = {}
            @player = nil

            register do
                |packet|
                handle_packet(packet)
            end

            connect(host, port, seed)

            self << UO::Packet::AccountLogin.new(@username, @password)
        end

        def player
            @player
        end
        def entity(serial)
            @entities[serial]
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
        def each_mobile
            @entities.each_value do
                |entity|
                yield entity if entity.kind_of?(Mobile)
            end
        end

        def signal_connect(sig, &handler)
            sh = @signals[sig]
            sh = @signals[sig] = [] unless sh
            sh << handler
        end
        def signal_connect_once(sig, &handler)
            sh = @signals[sig]
            sh = @signals[sig] = [] unless sh
            sh << SignalOnce.new(handler)
        end
        def signal_disconnect(sig, handler)
            sh = @signals[sig]
            return unless sh
            sh.delete(handler)
            @signals.delete(sig) if sh.empty?
        end
        def signal_fire(sig, *args)
            sh = @signals[sig]
            return unless sh
            sh.each do
                |handler|
                handler.call(self, sig, *args)
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
            @reader = UO::Packet::Reader.new(@io)
            signal_fire(:connect)
        end

        def run
            loop do
                packet = @reader.read
                handled = false
                @handlers.each do
                    |handler|
                    handled ||= handler.call(packet)
                end
                puts "Received unknown #{'0x%02x' % packet.command}\n" unless handled
            end
        end

        def <<(packet)
            raise "not a packet" unless packet.kind_of?(UO::Packet::Writer)
            @io << packet.to_s
            puts "Sent 0x%02x\n" % packet.command
        end

        def register(&handler)
            @handlers << handler
        end
        def register_extended(&handler)
            @extended_handlers << handler
        end

        def handle_packet(packet)
            case packet.command
            when 0x11 # mobile status
                serial = packet.uint
                name = packet.fixstring(30)
                hits, hits_max = packet.ushort, packet.ushort
                rename = packet.byte
                flags = packet.byte
                # XXX

                mobile = @entities[serial]
                mobile = @entities[serial] = Mobile.new(serial) unless mobile
                mobile.name = name

                signal_fire(:mobile_status, mobile)

            when 0x1a # world item
                serial = packet.uint
                item_id = packet.ushort
                amount = packet.ushort
                x, y = packet.ushort, packet.ushort
                direction = packet.byte
                z = packet.length >= 1 ? packet.byte : nil
                hue = packet.length >= 2 ? packet.ushort : nil
                flags = packet.length >= 1 ? packet.byte : nil

                item = @entities[serial]
                item = @entities[serial] = Item.new(serial) unless item
                item.item_id = item_id
                item.hue = hue
                item.position = Position.new(x, y, z, direction)

                signal_fire(:world_item, item)

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

                @entities = {}
                @player = @entities[serial] = Mobile.new(serial)
                @player.body = body
                @player.position = Position.new(x, y, z, direction)

            when 0x1c # speak ascii
                # XXX

            when 0x1d # delete
                serial = packet.uint

                entity = @entities.delete(serial)
                @player = nil if @player && @player.serial == serial

                signal_fire(:delete_entity, entity) if entity

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

                mobile = @entities[serial]
                mobile = @entities[serial] = Mobile.new(serial) unless mobile
                mobile.body = body
                mobile.hue = hue
                mobile.position = Position.new(x, y, z, direction)

            when 0x25 # cont add
                # XXX

            when 0x2e # item equip
                # XXX

            when 0x3a # skill update
                # XXX

            when 0x4e # personal light level
            when 0x4f # global light level
            when 0x54 # sound

            when 0x55 # redraw all
                signal_fire(:ingame)

            when 0x5b # time
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

                mobile = @entities[serial]
                mobile = @entities[serial] = Mobile.new(serial) unless mobile
                oldpos = mobile.position
                mobile.body = body
                mobile.hue = hue
                mobile.position = Position.new(x, y, z, direction)
                mobile.notoriety = notoriety

                signal_fire(:mobile_moving, mobile, oldpos)

            when 0x78 # mobile incoming
                serial = packet.uint
                body = packet.ushort
                x, y, z = packet.ushort, packet.ushort, packet.byte
                direction = packet.byte
                hue = packet.ushort
                flags = packet.byte
                notoriety = packet.byte

                mobile = @entities[serial]
                mobile = @entities[serial] = Mobile.new(serial) unless mobile
                mobile.body = body
                mobile.hue = hue
                mobile.position = Position.new(x, y, z, direction)
                mobile.notoriety = notoriety

                signal_fire(:mobile_incoming, mobile)

            when 0x8c # relay
                ip = packet.data(4).unpack('C4').join('.')
                port = packet.ushort
                auth_id = packet.uint
                puts "relay to #{ip}:#{port}\n"
                connect(ip, port, auth_id)
                puts "after connect\n"
                @reader = UO::Packet::Reader.new(UO::Decompress.new(@io))
                self << UO::Packet::GameLogin.new(auth_id, @username, @password)

            when 0xa1 # StatChngStr
            when 0xa2 # StatChngInt
            when 0xa3 # StatChngDex

            when 0xa8 # server list
                puts "server list:\n"
                packet.byte
                count = packet.ushort
                [1..count].each do
                    index = packet.ushort
                    name = packet.fixstring(32)
                    packet.byte
                    packet.byte
                    packet.uint
                    puts "\t#{name}\n"
                end

                self << UO::Packet::PlayServer.new(0)

            when 0xa9 # char list
                puts "character list:\n"
                count = packet.byte
                [1..count].each do
                    name = packet.fixstring(30)
                    packet.fixstring(30)
                    puts "\t#{name}\n"
                end

                self << UO::Packet::PlayCharacter.new(0)

            when 0xae # speak unicode
                # xXX

            when 0xb9 # supported features
            when 0xbc # season

            when 0xbf # extended
                case packet.extended
                when 0x0008 # map change
                    @map_id = packet.byte

                when 0x0018 # map patch

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
    end
end
