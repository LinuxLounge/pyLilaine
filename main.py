from lib.IRC import IRC
from lib.PluginSystem import PluginSystem
from threading import Thread
import string

irc = IRC(False) # with_tls?
plugins = PluginSystem("plugins/")

irc.connect("localhost", 6667, "pyLilaine", "lilaine", "pyLilaine Two Point Oh!", None)

plugind = Thread(target=plugins.run)
#plugind.daemon = True
plugind.start()

irc.addPluginSystem(plugins.qin, plugins.qout)

ircd = Thread(target=irc.run)
#ircd.daemon = True
ircd.start()

while 1:
    try:
        ircd.join(5)
        plugind.join(5)
    except:
        ircd.kill_received = True
        plugind.kill_received = True


