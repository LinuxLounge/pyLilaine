import sys
sys.path.append("../../")

from lib.Plugin import Plugin

class TestPlugin(Plugin):
    """
    This is a Plugin with the sole purpose
    to give back feedback to the related
    unit test
    """
    def loaded(self):
        self.lastEvent = None
    
    def setUnitTestInstance(self, instance):
        self.unittest = instance
        
    def getLastMessage(self):
        return self.lastEvent
        
    def onMsg(self, msg):
        self.lastEvent = msg
        
    def onNotice(self, msg):
        self.lastEvent = msg
        
    def onRaw(self, msg):
        self.lastEvent = msg
        
    def onCTCP(self, msg):
        self.lastEvent = msg
        
    def onJoin(self, user, channel):
        self.lastEvent = (user, channel)
        
    def onPart(self, user, channel, message):
        self.lastEvent = (user, channel, message)
        
    def onQuit(self, user, message):
        self.lastEvent = (user, message)
        
    def onTopic(self, user, channel, message):
        self.lastEvent = (user, channel, message)

    def onNick(self, user, newnick):
        self.lastEvent = (user, newnick)
        
    def onMode(self, user, channel, mode):
        self.lastEvent = (user, channel, mode)
        
    def onUserMode(self, nick, target, mode):
        self.lastEvent = (nick, target, mode)
        
    def onKick(self, user, channel, victim, reason):
        self.lastEvent = (user, channel, victim, reason)
