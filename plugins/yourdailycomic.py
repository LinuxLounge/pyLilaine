from lib.EventHandler import EventHandler, Event
from lib.Plugin import Plugin
from time import mktime
import sqlite3, feedparser, dateutil.parser, datetime

class P(Plugin):
    def loaded(self):
        self.command = "comic"
        
        self.events = EventHandler()
        self.events.register("check", 30*1000*60, None)
        
        conn = sqlite3.connect("dailycomic.db");
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS yourdailycomic_urls (name TEXT, url TEXT, latestentry TEXT)")
        cursor.execute("CREATE TABLE IF NOT EXISTS yourdailycomic_comics (cid INTEGER, title TEXT, link TEXT, published TEXT)")
        cursor.execute("CREATE TABLE IF NOT EXISTS yourdailycomic_channels (name TEXT)")
        conn.commit()
        conn.close()  
        print "yourdailycomic module loaded"
    
    def update(self, diff):
        self.events.update(diff)
        
        while 1:
            event = self.events.next()
            if not event:
                break
                
            if (event.getName() == "check"):
                self.checkforcomics()
                self.events.register("check", 30*1000*60, None)
    
    def checkforcomics(self):
        print "Checking for comics"
        conn = sqlite3.connect("dailycomic.db");
        cursor = conn.cursor()

        channels = cursor.execute("SELECT name FROM yourdailycomic_channels").fetchall()


        for row in cursor.execute("SELECT ROWID, name, url, latestentry FROM yourdailycomic_urls").fetchall():
            print "Checking Comic %s" % (row[1])
            feed = feedparser.parse(row[2])
            curr = dateutil.parser.parse(row[3], ignoretz=True)
            latest = curr
            for i in range(len(feed.entries)-1, -1, -1):
                entry = feed.entries[i]
                
                if (not hasattr(entry, "title")):
                    entry.title = row[1]
                if (not hasattr(entry, "link")):
                    entry.link = "No Link provided"
                
                if (not hasattr(entry, "published")):
                    if (not hasattr(entry, "updated")):
                        if ( len(cursor.execute("SELECT title FROM yourdailycomic_comics WHERE cid = ? AND title  = ?",(row[0], entry.title)).fetchall()) == 0):
                            entry.published = datetime.date.today().isoformat()
                        else:
                            continue 
                        
                    else:
                        entry.published = entry.updated
                
                tmpd = dateutil.parser.parse(entry.published, ignoretz=True)
                if (tmpd > curr):
                    if (tmpd > latest):
                        latest = tmpd
                    for chan in channels:
                        self.send("PRIVMSG %s New Comic on %s: %s (%s) " % (chan[0],row[1], entry.title, entry.link))
                    cursor.execute("INSERT INTO yourdailycomic_comics (cid, title, link, published) VALUES (?,?,?,?)",(row[0], entry.title, entry.link, tmpd.isoformat()))
            cursor.execute("UPDATE yourdailycomic_urls SET latestentry = ? WHERE ROWID = ? ", (latest.isoformat(), row[0]))
        conn.commit()
        conn.close()
        print "Commic Check done"

    def todayComics(self, target):
        td = datetime.date.today().isoformat()
        conn = sqlite3.connect("dailycomic.db");
        cursor = conn.cursor()
        self.send("PRIVMSG %s Today's comics:" % (target))
        i = 0
        for row in cursor.execute("SELECT name, title, link FROM yourdailycomic_urls JOIN  yourdailycomic_comics ON yourdailycomic_urls.ROWID = cid WHERE published >= ?", [td] ).fetchall():
            self.send("PRIVMSG %s %s: %s (%s) " % (target, row[0], row[1], row[2]))
            i += 1
            
        if i == 0:
            self.send("PRIVMSG %s There were no comics published" % (target))
   
   
    def addComic(self, name, url):
        conn = sqlite3.connect("dailycomic.db");
        cursor = conn.cursor()
        d = datetime.datetime(datetime.MINYEAR, 1, 1);
        cursor.execute("INSERT INTO yourdailycomic_urls (name, url, latestentry) VALUES(?,?,?)", (name, url, d.isoformat()))
        conn.commit()
        conn.close()

    def listSubs(self, target):
        conn = sqlite3.connect("dailycomic.db");
        cursor = conn.cursor()
        subs = ""
        for row in cursor.execute("SELECT name FROM yourdailycomic_urls").fetchall():
            subs += row[0]+", "
        self.send("PRIVMSG %s %s " % (target, subs[:-2]))
        conn.close()

    def addChannel(self, name):
        conn = sqlite3.connect("dailycomic.db");
        cursor = conn.cursor()
        cursor.execute("INSERT INTO yourdailycomic_channels (name) VALUES (?)", [name])
        conn.commit()
        conn.close()

    def rmChannel(self, name):
        conn = sqlite3.connect("dailycomic.db");
        cursor = conn.cursor()
        cursor.execute("DELETE FROM yourdailycomic_channels WHERE name = ?", [name])
        conn.commit()
        conn.close()

    def listChannels(self, target):
        conn = sqlite3.connect("dailycomic.db");
        cursor = conn.cursor()
        chans = "" 
        for row in cursor.execute("SELECT name FROM yourdailycomic_channels").fetchall():        
            chans += row[0]+", "    
        self.send("PRIVMSG %s %s" % (target, chans[:-2]))
        conn.close()

    def onCommand(self, target,  msg):
        tok = msg.getMessage().split()
        tokl = len(tok)
        
        #default
        if (tokl < 2):
            self.todayComics(target)
        elif(tok[1] == "help"):
            self.send("PRIVMSG %s Available Commands: " % (target))
            self.send("PRIVMSG %s !comic - Today's comics: " % (target))
            self.send("PRIVMSG %s !comic <check|subs> - Check for Comics/List comics" % (target))
            self.send("PRIVMSG %s !comic <add> <name> <feedurl>" % (target))
            self.send("PRIVMSG %s !comic chan <add|rm|list> <channel> - Manage channels" % (target))
            
        
        elif (tok[1] == "subs"):
            self.listSubs(target)

        elif (tok[1] == "check"):
            self.checkforcomics()
        elif (tok[1] == "add"):
            if (tokl < 4):
                self.send("PRIVMSG %s Syntax: !comic add <name> <url>" % (target))
            else:
                self.addComic(tok[2], tok[3])
                
        elif (tok[1] == "chan"):
        
                if (tok[2] == "list"):
                    self.listChannels(target)
                elif( tokl < 4 ):
                    self.send("PRIVMSG %s Syntax: !comic chan <add|rm|list> <channel> " %(target))
                elif(not msg.isAuthed()):
                    self.send("PRIVMSG %s You have to be authed for this operation" % (target))
                elif (tok[2] == "add" ):
                    self.addChannel(tok[3])
                    
                elif (tok[2] == "rm" ):
                    self.rmChannel(tok[3])
                else:
                    self.send("PRIVMSG %s Unknown command" % (target))
        else:
               self.send("PRIVMSG %s Unknown command" % (target))
