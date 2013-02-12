class Message(object):
    def __init__(self, raw_message):
        self.raw = raw_message
        self.tok = self.raw.split()
        
        # tokenize elements
        self.type = self.tok[1]
        if "@" in self.tok[0]:
            (self.nick, self.ident, self.host) = self.parseHostmask()
        else:
            self.server = self.tok[0]
        #FIX TODO Check Specs
        self.target = self.tok[2]
        self.message = " ".join(self.tok[3:])
        if (self.type == "PRIVMSG") or (self.type == "NOTICE"):
            self.message = self.message[1:]
            if (ord(self.message[0]) == 1 and ord(self.message[-1]) == 1):
                self.type = "CTCP"
                self.message = self.message.split(chr(1))[1]
        if self.type.isdigit():
            self.message = " ".join(self.tok[2:])
            self.type = int(self.type)
        
    def tokenize(self):
        return self.tok
        
    def parseHostmask(self):
        nickname = self.tok[0].split(":")[1].split("!")[0]
        ident = self.tok[0].split("!")[1].split("@")[0]
        host = self.tok[0].split("@")[1]
        return (nickname, ident, host)
        
    def getType(self):
        return self.type

