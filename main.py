from lib.IRC import IRC
from lib.PluginSystem import PluginSystem
from threading import Thread
import string, time, datetime, signal

global plugins, last_ms

def update(SIG, FRM):
    global plugins, last_ms
    this_ms = datetime.datetime.now()
    diff = (this_ms - last_ms).microseconds
    last_ms = this_ms
    plugins.update(diff/1000) #to ms

irc = IRC(False) # with_tls?
plugins = PluginSystem("plugins/")

irc.connect("localhost", 6667, "pyLilaine", "lilaine", "pyLilaine Two Point Oh!", None)

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
