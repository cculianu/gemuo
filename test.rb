$:.unshift(File.dirname($0) + '/glue')
$:.unshift(File.dirname($0))

require 'uo/client'
require 'uo/engines'

raise "syntax: test.rb host port username password" unless ARGV.length == 4

$client = UO::Client.new(ARGV[0], ARGV[1], nil,
                         ARGV[2], ARGV[3])

class TestTimer < UO::TimerEvent
    def tick
        puts "tick!\n"
    end
end

class Ingame
    def on_ingame
        # UO::Engines::SimpleWalk.new($client, UO::Position.new(1410, 1735))
        # $client.timer << TestTimer.new(10)
    end
end

class WalkDump
    def on_ingame
        puts "UO::Position.new(#{$client.player.position.x}, #{$client.player.position.y})\n"
    end
    def on_walk_ack
        puts "UO::Position.new(#{$client.player.position.x}, #{$client.player.position.y})\n"
    end
    def on_mobile_update(mobile)
        return unless mobile == $client.player
        puts "UO::Position.new(#{$client.player.position.x}, #{$client.player.position.y})\n"
    end
end

class ItemDump
    def on_ingame
        puts "UO::Position.new(#{$client.player.position.x}, #{$client.player.position.y})\n"
    end
    def on_walk_ack
        puts "UO::Position.new(#{$client.player.position.x}, #{$client.player.position.y})\n"
    end
    def on_mobile_update(mobile)
        return unless mobile == $client.player
        puts "UO::Position.new(#{$client.player.position.x}, #{$client.player.position.y})\n"
    end
end

class SkillJojo < UO::TimerEvent
    def initialize(skill1, skill2)
        super()
        @skills = [ skill1, skill2 ]
    end

    def tick
        return unless @current

        # use skill
        $client << UO::Packet::TextCommand.new(0x24, @current.to_s)

        restart(1.5)
        $client.timer << self
    end

    def on_ingame
        # get skills
        $client << UO::Packet::MobileQuery.new(0x05, $client.player.serial)
    end

    def on_skill_update
        if @current
            value = $client.skill(@other)
            if value == nil || value.value == 0
                @current = nil
                @other = nil
            end
        end
            
        unless @current
            # decide which is current
            values = @skills.collect do
                |skill_id|
                value = $client.skill(skill_id)
                unless value
                    puts "Error: no value for skill #{skill_id}\n"
                    return
                end
                value
            end

            if values[0].base < values[1].base
                @current = @skills[0]
                @other = @skills[1]
            else
                @current = @skills[1]
                @other = @skills[0]
            end

            $client << UO::Packet::ChangeSkillLock.new(@current, UO::LOCK_UP)
            $client << UO::Packet::ChangeSkillLock.new(@other, UO::LOCK_DOWN)

            tick
        end
    end

    def find_dagger
        $client.each_item do
            |item|
            #puts "item=0x%x\n" % item.item_id
            return item if item.item_id == 0xf52
        end
        nil
    end

    def on_target(allow_ground, target_id, flags)
        item = find_dagger
        unless item
            puts "Error: no dagger found\n"
            return
        end
        $client << UO::Packet::TargetResponse.new(0, target_id, flags, item.serial,
                                                  0xffff, 0xffff, 0xffff, 0)
    end
end

pos_bridge_left = UO::Position.new(1370, 1749)
pos_bridge_right = UO::Position.new(1401, 1749)
pos_left2 = UO::Position.new(1318, 1754)
pos_left2 = UO::Position.new(1303, 1748)
pos_left3 = UO::Position.new(1258, 1748)
karottenfeld1 = UO::Position.new(1237, 1738)
onionfeld1 = UO::Position.new(1205, 1698)
cottonfeld1 = UO::Position.new(1237, 1618)
pearfeld1 = UO::Position.new(1165, 1594)
cotton_eingang = UO::Position.new(4569, 1480)


$client.signal_connect(Ingame.new)
$client.signal_connect(WalkDump.new)
$client.signal_connect(SkillJojo.new(UO::SKILL_ARMSLORE, UO::SKILL_ITEMID))

$client.run
