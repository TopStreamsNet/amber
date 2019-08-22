import haven.HavenPanel as HavenPanel
import haven.automation.Utils as Utils
import haven.GameUI as GameUI
import haven.Charlist as Charlist
import haven.FlowerMenu as FlowerMenu

import time

while True:
    HavenPanel.lui.cons.out.println("Clay from Py")
    time.sleep(10)
    gui = HavenPanel.lui.root.getchild(GameUI)
    gob = Utils.findObjectByNames(gui, 1000, ["gfx/terobjs/herbs/clay-cave", "gfx/terobjs/herbs/glimmermoss", "gfx/terobjs/herbs/cavelanternNOT"])
    while gob != None:
        print("Gob: {0}".format(gob))
        gui.map.pfRightClick(gob, -1, 3, 0, None)
        gui.map.pfthread.join()
        index = 0
        while HavenPanel.lui.root.getchild(FlowerMenu) == None:
            print("No Flower Menu!")
            index = index + 1
            time.sleep(1)
            if index >= 5:
                break
        if index < 5:
            flowermenu = HavenPanel.lui.root.getchild(FlowerMenu)
            for i in range(len(flowermenu.opts)):
                if flowermenu.opts[i].name == "Pick":
                    flowermenu.choose(flowermenu.opts[i])
                    print("Picking!")
                    time.sleep(5)
        gob = Utils.findObjectByNames(gui, 1000, ["gfx/terobjs/herbs/clay-cave", "gfx/terobjs/herbs/glimmermoss", "gfx/terobjs/herbs/cavelanternNOT"])


    HavenPanel.lui.cons.run("act lo cs")
    Utils.waitForProgressFinish(gui,5000,"Stuck in CharSelect")
    while True:
        print("Going to sleep!")
        Wdg = HavenPanel.lui.root.rnext()
        while Wdg != None:
            if Charlist.isInstance(Wdg):
                break
            Wdg = Wdg.rnext()
        if Charlist.isInstance(Wdg):
            for i in xrange(0,20*60):
                print("Sleeping! {0}".format(i))
                time.sleep(1)
            print("Relogging!")
            Wdg.wdgmsg(Wdg,"play","Sally Shears")
            break

