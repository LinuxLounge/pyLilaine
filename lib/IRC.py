import queue, socket, ssl, select

from .EventHandler import EventHandler

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

    def addPluginSystem(self, qin, qout):
        self.lin.append(qin)
        self.lout.append(qout)
           
    def run(self):
        buf = ""
        while (not self.kill_received):
            ready_to_read, ready_to_write, in_error = select.select([self.handle],[],[], 0.5)
            if len(ready_to_read) == 1:
                buf += self.get()       # just append, as we don't know where the newlines are
                lines = buf.split("\n") # then make a list, splitting by newlines
                buf = lines.pop()       # but remove the last element, which is incomplete

                # loop over incoming lines
                for line in lines:
                    print("<- %s" % line)
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
        print("Disconnecting...")
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
            self.handle.close()
        self.kill_received = True

    def killed(self):
        return self.kill_received

    def connect(self, host, port, nickname, ident, realname, password = None):
        self.connected = False

        # remember for reconnect
        self.host = host
        self.port = port
        self.nickname = nickname
        self.ident = ident
        self.realname = realname
        self.password = password
        
        # resolve address now
        ai_list = socket.getaddrinfo(host, port)
        (af, socktype, proto, cn, sockaddr) = ai_list[0] # lets just look at the first entry for now

        # and create the socket
        self.handle = socket.socket(af, socktype, proto)

        # wrap this in tls if requested
        if (self.with_tls):
            self.handle = ssl.wrap_socket(self.handle)

        # and connect
        self.connecting = True
        try:
            print("Connecting to %s:%d..." % (sockaddr[0], sockaddr[1]))
            self.handle.connect(sockaddr)
        except socket.error as err:
            print("Unable to connect: %s" % err)
            print("Retrying in %ss..." % self.reconnect_delay)
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
        in case we get disconnected destroy the socket
        and reconnect
        '''
        self.handle.close()
        self.connecting = True
        self.connect(self.host, self.port, self.nickname, self.ident, self.realname, self.password)
            
    def put(self, msg):
        try:
            print("-> %s" % msg)
            self.handle.send(bytes("%s\n\n" % msg, 'UTF-8'))
        except socket.error:
            if (not self.connecting):
                self.reconnect()
        
    def get(self):
        try:
            return self.handle.recv(1024).decode('UTF-8')
        except socket.error:
            if (not self.connecting):
                self.reconnect()
            return ""
        except UnicodeDecodeError:
            print("Caught UnicodeDecodeError in IRC::get()")
            return ""

