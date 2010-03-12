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

from uo.serialize import PacketWriter

class Damage:
    def __init__(self, packet):
        self.serial = packet.uint()
        self.amount = packet.ushort()

class MobileStatus:
    def __init__(self, packet):
        self.serial = packet.uint()
        self.name = packet.fixstring(30)
        self.hits = packet.ushort()
        self.hits_max = packet.ushort()
        self.rename = packet.byte()
        self.flags = packet.byte()

        if self.flags >= 0x03:
            self.female = packet.boolean()
            self.stats = (packet.ushort(), packet.ushort(), packet.ushort())
            self.stamina, self.stamina_max = packet.ushort(), packet.ushort()
            self.mana, self.mana_max = packet.ushort(), packet.ushort()
            self.gold = packet.uint()
            self.armor = packet.ushort()
            self.mass = packet.ushort()
            self.stat_cap = packet.ushort()
            # XXX
        else:
            self.female = False
            self.stats = None
            self.stamina, self.stamina_max = None, None
            self.mana, self.mana_max = None, None
            self.gold = None
            self.armor = None
            self.mass = None
            self.stat_cap = None

class WorldItem:
    def __init__(self, packet):
        self.serial = packet.uint()
        self.item_id = packet.ushort()

        self.amount = 0
        if (self.serial & 0x80000000) != 0:
            self.serial &= ~0x80000000
            self.amount = packet.ushort()

        self.x, self.y = packet.ushort(), packet.ushort()

        self.direction = 0
        if (self.x & 0x8000) != 0:
            self.x &= ~0x8000
            self.direction = packet.byte()

        self.z = packet.byte()

        self.hue = 0
        if (self.y & 0x8000) != 0:
            self.y &= ~0x8000
            self.hue = packet.ushort()

        self.flags = 0
        if (self.y & 0x4000) != 0:
            self.y &= ~0x4000
            self.flags = packet.byte()

class LoginConfirm:
    def __init__(self, packet):
        self.serial = packet.uint()
        packet.uint()
        self.body = packet.ushort()
        self.x, self.y, self.z = packet.ushort(), packet.ushort(), packet.ushort()
        self.direction = packet.byte()
        packet.byte()
        packet.uint()
        packet.ushort()
        packet.ushort()
        self.map_width, self.map_height = packet.ushort(), packet.ushort()

class AsciiMessage:
    def __init__(self, packet):
        self.serial = packet.uint()
        self.graphic = packet.ushort()
        self.type = packet.byte()
        self.hue = packet.ushort()
        self.font = packet.ushort()
        self.name = packet.fixstring(30)
        self.text = packet.cstring()

class Delete:
    def __init__(self, packet):
        self.serial = packet.uint()

class MobileUpdate:
    def __init__(self, packet):
        self.serial = packet.uint()
        self.body = packet.ushort()
        packet.byte()
        self.hue = packet.ushort()
        self.flags = packet.byte()
        self.x, self.y = packet.ushort(), packet.ushort()
        packet.ushort()
        self.direction = packet.byte()
        self.z = packet.byte()

class WalkReject:
    def __init__(self, packet):
        self.seq = packet.byte()
        self.x, self.y = packet.ushort(), packet.ushort()
        self.direction = packet.byte()
        self.z = packet.byte()

class WalkAck:
    def __init__(self, packet):
        self.seq = packet.byte()
        self.notoriety = packet.byte()

class OpenContainer:
    def __init__(self, packet):
        self.serial = packet.uint()
        self.gump_id = packet.ushort()

class ContainerItem:
    def __init__(self, packet):
        self.serial = packet.uint()
        self.item_id = packet.ushort()
        packet.byte()
        self.amount = packet.ushort()
        self.x = packet.ushort()
        self.y = packet.ushort()
        self.parent_serial = packet.uint()
        self.hue = packet.ushort()

class EquipItem:
    def __init__(self, packet):
        self.serial = packet.uint()
        self.item_id = packet.ushort()
        packet.byte()
        self.layer = packet.byte()
        self.parent_serial = packet.uint()
        self.hue = packet.ushort()

class SkillValue:
    def __init__(self, id, packet):
        self.id = id
        self.value, self.base = packet.ushort(), packet.ushort()
        self.lock = packet.byte()
        self.cap = packet.ushort()

class SkillUpdate:
    def __init__(self, packet):
        self.skills = []

        type = packet.byte()
        if type == 0x02:
            while True:
                skill_id = packet.ushort()
                if skill_id == 0: break
                self.skills.append(SkillValue(skill_id - 1, packet))
        elif type == 0xdf:
            self.skills.append(SkillValue(packet.ushort(), packet))

class ContainerContent:
    def __init__(self, packet):
        count = packet.ushort()
        self.items = map(lambda x: ContainerItem(packet), range(count))

class LoginComplete:
    def __init__(self, packet):
        pass

class TargetRequest:
    def __init__(self, packet):
        self.allow_ground = packet.boolean()
        self.target_id = packet.uint()
        self.flags = packet.byte()

class MobileMoving:
    def __init__(self, packet):
        self.serial = packet.uint()
        self.body = packet.ushort()
        self.x, self.y, self.z = packet.ushort(), packet.ushort(), packet.byte()
        self.direction = packet.byte()
        self.hue = packet.ushort()
        self.flags = packet.byte()
        self.notoriety = packet.byte()

class MobileItem:
    def __init__(self, serial, packet):
        self.serial = serial
        self.item_id = packet.ushort()
        self.layer = packet.byte()
        if (self.item_id & 0x8000) != 0:
            self.item_id &= ~0x8000
            self.hue = packet.ushort()
        else:
            self.hue = 0

class MobileIncoming(MobileMoving):
    def __init__(self, packet):
        MobileMoving.__init__(self, packet)

        self.items = []
        while True:
            serial = packet.uint()
            if serial == 0: break
            self.items.append(MobileItem(serial, packet))

class MenuOption:
    def __init__(self, packet):
        self.item_id = packet.ushort()
        self.hue = packet.ushort()
        self.text = packet.pstring()

class Menu:
    def __init__(self, packet):
        self.dialog_serial = packet.uint()
        self.menu_serial = packet.ushort()
        self.title = packet.pstring()
        self.options = map(lambda x: MenuOption(packet), range(packet.byte()))

class MovePlayer:
    def __init__(self, packet):
        self.direction = packet.byte()

class Relay:
    def __init__(self, packet):
        self.ip = packet.ipv4()
        self.port = packet.ushort()
        self.auth_id = packet.uint()

class MobileHits:
    def __init__(self, packet):
        self.serial = packet.uint()
        self.hits_max, self.hits = packet.ushort(), packet.ushort()

class MobileMana:
    def __init__(self, packet):
        self.serial = packet.uint()
        self.mana_max, self.mana = packet.ushort(), packet.ushort()

class MobileStamina:
    def __init__(self, packet):
        self.serial = packet.uint()
        self.stamina_max, self.stamina = packet.ushort(), packet.ushort()

class Server:
    def __init__(self, packet):
        self.index = packet.ushort()
        self.name = packet.fixstring(32)
        packet.byte()
        packet.byte()
        packet.uint()

class ServerList:
    def __init__(self, packet):
        packet.byte()
        count = packet.ushort()
        self.servers = map(lambda x: Server(packet), range(count))

class Character:
    def __init__(self, slot, packet):
        self.slot = slot
        self.name = packet.fixstring(30)
        packet.fixstring(30)

class CharacterList:
    def __init__(self, packet):
        count = packet.byte()
        self.characters = map(lambda x: Character(x, packet), range(count))

    def find(self, name):
        for character in self.characters:
            if character.name == name:
                return character
        return None

class Extended:
    def __init__(self, packet):
        self.extended = packet.ushort()
        if self.extended == 0x0019:
            self.extended2 = packet.byte()
            if self.extended2 == 2:
                # statlock info
                self.serial = packet.uint()
                packet.byte()
                lockbits = packet.byte()
                self.stat_locks = ((lockbits >> 4) & 0x3,
                                   (lockbits >> 2) & 0x3,
                                   lockbits & 0x3)

class Ignore:
    def __init__(self, packet):
        pass

parsers = {
    0x0b: Damage,
    0x11: MobileStatus,
    0x1a: WorldItem,
    0x1b: LoginConfirm,
    0x1c: AsciiMessage,
    0x1d: Delete,
    0x20: MobileUpdate,
    0x21: WalkReject,
    0x22: WalkAck,
    0x23: Ignore, # DragAnimation
    0x24: OpenContainer,
    0x25: ContainerItem,
    0x2e: EquipItem,
    0x3a: SkillUpdate,
    0x3c: ContainerContent,
    0x4e: Ignore, # PersonalLight
    0x4f: Ignore, # GlobalLight
    0x54: Ignore, # Sound
    0x55: LoginComplete,
    0x5b: Ignore, # Time
    0x65: Ignore, # Weather
    0x6c: TargetRequest, # Target
    0x6d: Ignore, # PlayMusic
    0x6e: Ignore, # CharAction
    0x72: Ignore, # WarMode
    0x77: MobileMoving,
    0x78: MobileIncoming,
    0x7c: Menu,
    0x8c: Relay,
    0x95: Ignore, # HuePicker
    0x97: MovePlayer,
    0xa1: MobileHits,
    0xa2: MobileMana,
    0xa3: MobileStamina,
    0xa6: Ignore, # Scroll
    0xa8: ServerList,
    0xa9: CharacterList,
    0xb9: Ignore, # Features
    0xbc: Ignore, # Season
    0xbf: Extended,
    0xbd: Ignore, # ClientVersion
    0xc0: Ignore, # HuedEffect
    0xc7: Ignore, # ParticleEffect
    0xdc: Ignore, # AOSObjProp
    0xd6: Ignore, # AOSToolTip
}

def WalkRequest(direction, seq):
    p = PacketWriter(0x02)
    p.byte(direction)
    p.byte(seq)
    p.uint(0)
    return p.finish()

def TalkAscii(type, hue, font, text):
    p = PacketWriter(0x03)
    p.byte(type)
    p.ushort(hue)
    p.ushort(font)
    p.cstring(text)
    return p.finish()

def Use(serial):
    p = PacketWriter(0x06)
    p.uint(serial)
    return p.finish()

def LiftRequest(serial, amount=0xffff):
    p = PacketWriter(0x07)
    p.uint(serial)
    p.ushort(amount)
    return p.finish()

def Drop(serial, x, y, z, dest_serial):
    p = PacketWriter(0x08)
    p.uint(serial)
    p.ushort(x)
    p.ushort(y)
    p.byte(z)
    p.uint(dest_serial)
    return p.finish()

def Click(serial):
    p = PacketWriter(0x09)
    p.uint(serial)
    return p.finish()

def TextCommand(type, command):
    p = PacketWriter(0x12)
    p.byte(type)
    p.cstring(command)
    return p.finish()

def EquipRequest(item_serial, layer, target_serial):
    p = PacketWriter(0x13)
    p.uint(item_serial)
    p.byte(layer)
    p.uint(target_serial)
    return p.finish()

def UseSkill(skill):
    return TextCommand(0x24, str(skill))

def MobileQuery(type, serial):
    p = PacketWriter(0x34)
    p.uint(0xedededed)
    p.byte(type)
    p.uint(serial)
    return p.finish()

def VendorBuyReply(vendor_serial, item_serial, amount=1):
    p = PacketWriter(0x3b)
    p.uint(vendor_serial)
    p.byte(2) # flags
    p.byte(0) # layer
    p.uint(item_serial)
    p.ushort(amount)
    return p.finish()

def PlayCharacter(slot):
    p = PacketWriter(0x5d)
    p.uint(0)
    p.fixstring("", 30)
    p.ushort(0)
    p.uint(0)
    p.fixstring("", 24)
    p.uint(slot)
    p.uint(0xdeadbeef)
    return p.finish()

def TargetResponse(type, target_id, flags, serial, x, y, z, graphic):
    p = PacketWriter(0x6c)
    p.byte(type)
    p.uint(target_id)
    p.byte(flags)
    p.uint(serial)
    p.ushort(x)
    p.ushort(y)
    p.ushort(z)
    p.ushort(graphic)
    return p.finish()

def MenuResponse(serial, index):
    p = PacketWriter(0x7d)
    p.uint(serial)
    p.ushort(0) # menu id
    p.ushort(index)
    p.ushort(0) # item id
    p.ushort(0) # hue
    return p.finish()

def AccountLogin(username, password):
    p = PacketWriter(0x80)
    p.fixstring(username, 30)
    p.fixstring(password, 30)
    p.byte(0)
    return p.finish()

def GameLogin(username, password, auth_id):
    p = PacketWriter(0x91)
    p.uint(auth_id)
    p.fixstring(username, 30)
    p.fixstring(password, 30)
    return p.finish()

def VendorSellReply(vendor_serial, item_serial, amount=1):
    p = PacketWriter(0x9f)
    p.uint(vendor_serial)
    p.ushort(1)
    p.uint(item_serial)
    p.ushort(amount)
    return p.finish()

def PlayServer(index):
    p = PacketWriter(0xa0)
    p.ushort(index)
    return p.finish()

def TalkUnicode(type, hue, font, text):
    p = PacketWriter(0xad)
    p.byte(type)
    p.ushort(hue)
    p.ushort(font)
    p.fixstring('Eng', 4)
    p.byte(0x00)
    p.byte(0x10)
    p.byte(0x02)
    p.cstring(text)
    return p.finish()

def ClientVersion(version):
    p = PacketWriter(0xbd)
    p.ucstring(version)
    return p.finish()

def StatLock(stat, lock):
    p = PacketWriter(0xbf)
    p.ushort(0x001a)
    p.byte(stat)
    p.byte(lock)
    return p.finish()
