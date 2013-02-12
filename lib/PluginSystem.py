from Message import Message
import string, sys, os.path, imp, Queue


class PluginSystem(object):
    def __init__(self, path):
    	self.kill_received = False
        self.plugins = []
        self.path = path
        self.qin = Queue.Queue() # recv queue
        self.qout = Queue.Queue() # send queue
        self.load()
        
    def clear(self):
        self.plugins = [] # feed the gc!

    def load(self):
        plugin_files = [x[:-3] for x in os.listdir(self.path) if x.endswith(".py") and not x.startswith("__init__")]
        sys.path.insert(0, self.path)
        for plugin in plugin_files:
            p = __import__(plugin)
            imp.reload(p) # this is necessary for the module to be properly reimported when it has actually changed
            self.plugins.append(p.P(self.qout))

    def reload(self):
        self.clear()
        self.load()

    def run(self):
        while not self.kill_received:
            try:
                msg = Message(self.qin.get(timeout=2))
                self._process(msg)
            except Queue.Empty:
                pass
        print "Shutting down PluginSystem"

    def _process(self, msg): 
        msgType = msg.getType()

        if isinstance(msgType, int):
            # Numerical RAW
            for p in self.plugins:
                p.onRaw(msg)
        elif msgType == "PRIVMSG":
            # PRIVMSG
            for p in self.plugins:
                p.onMsg(msg)
        elif msgType == "CTCP":
            # CTCP
            for p in self.plugins:
                p.onCTCP(msg)
        elif msgType == "NOTICE":
            # NOTICE
            for p in self.plugins:
                p.onNotice(msg)
#        elif tok[1] == "JOIN":
#            for p in self.plugins:
#                p.onUserJoinedChannel(irc.getIdentitiy(tok[0]), tok[2][1:]) # Identity, Channel
#        elif tok[1] == "PART":
#            for p in self.plugins:
#                p.onUserLeftChannel(irc.getIdentitiy(tok[0]), tok[2]) # Identity, Channel
