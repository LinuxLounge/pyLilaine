from lib.Plugin import Plugin
import random

class P(Plugin):
    # configuration
    nickname = "Lilaine"
    secondary_nickname = "Lily"
    
    # here be dragons
    def loaded(self):
        print "nickname_keeper module loaded\n\tprimary=%s, secondary=%s" % (self.nickname, self.secondary_nickname)
        
    def onRaw(self, msg):
        # print "[nickname_keeper] debug - raw_event=%d - msg=%s" % (msg.type, msg.message)
        if (msg.getType() == 433):
            # 433: nickname :Nickname is already in use.
            tok = msg.tokenize()
            if (tok[1] == self.nickname):
                self.send("NICK %s" % self.secondary_nickname)
                self.send("WATCH +%s" % self.nickname)
                print "[nickname_keeper] Nickname taken, putting it on the watchlist..."
            elif (tok[1] == self.secondary_nickname):
                self.send("NICK %s%d" % (self.nickname, random.randrange(1,999)))
                print "[nickname_keeper] Secondary nickname also taken, adding some random numbers."
        elif (msg.getType() == 601) or (msg.getType() == 605):
            # 601 THIS IS SOME WORKAROUND FOR UNREALIRCD MADNESS, WTF?!
            # 605: nick userid host time :is offline
            tok = msg.tokenize()
            if (tok[1] == self.nickname):
                print "[nickname_keeper] Our nickname was given up, changing now and clearing watchlist!"
                self.send("NICK %s" % self.nickname)
                self.send("WATCH -%s" % self.nickname)
