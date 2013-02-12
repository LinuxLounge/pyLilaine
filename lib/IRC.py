import socket, ssl, Queue, select

class IRC(object):
    def __init__(self, with_tls):
    	self.kill_received = False
        self.handle = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if with_tls:
            self.handle = ssl.wrap_socket(self.handle)        
        ##they are just passing raw data strings
        self.lin =  []
        self.lout = []
        self.max_msg_per_loop = 5
        
    def killed(self):
        return self.kill_received

    def addPluginSystem(self, qin, qout):
        self.lin.append(qin)
        self.lout.append(qout)
           
    def run(self):
        buf = ""
        while (not self.kill_received):

            #timeout is in seconds
            ready_to_read, ready_to_write, in_error = select.select([self.handle],[],[], 0.5)
            if len(ready_to_read) == 1:
                buf = "%s%s" % (buf, self.get())
                lines = buf.split("\n")
                buf = lines.pop()

                # loop over incoming lines
                for line in lines:
                    print "<- %s" % line
                    tok = line.split(" ", 2)
                    if (tok[0] == "PING"): # no plugin should care about PING/PONG
                        self.put("PONG %s" % tok[1])
                    else:
                        # passing on to the plugind's
                        for qin in self.lin:
                            qin.put(line)

            for qout in self.lout:
                if not qout.empty():
                    i = 0
                    while (not qout.empty() and i < self.max_msg_per_loop):
                        self.put(qout.get())
                        i += 1
        print "Shutting down IRCD"
        self.handle.close()
            # MOVE RELOAD TO PLUGINSYSTEM ITSELF
#              if tok[1] == "PRIVMSG" and tok[3] == ":reload":
#                    irc.put("PRIVMSG #lilaine :Reloading...")
#                    plugins.reload()
#                    irc.put("PRIVMSG #lilaine :Done!")

    def connect(self, host, port, nickname, ident, realname, password = None):
        self.handle.connect((host, port))
        
        # authentication
        if password != None:
            self.put("PASSWORD %s" % password)
            
        self.put("NICK %s" % nickname)
        self.put("USER %s %s pyLilaine :%s" % (ident, ident, realname))
            
    def put(self, msg):
        print "-> %s" % msg
        self.handle.send("%s\n\n" % msg)
        
    def get(self):
        return self.handle.recv(1024)
        
