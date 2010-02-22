$:.unshift(File.dirname($0))

require 'gemuo/client'
require 'gemuo/engines/main'
require 'gemuo/engines/collect'
require 'gemuo/engines/debug'
require 'gemuo/engines/stack'
require 'gemuo/engines/skills'
require 'gemuo/engines/stats'

raise "syntax: test.rb host port username password charname str dex int" unless ARGV.length == 8

client = GemUO::Client.new(ARGV[0], ARGV[1], nil,
                        ARGV[2], ARGV[3], ARGV[4])

stats_goal = [ARGV[5].to_i, ARGV[6].to_i, ARGV[7].to_i]

pos_bridge_left = GemUO::Position.new(1370, 1749)
pos_bridge_right = GemUO::Position.new(1401, 1749)
pos_left2 = GemUO::Position.new(1318, 1754)
pos_left2 = GemUO::Position.new(1303, 1748)
pos_left3 = GemUO::Position.new(1258, 1748)
karottenfeld1 = GemUO::Position.new(1237, 1738)
onionfeld1 = GemUO::Position.new(1205, 1698)
cottonfeld1 = GemUO::Position.new(1237, 1618)
pearfeld1 = GemUO::Position.new(1165, 1594)
cotton_eingang = GemUO::Position.new(4569, 1480)

engines = []

skills = [ GemUO::SKILL_ANATOMY,
           GemUO::SKILL_ITEM_ID,
           GemUO::SKILL_ARMS_LORE,
           #GemUO::SKILL_DETECT_HIDDEN,
           GemUO::SKILL_EVAL_INT,
           GemUO::SKILL_HIDING,
           #GemUO::SKILL_MUSICIANSHIP,
           #GemUO::SKILL_PEACEMAKING,
           #GemUO::SKILL_SPIRIT_SPEAK,
         ]
engines << GemUO::Engines::EasySkills.new(client, skills)
engines << GemUO::Engines::StatLock.new(client, stats_goal)
# engines << StatSkillJojo.new(client, GemUO::SKILL_ARMSLORE, GemUO::SKILL_ITEMID)
# engines << GemUO::Engines::EntityDump.new(client)
# engines << GemUO::Engines::WalkDump.new(client)

GemUO::Engines::Main.new(client, engines).start

client.run
