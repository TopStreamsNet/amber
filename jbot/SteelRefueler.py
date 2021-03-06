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
import haven.automation.AreaSelectCallback as AreaSelectCallback
import haven.automation.JythonAutomation as JythonAutomation
import haven.ISBox as ISBox
import haven.VMeter as VMeter

from time import sleep
from synchronize import make_synchronized

class State:
    WAIT, RUN, TERM = range(3)

class StartButton(Button):
    def __init__(self, width, caption):
        Button.__init__(self, width, caption)
    def click(self):
        self.parent.state = State.RUN
        HavenPanel.lui.cons.out.println("Refueling!")

class ClearButton(Button):
    def __init__(self, width, caption):
        Button.__init__(self, width, caption)
    def click(self):
        self.parent.state = State.WAIT
        self.parent.lbl_branchpiles = None
        self.parent.lbl_coalpiles = None
        self.parent.lbl_wblockpiles = None
        self.parent.lbl_crucibels = None

        self.parent.branchpiles = []
        self.parent.coalpiles = []
        self.parent.wblockpiles = []
        self.parent.crucibels = []

        self.parent.pointZero = None
        HavenPanel.lui.cons.out.println("All Cleared!")

class SteelRefuelerBot(GobSelectCallback, AreaSelectCallback, Window):
    state = State.WAIT
    gui = None

    lbl_branchpiles = None
    lbl_coalpiles = None
    lbl_wblockpiles = None
    lbl_crucibels = None

    branchpiles = []
    coalpiles = []
    wblockpiles = []
    crucibels = []

    pointZero = None

    def __init__(self, coord, title):
        Window.__init__(self, coord, title)

        self.add(Label("Crucibels selected: "), Coord(15, 15))
        self.lbl_crucibels = Label("0")
        self.add(self.lbl_crucibels, Coord(120,15))

        self.add(Label("Branchpiles selected: "), Coord(15, 30))
        self.lbl_branchpiles = Label("0")
        self.add(self.lbl_branchpiles, Coord(120,30))

        self.add(Label("Coalpiles selected: "), Coord(15, 45))
        self.lbl_coalpiles = Label("0")
        self.add(self.lbl_coalpiles, Coord(120,45))

        self.add(Label("Wblockpiles selected: "), Coord(15, 60))
        self.lbl_wblockpiles = Label("0")
        self.add(self.lbl_wblockpiles, Coord(120,60))

        startbtn = StartButton(70, "Refuel!")
        self.add(startbtn, Coord(65, 140))

        clearbtn = ClearButton(70, "Clear")
        self.add(clearbtn, Coord(140, 140))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.gui.map.unregisterGobSelect()
        self.gui.map.unregisterAreaSelect()
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
            if(res.name.startswith("gfx/terobjs/steelcrucible")):
                self.crucibels.append(gob)
                self.lbl_crucibels.settext("{0}".format(len(self.crucibels)))
            elif(res.name.startswith("gfx/terobjs/stockpile-branch")):
                self.branchpiles.append(gob)
                self.lbl_branchpiles.settext("{0}".format(len(self.branchpiles)))
            elif(res.name.startswith("gfx/terobjs/stockpile-coal")):
                self.coalpiles.append(gob)
                self.lbl_coalpiles.settext("{0}".format(len(self.coalpiles)))
            elif(res.name.startswith("gfx/terobjs/stockpile-wblock")):
                self.wblockpiles.append(gob)
                self.lbl_wblockpiles.settext("{0}".format(len(self.wblockpiles)))

    def areaselect(self, a, b):
        HavenPanel.lui.cons.out.println("Coord A {0} : Coord B {1}".format(a,b))
        self.pointZero = a

    @make_synchronized
    def getfuel(self, oc):
        for pile in self.branchpiles:
            if oc.getgob(pile.id) == None:
                continue
            self.gui.map.pfRightClick(pile, -1, 3, 1, None)
            self.gui.map.pfthread.join()
            availableFuelBranch = self.gui.maininv.getItemPartialCount("Branch")
            if availableFuelBranch >= 18:
                return

        for pile in self.wblockpiles:
            if oc.getgob(pile.id) == None:
                continue
            self.gui.map.pfRightClick(pile, -1, 3, 1, None)
            self.gui.map.pfthread.join()
            availableFuelBlock = self.gui.maininv.getItemPartialCount("Block")
            if availableFuelBlock >= 3:
                return

        for pile in self.coalpiles:
            if oc.getgob(pile.id) == None:
                continue
            self.gui.map.pfRightClick(pile, -1, 3, 1, None)
            self.gui.map.pfthread.join()
            availableFuelCoal = self.gui.maininv.getItemPartialCount("Coal")
            if availableFuelCoal >= 9:
                return


    def run(self):
        self.gui = HavenPanel.lui.root.getchild(GameUI)
        self.gui.add(self,Coord(self.gui.sz.x / 2 - self.sz.x / 2, self.gui.sz.y / 2 - self.sz.y / 2 - 200))
        self.gui.map.registerGobSelect(self)
        self.gui.map.registerAreaSelect(self)
        while self.state != State.TERM:
            if self.state == State.RUN:
                for crucibel in self.crucibels:
                    HavenPanel.lui.cons.out.println("Filling {0}".format(crucibel))
                    availableFuelCoal = self.gui.maininv.getItemPartialCount("Coal")
                    availableFuelBlock = self.gui.maininv.getItemPartialCount("Block")
                    availableFuelBranch = self.gui.maininv.getItemPartialCount("Branch")
                    if (availableFuelCoal < 9 and availableFuelBlock < 3 and availableFuelBranch < 18):
                        self.getfuel(self.gui.map.glob.oc)

                    fuel = self.gui.maininv.getItemPartial("Coal")
                    if fuel == None:
                        fuel = self.gui.maininv.getItemPartial("Block")
                    if fuel == None:
                        fuel = self.gui.maininv.getItemPartial("Branch")
                    if fuel == None:
                        continue

                    fuelticks = 0
                    if "Block" in fuel.item.getname():
                        fuelticks = 27
                    elif "Coal" in fuel.item.getname():
                        fuelticks = 11
                    else:
                        fuelticks = 5



                    self.gui.map.pfRightClick(crucibel, -1, 3, 0, None)
                    self.gui.map.pfthread.join()
                    cwnd = self.gui.waitfForWnd("Steelbox", 1500)
                    if cwnd == None:
                        self.gui.map.pfLeftClick(self.pointZero.mul(11).add(5,5), None)
                        self.gui.map.pfthread.join()
                        self.gui.map.pfRightClick(crucibel, -1, 3, 0, None)
                        self.gui.map.pfthread.join()
                    cwnd = self.gui.waitfForWnd("Steelbox", 1500)
                    if cwnd == None:
                        continue
                    vm = cwnd.getchild(VMeter)
                    if vm == None:
                        continue

                    if (vm.amount > (100 - fuelticks)):
                        continue

                    fueltoload = (100 - vm.amount) / fuelticks
                    fuelname = fuel.item.getname()

                    for step in range(fueltoload):
                        fuel.item.wdgmsg("take", Coord(fuel.item.sz.x / 2, fuel.item.sz.y / 2))
                        while(self.gui.hand.isEmpty() and self.state == State.RUN):
                            HavenPanel.lui.cons.out.println("Waiting for Fuel in hand!")
                            sleep(1)
                        self.gui.map.wdgmsg("itemact", Coord.z, crucibel.rc.floor(OCache.posres), 0, 0, int(crucibel.id), crucibel.rc.floor(OCache.posres), 0, -1)
                        while(not(self.gui.hand.isEmpty()) and self.state == State.RUN):
                            HavenPanel.lui.cons.out.println("Waiting for EMPTY hand!")
                            sleep(1)
                        fuel = self.gui.maininv.getItemPartial(fuelname)

                for second in range(3600):
                    if second % 600 == 0:
                        HavenPanel.lui.cons.out.println("Still alive sleeping: {0}".format(second))
                    sleep(1)







# Our Automation
with SteelRefuelerBot(Coord(270,180),"Steel Refueler Bot") as bot:
    bot.run()