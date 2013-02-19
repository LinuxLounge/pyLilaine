import Queue, socket, ssl, select

from EventHandler import EventHandler

class IRC(object):
    def __init__(self, with_tls):
    	self.kill_received = False
        self.lin =  []
        self.lout = []
        self.events = EventHandler()
        self.max_msg_per_loop = 5
        # ping / pong
        self.max_ping_delay = 10 # seconds
        self.ping_interval = 120 # seconds
        self.ping_message = "keep-alive"
        # settings
        self.with_tls = with_tls
        self.reconnect_delay = 10
        # state
        self.connected = False
        self.connecting = False
        # init
        self.create()

    def addPluginSystem(self, qin, qout):
        self.lin.append(qin)
        self.lout.append(qout)
           
    def run(self):
        buf = ""
        while (not self.kill_received):
            ready_to_read, ready_to_write, in_error = select.select([self.handle],[],[], 0.5)
            if len(ready_to_read) == 1:
                buf = "%s%s" % (buf, self.get())
                lines = buf.split("\n")
                buf = lines.pop()

                # loop over incoming lines
                for line in lines:
                    print "<- %s" % line
                    tok = line.split()
                    
                    # PING request
                    if (tok[0] == "PING"):
                        self.put("PONG %s" % tok[1])
                    # PONG answer
                    elif (tok[1] == "PONG"):
                        if (tok[3].endswith(self.ping_message)):
                            self.events.cancel("reconnect")
                            self.events.register("timeout", self.ping_interval * 1000)
                    # passing on to the registered queues
                    else:
                        for qin in self.lin:
                            qin.put(line)

            for qout in self.lout:
                if (not qout.empty()):
                    i = 0
                    while (not qout.empty() and i < self.max_msg_per_loop):
                        self.put(qout.get())
                        i += 1
        print "Shutting down IRCD"
        self.handle.close()
        
    def update(self, diff):
        self.events.update(diff)
        
        while 1:
            event = self.events.next()
            if (not event):
                break
                
            if (event.getName() == "timeout"):
                if (self.connected):
                    self.put("PING :%s" % self.ping_message)
                    self.events.register("reconnect", self.max_ping_delay * 1000)
            elif (event.getName() == "reconnect"):
                self.reconnect()

    def kill(self):
        if (self.connected):
            self.put("QUIT :SIGINT")
        self.kill_received = True

    def killed(self):
        return self.kill_received

    def create(self):
        self.connected = False
        self.handle = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if (self.with_tls):
            self.handle = ssl.wrap_socket(self.handle)

    def connect(self, host, port, nickname, ident, realname, password = None):
        # remember for reconnect
        self.host = host
        self.port = port
        self.nickname = nickname
        self.ident = ident
        self.realname = realname
        self.password = password
        
        # connect socket
        self.connecting = True
        try:
            print "Connecting to %s:%d..." % (host, port)
            self.handle.connect((host, port))
        except socket.error as err:
            print "Unable to connect: %s" % err
            print "Retrying in %ss..." % self.reconnect_delay
            self.events.register("reconnect", self.reconnect_delay * 1000)
            return
        
        # authentication
        if (password != None):
            self.put("PASSWORD %s" % password)
            
        self.put("NICK %s" % nickname)
        self.put("USER %s %s pyLilaine :%s" % (ident, ident, realname))
        
        self.connecting = False
        self.connected = True
        self.events.register("timeout", self.ping_interval * 1000)
        
    def reconnect(self):
        '''
        in case we get disconnected the socket is destroyed
        and we have to create a new one
        '''
        self.connecting = True
        self.create()
        self.connect(self.host, self.port, self.nickname, self.ident, self.realname, self.password)
            
    def put(self, msg):
        try:
            print "-> %s" % msg
            self.handle.send("%s\n\n" % msg)
        except socket.error:
            if (not self.connecting):
                self.reconnect()
        
    def get(self):
        try:
            return self.handle.recv(1024)
        except socket.error:
            if (not self.connecting):
                self.reconnect()
        
