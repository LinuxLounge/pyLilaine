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
        
    def onNotice(self, msg):
        pass
        
    def onCTCP(self, msg):
        pass
