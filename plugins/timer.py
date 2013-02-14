from lib.EventHandler import EventHandler, Event
from lib.Plugin import Plugin

class P(Plugin):
    def loaded(self):
        self.events = EventHandler()
        print "timer module loaded"
    
    def update(self, diff):
        self.events.update(diff)
        
        while 1:
            event = self.events.next()
            if not event:
                break
                
            if (event.getName() == "reminder"):
                self.send("NOTICE %s :Timer expired!" % event.getBlob())
        
    def onMsg(self, msg):
        tok = msg.tokenize()
        
        if (tok[0] == "!timer"):
            if (len(tok) < 2):
                self.send("NOTICE %s :Syntax: !timer <delay>" % msg.nick)
            else:
                if (not tok[1].isdigit()):
                    self.send("NOTICE %s :TypeError: Delay needs to be a decimal value!" % msg.nick)
                else:
                    self.events.register("reminder", int(tok[1]) * 1000 * 60, msg.nick)
                    self.send("NOTICE %s :Timer set for %s minutes." % (msg.getUser()[0], tok[1]))
