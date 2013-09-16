class Message(object):
    def __init__(self, raw_message, authed = []):
        self.__raw__ = raw_message
        self.__tok__ = self.__raw__.split()
        self.__authed__ = False
        # type
        self.__type__ = self.__tok__[1]

        # server / user!ident@host
        if "@" in self.__tok__[0]:
            (self.__nick__, self.__ident__, self.__host__) = self.__parseHostmask__()
            if (self.__nick__+self.__ident__+self.__host__ in authed):
                self.__authed__ = True
        else:
            self.__server__ = self.__tok__[0][1:]
        
        # target    
        self.__target__ = self.__tok__[2]
        
        # message
        # Numerical RAW
        if self.__type__.isdigit():
            self.__message__ = raw_message # too many different formats, leave parsing to plugins
            self.__type__ = int(self.__type__)
        # PRIVMSG
        elif (self.__type__ == "PRIVMSG"):
            self.__message__ = self.__raw__.split(":", 2)[2]
            # CTCP (is actually a PRIVMSG, but we treat it as type=CTCP)
            try:
                if (ord(self.__message__[0]) == 1 and ord(self.__message__[-1]) == 1):
                    self.__type_ = "CTCP"
                    self.__message__ = self.__message__.split(chr(1))[1]
            except IndexError:
                pass
                 
        # NOTICE NICK TOPIC PART
        # are already handled above, at this time no further optimization necessary
        elif (self.__type__ == "NOTICE") or (self.__type__ == "NICK") or (self.__type__ == "TOPIC") or (self.__type__ == "PART") or (self.__type__ == "QUIT"):
           self.__message__ = self.__raw__.split(":", 2)[2]
        
        # JOIN
        # message contains channel name
        elif (self.__type__ == "JOIN"):
            self.__target__ = self.__tok__[2][1:]
        
        # MODE
        # separate between channel and usermode
        elif (self.__type__ == "MODE"):
            if (not self.__tok__[2].startswith("#")):
                self.__type__ = "USERMODE"
                self.__nick__ = self.__tok__[0][1:] # for a usermode change we only receive the nickname, no ident or host
                self.__mode__ = self.__raw__.split(":", 2)[2]
            else:
                self.__mode__ = " ".join(self.__tok__[3:]) # channel modes are not prefixed by a colon
        
        # KICK
        # has two targets, channel and nick
        elif (self.__type__ == "KICK"):
            self.__victim__ = self.__tok__[3]
            self.__message__ = " ".join(self.__tok__[4:])[1:]
       
        else:
            # we might remove this later, but for now we need to test if everything is handled properly
            print("[warning] Message objected with unhandled type '%s' created." % self.__type__)

    # private
    def __parseHostmask__(self):
        nickname = self.__tok__[0].split(":")[1].split("!")[0]
        ident = self.__tok__[0].split("!")[1].split("@")[0]
        host = self.__tok__[0].split("@")[1]
        return (nickname, ident, host)
    
    # public
    def tokenize(self):
        return self.__tok__ # it is already being split in __init__ so we can simply return here
    
    def getRaw(self):
        return self.__raw__
    
    def getType(self):
        return self.__type__
        
    def getUser(self):
        return (self.__nick__, self.__ident__, self.__host__)
        
    def getNick(self): # there are some events where we only know the nickname, no ident or host (e.g. USERMODE)
        return self.__nick__
        
    def getServerName(self):
        return self.__server__
        
    def getTarget(self):
        return self.__target__
        
    def getVictim(self):
        return self.__victim__
        
    def getMessage(self):
        return self.__message__
        
    def getMode(self):
        return self.__mode__

    def getReplyTo(self):
        if (self.__target__[0] == '#'):
            return self.__target__
        else:
            return self.__nick__

    def isAuthed(self):
        return self.__authed__
