#
# L2VisionGrapher.py
# by zdev
#
# Handles collecting data for graphs.
#
#------------------------------------------------------------------------------

from threading import Thread
from time import sleep
import L2VisionModel

#------------------------------------------------------------------------------
# Grapher thread class

class GrapherThread(Thread):

    def handle_toon_stats(self, toon):
        # keep last 15 minutes worth of stats
        # one every 10 seconds
        # six every minute
        # ninety every 15 minutes

        if len(toon.cp_stats) == 180:
            del toon.cp_stats[0]

        if len(toon.hp_stats) == 180:
            del toon.hp_stats[0]

        if len(toon.mp_stats) == 180:
            del toon.mp_stats[0]

        toon.cp_stats.append(toon.cp_cur)
        toon.hp_stats.append(toon.hp_cur)
        toon.mp_stats.append(toon.mp_cur)

    def handle_time_slice(self):
        lvm = L2VisionModel.get_instance()
        lvm.lock.acquire()
        try:
            for toon in lvm.toons.values():
                self.handle_toon_stats(toon)
        finally:
            lvm.lock.release()

    def run(self):
        self.running = True
        while self.running:
            self.handle_time_slice()
            sleep(10)
