from lib.IRC import IRC
from lib.PluginSystem import PluginSystem
from threading import Thread
import string

irc = IRC(False) # with_tls?
plugins = PluginSystem("plugins/")

irc.connect("localhost", 6667, "pyLilaine", "lilaine", "pyLilaine Two Point Oh!", None)

plugind = Thread(target=plugins.run)
plugind.start()

irc.addPluginSystem(plugins.qin, plugins.qout)

ircd = Thread(target=irc.run)
ircd.start()

while 1:
    try:
        ircd.join(2)
        plugind.join(2)
    except KeyboardInterrupt:
        irc.kill_received = True
        plugins.kill_received = True
        break
