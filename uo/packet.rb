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

module UO::Packet
    class Writer
        def initialize(cmd)
            @cmd = cmd
            @data = ''
            byte(@cmd)
            @length = UO.packet_length(@cmd)
            ushort(0xffff) unless @length
        end

        def command
            @cmd
        end

        def uint(d)
            @data << [d].pack('N')
            self
        end
        def ushort(d)
            @data << [d].pack('n')
            self
        end
        def byte(d)
            @data << [d].pack('C')
            self
        end
        def fixstring(d, length)
            raise "too long" if d.length > length
            @data << d
            @data << "\0" * (length - d.length) if d.length < length
        end

        def to_s
            if @length
                raise "invalid length" unless @length == @data.length
            else
                @data[1..2] = [@data.length].pack('n')
            end
            @data
        end
    end

    class Packet
        def initialize(cmd, body)
            @cmd = cmd
            @body = body
            @ext = ushort if @cmd == 0xbf
        end

        def command
            @cmd
        end
        def extended
            raise "Not an extended packet" unless @cmd == 0xbf
            @ext
        end

        def length
            @body.length
        end

        def data(length)
            raise "too short" if length > @body.length
            @body.slice!(0..length-1)
        end
        def uint
            data(4).unpack('N')[0]
        end
        def ushort
            data(2).unpack('n')[0]
        end
        def byte
            raise "too short" if @body.empty?
            @body.slice!(0)
        end
        def fixstring(length)
            data(length).sub(/\0+$/, '')
        end
    end

    class Reader
        def initialize(io)
            @io = io
        end

        def data(length)
            d = @io.sysread(length)
            raise EOFError.new unless d && d.length == length
            return d
        end
        def uint
            data(4).unpack('N')[0]
        end
        def ushort
            data(2).unpack('n')[0]
        end
        def byte
            data(1).unpack('C')[0]
        end

        def read
            cmd = byte
            length = UO.packet_length(cmd)
            if length == 0
                length = ushort - 3
            else
                length -= 1
            end
            return Packet.new(cmd, data(length))
        end
    end

    class PlayCharacter < Writer
        def initialize(slot)
            super(0x5d)
            uint(0)
            fixstring("", 30)
            ushort(0)
            uint(0)
            fixstring("", 24)
            uint(slot)
            uint(0xdeadbeef)
        end
    end

    class AccountLogin < Writer
        def initialize(username, password)
            super(0x80)
            fixstring(username, 30)
            fixstring(password, 30)
            byte(0)
        end
    end

    class GameLogin < Writer
        def initialize(auth_id, username, password)
            super(0x91)
            uint(auth_id)
            fixstring(username, 30)
            fixstring(password, 30)
        end
    end

    class PlayServer < Writer
        def initialize(index)
            super(0xa0)
            ushort(index)
        end
    end
end
