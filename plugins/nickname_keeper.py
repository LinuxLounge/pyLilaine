from lib.EventHandler import EventHandler, Event
from lib.Plugin import Plugin
import random

class P(Plugin):
    # configuration
    nickname = "Lilaine"
    secondary_nickname = "Lily"
    
    # here be dragons
    def loaded(self):
        self.events = EventHandler()
        self.working = False
        print("nickname_keeper module loaded\n\tprimary=%s, secondary=%s" % (self.nickname, self.secondary_nickname))
        
    def onRaw(self, msg):
        # print "[nickname_keeper] debug - raw_event=%d - msg=%s" % (msg.getType(), msg.getMessage())
        if (msg.getType() == 433):
            # 433: nickname :Nickname is already in use.
            tok = msg.getMessage().split()
            if (tok[3] == self.nickname):
                self.send("NICK %s" % self.secondary_nickname)
                self.send("WATCH +%s" % self.nickname)
                self.working = True
                print("[nickname_keeper] Nickname taken, putting it on the watchlist...")
            elif (tok[3] == self.secondary_nickname):
                self.send("NICK %s%d" % (self.nickname, random.randrange(1,999)))
                print("[nickname_keeper] Secondary nickname also taken, adding some random numbers.")
        elif (msg.getType() == 601) or (msg.getType() == 605):
            # 601 THIS IS SOME WORKAROUND FOR UNREALIRCD MADNESS, WTF?!
            # 605: nick userid host time :is offline
            tok = msg.getMessage().split()
            if (tok[3] == self.nickname):
                print("[nickname_keeper] Our nickname was given up, changing now and clearing watchlist!")
                self.send("NICK %s" % self.nickname)
                self.send("WATCH -%s" % self.nickname)
                self.working = False
        elif (msg.getType() == 451):
            # 451: WATCH :You have not registered
            self.events.register("watch", 10000, self.nickname) # retry
            print("[nickname_keeper] Tried to WATCH too early, retrying in 10s")
            
    def update(self, diff):
        self.events.update(diff)
        
        while 1:
            event = self.events.next()
            if not event:
                break
            
            if (event.getName() == "watch"):
                if (self.working):
                    self.send("WATCH +%s" % event.getBlob())
                    
    def onNick(self, user, newnick):
        if (user[0] == self.nickname):
            self.send("NICK %s" % self.nickname)
            self.send("WATCH -%s" % self.nickname)
            self.working = False
