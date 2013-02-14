class Message(object):
    def __init__(self, raw_message):
        self.__raw__ = raw_message
        self.__tok__ = self.__raw__.split()
        
        # type
        self.__type__ = self.__tok__[1]

        # server / user!ident@host
        if "@" in self.__tok__[0]:
            (self.__nick__, self.__ident__, self.__host__) = self.__parseHostmask__()
        else:
            self.__server__ = self.__tok__[0][1:]
        
        # target    
        self.__target__ = self.__tok__[2]
        
        # message
        self.__message__ = " ".join(self.__tok__[3:])[1:] # strip leading colon        
        # PRIVMSG
        if (self.__type__ == "PRIVMSG"):
            # CTCP (is actually a PRIVMSG, but we treat it as type=CTCP)
            try:
                if (ord(self.__message__[0]) == 1 and ord(self.__message__[-1]) == 1):
                    self.__type_ = "CTCP"
                    self.__message__ = self.__message__.split(chr(1))[1]
            except IndexError:
                pass
                
        # NOTICE NICK TOPIC PART
        # are already handled above, at this time no further optimization necessary
        elif (self.__type__ == "NOTICE") or (self.__type__ == "NICK") or (self.__type__ == "TOPIC") or (self.__type__ == "PART"):
            pass
        
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
                self.__mode__ = self.__message__
            else:
                self.__mode__ = " ".join(self.__tok__[3:]) # channels modes are prefixed with a colon while usermodes aren't
        
        # KICK
        # has two targets, channel and nick
        elif (self.__type__ == "KICK"):
            self.__victim__ = self.__tok__[3]
            self.__message__ = " ".join(self.__tok__[4:])[1:]
        
        # Numerical RAW
        elif self.__type__.isdigit():
            self.__message__ = " ".join(self.__tok__[2:])
            self.__type__ = int(self.__type__)
        else:
            # we might remove this later, but for now we need to test if everything is handled properly
            print "[warning] Message objected with unhandled type '%s' created." % self.__type__

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

