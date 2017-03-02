import haven.HavenPanel as HavenPanel
import haven.GameUI as GameUI
import haven.Coord as Coord
import haven.OCache as OCache

from synchronize import make_synchronized
from time import sleep

@make_synchronized
def gettilegobs(oc,coord,gui):
    gobs = []
    for gob in oc:
        res = gob.getres()
        dist = gob.rc.dist(coord)
        if res != None and dist < 1:
            gobs.append(gob)
    return gobs

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

def zloezlo(coord, waitforemptyhand = False, timeout=-1, fallbackcoord=None):
    gui = HavenPanel.lui.root.getchild(GameUI)
    gui.map.wdgmsg("itemact", Coord.z, coord.floor(OCache.posres), 0)
    if (waitforemptyhand and not(gui.hand.isEmpty())):
        tout = 0
        while(not(self.gui.hand.isEmpty())):
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

