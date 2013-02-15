from Message import Message
import string, sys, os.path, imp, Queue

class PluginSystem(object):
    def __init__(self):
    	self.kill_received = False
        self.qin = Queue.Queue() # recv queue
        self.qout = Queue.Queue() # send queue
        self.clear()
        
    # Plugin Loading/Unloading
    def clear(self):
        self.__plugins__ = [] # feed the gc!

    def loadDirectory(self, path):
        self.clear()
        self.__path__ = path
        
        plugin_files = [x[:-3] for x in os.listdir(self.__path__) if x.endswith(".py") and not x.startswith("__init__")]
        sys.path.insert(0, self.__path__)
        
        for plugin in plugin_files:
            self.loadPlugin(plugin)
            
    def loadPlugin(self, plugin):
        p = __import__(plugin)
        imp.reload(p) # triggers recompile
        self.__plugins__.append(p.P(self.qout)) # remember instance and hand oover send queue
        
    def loadPluginTesting(self, plugin_instance): # this is an interface for unit testing only
        self.__plugins__.append(plugin_instance)

    def reload(self):
        if self.__path__:
            self.loadPluginDirectory(self.__path__)

    # Runtime Processing
    def run(self):
        while not self.kill_received:
            try:
                msg = Message(self.qin.get(timeout=2))
                self.process(msg)
            except Queue.Empty:
                pass
        print "Shutting down PluginSystem"
        
    def kill(self):
        self.kill_received = True

    def update(self, diff):
        for p in self.__plugins__:
            p.update(diff)

    def process(self, msg): 
        msgType = msg.getType()

        if isinstance(msgType, int):
            # Numerical RAW
            # :irc.host.org 000 nickname :message
            for p in self.__plugins__:
                p.onRaw(msg)
        elif msgType == "PRIVMSG":
            # PRIVMSG
            # :nick!user@host PRIVMSG target :message
            # target = #chan | nick
            for p in self.__plugins__:
                p.onMsg(msg)
        elif msgType == "CTCP":
            # CTCP
            for p in self.__plugins__:
                p.onCTCP(msg)
        elif msgType == "NOTICE":
            # NOTICE
            # :nick!user@host NOTICE target :message
            # target = #chan | nick
            for p in self.__plugins__:
                p.onNotice(msg)
        elif msgType == "JOIN":
            # JOIN
            # :nick!user@host JOIN :#chan
            #  ------1-------       --2--
            for p in self.__plugins__:
                p.onJoin(msg.getUser(), msg.getTarget())
        elif msgType == "PART":
            # PART
            # :nick!user@host PART #chan :message
            #  ------1-------      --2--  ---3---
            for p in self.__plugins__:
                p.onPart(msg.getUser(), msg.getTarget(), msg.getMessage())
        elif msgType == "TOPIC":
            # TOPIC
            # :nick!user@host TOPIC #chan :message
            #                       --1--  ---2---
            for p in self.__plugins__:
                p.onTopic(msg.getUser(), msg.getTarget(), msg.getMessage())
        elif msgType == "NICK":
            # NICK
            # :nick!user@host NICK :newnick
            #  ------1-------       ---2---
            for p in self.__plugins__:
                p.onNick(msg.getUser(), msg.getMessage())
        elif msgType == "MODE":
            # MODE
            # :nick!user@host MODE #chan :+nt
            #  ------1-------      --2--  -3-
            for p in self.__plugins__:
                p.onMode(msg.getUser(), msg.getTarget(), msg.getMode())
        elif msgType == "USERMODE":
            # MODE
            # :nick MODE nick :+iwxz
            #  --1-      --2-  --3--
            for p in self.__plugins__:
                p.onUserMode(msg.getNick(), msg.getTarget(), msg.getMode())
        elif msgType == "KICK":
            # KICK
            # :nick!user@host KICK #chan nick :reason
            #  ------1-------      --2-- --3-  ---4--
            for p in self.__plugins__:
                p.onKick(msg.getUser(), msg.getTarget(), msg.getVictim(), msg.getMessage())
