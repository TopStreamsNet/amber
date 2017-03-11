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

from time import sleep, time

class State:
    WAIT, RUN, TERM = range(3)

class DreamHarvesterButton(Button):
    def __init__(self, width, caption):
        Button.__init__(self, width, caption)
    def click(self):
        print("Harvesting!")
        self.parent.state = State.RUN

class ClearButton(Button):
    def __init__(self, width, caption):
        Button.__init__(self, width, caption)
    def click(self):
        print("All Cleared!")
        self.parent.catchers=[]
        self.parent.lbl_catchers.settext("0")
        self.parent.chests=[]
        self.parent.lbl_chests.settext("0")
        self.parent.state = State.TERM

class DreamHarvesterBot(GobSelectCallback, Window):
    lbl_catchers = None
    lbl_chests = None

    catchers = []
    chests = []

    state = State.WAIT

    def __init__(self, coord, title):
        Window.__init__(self, coord, title)

        self.add(Label("Catchers selected: "), Coord(15, 15))
        self.lbl_catchers = Label("0")
        self.add(self.lbl_catchers, Coord(120,15))

        self.add(Label("Chests selected: "), Coord(15, 30))
        self.lbl_chests = Label("0")
        self.add(self.lbl_chests, Coord(120,30))

        dreamharvesterbtn = DreamHarvesterButton(70, "Harvest!")
        self.add(dreamharvesterbtn, Coord(65, 140))

        clearbtn = ClearButton(70, "Clear")
        self.add(clearbtn, Coord(140, 140))

    def gobselect(self, gob):
        res = gob.getres()
        if(res != None):
            print("gob selected: {0}".format(res.name))
            if(res.name.startswith("gfx/terobjs/dreca")):
                self.catchers.append(gob)
                self.lbl_catchers.settext("{0}".format(len(self.catchers)))
            elif(res.name.startswith("gfx/terobjs/chest")):
                self.chests.append(gob)
                self.lbl_chests.settext("{0}".format(len(self.chests)))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.destroy()

    def wdgmsg(self, sender, msg, *args):
        if sender == self.cbtn:
            self.die()

    def type(self, key, ev):
        if (key == 27):
            if (self.cbtn.visible):
                self.die()
                return True
        return False

    def die(self):
        self.reqdestroy()
        self.state = State.TERM

# Our Automation
with DreamHarvesterBot(Coord(270,180),"Dream Harvester Bot") as harvester:
    gui = HavenPanel.lui.root.getchild(GameUI)
    gui.map.registerGobSelect(harvester)
    gui.add(harvester, Coord(gui.sz.x / 2 - harvester.sz.x / 2, gui.sz.y / 2 - harvester.sz.y / 2 - 200))
    while harvester.state == State.WAIT:
        print("Sleeping")
        sleep(1)
    while harvester.state == State.RUN:
        for catcher in harvester.catchers:
            print("Checking catcher: {0}".format(catcher))
            HavenPanel.lui.root.getchild(GameUI).map.pfRightClick(catcher, -1, 3, 0, None)
            HavenPanel.lui.root.getchild(GameUI).map.pfthread.join()
            while HavenPanel.lui.root.getchild(FlowerMenu) is None and harvester.state == State.RUN:
                print("Waiting for flowers!")
                sleep(1)
            if HavenPanel.lui.root.getchild(FlowerMenu) is not None:
                print("Got Flowers! {0}".format(HavenPanel.lui.root.getchild(FlowerMenu)))
                HavenPanel.lui.root.getchild(FlowerMenu).choose(None)
                sleep(1)
                if HavenPanel.lui.root.getchild(FlowerMenu) is not None:
                    HavenPanel.lui.root.getchild(FlowerMenu).destroy()
            sleep(5)

    '''
    gui = HavenPanel.lui.root.getchild(GameUI)
    gui.add(harvester,Coord(gui.sz.x / 2 - harvester.sz.x / 2, gui.sz.y / 2 - harvester.sz.y / 2 - 200))
    HavenPanel.lui.root.getchild(GameUI).map.registerGobSelect(harvester)
    while(JythonAutomation.getInstance().getRun() != True):
        sleep(1)

    while(JythonAutomation.getInstance().getTerminate() == False):
        for catcher in harvester.catchers:
            print("Checking catcher: {0}".format(catcher))
            # RightClick the body and see what comes out
            HavenPanel.lui.root.getchild(GameUI).map.pfRightClick(catcher, -1, 3, 0, None)
            HavenPanel.lui.root.getchild(GameUI).map.pfthread.join()
            # Wait for choices
            t1 = time()
            while HavenPanel.lui.root.getchild(FlowerMenu) == None:
                print("Waiting for flowers!")
                sleep(1)
                if (time() - t1) > 5:
                    print("No flowers - go to sleep!")
                    sleep(600)
                    HavenPanel.lui.root.getchild(GameUI).map.pfRightClick(catcher, -1, 3, 0, None)
                    HavenPanel.lui.root.getchild(GameUI).map.pfthread.join()
                    t1 = time()
            flowermenu = HavenPanel.lui.root.getchild(FlowerMenu)
            for i in range(len(flowermenu.opts)):
                print("{0} {1}".format(i,flowermenu.opts[i]))
                if flowermenu.opts[i].name == "Harvest":
                    print("Going to Harvest {0}".format(catcher))
                    break
                    dreams_num_orig = gui.maininv.getItemPartialCount("Beautiful Dream")
                    flowermenu.choose(flowermenu.opts[i])
                    t1 = time()
                    while(dreams_num_orig >= gui.maininv.getItemPartialCount("Beautiful Dream")):
                        print("Waiting for dreams!")
                        sleep(1)
                        if (time() - t1) > 5:
                            break
                    break
            dreams_num = gui.maininv.getItemPartialCount("Beautiful Dream")
            while (dreams_num >= 12):
                print("Have dreams {0}".format(dreams_num))
                for chest in harvester.chests:
                    HavenPanel.lui.root.getchild(GameUI).map.pfRightClick(chest, -1, 3, 0, None)
                    HavenPanel.lui.root.getchild(GameUI).map.pfthread.join()
                    spwnd = gui.waitfForWnd("Chest", 1500);
                    if spwnd == None:
                        continue
                    dream = gui.maininv.getItemPartial("Beautiful Dream")
                    dream.item.wdgmsg("transfer-identical", dream.item)
                    dreams_num_orig = gui.maininv.getItemPartialCount("Beautiful Dream")
                    t1 = time()
                    while(dreams_num_orig == gui.maininv.getItemPartialCount("Beautiful Dream")):
                        print("Waiting for dreams to be gone!")
                        sleep(1)
                        if (time() - t1) > 5:
                            break
                    dreams_num = gui.maininv.getItemPartialCount("Beautiful Dream")
                    if dreams_num == 0:
                        break
    '''









