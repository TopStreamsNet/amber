import haven.Window as Window
import haven.Coord2d as Coord2d
import haven.Button as Button
import haven.FlowerMenu as FlowerMenu
import haven.automation.Utils as Utils
import haven.automation.GobSelectCallback as GobSelectCallback
import haven.automation.AreaSelectCallback as AreaSelectCallback
import haven.ResDrawable as ResDrawable
import haven.FastMesh.MeshRes as MeshRes


from time import sleep, time

import JbotUtils
reload(JbotUtils)
from JbotUtils import *

# Config
PLANT_FREQ = 3600
PLANT_NUM = 1
HARVEST_STAGE = 3
TIMEOUT = 5
MAX_SEEDS = 14

class State:
    WAIT, RUN, TERM = range(3)

class StartButton(Button):
    def __init__(self, width, caption):
        Button.__init__(self, width, caption)
    def click(self):
        self.parent.field_length = self.parent.BottomRight.x - self.parent.TopLeft.x + 1
        self.parent.field_width = self.parent.BottomRight.y - self.parent.TopLeft.y + 1
        self.parent.state = State.RUN
        HavenPanel.lui.cons.out.println("Farming!")

class ClearButton(Button):
    def __init__(self, width, caption):
        Button.__init__(self, width, caption)
    def click(self):
        self.parent.state = State.WAIT
        HavenPanel.lui.cons.out.println("All Cleared!")

class FarmerBot(GobSelectCallback, AreaSelectCallback, Window):
    state = State.WAIT
    gui = None

    TopLeft = None
    BottomRight = None
    field_length = 0
    field_width = 0

    next_tile = 0

    last_planted_cycle = 0
    last_planted_num = 0

    seedbarrels_gobs = []
    lbl_seedbarrels = None

    barrelsInfo = {}
    barrelsInfo_dirty = True

    def __init__(self, coord, title):
        Window.__init__(self, coord, title)

        self.add(Label("Seedbarrels selected: "), Coord(15, 15))
        self.lbl_seedbarrels = Label("0")
        self.add(self.lbl_seedbarrels, Coord(170,15))

        startbtn = StartButton(70, "Farm!")
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

    def type(self, key, ev):
        if (key == 27):
            if (self.cbtn.visible):
                self.die()
                return True
        return False

    def die(self):
        self.reqdestroy()
        self.state = State.TERM

    def gobselect(self, gob):
        res = gob.getres()
        if(res != None):
            HavenPanel.lui.cons.out.println("gob selected: {0}".format(res.name))
            if res.name.startswith("gfx/terobjs/barrel") and gob not in self.seedbarrels_gobs:
                self.seedbarrels_gobs.append(gob)
                self.lbl_seedbarrels.settext("{0}".format(len(self.seedbarrels_gobs)))

    def areaselect(self, a, b):
        HavenPanel.lui.cons.out.println("Coord A {0} : Coord B {1}".format(a,b))
        self.TopLeft = a
        self.BottomRight = b

    def check_next_tile(self):
        shift_width=int(self.next_tile/self.field_width)
        shift_length=self.next_tile%self.field_width
        coord = self.TopLeft.add(shift_width,shift_length).mul(11).add(5,5)
        #HavenPanel.lui.cons.out.println("tile {0} {1}:{2}".format(self.next_tile,shift_width,shift_length))
        ability  = "CanPlant"
        tile = self.next_tile
        for gob in gettilegobs(self.gui.map.glob.oc, Coord2d(coord)):
            res = gob.getres()
            if res.name.startswith("gfx/terobjs/plants"):
                rd = gob.getattr(ResDrawable)
                stage = 0
                stgmaxval = 0
                if rd != None:
                    stage = rd.sdt.peekrbuf(0)
                    for layer in res.layers(MeshRes):
                        stg = layer.id / 10
                        if (stg > stgmaxval):
                            stgmaxval = stg
                    #HavenPanel.lui.cons.out.println("Found {0} stage {1}/{2}".format(res.name,stage,stgmaxval))
                    if stage == stgmaxval or stage == HARVEST_STAGE:
                        #HavenPanel.lui.cons.out.println("Crop is ripe - Harvesting")
                        coord = gob
                        ability = "CanHarvest"
                    else:
                        #HavenPanel.lui.cons.out.println("Crop is growing - go next")
                        ability = "Skip"
        self.next_tile = (self.next_tile+1)%(self.field_length*self.field_width)
        return [ability, tile, coord]

    def cur_cycle(self):
        return int(self.gui.map.glob.globtime()/1000/PLANT_FREQ)

    def shouldplant(self):
        if self.cur_cycle() > self.last_planted_cycle:
            #HavenPanel.lui.cons.out.println("New cycle {0}".format(self.cur_cycle()))
            return True
        elif self.cur_cycle() == self.last_planted_cycle and self.last_planted_num < PLANT_NUM:
            HavenPanel.lui.cons.out.println("Planting {0}/{1} : {2}".format(self.last_planted_num+1,PLANT_NUM,self.cur_cycle()))
            return True
        return False

    def plant(self, tile, coord):
        iteminfo = self.gui.vhand.item.info()
        ninf = ItemInfo.find(GItem.NumberInfo, iteminfo)
        num = ninf.itemnum()
        f = open('plant.log', 'a+')
        f.write("[{0}] dt {1} mp {2} yt {3} tile={4} quality={5}\n".format(self.gui.map.glob.servertime,
                                                                           self.gui.map.glob.ast.dt,
                                                                           self.gui.map.glob.ast.mp,
                                                                           self.gui.map.glob.ast.yt,
                                                                           tile,
                                                                           self.gui.vhand.item.quality().q))
        f.close()
        if num == 5:
            itemactcoord(coord,True,TIMEOUT,Coord(self.TopLeft.x+self.field_length/2,self.TopLeft.y+self.field_width/2))
        else:
            itemactcoord(coord,False)
            new_num = num
            while(new_num == num):
                sleep(1)
                iteminfo = self.gui.vhand.item.info()
                ninf = ItemInfo.find(GItem.NumberInfo, iteminfo)
                new_num = ninf.itemnum()
            slot = getfreeslot(self.gui.vhand,self.gui.maininv)
            self.gui.maininv.drop(Coord.z,slot)

        self.last_planted_num += 1
        self.last_planted_cycle = self.cur_cycle()

    def getBarrelInfo(self):
        for barrel in self.seedbarrels_gobs:
            # Open barrel
            self.gui.map.pfRightClick(barrel, -1, 3, 0, None)
            self.gui.map.pfthread.join()
            brlwnd = self.gui.waitfForWnd("Barrel", 1500)
            # If it didn't work move and try again
            if fallbackonfail((brlwnd == None),Coord(self.TopLeft.x+self.field_length/2,self.TopLeft.y+self.field_width/2)):
                self.gui.map.pfRightClick(barrel, -1, 3, 0, None)
                self.gui.map.pfthread.join()
                brlwnd = self.gui.waitfForWnd("Barrel", 1500)
            # If this barrel still can not be open - go next
            if brlwnd == None:
                continue
            brlInfo = getBarrelContent(brlwnd)
            quality = 0
            if brlInfo['quantity'] > 0:
                previous_seeds_count = self.gui.maininv.getItemPartialCount("seeds")
                previous_seeds = self.gui.maininv.getItemsPartial("seeds")
                self.gui.map.pfRightClick(barrel, -1, 3, 1, None)
                self.gui.map.pfthread.join()
                tout=0
                while(self.gui.maininv.getItemPartialCount("seeds") <= previous_seeds_count):
                    sleep(1)
                    tout += 1
                    if tout > TIMEOUT:
                        break
                # Not getting any seeds
                if tout > TIMEOUT:
                    continue
                # Check new seeds
                for seeds in self.gui.maininv.getItemsPartial("seeds"):
                    if seeds in previous_seeds:
                        continue
                    quality = seeds.item.quality().q

                    if takeitem(seeds,TIMEOUT):
                        itemactgob(barrel,0,True,TIMEOUT)
            HavenPanel.lui.cons.out.println("Barrel {0} quality {1} quantity {2} content {3}".format(barrel,
                                                                                                     quality,
                                                                                                     brlInfo['quantity'],
                                                                                                     brlInfo['item']))
            self.barrelsInfo[barrel]={'quality':quality, 'quantity':brlInfo['quantity']}
            self.barrelsInfo_dirty=False

    def sortseeds(self):
        for seeds in self.gui.maininv.getItemsPartial("seed"):
            seedquality = seeds.item.quality().q
            seednum = getnum(seeds)
            trash = None
            for barrelInfo in sorted(self.barrelsInfo.items(), key=lambda x: x[1]['quality'], reverse=True):
                (barrel, info) = barrelInfo
                if seedquality >= info['quality']:
                    if takeitem(seeds,TIMEOUT):
                        itemactgob(barrel,0,True,TIMEOUT,Coord(self.TopLeft.x+self.field_length/2,self.TopLeft.y+self.field_width/2))
                        self.barrelsInfo[barrel]['quantity'] += seednum
                    break
                trash = barrel
            if trash != None:
                if takeitem(seeds,TIMEOUT):
                    itemactgob(trash,0,True,TIMEOUT,Coord(self.TopLeft.x+self.field_length/2,self.TopLeft.y+self.field_width/2))
                    self.barrelsInfo[trash]['quantity'] += seednum
        self.barrelsInfo_dirty = True

    def getseedsfrombarrel(self, barrel):
        seeds = None
        HavenPanel.lui.cons.out.println("GetSeed {0}".format(barrel))
        previous_seeds_count = self.gui.maininv.getItemPartialCount("seeds")
        previous_seeds = self.gui.maininv.getItemsPartial("seeds")
        self.gui.map.pfRightClick(barrel, -1, 3, 1, None)
        self.gui.map.pfthread.join()
        tout=0
        while(self.gui.maininv.getItemPartialCount("seeds") <= previous_seeds_count):
            sleep(1)
            tout += 1
            if tout > TIMEOUT:
                break
        if fallbackonfail((tout > TIMEOUT),Coord(self.TopLeft.x+self.field_length/2,self.TopLeft.y+self.field_width/2)):
            self.gui.map.pfRightClick(barrel, -1, 3, 1, None)
            self.gui.map.pfthread.join()
            while(self.gui.maininv.getItemPartialCount("seeds") <= previous_seeds_count):
                sleep(1)
                tout += 1
                if tout > TIMEOUT:
                    break
        for seeds in self.gui.maininv.getItemsPartial("seeds"):
            if seeds not in previous_seeds:
                iteminfo = seeds.item.info()
                ninf = ItemInfo.find(GItem.NumberInfo, iteminfo)
                num = ninf.itemnum()
                self.barrelsInfo[barrel]['quantity'] -= num
        return seeds

    def takeseed(self):
        topq = 0
        topseeds = None
        for seeds in self.gui.maininv.getItemsPartial("seeds"):
            if seeds.item.quality().q >= topq:
                iteminfo = seeds.item.info()
                ninf = ItemInfo.find(GItem.NumberInfo, iteminfo)
                num = ninf.itemnum()
                if num >= 5:
                    topq = seeds.item.quality().q
                    topseeds = seeds
        for barrelInfo in sorted(self.barrelsInfo.items(), key=lambda x: x[1]['quality'], reverse=True):
            (barrel, info) = barrelInfo
            if info['quality'] > topq:
                if info['quantity'] >= 5:
                    tmpseeds = self.getseedsfrombarrel(barrel)
                    if(tmpseeds != None):
                        topq = tmpseeds.item.quality().q
                        topseeds = tmpseeds
                    break
        if topseeds != None:
            takeitem(topseeds, TIMEOUT)
        '''
        else:
            HavenPanel.lui.cons.out.println("No seeds to plant")
        '''
        return not(self.gui.hand.isEmpty())

    def harvest(self, tile, harvestable):
        self.gui.map.pfRightClick(harvestable, -1, 3, 0, None)
        self.gui.map.pfthread.join()
        tout = 0
        while HavenPanel.lui.root.getchild(FlowerMenu) == None and self.state == State.RUN:
            sleep(1)
            tout += 1
            if tout > TIMEOUT:
                break
        if fallbackonfail((tout > TIMEOUT),Coord(self.TopLeft.x+self.field_length/2,self.TopLeft.y+self.field_width/2)):
            self.gui.map.pfRightClick(harvestable, -1, 3, 0, None)
            self.gui.map.pfthread.join()
            tout = 0
            while HavenPanel.lui.root.getchild(FlowerMenu) == None and self.state == State.RUN:
                sleep(1)
                tout += 1
                if tout > TIMEOUT:
                    return
        flowermenu = HavenPanel.lui.root.getchild(FlowerMenu)
        for i in range(len(flowermenu.opts)):
            if flowermenu.opts[i].name == "Harvest":
                previous_seeds = self.gui.maininv.getItemsPartial("seeds")
                previous_nums = {}
                for seeds in previous_seeds:
                    previous_nums[seeds]=getnum(seeds)

                HavenPanel.lui.cons.out.println("Going to Harvest {0}".format(harvestable))
                flowermenu.choose(flowermenu.opts[i])
                if Utils.waitForProgressFinish(self.gui,6000,"Stuck in Harvesting") == True:
                    for seeds in self.gui.maininv.getItemsPartial("seeds"):
                        if seeds not in previous_seeds:
                            f = open('plant.log', 'a+')
                            f.write("[{0}] tile={1} quality={2}\n".format(self.gui.map.glob.servertime,
                                                                                       tile,
                                                                                       seeds.item.quality().q))
                            f.close()
                            break
                        elif getnum(seeds) != previous_nums[seeds]:
                            f = open('plant.log', 'a+')
                            f.write("[{0}] tile={1} quality={2}\n".format(self.gui.map.glob.servertime,
                                                                          tile,
                                                                          seeds.item.quality().q))
                            f.close()
                            break
                break

    def run(self):
        self.gui = HavenPanel.lui.root.getchild(GameUI)
        self.gui.add(self,Coord(self.gui.sz.x / 2 - self.sz.x / 2, self.gui.sz.y / 2 - self.sz.y / 2 - 200))
        self.gui.map.registerGobSelect(self)
        self.gui.map.registerAreaSelect(self)
        while self.state != State.TERM:
            if self.state == State.RUN:
                if self.barrelsInfo_dirty == True:
                    self.getBarrelInfo()
                [ability, tile, coord] = self.check_next_tile()
                if ability == "CanPlant" and self.shouldplant() == True and self.takeseed() == True:
                    HavenPanel.lui.cons.out.println("Next action: {0} tile: {1} coord: {2}".format(ability, tile, coord))
                    self.plant(tile, Coord2d(coord))
                elif ability == "CanHarvest":
                    HavenPanel.lui.cons.out.println("Next action: {0} tile: {1} coord: {2}".format(ability, tile, coord))
                    self.harvest(tile,coord)

                if self.gui.maininv.getItemPartialCount("seed") > MAX_SEEDS:
                    HavenPanel.lui.cons.out.println("Sorting seeds!")
                    self.sortseeds()
            elif self.state == State.WAIT:
                sleep(1)

with FarmerBot(Coord(270,180),"Farmer Bot") as bot:
    bot.run()