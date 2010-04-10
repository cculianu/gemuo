#
#  GemUO
#
#  (c) 2005-2010 Max Kellermann <max@duempel.org>
#                Kai Sassmannshausen <kai@sassie.org>
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

import uo.packets as p
from gemuo.engine import Engine
from twisted.internet import reactor
from gemuo.error import Timeout

class Buy(Engine):

    def __init__(self, client, itemid, amount):
        Engine.__init__(self, client)
        self.buy_items = list()
        self.vendor = None
        self.itemid = itemid
        self.amount = amount
        self.call_id = reactor.callLater(2, self._timeout)
        self.get_offer()

    def on_packet(self, packet):
        if isinstance(packet, p.ContainerContent):
            self.create_buy_list(packet)
        elif isinstance(packet, p.VendorBuyList):
            self.update_buy_list(packet)
        elif isinstance(packet, p.EquipItem):
            self.get_vendor(packet)
        elif isinstance(packet, p.AsciiMessage):
            self.check_success(packet)

    def get_offer(self):
        self._client.send(p.TalkUnicode("vendor buy", 0x3c))

    def _buy(self, serial):
        if serial is not None:
            self._client.send(p.VendorBuyReply(self.vendor, serial, self.amount))
        else:
            self._failure('No serial')

    def update_buy_list(self, buy_list):
        for bi in self.buy_items:
            for i in buy_list.items:
                if  bi.item_id + 1020000  == int(i.description):
                    bi.price = i.price
                    break
        #self.print_offer()
        self._buy(self.get_item_serial())

    def print_offer(self):
        print "Offer:"
        for i in self.buy_items:
            print "ItemID: " + str(i.item_id) + "\t Amount: " + str(i.amount) \
                + "\t Price: " + str(i.price) + "\t(" + str(i.serial) + ")"  

    def get_vendor(self, packet):
        if packet.layer:
            if packet.layer == 0x1b:
                self.vendor = packet.parent_serial

    def get_item_serial(self):
        for bi in self.buy_items:
            if bi.item_id == self.itemid:
                return bi.serial
        return None

    def create_buy_list(self, container_content):
        for i in container_content.items:
            bi = BuyItem(i.serial, i.item_id, i.amount)
            self.buy_items.append(bi)

    def check_success(self, ascii_message):
        if self.vendor is not None:
            if self.vendor == ascii_message.serial:
                if "The total of thy purchase is" in ascii_message.text:
                    self.call_id.cancel()
                    self._success()
    
    def _timeout(self):
        self._failure(Timeout("Buy timeout"))
    
class Buy_at_price(Buy):

    def __init__(self, client, itemid, amount, price):
       Engine.__init__(self, client)
       self.price = price
       self.buy_items = list()
       self.vendor = None
       self.itemid = itemid
       self.amount = amount
       self.call_id = reactor.callLater(2, self._timeout)
       self.get_offer()

    def get_item_price(self):
        for bi in self.buy_items:
            if bi.item_id == self.itemid:
                return bi.price
        return None

    def _buy(self, serial):
        if serial is not None:
            if self.get_item_price() <= self.price:
                self._client.send(p.VendorBuyReply(self.vendor, serial, self.amount))
            else:
                self._failure("Item is to expensive here: "  + str(self.get_item_price()) + \
                                  "/" + str(self.price))
        else:
            self._failure("No serial")

class BuyItem():
    
    def __init__(self, serial, item_id, amount):
        self.serial = serial
        self.item_id = item_id
        self.amount = amount
        self.price = None

