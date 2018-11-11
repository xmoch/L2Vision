#
# views.py
# by zdev
#
# Handles HTTP requests
#
#------------------------------------------------------------------------------

from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
import L2VisionModel
import copy
import time

#------------------------------------------------------------------------------

def render(template, data):
    data['version'] = L2VisionModel._version
    return render_to_response(template, data)

#------------------------------------------------------------------------------

def index(request):
    lvm = L2VisionModel.get_instance()
    lvm.lock.acquire()
    try:
        toons = []
        for toon in lvm.toons.values():
            toons.append(toon.name)
    finally:
        lvm.lock.release()
    return render('l2v/templates/index.html', { 'toons' : toons })

#------------------------------------------------------------------------------

def calc_bar_widths(cv, mv):
    if cv == mv:
        cbl = 8
        cbm = 194
        cbr = 8
    elif cv == 0:
        cbl = 0
        cbm = 0
        cbr = 0
    else:
        cbl = 0
        cbm = 0
        cbr = 0
        if mv > 0:
            pct = (cv * 100) / mv
            bpw = (210 * pct) / 100
            if bpw < 8:
                cbl = bpw
            else:
                cbl = 8
            if bpw > 202:
                cbr = bpw - 202
            else:
                cbr = 0
            if bpw > 8:
                cbm = bpw - 8
    return (cbl, cbm, cbr)

#------------------------------------------------------------------------------

class InventoryItemForDisplay():
    def __init__(self, name):
        self.name = name
        self.hilite = False
        self.starting_count = 0
        self.current_count = 0
        self.difference = 0
        self.consumable = False
        self.rate = 'n/a'

#------------------------------------------------------------------------------

class MobForDisplay():
    def __init__(self, name):
        self.name = name
        self.hilite = False
        self.kills = 0

#------------------------------------------------------------------------------

class MsgForDisplay():
    def __init__(self, type, name, text, timestamp):
        self.type = type
        self.name = name
        self.text = text
        self.timestamp = time.strftime('%b %d %H:%M:%S', time.localtime(timestamp))
        self.cls = "%d" % type

#------------------------------------------------------------------------------

class VisitorForDisplay():
    def __init__(self, name, timestamp):
        self.name = name
        self.timestamp = time.strftime('%b %d %H:%M:%S', time.localtime(timestamp))

#------------------------------------------------------------------------------

def get_duration(t):
    seconds = long(t)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    minutes = long(minutes)
    hours = long(hours)
    days = long(days)
    return "%02d:%02d:%02d:%02d" % (days, hours, minutes, seconds)

#------------------------------------------------------------------------------

def insert_system_data(toon, data):
    data['current_time'] = time.strftime('%b %d %H:%M:%S')
    data['last_ping'] = time.strftime('%b %d %H:%M:%S', time.localtime(toon.last_ping))
    data['first_ping'] = time.strftime('%b %d %H:%M:%S', time.localtime(toon.first_ping))

#------------------------------------------------------------------------------

def insert_vital_data(toon, data):
    data['name'] = toon.name
    lvl, lvl_pct = L2VisionModel.get_level(toon.xp)
    data['lvl'] = lvl
    data['lvl_pct'] = '%0.2f%%' % lvl_pct
    data['cp_cur'] = toon.cp_cur
    data['cp_max'] = toon.cp_max
    data['hp_cur'] = toon.hp_cur
    data['hp_max'] = toon.hp_max
    data['mp_cur'] = toon.mp_cur
    data['mp_max'] = toon.mp_max
    data['cp_lowest'] = toon.cp_lowest
    data['hp_lowest'] = toon.hp_lowest
    data['mp_lowest'] = toon.mp_lowest
    data['cp_lowest_time'] = time.strftime('%b %d %H:%M:%S', time.localtime(toon.cp_lowest_time))
    data['hp_lowest_time'] = time.strftime('%b %d %H:%M:%S', time.localtime(toon.hp_lowest_time))
    data['mp_lowest_time'] = time.strftime('%b %d %H:%M:%S', time.localtime(toon.mp_lowest_time))
    data['xp'] = toon.xp
    data['sp'] = toon.sp
    data['cp_bar_left'], data['cp_bar_middle'], data['cp_bar_right'] = calc_bar_widths(toon.cp_cur, toon.cp_max)
    data['hp_bar_left'], data['hp_bar_middle'], data['hp_bar_right'] = calc_bar_widths(toon.hp_cur, toon.hp_max)
    data['mp_bar_left'], data['mp_bar_middle'], data['mp_bar_right'] = calc_bar_widths(toon.mp_cur, toon.mp_max)
    data['xp_bar_left'], data['xp_bar_middle'], data['xp_bar_right'] = calc_bar_widths(int(lvl_pct), 100)

    if not toon.last_info_ping:
        data['lvl'] = 'n/a'
        data['xp'] = 'n/a'
        data['sp'] = 'n/a'

    if toon.cp_stats:
        xx_pts = range(0, len(toon.cp_stats))
        cp_pts = ','.join(map(str, toon.cp_stats))
        hp_pts = ','.join(map(str, toon.hp_stats))
        mp_pts = ','.join(map(str, toon.mp_stats))
        zz_stats = []
        for i in range(0, len(toon.cp_stats)):
            zz_stats.append(0)
        zz_pts = ','.join(map(str, zz_stats))
    else:
        xx_pts = '0'
        cp_pts = '0'
        hp_pts = '0'
        mp_pts = '0'
        zz_pts = '0'

    data['xx_graph_seq'] = xx_pts
    data['cp_graph_seq'] = cp_pts
    data['hp_graph_seq'] = hp_pts
    data['mp_graph_seq'] = mp_pts
    data['zz_graph_seq'] = zz_pts

    # bars for the really low levels are invisible because they are so close to
    # zero so what we'll do is make sure that they are at least 1% of the highest bar
    min_bar = L2VisionModel.xp_table[len(L2VisionModel.xp_table) - 1] / 100

    xp_goal_bars = []
    xp_done_bars = []
    for i in range(1, len(L2VisionModel.xp_table) - 1):
        gv = L2VisionModel.xp_table[i]
        if gv < min_bar:
            gv = min_bar
        xp_goal_bars.append(gv)

        if i <= lvl:
            dv = L2VisionModel.xp_table[i]
            if dv < min_bar:
                dv = min_bar
        elif i == lvl + 1:
            dv = round(round((lvl_pct * gv) / 100))
            if dv < min_bar:
                dv = min_bar
        else:
            dv = 0
        xp_done_bars.append(dv)
    data['xp_goal_bars'] = ','.join(map(str, xp_goal_bars))
    data['xp_done_bars'] = ','.join(map(str, xp_done_bars))

#------------------------------------------------------------------------------

def insert_hunt_data(toon, data):
    if not toon.last_info_ping:
        data['hunting_time'] = 'n/a'
    else:
        data['hunting_time'] = get_duration(toon.accrued_hunting_time)

    data['xp_gain'] = toon.xp - toon.starting_xp
    data['xp_gain_pct'] = '%0.2f%%' % L2VisionModel.get_pct_for_xp(toon.xp, toon.xp - toon.starting_xp)
    data['sp_gain'] = toon.sp - toon.starting_sp

    adena_gain = 0
    filtered_items = []
    for item_id in toon.current_items.keys():
        sitem = toon.starting_items[item_id]
        citem = toon.current_items[item_id]

        if citem.name == 'Adena':
            adena_gain = citem.quantity - sitem.quantity;

        ditem = InventoryItemForDisplay(citem.name)
        try:
            ignore = toon.hilite_items[item_id]
            ditem.hilite = True
        except:
            ditem.hilite = False
        ditem.starting_count = sitem.quantity
        ditem.current_count = citem.quantity
        ditem.difference = citem.quantity - sitem.quantity
        try:
            ignore = toon.consumable_items[item_id]
            ditem.consumable = True
        except:
            ditem.consumable = False
        if toon.accrued_hunting_time > 0:
            ditem.rate = '%d/hr' % ((ditem.difference * 3600) / toon.accrued_hunting_time)
        
        if ditem.difference != 0 or ditem.consumable:
            filtered_items.append(ditem)

    def item_compare(x, y):
        return cmp(x.name, y.name)
    filtered_items.sort(item_compare)

    filtered_mobs = []
    for mob in toon.mobs.values():
        dmob = MobForDisplay(mob.name)
        dmob.kills = mob.kills
        try:
            ignore = toon.hilite_mobs[mob.mob_id]
            dmob.hilite = True
        except:
            dmob.hilite = False;
        if dmob.kills > 0:
            filtered_mobs.append(dmob)

    def mob_compare(x, y):
        return cmp(x.name, y.name)
    filtered_mobs.sort(mob_compare)

    data['items'] = filtered_items
    data['mobs'] = filtered_mobs
    data['adena_gain'] = adena_gain

#------------------------------------------------------------------------------

def insert_modeling_data(toon, data):
    adena_gain = 0
    for item_id in toon.current_items.keys():
        sitem = toon.starting_items[item_id]
        citem = toon.current_items[item_id]
        if citem.name == 'Adena':
            adena_gain = citem.quantity - sitem.quantity
            break

    xp_rate = 0.0
    sp_rate = 0.0
    adena_rate = 0.0
    if not toon.last_info_ping:
        data['xp_rate'] = 'n/a'
        data['sp_rate'] = 'n/a'
        data['adena_rate'] = 'n/a'
    elif toon.accrued_hunting_time > 0:
        xp_rate = float(toon.xp - toon.starting_xp) / float(toon.accrued_hunting_time)
        sp_rate = float(toon.sp - toon.starting_sp) / float(toon.accrued_hunting_time)
        adena_rate = float(adena_gain) / float(toon.accrued_hunting_time)
        data['xp_rate'] = '%0.4f/s' % xp_rate
        data['sp_rate'] = '%0.4f/s' % sp_rate
        data['adena_rate'] = '%0.4f/s' % adena_rate
    else:
        data['xp_rate'] = '%0.4f/s' % 0.0
        data['sp_rate'] = '%0.4f/s' % 0.0
        data['adena_rate'] = '%0.4f/s' % 0.0

    if xp_rate > 0:
        needed_xp = L2VisionModel.get_xp_needed_for_next_lvl(toon.xp)
        needed_time = float(needed_xp) / float(xp_rate)
        data['next_level_time'] = get_duration(round(needed_time))
    else:
        data['next_level_time'] = 'n/a'

    xp_gain_in_1hr = round(3600 * xp_rate)
    xp_pct_gain_in_1hr = L2VisionModel.get_pct_for_xp(toon.xp, xp_gain_in_1hr)
    if not toon.last_info_ping:
        data['1hr_xp_gain'] = 'n/a'
        data['1hr_xp_gain_pct'] = 'n/a'
        data['1hr_sp_gain'] = 'n/a'
        data['1hr_adena_gain'] = 'n/a'
    else:
        data['1hr_xp_gain'] = "%d" % xp_gain_in_1hr
        data['1hr_xp_gain_pct'] = "%0.2f%%" % xp_pct_gain_in_1hr
        data['1hr_sp_gain'] = "%d" % round(3600 * sp_rate)
        data['1hr_adena_gain'] = "%d" % round(3600 * adena_rate)

#------------------------------------------------------------------------------

def insert_visitor_data(toon, data):
    visitors = []
    for visitor in toon.visitors.values():
        visitors.append(VisitorForDisplay(visitor.name, visitor.timestamp))

    def visitor_compare(x, y):
        if x.timestamp == y.timestamp:
            return cmp(x.name, y.name)
        else:
            return cmp(x.timestamp, y.timestamp)
    visitors.sort(visitor_compare)
    data['visitors'] = visitors

#------------------------------------------------------------------------------

def insert_chat_data(toon, data):
    msgs = []
    for msg in toon.msgs:
        msgs.append(MsgForDisplay(msg.type, msg.name, msg.text, msg.timestamp))
    data['msgs'] = msgs

#------------------------------------------------------------------------------

def insert_map_location(toon, data):
    # (0, 0) on the map is at pixel location 822, 1315
    # every pixel on the map represents 200 units in the L2 grid
    # map view width is 528 and height is 300
    # map dimensions are 1968 x 2620

    # move 0, 0 on the map to the upper left corner
    x_shift = -822
    y_shift = -1315

    # move 0, 0 on the map to the center of the screen
    x_shift = x_shift + (856 / 2)
    y_shift = y_shift + (300 / 2)

    # determine pixel version of toon's coordinates
    px = toon.x / 200
    py = toon.y / 200

    # move player's location to center of the screen
    x_shift = x_shift - px
    y_shift = y_shift - py

    data['map_x_shift'] = x_shift
    data['map_y_shift'] = y_shift
    data['map_toon_x'] = (856 / 2) - 1
    data['map_toon_y'] = (300 / 2) - 1

#------------------------------------------------------------------------------

def insert_tab_state(selected_tab, data):
    if selected_tab == 'view':
        data['view_tab_state'] = 'selected'
    else:
        data['view_tab_state'] = 'normal'
    if selected_tab == 'world_map':
        data['world_map_tab_state'] = 'selected'
    else:
        data['world_map_tab_state'] = 'normal'
    if selected_tab == 'loot':
        data['loot_tab_state'] = 'selected'
    else:
        data['loot_tab_state'] = 'normal'
    if selected_tab == 'mobs':
        data['mobs_tab_state'] = 'selected'
    else:
        data['mobs_tab_state'] = 'normal'
    if selected_tab == 'visitors':
        data['visitors_tab_state'] = 'selected'
    else:
        data['visitors_tab_state'] = 'normal'
    if selected_tab == 'chat':
        data['chat_tab_state'] = 'selected'
    else:
        data['chat_tab_state'] = 'normal'
    if selected_tab == 'graphs':
        data['graphs_tab_state'] = 'selected'
    else:
        data['graphs_tab_state'] = 'normal'

#------------------------------------------------------------------------------

def view(request, name):
    lvm = L2VisionModel.get_instance()
    lvm.lock.acquire()
    try:
        data = {}
        toon = lvm.toons[name]
        insert_system_data(toon, data)
        insert_vital_data(toon, data)
        insert_hunt_data(toon, data)
        insert_modeling_data(toon, data)
        insert_tab_state('view', data)
    finally:
        lvm.lock.release()
    return render('l2v/templates/view.html', data)

#------------------------------------------------------------------------------

def loot(request, name):
    lvm = L2VisionModel.get_instance()
    lvm.lock.acquire()
    try:
        data = {}
        toon = lvm.toons[name]
        insert_system_data(toon, data)
        insert_vital_data(toon, data)
        insert_hunt_data(toon, data)
        insert_modeling_data(toon, data)
        insert_tab_state('loot', data)
    finally:
        lvm.lock.release()
    return render('l2v/templates/loot.html', data)

#------------------------------------------------------------------------------

def mobs(request, name):
    lvm = L2VisionModel.get_instance()
    lvm.lock.acquire()
    try:
        data = {}
        toon = lvm.toons[name]
        insert_system_data(toon, data)
        insert_vital_data(toon, data)
        insert_hunt_data(toon, data)
        insert_modeling_data(toon, data)
        insert_tab_state('mobs', data)
    finally:
        lvm.lock.release()
    return render('l2v/templates/mobs.html', data)

#------------------------------------------------------------------------------

def visitors(request, name):
    lvm = L2VisionModel.get_instance()
    lvm.lock.acquire()
    try:
        data = {}
        toon = lvm.toons[name]
        insert_system_data(toon, data)
        insert_vital_data(toon, data)
        insert_hunt_data(toon, data)
        insert_visitor_data(toon, data)
        insert_modeling_data(toon, data)
        insert_tab_state('visitors', data)
    finally:
        lvm.lock.release()
    return render('l2v/templates/visitors.html', data)

#------------------------------------------------------------------------------

def chat(request, name):
    lvm = L2VisionModel.get_instance()
    lvm.lock.acquire()
    try:
        data = {}
        toon = lvm.toons[name]
        insert_system_data(toon, data)
        insert_vital_data(toon, data)
        insert_hunt_data(toon, data)
        insert_chat_data(toon, data)
        insert_modeling_data(toon, data)
        insert_tab_state('chat', data)
    finally:
        lvm.lock.release()
    return render('l2v/templates/chat.html', data)

#------------------------------------------------------------------------------

def graphs(request, name):
    lvm = L2VisionModel.get_instance()
    lvm.lock.acquire()
    try:
        data = {}
        toon = lvm.toons[name]
        insert_system_data(toon, data)
        insert_vital_data(toon, data)
        insert_hunt_data(toon, data)
        insert_modeling_data(toon, data)
        insert_tab_state('graphs', data)
    finally:
        lvm.lock.release()
    return render('l2v/templates/graphs.html', data)

#------------------------------------------------------------------------------

def world_map(request, name):
    lvm = L2VisionModel.get_instance()
    lvm.lock.acquire()
    try:
        data = {}
        toon = lvm.toons[name]
        insert_system_data(toon, data)
        insert_vital_data(toon, data)
        insert_hunt_data(toon, data)
        insert_modeling_data(toon, data)
        insert_map_location(toon, data)
        insert_tab_state('world_map', data)
    finally:
        lvm.lock.release()
    return render('l2v/templates/map.html', data)

#------------------------------------------------------------------------------

def reset_all(request):
    lvm = L2VisionModel.get_instance()
    lvm.lock.acquire()
    try:
        lvm.toons.clear()
    finally:
        lvm.lock.release()
    return render('l2v/templates/resetall.html', {})

#------------------------------------------------------------------------------

def reset(request, name):
    lvm = L2VisionModel.get_instance()
    lvm.lock.acquire()
    try:
        lvm.toons.pop(name)
        
        data = {
            'name': name,
        }
    finally:
        lvm.lock.release()
    return render('l2v/templates/reset.html', data)
