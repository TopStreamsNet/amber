import haven.Window as Window
import haven.Coord as Coord
import haven.HavenPanel as HavenPanel
import haven.GameUI as GameUI
import haven.Button as Button
import haven.Label as Label
import haven.FlowerMenu as FlowerMenu
import haven.OCache as OCache
import haven.automation.Utils as Utils
import haven.automation.GobSelectCallback as GobSelectCallback
import haven.automation.JythonAutomation as JythonAutomation
import haven.ISBox as ISBox

from time import sleep
from synchronize import make_synchronized

TIMEOUT = 5 # 5 seconds
MAX_HIDES = 4 # 4 Maximum hides in inventory
MAX_ENTRAILS = 3 # 3 Maximum entrails in inventory
MAX_INTESTINES = 3 # 3 Maximum intestines in inventory
MAX_MEAT = 3 # 3 Maximum meat in inventory
MAX_BONES = 3 # 3 Maximum meat in inventory

class State:
    WAIT, RUN, TERM = range(3)

class StartButton(Button):
    def __init__(self, width, caption):
        Button.__init__(self, width, caption)
    def click(self):
        self.parent.state = State.RUN
        HavenPanel.lui.cons.out.println("Butchering!")
		
class ClearButton(Button):
    def __init__(self, width, caption):
        Button.__init__(self, width, caption)
    def click(self):
        self.parent.state = State.WAIT
        self.parent.bodies=[]
        self.parent.lbl_bodies.settext("0")
        self.parent.hidepiles=[]
        self.parent.lbl_hidepiles.settext("0")
        self.parent.trashpiles=[]
        self.parent.lbl_trashpiles.settext("0")
        self.parent.cupboards=[]
        self.parent.lbl_cupboards.settext("0")
        self.parent.bonepiles=[]
        self.parent.lbl_bonepiles.settext("0")
        HavenPanel.lui.cons.out.println("All Cleared!")

@make_synchronized
def pickdropped(oc, gui, bot):
    gobs = []
    for gob in oc:
        res = gob.getres()
        dist = gob.rc.dist(gui.map.player().rc)
        if res != None and dist < 22:
            gobs.append(gob)
    for gob in gobs:
        gui.map.pfRightClick(gob, -1, 3, 0, None)
        gui.map.pfthread.join()
        bot.checkbones(MAX_BONES)
			
class ButcherBot(GobSelectCallback, Window):
    state = State.WAIT
    gui = None

    lbl_bodies = None
    lbl_hidepiles = None
    lbl_trashpiles = None
    lbl_cupboards = None
    lbl_bonepiles = None
    
    bodies = []
    hidepiles = []
    trashpiles = []
    cupboards = []
    bonepiles = []
            
    def __init__(self, coord, title):
        Window.__init__(self, coord, title)

        self.add(Label("Bodies selected: "), Coord(15, 15))
        self.lbl_bodies = Label("0")
        self.add(self.lbl_bodies, Coord(120,15))

        self.add(Label("Hide piles selected: "), Coord(15, 30))
        self.lbl_hidepiles = Label("0")
        self.add(self.lbl_hidepiles, Coord(120,30))

        self.add(Label("Trash piles selected: "), Coord(15, 45))
        self.lbl_trashpiles = Label("0")
        self.add(self.lbl_trashpiles, Coord(120,45))

        self.add(Label("Cupboards selected: "), Coord(15, 60))
        self.lbl_cupboards = Label("0")
        self.add(self.lbl_cupboards, Coord(120,60))

        self.add(Label("Bone piles selected: "), Coord(15, 75))
        self.lbl_bonepiles = Label("0")
        self.add(self.lbl_bonepiles, Coord(120,75))

        butchertbtn = StartButton(70, "Butcher!")
        self.add(butchertbtn, Coord(65, 140))
        
        clearbtn = ClearButton(70, "Clear")
        self.add(clearbtn, Coord(140, 140))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        HavenPanel.lui.root.getchild(GameUI).map.unregisterGobSelect()
        self.destroy()

    def wdgmsg(self, sender, msg, *args):
        if sender == self.cbtn:
            self.die()
        else:
            Window.wdgmsg(self,sender, msg, args)

    def type(self, key, ev):
        if (key == 27):
            if (self.cbtn.visible):
                self.die()
                return True
        return Window.type(self,key, ev)

    def die(self):
        self.reqdestroy()
        self.state = State.TERM

    def gobselect(self, gob):
        res = gob.getres()
        if(res != None):
            HavenPanel.lui.cons.out.println("gob selected: {0}".format(res.name))
            if(res.name.startswith("gfx/kritter")):
                self.bodies.append(gob)
                self.lbl_bodies.settext("{0}".format(len(self.bodies)))
            elif(res.name.startswith("gfx/terobjs/stockpile-hide")):
                self.hidepiles.append(gob)
                self.lbl_hidepiles.settext("{0}".format(len(self.hidepiles)))
            elif(res.name.startswith("gfx/terobjs/stockpile-trash")):
                self.trashpiles.append(gob)
                self.lbl_trashpiles.settext("{0}".format(len(self.trashpiles)))
            elif(res.name.startswith("gfx/terobjs/cupboard")):
                self.cupboards.append(gob)
                self.lbl_cupboards.settext("{0}".format(len(self.cupboards)))
            elif(res.name.startswith("gfx/terobjs/stockpile-bone")):
                self.bonepiles.append(gob)
                self.lbl_bonepiles.settext("{0}".format(len(self.bonepiles)))

    @make_synchronized
    def checkbody(self, body, oc):
        # check if this body is still around
        if (oc.getgob(body.id) != None):
            return True
        return False

    def workonbody(self,body):
        HavenPanel.lui.cons.out.println("Working on body: {0}".format(body))
        # RightClick the body and see what comes out
        self.gui.map.pfRightClick(body, -1, 3, 0, None)
        self.gui.map.pfthread.join()
        # Wait for choices
        timeout = 0
        while HavenPanel.lui.root.getchild(FlowerMenu) == None and self.state == State.RUN:
            HavenPanel.lui.cons.out.println("Waiting for flowers!")
            timeout = timeout + 1
            sleep(1)
            if timeout >= TIMEOUT:
                return
        flowermenu = HavenPanel.lui.root.getchild(FlowerMenu)
        for i in range(len(flowermenu.opts)):
            if flowermenu.opts[i].name == "Skin":
                HavenPanel.lui.cons.out.println("Going to Skin {0}".format(body))
                flowermenu.choose(flowermenu.opts[i])
                Utils.waitForProgressFinish(self.gui,60000,"Stuck in Skinning")
                break
            elif flowermenu.opts[i].name == "Butcher":
                HavenPanel.lui.cons.out.println("Going to Butcher {0}".format(body))
                flowermenu.choose(flowermenu.opts[i])
                Utils.waitForProgressFinish(self.gui,60000,"Stuck in Butchering")
                break

    def checkhides(self, max_hides):
        # Check how many hides we have in our inventory
        hide_num = self.gui.maininv.getItemPartialCount("hide")
        hide_num = hide_num + self.gui.maininv.getItemPartialCount("Hide")
        while (hide_num > max_hides and self.state == State.RUN):
            HavenPanel.lui.cons.out.println("Have hides {0}".format(hide_num))
            for pile in self.hidepiles:
                self.gui.map.pfRightClick(pile, -1, 3, 0, None)
                self.gui.map.pfthread.join()
                spwnd = self.gui.waitfForWnd("Stockpile", 1500)
                if spwnd == None:
                    continue
                isb = spwnd.getchild(ISBox)
                if isb.getfreespace() == 0:
                    continue
                hide = self.gui.maininv.getItemPartial("hide")
                if (hide == None):
                    hide = self.gui.maininv.getItemPartial("Hide")
                if (hide == None):
                    return
                hide.item.wdgmsg("take", Coord(hide.item.sz.x / 2, hide.item.sz.y / 2))
                while(self.gui.hand.isEmpty() and self.state == State.RUN):
                    HavenPanel.lui.cons.out.println("Waiting for Hide in hand!")
                    sleep(1)
                self.gui.map.wdgmsg("itemact", Coord.z, pile.rc.floor(OCache.posres), 1, 0, int(pile.id), pile.rc.floor(OCache.posres), 0, -1)
                while(not(self.gui.hand.isEmpty()) and self.state == State.RUN):
                    HavenPanel.lui.cons.out.println("Waiting for EMPTY hand!")
                    sleep(1)
                hide_num = self.gui.maininv.getItemPartialCount("hide")
                hide_num = hide_num + self.gui.maininv.getItemPartialCount("Hide")
                if(hide_num == 0):
                    return

    def checkintestines(self, max_intestines):
        # Check how many intestines we have in the inventory
        intestines_num = self.gui.maininv.getItemPartialCount("Intestines")
        while (intestines_num > max_intestines and self.state == State.RUN):
            HavenPanel.lui.cons.out.println("Have Intestines {0}".format(intestines_num))
            for pile in self.trashpiles:
                self.gui.map.pfRightClick(pile, -1, 3, 0, None)
                self.gui.map.pfthread.join()
                spwnd = self.gui.waitfForWnd("Stockpile", 1500)
                if spwnd == None:
                    continue
                isb = spwnd.getchild(ISBox)
                if isb.getfreespace() == 0:
                    continue
                intestines = self.gui.maininv.getItemPartial("Intestines")
                if (intestines == None):
                    return
                intestines.item.wdgmsg("take", Coord(intestines.item.sz.x / 2, intestines.item.sz.y / 2))
                while(self.gui.hand.isEmpty() and self.state == State.RUN):
                    HavenPanel.lui.cons.out.println("Waiting for Intestines in hand!")
                    sleep(1)
                self.gui.map.wdgmsg("itemact", Coord.z, pile.rc.floor(OCache.posres), 1, 0, int(pile.id), pile.rc.floor(OCache.posres), 0, -1)
                while(not(self.gui.hand.isEmpty()) and self.state == State.RUN):
                    HavenPanel.lui.cons.out.println("Waiting for EMPTY hand!")
                    sleep(1)
                intestines_num = self.gui.maininv.getItemPartialCount("Intestines")
                if(intestines_num == 0):
                    return

    def checkentrails(self, max_entrails):
        # Check how many entrails we have in the inventory
        entrails_num = self.gui.maininv.getItemPartialCount("Entrails")
        while (entrails_num > max_entrails and self.state == State.RUN):
            HavenPanel.lui.cons.out.println("Have Entrails {0}".format(entrails_num))
            for pile in self.trashpiles:
                self.gui.map.pfRightClick(pile, -1, 3, 0, None)
                self.gui.map.pfthread.join()
                spwnd = self.gui.waitfForWnd("Stockpile", 1500)
                if spwnd == None:
                    continue
                isb = spwnd.getchild(ISBox)
                if isb.getfreespace() == 0:
                    continue
                entrails = self.gui.maininv.getItemPartial("Entrails")
                if (entrails == None):
                    return
                entrails.item.wdgmsg("take", Coord(entrails.item.sz.x / 2, entrails.item.sz.y / 2))
                while(self.gui.hand.isEmpty() and self.state == State.RUN):
                    HavenPanel.lui.cons.out.println("Waiting for Entrails in hand!")
                    sleep(1)
                self.gui.map.wdgmsg("itemact", Coord.z, pile.rc.floor(OCache.posres), 1, 0, int(pile.id), pile.rc.floor(OCache.posres), 0, -1)
                while(not(self.gui.hand.isEmpty()) and self.state == State.RUN):
                    HavenPanel.lui.cons.out.println("Waiting for EMPTY hand!")
                    sleep(1)
                entrails_num = self.gui.maininv.getItemPartialCount("Entrails")
                if(entrails_num == 0):
                    return

    def checkbones(self, max_bones):
        # Check how many bones we have in the inventory
        bones_num = self.gui.maininv.getItemPartialCount("Antlers")
        bones_num = bones_num + self.gui.maininv.getItemPartialCount("Bone")
        bones_num = bones_num + self.gui.maininv.getItemPartialCount("Tooth")
        bones_num = bones_num + self.gui.maininv.getItemPartialCount("Tusk")
        while (bones_num > max_bones and self.state == State.RUN):
            HavenPanel.lui.cons.out.println("Have Bones {0}".format(bones_num))
            for pile in self.bonepiles:
                self.gui.map.pfRightClick(pile, -1, 3, 0, None)
                self.gui.map.pfthread.join()
                spwnd = self.gui.waitfForWnd("Stockpile", 1500)
                if spwnd == None:
                    continue
                isb = spwnd.getchild(ISBox)
                if isb.getfreespace() == 0:
                    continue
                bone = self.gui.maininv.getItemPartial("Bone")
                if (bone == None):
                    bone = self.gui.maininv.getItemPartial("Tooth")
                if (bone == None):
                    bone = self.gui.maininv.getItemPartial("Tusk")
                if (bone == None):
                    bone = self.gui.maininv.getItemPartial("Antlers")
                if (bone == None):
                    return
                bone.item.wdgmsg("take", Coord(bone.item.sz.x / 2, bone.item.sz.y / 2))
                while(self.gui.hand.isEmpty() and self.state == State.RUN):
                    HavenPanel.lui.cons.out.println("Waiting for Bone in hand!")
                    sleep(1)
                self.gui.map.wdgmsg("itemact", Coord.z, pile.rc.floor(OCache.posres), 1, 0, int(pile.id), pile.rc.floor(OCache.posres), 0, -1)
                while(not(self.gui.hand.isEmpty()) and self.state == State.RUN):
                    HavenPanel.lui.cons.out.println("Waiting for EMPTY hand!")
                    sleep(1)
                bones_num = self.gui.maininv.getItemPartialCount("Antlers")
                bones_num = bones_num + self.gui.maininv.getItemPartialCount("Bone")
                bones_num = bones_num + self.gui.maininv.getItemPartialCount("Tooth")
                bones_num = bones_num + self.gui.maininv.getItemPartialCount("Tusk")
                if(bones_num == 0):
                    return

    def checkmeat(self, max_meat):
        meat_num = self.gui.maininv.getItemPartialCount("Raw")
        while meat_num >= MAX_MEAT:
            HavenPanel.lui.cons.out.println("Have meat {0}".format(meat_num))
            for cupboard in self.cupboards:
                self.gui.map.pfRightClick(cupboard, -1, 3, 0, None)
                self.gui.map.pfthread.join()
                spwnd = self.gui.waitfForWnd("Cupboard", 1500);
                if spwnd == None:
                    continue
                meat = self.gui.maininv.getItemPartial("Raw")
                meat.item.wdgmsg("transfer-identical", meat.item)
                sleep(1) #FIXME: check this properly
                meat_num = self.gui.maininv.getItemPartialCount("Raw")
                if meat_num == 0:
                    return

    def run(self):
        self.gui = HavenPanel.lui.root.getchild(GameUI)
        self.gui.add(self,Coord(self.gui.sz.x / 2 - self.sz.x / 2, self.gui.sz.y / 2 - self.sz.y / 2 - 200))
        HavenPanel.lui.root.getchild(GameUI).map.registerGobSelect(self)
        while self.state != State.TERM:
            if self.state == State.RUN:
                # For every configured body
                gone = []
                if len(self.bodies) == 0:
                    return
                for body in self.bodies:
                    if self.checkbody(body, self.gui.map.glob.oc):
                        self.workonbody(body)
                    else:
                        HavenPanel.lui.cons.out.println("{0} body is gone, marked for removal".format(body))
                        gone.append(body)
                    self.checkhides(MAX_HIDES)
                    self.checkintestines(MAX_INTESTINES)
                    self.checkentrails(MAX_ENTRAILS)
                    self.checkmeat(MAX_MEAT)
                for body in gone:
                    self.bodies.remove(body)
                    # move to where Gob should have been
                    self.gui.map.pfLeftClick(body.rc.floor(), None)
                    self.gui.map.pfthread.join()
                    pickdropped(self.gui.map.glob.oc, self.gui, self)
                self.checkhides(0)
                self.checkintestines(0)
                self.checkentrails(0)
                self.checkmeat(0)
                self.checkbones(0)
            else:
                sleep(1)


# Our Automation
with ButcherBot(Coord(270,180),"Butcher Bot") as bot:
    bot.run()

