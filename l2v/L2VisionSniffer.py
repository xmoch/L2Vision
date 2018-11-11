#
# L2VisionSniffer.py
# by zdev
#
# Handles threading.
#
#------------------------------------------------------------------------------

from threading import Thread
from time import sleep
import array
import socket
import struct
import time
import L2VisionModel

#------------------------------------------------------------------------------
# Sniffer thread class

class SnifferThread(Thread):

    def read_int16(self, msg, offset):
        value = (struct.unpack_from('<h', msg, offset))[0]
        offset = offset + 2
        return (value, offset)

    def read_uint16(self, msg, offset):
        value = (struct.unpack_from('<H', msg, offset))[0]
        offset = offset + 2
        return (value, offset)

    def read_int32(self, msg, offset):
        value = (struct.unpack_from('<i', msg, offset))[0]
        offset = offset + 4
        return (value, offset)

    def read_uint32(self, msg, offset):
        value = (struct.unpack_from('<I', msg, offset))[0]
        offset = offset + 4
        return (value, offset)

    def read_int64(self, msg, offset):
        value = (struct.unpack_from('<q', msg, offset))[0]
        offset = offset + 8
        return (value, offset)

    def read_uint64(self, msg, offset):
        value = (struct.unpack_from('<Q', msg, offset))[0]
        offset = offset + 8
        return (value, offset)

    def read_string(self, msg, offset):
        s = array.array('c')
        while offset < len(msg):
            c = struct.unpack_from('<cx', msg, offset)
            offset += 2
            if ord(c[0]) == 0:
                break
            else:
                s.append(c[0])
        return (s.tostring(), offset)

    def calc_vital_lows(self, toon):
        if toon.cp_cur < toon.cp_lowest:
            toon.cp_lowest = toon.cp_cur
            toon.cp_lowest_time = time.time()

        if toon.hp_cur < toon.hp_lowest:
            toon.hp_lowest = toon.hp_cur
            toon.hp_lowest_time = time.time()

        if toon.mp_cur < toon.mp_lowest:
            toon.mp_lowest = toon.mp_cur
            toon.mp_lowest_time = time.time()


    def handle_char_info_packet(self, msg, offset, toon):
        hp_cur = 0
        hp_max = 0
        (toon.xp, offset) = self.read_uint64(msg, offset)
        (toon.sp, offset) = self.read_uint64(msg, offset)
        (toon.cp_max, offset) = self.read_uint32(msg, offset)
        (toon.cp_cur, offset) = self.read_uint32(msg, offset)
        (hp_max, offset) = self.read_uint32(msg, offset)
        (hp_cur, offset) = self.read_uint32(msg, offset)
        (toon.mp_max, offset) = self.read_uint32(msg, offset)
        (toon.mp_cur, offset) = self.read_uint32(msg, offset)
        (toon.x, offset) = self.read_int32(msg, offset)
        (toon.y, offset) = self.read_int32(msg, offset)
        (toon.z, offset) = self.read_int32(msg, offset)

        if hp_cur < 100000 and hp_max < 100000:
            toon.hp_cur = hp_cur
            toon.hp_max = hp_max

        self.calc_vital_lows(toon)

        # if xp/sp are zero, that means we have not received any packets
        # yet or the stats were reset, so in that case, use the current
        # xp/sp as the basis point

        if toon.starting_xp == 0 and toon.starting_sp == 0:
            toon.starting_xp = toon.xp
            toon.starting_sp = toon.sp

        # calculate some statistics for later display

        if toon.last_info_ping:
            interval = time.time() - toon.last_info_ping
            toon.accrued_hunting_time = toon.accrued_hunting_time + interval
        toon.last_info_ping = time.time()

    def handle_updated_item_packet(self, msg, offset, toon):
        (item_id, offset) = self.read_uint64(msg, offset)
        (quantity, offset) = self.read_uint64(msg, offset)
        (item_name, offset) = self.read_string(msg, offset)

        item = L2VisionModel.InventoryItem(item_name, item_id, quantity)

        # if item doesn't exist, that means we have not received any packets
        # yet or the stats were reset, so in that case, use the current
        # item quantity as the basis point
        try:
            starting_item = toon.starting_items[item_id]
        except KeyError:
            toon.starting_items[item_id] = item
        toon.current_items[item_id] = item

    def handle_added_item_packet(self, msg, offset, toon):
        (item_id, offset) = self.read_uint64(msg, offset)
        (quantity, offset) = self.read_uint64(msg, offset)
        (item_name, offset) = self.read_string(msg, offset)

        item = L2VisionModel.InventoryItem(item_name, item_id, quantity)

        # if item doesn't exist, that means we have not received any packets
        # yet or the stats were reset, so in that case, use the current
        # item quantity as the basis point
        try:
            starting_item = toon.starting_items[item_id]
        except KeyError:
            sitem = L2VisionModel.InventoryItem(item_name, item_id, 0)
            toon.starting_items[item_id] = sitem
        toon.current_items[item_id] = item

    def handle_removed_item_packet(self, msg, offset, toon):
        (item_id, offset) = self.read_uint64(msg, offset)
        (quantity, offset) = self.read_uint64(msg, offset)
        (item_name, offset) = self.read_string(msg, offset)

        item = L2VisionModel.InventoryItem(item_name, item_id, 0)

        # if item doesn't exist, that means we have not received any packets
        # yet or the stats were reset, so in that case, use the current
        # item quantity as the basis point
        try:
            starting_item = toon.starting_items[item_id]
        except KeyError:
            sitem = L2VisionModel.InventoryItem(item_name, item_id, 1)
            toon.starting_items[item_id] = sitem
        toon.current_items[item_id] = item

    def handle_hilite_item_packet(self, msg, offset, toon):
        (item_id, offset) = self.read_uint64(msg, offset)
        (hilite, offset) = self.read_uint32(msg, offset)
        (item_name, offset) = self.read_string(msg, offset)

        if hilite == 0:
            try:
                toon.hilite_items.pop(item_id)
            except:
                pass
        else:
            toon.hilite_items[item_id] = item_name

    def handle_consumable_item_packet(self, msg, offset, toon):
        (item_id, offset) = self.read_uint64(msg, offset)
        (consumable, offset) = self.read_uint32(msg, offset)
        (item_name, offset) = self.read_string(msg, offset)

        if consumable == 0:
            try:
                toon.consumable_items.pop(item_id)
            except:
                pass
        else:
            toon.consumable_items[item_id] = item_name

    def handle_killed_mob_packet(self, msg, offset, toon):
        (mob_id, offset) = self.read_uint64(msg, offset)
        (mob_name, offset) = self.read_string(msg, offset)

        try:
            mob = toon.mobs[mob_id]
            mob.kills = mob.kills + 1
        except KeyError:
            mob = L2VisionModel.Mob(mob_name, mob_id, 1)
            toon.mobs[mob_id] = mob

    def handle_hilite_mob_packet(self, msg, offset, toon):
        (mob_id, offset) = self.read_uint64(msg, offset)
        (hilite, offset) = self.read_uint32(msg, offset)
        (mob_name, offset) = self.read_string(msg, offset)

        if hilite == 0:
            try:
                toon.hilite_mobs.pop(mob_id)
            except:
                pass
        else:
            toon.hilite_mobs[mob_id] = mob_name

    def handle_chat_packet(self, msg, offset, toon):
        (type, offset) = self.read_uint32(msg, offset)
        (name, offset) = self.read_string(msg, offset)
        (text, offset) = self.read_string(msg, offset)

        msg = L2VisionModel.Msg(type, name, text, time.time())
        toon.msgs.append(msg)

    def handle_visitor_packet(self, msg, offset, toon):
        (name, offset) = self.read_string(msg, offset)

        visitor = L2VisionModel.Visitor(name, time.time())
        toon.visitors[name] = visitor

    def handle_L2Net_packet(self, msg, offset, toon):
        hp_max = 0
        hp_cur = 0
        (toon.cp_max, offset) = self.read_uint32(msg, offset)
        (toon.cp_cur, offset) = self.read_uint32(msg, offset)
        (hp_max, offset) = self.read_uint32(msg, offset)
        (hp_cur, offset) = self.read_uint32(msg, offset)
        (toon.mp_max, offset) = self.read_uint32(msg, offset)
        (toon.mp_cur, offset) = self.read_uint32(msg, offset)
        (ignore, offset) = self.read_uint32(msg, offset)
        (ignore, offset) = self.read_uint32(msg, offset)
        (ignore, offset) = self.read_uint32(msg, offset)
        (ignore, offset) = self.read_uint32(msg, offset)

        if hp_cur < 100000 and hp_max < 100000:
            toon.hp_cur = hp_cur
            toon.hp_max = hp_max

        self.calc_vital_lows(toon)

    def handle_packet(self, msg):
        offset = 0

        (type, offset) = self.read_uint32(msg, offset)
        (name, offset) = self.read_string(msg, offset)
        (char_id, offset) = self.read_uint32(msg, offset)

        lvm = L2VisionModel.get_instance()
        lvm.lock.acquire()
        try:
            if type != 0 and type != 2:
                # type 0 : update packets from L2.Net
                # type 1 : script UDP packets
                # type 2 : script BB UDP packets
                # type 3 : NPC update packets
                #
                # we're interested in the type 0 update packet from L2.Net as well
                # as the type 2 script BB packets coming from the L2Vision.l2s script
                return

            # for script BB packets, check that it is ours and if not, ignore
            if type == 2:
                (magic, offset) = self.read_uint32(msg, offset)
                if magic != 98765:
                    # not one of our user packets
                    return

            # L2.Net update packets report data on other party members as well.
            # So we need to read out the name and char_id from inside
            # the packet.
            if type == 0:
                (name, offset) = self.read_string(msg, offset)
                (char_id, offset) = self.read_uint32(msg, offset)

            # check if the toon has been registered already and if not
            # create a new char model class for it and stick it in
            # our list of toons
            try:
                toon = lvm.toons[name]
            except KeyError:
                toon = L2VisionModel.CharModel(name, char_id)
                toon.first_ping = time.time()
                lvm.toons[name] = toon

            # L2.Net packet
            if type == 0:
                self.handle_L2Net_packet(msg, offset, toon)
            else:
                toon.last_ping = time.time()

                (our_pkt_type, offset) = self.read_uint32(msg, offset)
                if our_pkt_type == 1:
                    self.handle_char_info_packet(msg, offset, toon)
                elif our_pkt_type == 2:
                    self.handle_updated_item_packet(msg, offset, toon)
                elif our_pkt_type == 3:
                    self.handle_killed_mob_packet(msg, offset, toon)
                elif our_pkt_type == 4:
                    self.handle_hilite_item_packet(msg, offset, toon)
                elif our_pkt_type == 5:
                    self.handle_hilite_mob_packet(msg, offset, toon)
                elif our_pkt_type == 6:
                    self.handle_consumable_item_packet(msg, offset, toon)
                elif our_pkt_type == 7:
                    self.handle_added_item_packet(msg, offset, toon)
                elif our_pkt_type == 8:
                    self.handle_removed_item_packet(msg, offset, toon)
                elif our_pkt_type == 9:
                    self.handle_chat_packet(msg, offset, toon)
                elif our_pkt_type == 10:
                    self.handle_visitor_packet(msg, offset, toon)
        finally:
            lvm.lock.release()

    def run(self):
        # setup our listener to bind on all interfaces listening
        # for the UDP packets coming from L2.Net
        sniff_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try :
            sniff_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sniff_sock.bind(("", 33801))
            sniff_sock.setblocking(0)

            # run until main thread tells us to stop by setting the running
            # var to False
            self.running = True
            while self.running:
                try:
                    msg = sniff_sock.recv(65536)
                    self.handle_packet(msg)
                except socket.error:
                    sleep(1)
        finally:
            sniff_sock.close()
