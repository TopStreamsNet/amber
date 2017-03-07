import haven.HavenPanel as HavenPanel
import haven.GameUI as GameUI
import haven.Coord as Coord
import haven.OCache as OCache
import haven.Label as Label
import haven.ItemInfo as ItemInfo
import haven.GItem as GItem

from synchronize import make_synchronized
from time import sleep
import re

@make_synchronized
def gettilegobs(oc,coord):
    gobs = []
    for gob in oc:
        try:
            res = gob.getres()
        except:
            continue
        dist = gob.rc.dist(coord)
        if res != None and dist < 1:
            gobs.append(gob)
    return gobs

@make_synchronized
def gobexists(oc,gob):
    if (oc.getgob(gob.id) != None):
        return True
    return False

def getfreeslot(item, inventory):
    gui = HavenPanel.lui.root.getchild(GameUI)
    tilesize = 33
    HavenPanel.lui.cons.out.println("!!!item {0} inventory {1}".format(item, inventory))
    invitems = inventory.getItemsPartial("")
    if len(invitems) == 0:
        return Coord.z
    for y in range(1, inventory.sz.y, tilesize):
        for x in range(1, inventory.sz.x, tilesize):
            if (x+item.sz.x > inventory.sz.x or y+item.sz.y > inventory.sz.y):
                continue
            desired_topleft = Coord(x,y)
            desired_bottomright = Coord(x+item.sz.x,y+item.sz.y)
            HavenPanel.lui.cons.out.println("- {0}x{1}".format(desired_topleft,desired_bottomright))
            intersects = False
            for invitem in invitems:
                occupied_topleft = invitem.c
                occupied_bottomright = Coord(invitem.c.x+invitem.sz.x,invitem.c.y+invitem.sz.y)
                # check if we found an item that intersects
                if (desired_topleft.x < occupied_bottomright.x and desired_bottomright.x > occupied_topleft.x and
                    desired_topleft.y < occupied_bottomright.y and desired_bottomright.y > occupied_topleft.y):
                    intersects = True
                    break
            if intersects == False:
                return Coord(x,y)
    return None



def takeitem(item, timeout):
    gui = HavenPanel.lui.root.getchild(GameUI)
    item.item.wdgmsg("take", Coord(item.item.sz.x / 2, item.item.sz.y / 2))
    tout = 0
    while(gui.hand.isEmpty()):
        HavenPanel.lui.cons.out.println("Waiting for {0} in hand!".format(item))
        sleep(1)
        tout += 1
        if tout > timeout:
            return False
    return True

def itemactcoord(coord, waitforemptyhand=False, timeout=-1, fallbackcoord=None):
    gui = HavenPanel.lui.root.getchild(GameUI)
    gui.map.wdgmsg("itemact", Coord.z, coord.floor(OCache.posres), 0)
    if (waitforemptyhand and not(gui.hand.isEmpty())):
        tout = 0
        while(not(gui.hand.isEmpty())):
            HavenPanel.lui.cons.out.println("Waiting for EMPTY hand!")
            sleep(1)
            tout += 1
            if tout > timeout and fallbackcoord != None:
                gui.map.pfLeftClick(fallbackcoord.mul(11).add(5,5), None)
                gui.map.pfthread.join()
                return itemactcoord(coord, waitforemptyhand, timeout, None)
            elif tout > timeout and fallbackcoord == None:
                return False
    return True

def itemactgob(gob, shift=0, waitforemptyhand = False, timeout=-1, fallbackcoord=None):
    gui = HavenPanel.lui.root.getchild(GameUI)
    gui.map.wdgmsg("itemact", Coord.z, gob.rc.floor(OCache.posres), shift, 0, int(gob.id), gob.rc.floor(OCache.posres), 0, -1)
    if (waitforemptyhand and not(gui.hand.isEmpty())):
        tout=0
        while(not(gui.hand.isEmpty())):
            HavenPanel.lui.cons.out.println("Waiting for EMPTY hand!")
            sleep(1)
            tout += 1
            if tout > timeout and fallbackcoord != None:
                gui.map.pfLeftClick(fallbackcoord.mul(11).add(5,5), None)
                gui.map.pfthread.join()
                return itemactgob(gob, shift, waitforemptyhand, timeout, None)
            elif tout > timeout and fallbackcoord == None:
                return False
    return True

def fallbackonfail(failcond, fallbackcoord):
    gui = HavenPanel.lui.root.getchild(GameUI)
    if failcond:
        gui.map.pfLeftClick(fallbackcoord.mul(11).add(5,5), None)
        gui.map.pfthread.join()
    return failcond

RE_CONTENTS_NMBR = re.compile("Contents: (\d+) (.*).")
def getBarrelContent(brlwnd):
    ret = {'quantity':0,'item':None}
    brl_lbl = brlwnd.getchild(Label)
    contStr = brl_lbl.gettexts()
    if not(contStr.endswith("Empty.")):
        rslt = RE_CONTENTS_NMBR.match(contStr)
        ret['quantity'] = int(rslt.group(1))
        ret['item'] = rslt.group(2)
    return ret

def getnum(stack):
    iteminfo = stack.item.info()
    ninf = ItemInfo.find(GItem.NumberInfo, iteminfo)
    return ninf.itemnum()