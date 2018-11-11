#
# L2VisionModel.py
# by zdev
#
# Contains all the data.
#
#------------------------------------------------------------------------------

from threading import Lock

#------------------------------------------------------------------------------
# Version String

_version = "v0.50"

#------------------------------------------------------------------------------
# XP table

xp_table = (
    -1,
    0,
    68,
    363,
    1168,
    2884,
    6038,
    11287,
    19423,
    31378,
    48229, # lvl 10
    71201,
    101676,
    141192,
    191452,
    254327,
    331864,
    426284,
    539995,
    675590,
    835854, # lvl 20
    1023775,
    1242536,
    1495531,
    1786365,
    2118860,
    2497059,
    2925229,
    3407873,
    3949727,
    4555766, # lvl 30
    5231213,
    5981539,
    6812472,
    7729999,
    8740372,
    9850111,
    11066012,
    12395149,
    13844879,
    15422851, # lvl 40
    17137002,
    18995573,
    21007103,
    23180442,
    25524751,
    28049509,
    30764519,
    33679907,
    36806133,
    40153995, # lvl 50
    45524865,
    51262204,
    57383682,
    63907585,
    70852742,
    80700339,
    91162131,
    102265326,
    114038008,
    126509030, # lvl 60
    146307211,
    167243291,
    189363788,
    212716741,
    237351413,
    271973532,
    308441375,
    346825235,
    387197529,
    429632402, # lvl 70
    474205751,
    532692055,
    606319094,
    696376867,
    804219972,
    931275828,
    1151275834,
    1511275834,
    2099275834,
    4200000000, # lvl 80
    6300000000,
    8820000000,
    11844000000,
    15472800000,
    19827360000,
    25314000000L)

#------------------------------------------------------------------------------
# Singleton get method

def get_instance():
    global _l2v_world_model
    return _l2v_world_model

#------------------------------------------------------------------------------
# XP calculation method

def get_level(xp):
    global xp_table

    lvl = 0
    while lvl + 1 < len(xp_table):
        if xp < xp_table[lvl + 1]:
            break
        lvl = lvl + 1

    previous_lvl_xp = xp_table[lvl]
    next_lvl_xp = xp_table[lvl + 1]
    
    lvl_pct = (float(xp - previous_lvl_xp) * 100) / float(next_lvl_xp - previous_lvl_xp)

    return (lvl, lvl_pct)

#------------------------------------------------------------------------------
# XP needed for next level

def get_xp_needed_for_next_lvl(xp):
    global xp_table

    lvl = 0
    while lvl + 1 < len(xp_table):
        if xp < xp_table[lvl + 1]:
            break
        lvl = lvl + 1

    previous_lvl_xp = xp_table[lvl]
    next_lvl_xp = xp_table[lvl + 1]

    return next_lvl_xp - xp

#------------------------------------------------------------------------------
# XP pct that is represented by the given amount of xp

def get_pct_for_xp(cur_xp, xp):
    global xp_table

    lvl = 0
    while lvl + 1 < len(xp_table):
        if cur_xp < xp_table[lvl + 1]:
            break
        lvl = lvl + 1

    previous_lvl_xp = xp_table[lvl]
    next_lvl_xp = xp_table[lvl + 1]
    
    lvl_pct = float(xp * 100) / float(next_lvl_xp - previous_lvl_xp)

    return lvl_pct

#------------------------------------------------------------------------------
# WorldModel class

class WorldModel():

    def __init__(self):
        self.lock = Lock()
        self.toons = {}

#------------------------------------------------------------------------------
# InventoryItem class

class InventoryItem():
    def __init__(self, name, item_id, quantity):
        self.name = name
        self.item_id = item_id
        self.quantity = quantity

#------------------------------------------------------------------------------
# Mob class

class Mob():
    def __init__(self, name, mob_id, kills):
        self.name = name
        self.mob_id = mob_id
        self.kills = kills

#------------------------------------------------------------------------------
# Msg class

class Msg():
    def __init__(self, type, name, text, timestamp):
        # type 0 - local
        # type 2 - pm
        self.type = type
        self.name = name
        self.text = text
        self.timestamp = timestamp

#------------------------------------------------------------------------------
# Visitor class

class Visitor():
    def __init__(self, name, timestamp):
        self.name = name
        self.timestamp = timestamp

#------------------------------------------------------------------------------
# CharModel class

class CharModel():

    def __init__(self, name, char_id):
        self.name = name
        self.char_id = char_id

        self.hp_cur = 0
        self.hp_max = 0
        self.mp_cur = 0
        self.mp_max = 0
        self.cp_cur = 0
        self.cp_max = 0
        self.x = 0
        self.y = 0
        self.z = 0

        self.xp = 0
        self.sp = 0
        self.starting_xp = 0
        self.starting_sp = 0

        self.starting_items = {}
        self.current_items = {}
        self.mobs = {}
        self.hilite_items = {}
        self.hilite_mobs = {}
        self.consumable_items = {}
        self.msgs = []
        self.visitors = {}

        self.cp_lowest = 1000000000
        self.hp_lowest = 1000000000
        self.mp_lowest = 1000000000
        self.cp_lowest_time = None
        self.hp_lowest_time = None
        self.mp_lowest_time = None

        self.last_ping = None
        self.first_ping = None
        self.last_info_ping = None
        self.accrued_hunting_time = 0

        self.cp_stats = []
        self.hp_stats = []
        self.mp_stats = []
        for i in range(0, 180):
            self.cp_stats.append(0)
            self.hp_stats.append(0)
            self.mp_stats.append(0)

#------------------------------------------------------------------------------
# Globals

_l2v_world_model = WorldModel()

