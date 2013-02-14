from lib.IRC import IRC
from lib.PluginSystem import PluginSystem
from threading import Thread
import string, time, datetime

irc = IRC(False) # with_tls?
plugins = PluginSystem("plugins/")

irc.connect("localhost", 6667, "pyLilaine", "lilaine", "pyLilaine Two Point Oh!", None)

plugind = Thread(target=plugins.run)
plugind.start()

irc.addPluginSystem(plugins.qin, plugins.qout)

ircd = Thread(target=irc.run)
ircd.start()

last_ms = datetime.datetime.now()
while 1:
    this_ms = datetime.datetime.now()
    diff = (this_ms - last_ms).microseconds
    last_ms = this_ms

    plugins.update(diff / 1000) # to ms

    try: # joining a thread delays the main thread, so their timeouts added equals the update diff
        ircd.join(0.2)
        plugind.join(0.2)
    except KeyboardInterrupt:
        irc.kill()
        plugins.kill()
        break
