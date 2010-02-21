$:.unshift(File.dirname($0))

require 'gemuo/simple'
require 'gemuo/engines/skills'
require 'gemuo/engines/stats'
#require 'gemuo/engines/use'
require 'gemuo/engines/debug'

client = GemUO::SimpleClient.new

skills = [ GemUO::SKILL_PROVOCATION,
           GemUO::SKILL_PROVOCATION,
           GemUO::SKILL_PEACEMAKING,
         ]
GemUO::Engines::StatLock.new(client, [100, 25, 100]).start
GemUO::Engines::EasySkills.new(client, skills).start
#GemUO::Engines::Use.new(client, 0xe9c).start # drums
GemUO::Engines::MessageDump.new(client).start

client.run
