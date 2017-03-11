import JbotUtils
reload(JbotUtils)
from JbotUtils import *

import haven.automation.PrivMsgCallback as PrivMsgCallback

from time import sleep
from synchronize import make_synchronized

class MetaBot(PrivMsgCallback):
    run = True
    def privmsg(self, frm, line):
        print "{0}: {1}".format(frm, line)
        if line == "exit":
            self.run = False

q = MetaBot()
HavenPanel.lui.root.getchild(GameUI).map.registerprivmsgcb(q)
while q.run == True:
    sleep(1)