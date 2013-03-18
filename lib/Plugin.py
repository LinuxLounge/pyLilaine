class Plugin(object):
    def __init__(self, out):
        self.out = out
        self.loaded()
        
    def send(self, msg):
	    self.out.put(msg)
	    
    def loaded(self):
        pass
	    
    def update(self, diff): # diff = time in ms since last call
        pass
        
    def onRaw(self, msg):
        pass
        
    def onMsg(self, msg):
        pass
        
    def onCTCP(self, msg): # ctcp is actually a subtype of privmsg
        pass
        
    def onNotice(self, msg):
        pass
        
    def onJoin(self, user, channel):
        pass
        
    def onPart(self, user, channel, message):
        pass
        
    def onQuit(self, user, message):
        pass
        
    def onTopic(self, user, channel, message):
        pass

    def onNick(self, user, newnick):
        pass
        
    def onMode(self, user, channel, mode):
        pass
        
    def onUserMode(self, nick, target, mode): # user mode events do not send ident/host
        pass
        
    def onKick(self, user, channel, victim, reason):
        pass

    def onCommand(self, target, msg):
        pass
