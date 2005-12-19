$:.unshift(File.dirname($0) + '/glue')
$:.unshift(File.dirname($0))

require 'uo/client'

raise "syntax: test.rb host port username password" unless ARGV.length == 4

client = UO::Client.new(ARGV[0], ARGV[1], nil,
                        ARGV[2], ARGV[3])
client.run
