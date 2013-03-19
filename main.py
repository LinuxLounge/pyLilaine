from lib.IRC import IRC
from lib.PluginSystem import PluginSystem
from threading import Thread
import string, time, datetime, signal, ConfigParser

global plugins, last_ms

def update(SIG, FRM):
    global plugins, last_ms
    this_ms = datetime.datetime.now()
    diff = (this_ms - last_ms).microseconds / 1000
    last_ms = this_ms
    plugins.update(diff)
    irc.update(diff)



config = ConfigParser.RawConfigParser()
config.read('pylilaine.conf')


host = config.get("server","host")
port = config.getint("server","port")
ssl  = config.getboolean("server","ssl")

password = None

if (config.has_option("server", "password")):
    password = config.get("server","password")
        
    
nick = config.get("bot","nick")
ident = config.get("bot","ident")
realname = config.get("bot","realname")
description = config.get("bot", "description")
    

irc = IRC(ssl) # with_tls?
irc.connect(host, port, nick, ident, description, password)

plugins = PluginSystem(config.get("bot", "adminpw"))
plugins.loadDirectory(config.get("bot", "plugins"))

plugind = Thread(target=plugins.run)
plugind.start()

irc.addPluginSystem(plugins.qin, plugins.qout)

ircd = Thread(target=irc.run)
ircd.start()

# register handler for SIGALRM
signal.signal(signal.SIGALRM, update)
# set interval to 400 ms
signal.setitimer(signal.ITIMER_REAL, 0.4, 0.4)
last_ms = datetime.datetime.now()

while 1:
    try:
        time.sleep(1000)
    except KeyboardInterrupt:
        irc.kill()
        plugins.kill()
        break
