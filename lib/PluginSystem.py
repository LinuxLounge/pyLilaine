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
        
    def kill(self):
        self.kill_received = True

    def update(self, diff):
        for p in self.plugins:
            p.update(diff)

    def _process(self, msg): 
        msgType = msg.getType()

        if isinstance(msgType, int):
            # Numerical RAW
            # :irc.host.org 000 nickname :message
            for p in self.plugins:
                p.onRaw(msg)
        elif msgType == "PRIVMSG":
            # PRIVMSG
            # :nick!user@host PRIVMSG target :message
            # target = #chan | nick
            for p in self.plugins:
                p.onMsg(msg)
        elif msgType == "CTCP":
            # CTCP
            for p in self.plugins:
                p.onCTCP(msg)
        elif msgType == "NOTICE":
            # NOTICE
            # :nick!user@host NOTICE target :message
            # target = #chan | nick
            for p in self.plugins:
                p.onNotice(msg)
        elif msgType == "JOIN":
            # JOIN
            # :nick!user@host JOIN :#chan
            #  ------1-------       --2--
            for p in self.plugins:
                p.onJoin(msg.getUser(), msg.getTarget())
        elif msgType == "PART":
            # PART
            # :nick!user@host PART #chan :message
            #  ------1-------      --2--  ---3---
            for p in self.plugins:
                p.onPart(msg.getUser(), msg.getTarget(), msg.getMessage())
        elif msgType == "TOPIC":
            # TOPIC
            # :nick!user@host TOPIC #chan :message
            #                       --1--  ---2---
            for p in self.plugins:
                p.onTopic(msg.getUser(), msg.getTarget(), msg.getMessage())
        elif msgType == "NICK":
            # NICK
            # :nick!user@host NICK :newnick
            #  ------1-------       ---2---
            for p in self.plugins:
                p.onNick(msg.getUser(), msg.getMessage())
        elif msgType == "MODE":
            # MODE
            # :nick!user@host MODE #chan :+nt
            #  ------1-------      --2--  -3-
            for p in self.plugins:
                p.onMode(msg.getUser(), msg.getTarget(), msg.getMode())
        elif msgType == "USERMODE":
            # MODE
            # :nick MODE nick :+iwxz
            #  --1-      --2-  --3--
            for p in self.plugins:
                p.onUserMode(msg.getNick(), msg.getTarget(), msg.getMode())
        elif msgType == "KICK":
            # KICK
            # :nick!user@host KICK #chan nick :reason
            #  ------1-------      --2-- --3-  ---4--
            for p in self.plugins:
                p.onKick(msg.getUser(), msg.getTarget(), msg.getVictim(), msg.getMessage())
