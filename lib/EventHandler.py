import Queue

class Event(object):
    def __init__(self, name, timer, blob = None):
        self.timer = timer
        self.name = name
        self.blob = blob

    def getName(self):
        return self.name
        
    def getRemainder(self):
        return self.timer
        
    def getBlob(self):
        return self.blob

    def update(self, diff):
        self.timer -= diff

    def hasPassed(self):
        return self.timer <= 0

class EventHandler(object):
    def __init__(self):
        self.__events = []
        self.__finished = Queue.Queue()
        
    def update(self, diff):
        for event in self.__events:
            event.update(diff)
            if (event.hasPassed()):
                self.__finished.put(event)
                self.__events.remove(event)

    def next(self):
        try:
            return self.__finished.get(False) # do not block here
        except Queue.Empty:
            return False
        
    def register(self, name, delay, blob = None):
        self.__events.append(Event(name, delay, blob))
       
    def cancel(self, name):
        self.__events = [event for event in self.__events if event.getName() != name]
