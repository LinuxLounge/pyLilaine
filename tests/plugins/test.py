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
